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

# Persistent Disk pricing (USD per GB-month).
# pd-extreme is the per-GB capacity rate ($0.125); provisioned IOPS
# ($0.065/IOPS-month) are billed separately and not modeled here.
# Pricing last verified: 2026-07 — https://cloud.google.com/compute/disks-image-pricing
_PD_PRICES: dict[str, float] = {
    "pd-ssd": 0.170,
    "pd-standard": 0.040,
    "pd-extreme": 0.125,
}

# Network egress pricing (USD/GB, tiered): free tier 1 GB, then
# 0.12 up to 1 TB, 0.11 for 1–10 TB, 0.08 beyond 10 TB.
_EGRESS_TIERS: list[tuple[float, float]] = [
    (1, 0.00),
    (1023, 0.12),  # remainder of first 1 TB
    (9216, 0.11),  # 1 TB – 10 TB
    (float("inf"), 0.08),
]

# Fallback regional price multipliers relative to us-east1.
# Verified against cloud.google.com pricing tables for e2/n2 (2026-07).
_FALLBACK_REGION_MULTIPLIER: dict[str, float] = {
    "us-east1": 1.00,
    "us-west1": 1.00,
    "europe-west1": 1.10,
    "asia-northeast1": 1.28,
    "asia-northeast3": 1.28,
    "asia-southeast1": 1.23,
    "asia-east2": 1.40,
    "asia-east1": 1.16,
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
        api_price = await self._fetch_instance_price(
            instance_type, gcp_region, instance["vcpu"], instance["ram"]
        )
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
        # E2 custom shapes require an even vCPU count (2–32) and 0.5–8 GB RAM
        # per vCPU (max 128 GB), so bill against the nearest valid shape and
        # skip the substitution entirely when the spec exceeds E2 limits.
        custom_vcpu = max(2, spec.cpu_cores + (spec.cpu_cores % 2))
        custom_ram = max(spec.ram_gb, custom_vcpu * 0.5)
        if custom_vcpu <= 32 and custom_ram <= min(128.0, custom_vcpu * 8.0):
            custom_hourly = (
                custom_vcpu * _E2_CUSTOM_VCPU_RATE
                + custom_ram * _E2_CUSTOM_RAM_RATE
            ) * region_mult
            if custom_hourly < hourly_od:
                hourly_od = custom_hourly
                hourly_cud = hourly_od * _FALLBACK_CUD_1Y_DISCOUNT
                instance_type = (
                    f"e2-custom-{custom_vcpu}-{int(custom_ram * 1024)}"
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
        self, instance_type: str, region: str, vcpu: float, ram_gb: float
    ) -> Optional[float]:
        """Query the GCP Cloud Billing Catalog API for on-demand hourly price.

        Compute Engine bills VMs through two separate SKUs — one per
        vCPU-hour and one per GB-hour of RAM (e.g. "N2 Instance Core
        running in Americas" / "N2 Instance Ram running in Americas") —
        so both unit rates are collected and combined with the matched
        machine's vCPU count and RAM size. Returns hourly price in USD,
        or None on failure / no matching SKUs.
        """
        if not self._api_key:
            return None

        series = instance_type.split("-")[0].lower()
        # C2 SKU descriptions read "Compute optimized Core/Ram", not "C2 ...".
        series_kw = "compute optimized" if series == "c2" else f"{series} instance"

        try:
            client = await self._get_client()
            core_rate: Optional[float] = None
            ram_rate: Optional[float] = None

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

                for sku in data.get("skus", []):
                    desc = sku.get("description", "").lower()
                    category = sku.get("category", {})

                    if category.get("usageType") != "OnDemand":
                        continue
                    if series_kw not in desc:
                        continue
                    excluded = (
                        "preemptible", "spot", "commitment", "custom",
                        "sole tenancy", "reserved",
                    )
                    if any(term in desc for term in excluded):
                        continue
                    if not self._region_matches(sku, region):
                        continue

                    price = self._extract_hourly_unit_price(sku)
                    if price is None:
                        continue

                    if "core" in desc and core_rate is None:
                        core_rate = price
                    elif "ram" in desc and ram_rate is None:
                        ram_rate = price

                    if core_rate is not None and ram_rate is not None:
                        return core_rate * vcpu + ram_rate * ram_gb

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
    def _region_matches(sku: dict, region: str) -> bool:
        """Check whether a SKU applies to the given region."""
        region = region.lower()
        service_regions = [r.lower() for r in sku.get("serviceRegions", [])]
        if any(region in sr for sr in service_regions):
            return True
        geo = sku.get("geoTaxonomy", {})
        geo_regions = [r.lower() for r in geo.get("regions", [])]
        return any(region in gr for gr in geo_regions)

    @staticmethod
    def _extract_hourly_unit_price(sku: dict) -> Optional[float]:
        """Extract the per-unit hourly USD price from a SKU, if hourly."""
        pricing_info = sku.get("pricingInfo", [])
        if not pricing_info:
            return None
        pricing_expr = pricing_info[0].get("pricingExpression", {})

        # Catalog API reports compute usage in hours as usageUnit "h"
        usage_unit = pricing_expr.get("usageUnit", "").lower()
        unit_desc = pricing_expr.get("usageUnitDescription", "").lower()
        if usage_unit not in ("h", "hr", "hour") and "hour" not in unit_desc:
            return None

        tiered_rates = pricing_expr.get("tieredRates", [])
        if not tiered_rates:
            return None
        unit_price = tiered_rates[-1].get("unitPrice", {})
        nanos = int(unit_price.get("nanos", 0))
        units = int(unit_price.get("units", 0))
        price = units + nanos / 1_000_000_000
        return price if price > 0 else None
