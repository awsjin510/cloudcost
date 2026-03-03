"""GCP cost calculator using the Cloud Billing Catalog API.

The module queries the public GCP Cloud Billing Catalog API for Compute
Engine pricing. An API key is required (set GCP_API_KEY env var) but the
API itself is free to use. No OAuth / service account needed.

API docs: https://cloud.google.com/billing/v1/how-tos/catalog-api

Architecture:
  1. Query Cloud Billing Catalog API for Compute Engine SKUs.
  2. Match SKU descriptions to the target instance type + region.
  3. Extract On-Demand and CUD (Committed Use Discount) pricing.
  4. Fall back to embedded pricing tables if API key is missing or API fails.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx

from cloudcost.models.naming import get_provider_region, match_instance
from cloudcost.models.spec import (
    CloudProvider,
    CloudSpec,
    PricingResult,
    PricingTier,
    ProviderEstimate,
)

from cloudcost.utils.pricing import calc_tiered_cost

from .base import BaseCalculator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GCP Cloud Billing Catalog API
# ---------------------------------------------------------------------------
GCP_BILLING_API = "https://cloudbilling.googleapis.com/v1"
COMPUTE_SERVICE_ID = "6F81-5844-456A"  # Compute Engine service ID

# ---------------------------------------------------------------------------
# Fallback on-demand pricing (USD/hour, us-east1 baseline, Linux)
# Used when API key is missing or API is unreachable
# ---------------------------------------------------------------------------
_FALLBACK_PRICES: dict[str, float] = {
    "e2-micro": 0.00838,
    "e2-small": 0.01675,
    "e2-medium": 0.03351,
    "e2-standard-2": 0.06701,
    "e2-standard-4": 0.13402,
    "e2-standard-8": 0.26805,
    "e2-standard-16": 0.53609,
    "e2-standard-32": 1.07218,
    "n2-standard-2": 0.09710,
    "n2-standard-4": 0.19420,
    "n2-standard-8": 0.38840,
    "n2-standard-16": 0.77680,
    "n2-standard-32": 1.55360,
    "n2-standard-48": 2.33040,
    "n2-standard-64": 3.10720,
    "c2-standard-4": 0.20990,
    "c2-standard-8": 0.41980,
    "c2-standard-16": 0.83960,
    "n2-highmem-2": 0.13110,
    "n2-highmem-4": 0.26220,
    "n2-highmem-8": 0.52440,
    "n2-highmem-16": 1.04880,
}

# 1-year CUD discount ratio (approximate, used as fallback)
_FALLBACK_CUD_1Y_DISCOUNT = 0.63

# E2 custom instance per-unit rates (us-east1 baseline, USD/hr)
# When requested RAM < matched standard instance's RAM, custom is cheaper.
_E2_CUSTOM_VCPU_RATE = 0.022859
_E2_CUSTOM_RAM_RATE = 0.003067

# Persistent Disk pricing (USD per GB-month)
_PD_PRICES: dict[str, float] = {
    "pd-ssd": 0.170,
    "pd-standard": 0.040,
    "pd-extreme": 0.250,
}

# Network egress pricing (USD/GB, tiered)
_EGRESS_TIERS: list[tuple[float, float]] = [
    (1, 0.00),
    (1024, 0.12),
    (10240, 0.11),
    (float("inf"), 0.08),
]

# Fallback regional price multipliers relative to us-east1
_FALLBACK_REGION_MULTIPLIER: dict[str, float] = {
    "us-east1": 1.00,
    "us-west1": 1.00,
    "europe-west1": 1.10,
    "asia-northeast1": 1.22,
    "asia-northeast3": 1.22,
    "asia-southeast1": 1.13,
    "asia-east2": 1.16,
    "asia-east1": 1.11,
}

# GCP region to human-readable description mapping (for SKU matching)
_GCP_REGION_TO_DESCRIPTION: dict[str, list[str]] = {
    "us-east1": ["us-east1", "americas"],
    "us-west1": ["us-west1", "americas"],
    "europe-west1": ["europe-west1", "emea"],
    "asia-northeast1": ["asia-northeast1", "asia pacific", "tokyo"],
    "asia-northeast3": ["asia-northeast3", "asia pacific", "seoul"],
    "asia-southeast1": ["asia-southeast1", "asia pacific", "singapore"],
    "asia-east2": ["asia-east2", "asia pacific", "hong kong"],
    "asia-east1": ["asia-east1", "asia pacific", "taiwan"],
}


class GCPCalculator(BaseCalculator):
    """GCP Compute Engine cost estimator using the Cloud Billing Catalog API."""

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None) -> None:
        super().__init__(http_client)
        self._api_key = os.environ.get("GCP_API_KEY", "")

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        gcp_region = get_provider_region(spec.region, CloudProvider.GCP)
        instance = match_instance(spec, CloudProvider.GCP)
        instance_type = instance["type"]

        warnings: list[str] = []

        # --- Compute pricing (try API first, then fallback) ---
        api_price = await self._fetch_instance_price(instance_type, gcp_region)
        region_mult = _FALLBACK_REGION_MULTIPLIER.get(gcp_region, 1.15)

        if api_price is not None:
            hourly_od = api_price
            hourly_cud = hourly_od * _FALLBACK_CUD_1Y_DISCOUNT
        else:
            # Fallback to embedded tables
            base_hourly = _FALLBACK_PRICES.get(instance_type)
            if base_hourly is None:
                base_hourly = 0.10
                warnings.append(f"No pricing data for {instance_type}, using estimate")

            hourly_od = base_hourly * region_mult
            hourly_cud = hourly_od * _FALLBACK_CUD_1Y_DISCOUNT

            if not self._api_key:
                warnings.append(
                    "Using fallback pricing — set GCP_API_KEY env var for live API data"
                )
            else:
                warnings.append(
                    f"Used fallback pricing for {instance_type} — GCP API unreachable"
                )

        # Check if an e2-custom instance is cheaper than the matched standard
        # instance. This happens when the user's requested RAM is less than
        # the standard instance's RAM (e.g. 2 GB requested → e2-medium has 4 GB).
        custom_hourly = (
            spec.cpu_cores * _E2_CUSTOM_VCPU_RATE
            + spec.ram_gb * _E2_CUSTOM_RAM_RATE
        ) * region_mult
        if custom_hourly < hourly_od:
            hourly_od = custom_hourly
            hourly_cud = hourly_od * _FALLBACK_CUD_1Y_DISCOUNT
            instance_type = (
                f"e2-custom-{spec.cpu_cores}-{int(spec.ram_gb * 1024)}"
            )
            warnings.append(
                "Using e2-custom instance (more cost-effective for this spec)"
            )

        monthly_hours = spec.monthly_hours
        compute_od = hourly_od * monthly_hours
        compute_cud = hourly_cud * monthly_hours

        # Storage
        pd_type = "pd-ssd"
        if spec.storage_type.value == "hdd":
            pd_type = "pd-standard"
        elif spec.storage_type.value == "nvme":
            pd_type = "pd-extreme"
        storage_monthly = spec.storage_gb * _PD_PRICES.get(pd_type, 0.17)

        # Network
        network_monthly = calc_tiered_cost(spec.network_transfer_gb, _EGRESS_TIERS)

        total_od = compute_od + storage_monthly + network_monthly
        total_cud = compute_cud + storage_monthly + network_monthly

        details_od = {
            "compute": round(compute_od, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
            "disk_type": pd_type,
        }
        details_cud = {
            "compute": round(compute_cud, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
            "disk_type": pd_type,
        }

        on_demand = PricingResult(
            provider=CloudProvider.GCP,
            tier=PricingTier.ON_DEMAND,
            instance_type=instance_type,
            hourly_cost=round(hourly_od, 4),
            monthly_cost=round(total_od, 2),
            details=details_od,
        )
        reserved_1y = PricingResult(
            provider=CloudProvider.GCP,
            tier=PricingTier.RESERVED_1Y,
            instance_type=instance_type,
            hourly_cost=round(hourly_cud, 4),
            monthly_cost=round(total_cud, 2),
            details=details_cud,
            notes=["GCP 1-Year Committed Use Discount (CUD)"],
        )

        return ProviderEstimate(
            provider=CloudProvider.GCP,
            region_name=gcp_region,
            matched_instance=instance_type,
            on_demand=on_demand,
            reserved_1y=reserved_1y,
            total_monthly_on_demand=round(total_od, 2),
            total_monthly_reserved_1y=round(total_cud, 2),
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # GCP Cloud Billing Catalog API helpers
    # ------------------------------------------------------------------

    async def _fetch_instance_price(
        self, instance_type: str, region: str
    ) -> Optional[float]:
        """Query the GCP Cloud Billing Catalog API for on-demand hourly price.

        Scans Compute Engine SKUs for the matching instance type and region.
        Returns hourly price in USD, or None on failure.
        """
        if not self._api_key:
            return None

        try:
            client = await self._get_client()
            region_keywords = _GCP_REGION_TO_DESCRIPTION.get(region, [region])

            # Instance type to search terms (e.g., "n2-standard-4" -> "N2 Standard")
            family, size = self._parse_instance_family(instance_type)

            page_token = ""
            while True:
                params: dict[str, Any] = {
                    "key": self._api_key,
                    "currencyCode": "USD",
                    "pageSize": 5000,
                }
                if page_token:
                    params["pageToken"] = page_token

                url = f"{GCP_BILLING_API}/services/{COMPUTE_SERVICE_ID}/skus"
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

                skus = data.get("skus", [])
                for sku in skus:
                    desc = sku.get("description", "").lower()
                    category = sku.get("category", {})
                    resource_group = category.get("resourceGroup", "").lower()
                    usage_type = category.get("usageType", "")

                    # Match: on-demand, correct family, correct region
                    if usage_type != "OnDemand":
                        continue
                    if family.lower() not in desc:
                        continue
                    if "preemptible" in desc or "spot" in desc or "commitment" in desc:
                        continue

                    # Check region match via service regions
                    service_regions = [
                        r.lower() for r in sku.get("serviceRegions", [])
                    ]
                    region_match = any(
                        region.lower() in sr for sr in service_regions
                    )
                    if not region_match:
                        # Also check geo taxonomy
                        geo = sku.get("geoTaxonomy", {})
                        geo_regions = [
                            r.lower() for r in geo.get("regions", [])
                        ]
                        region_match = any(
                            region.lower() in gr for gr in geo_regions
                        )
                    if not region_match:
                        continue

                    # Extract pricing
                    pricing_info = sku.get("pricingInfo", [])
                    if not pricing_info:
                        continue
                    pricing_expr = (
                        pricing_info[0]
                        .get("pricingExpression", {})
                    )
                    tiered_rates = pricing_expr.get("tieredRates", [])
                    if not tiered_rates:
                        continue

                    # Get the unit price (usually in nanos)
                    unit_price = tiered_rates[-1].get("unitPrice", {})
                    nanos = int(unit_price.get("nanos", 0))
                    units = int(unit_price.get("units", 0))
                    price = units + nanos / 1_000_000_000

                    if price > 0:
                        # The API returns price per unit. For VMs, we need
                        # to multiply by the number of cores/units.
                        usage_unit = pricing_expr.get("usageUnit", "")
                        if "hour" in usage_unit.lower():
                            # Check if this is per-core or per-instance
                            vcpu_count = self._get_instance_vcpu(instance_type)
                            if "core" in resource_group or "cpu" in resource_group:
                                return price * vcpu_count
                            return price

                page_token = data.get("nextPageToken", "")
                if not page_token:
                    break

            return None

        except Exception:
            logger.warning(
                "Failed to fetch GCP pricing for %s in %s",
                instance_type,
                region,
                exc_info=True,
            )
            return None

    @staticmethod
    def _parse_instance_family(instance_type: str) -> tuple[str, str]:
        """Parse instance type like 'n2-standard-4' into ('N2 Standard', '4')."""
        parts = instance_type.split("-")
        if len(parts) >= 3:
            family = f"{parts[0]} {parts[1]}"
            size = parts[2]
        elif len(parts) == 2:
            family = parts[0]
            size = parts[1]
        else:
            family = instance_type
            size = ""
        return family, size

    @staticmethod
    def _get_instance_vcpu(instance_type: str) -> int:
        """Extract vCPU count from instance type name."""
        parts = instance_type.split("-")
        try:
            return int(parts[-1])
        except (ValueError, IndexError):
            return 1

