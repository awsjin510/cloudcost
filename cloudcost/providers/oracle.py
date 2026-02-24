"""Oracle Cloud Infrastructure (OCI) cost calculator using the public pricing API.

The module queries Oracle's public pricing JSON endpoint used by the
official OCI Cost Estimator. No authentication is needed.

Pricing source: https://www.oracle.com/cloud/costestimator.html
API endpoint:   https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/

Architecture:
  1. Fetch OCI product pricing from the public API.
  2. Match compute products to the target instance type.
  3. Extract On-Demand and Annual Flex pricing.
  4. Fall back to embedded pricing tables if API is unreachable.
"""

from __future__ import annotations

import logging
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
# OCI Public Pricing API
# ---------------------------------------------------------------------------
OCI_PRICING_API = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/"

# Mapping from our instance names to OCI part numbers / search terms
_OCI_INSTANCE_TO_PART: dict[str, str] = {
    "VM.Standard.E4.Flex": "B93581",    # E4 Flex OCPU
    "VM.Standard3.Flex": "B92384",      # Standard3 Flex OCPU
    "VM.Optimized3.Flex": "B92386",     # Optimized3 Flex OCPU
}

# ---------------------------------------------------------------------------
# Fallback pricing (USD/hour) when API is unreachable
# ---------------------------------------------------------------------------
_FALLBACK_PRICES: dict[str, float] = {
    "VM.Standard.E4.Flex-1": 0.01,
    "VM.Standard.E4.Flex-2": 0.02,
    "VM.Standard.E4.Flex-4": 0.04,
    "VM.Standard.E4.Flex-8": 0.08,
    "VM.Standard.E4.Flex-16": 0.16,
    "VM.Standard3.Flex-2": 0.032,
    "VM.Standard3.Flex-4": 0.064,
    "VM.Standard3.Flex-8": 0.128,
    "VM.Standard3.Flex-16": 0.256,
    "VM.Optimized3.Flex-2": 0.036,
    "VM.Optimized3.Flex-4": 0.072,
    "VM.Optimized3.Flex-8": 0.144,
}

# OCI doesn't have traditional reserved instances in the same way;
# they offer Annual Flex pricing at roughly 50% discount.
_FALLBACK_ANNUAL_FLEX_DISCOUNT = 0.50

# Block Volume pricing (USD per GB-month)
_BLOCK_VOLUME_PRICES: dict[str, float] = {
    "ssd": 0.0255,
    "hdd": 0.0255,  # OCI balanced is same price
    "nvme": 0.0340,
}

# Network egress tiers: first 10 TB/month free, then $0.0085/GB
_EGRESS_TIERS: list[tuple[float, float]] = [
    (10240, 0.00),          # first 10 TB free
    (float("inf"), 0.0085), # beyond 10 TB
]


class OracleCalculator(BaseCalculator):
    """OCI cost estimator using the public Oracle pricing API."""

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None) -> None:
        self._client = http_client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        oci_region = get_provider_region(spec.region, CloudProvider.ORACLE)
        instance = match_instance(spec, CloudProvider.ORACLE)
        instance_type = instance["type"]

        warnings: list[str] = []

        # --- Compute pricing (try API first, then fallback) ---
        api_prices = await self._fetch_compute_price(instance_type)

        if api_prices:
            hourly_od = api_prices["on_demand"]
            hourly_annual = api_prices.get(
                "annual_flex", hourly_od * _FALLBACK_ANNUAL_FLEX_DISCOUNT
            )
        else:
            # Fallback to embedded tables
            base_hourly = _FALLBACK_PRICES.get(instance_type)
            if base_hourly is None:
                base_hourly = 0.03
                warnings.append(f"No pricing data for {instance_type}, using estimate")

            hourly_od = base_hourly
            hourly_annual = hourly_od * _FALLBACK_ANNUAL_FLEX_DISCOUNT
            warnings.append(
                f"Used fallback pricing for {instance_type} — OCI API unreachable"
            )

        monthly_hours = spec.monthly_hours
        compute_od = hourly_od * monthly_hours
        compute_annual = hourly_annual * monthly_hours

        # Storage
        storage_key = spec.storage_type.value
        storage_rate = _BLOCK_VOLUME_PRICES.get(storage_key, 0.0255)
        storage_monthly = spec.storage_gb * storage_rate

        # Network — OCI has generous free tier (first 10 TB free)
        network_monthly = calc_tiered_cost(spec.network_transfer_gb, _EGRESS_TIERS)

        total_od = compute_od + storage_monthly + network_monthly
        total_annual = compute_annual + storage_monthly + network_monthly

        details_od = {
            "compute": round(compute_od, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
        }
        details_annual = {
            "compute": round(compute_annual, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
        }

        on_demand = PricingResult(
            provider=CloudProvider.ORACLE,
            tier=PricingTier.ON_DEMAND,
            instance_type=instance_type,
            hourly_cost=round(hourly_od, 4),
            monthly_cost=round(total_od, 2),
            details=details_od,
        )
        reserved_1y = PricingResult(
            provider=CloudProvider.ORACLE,
            tier=PricingTier.RESERVED_1Y,
            instance_type=instance_type,
            hourly_cost=round(hourly_annual, 4),
            monthly_cost=round(total_annual, 2),
            details=details_annual,
            notes=["OCI Annual Flex commitment pricing"],
        )

        return ProviderEstimate(
            provider=CloudProvider.ORACLE,
            region_name=oci_region,
            matched_instance=instance_type,
            on_demand=on_demand,
            reserved_1y=reserved_1y,
            total_monthly_on_demand=round(total_od, 2),
            total_monthly_reserved_1y=round(total_annual, 2),
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # OCI Public Pricing API helpers
    # ------------------------------------------------------------------

    async def _fetch_compute_price(
        self, instance_type: str
    ) -> Optional[dict[str, float]]:
        """Query OCI's public pricing API for compute instance pricing.

        Returns dict with 'on_demand' and optionally 'annual_flex' keys
        (hourly rates), or None if API is unreachable.
        """
        try:
            client = await self._get_client()

            # Parse instance type: "VM.Standard.E4.Flex-4" -> family "VM.Standard.E4.Flex", cores "4"
            base_family, ocpu_count = self._parse_instance_type(instance_type)

            # Try direct part number lookup first (most reliable)
            known_part = _OCI_INSTANCE_TO_PART.get(base_family)
            if known_part:
                resp = await client.get(
                    f"{OCI_PRICING_API}{known_part}",
                    params={"currencyCode": "USD"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items", [data] if "prices" in data else [])
                    for item in items:
                        result = self._extract_prices(item, ocpu_count)
                        if result:
                            return result

            # Fallback: search the full product listing
            params: dict[str, Any] = {
                "currencyCode": "USD",
                "limit": 500,
            }

            resp = await client.get(OCI_PRICING_API, params=params)
            resp.raise_for_status()
            data = resp.json()

            items = data.get("items", [])
            family_desc = base_family.lower().replace(".", " ")

            for item in items:
                description = item.get("description", "").lower()
                service_name = item.get("serviceName", "").lower()

                if family_desc in description and "compute" in service_name:
                    result = self._extract_prices(item, ocpu_count)
                    if result:
                        return result

            return None

        except Exception:
            logger.debug(
                "Failed to fetch OCI pricing for %s",
                instance_type,
                exc_info=True,
            )
            return None

    @staticmethod
    def _extract_prices(item: dict, ocpu_count: int) -> Optional[dict[str, float]]:
        """Extract on-demand and annual flex prices from an API item."""
        prices = item.get("prices", [])
        result: dict[str, float] = {}

        for price_entry in prices:
            model = price_entry.get("model", "").lower()
            value = price_entry.get("value", 0)

            if value <= 0:
                continue

            if "pay as you go" in model or "payg" in model:
                result["on_demand"] = float(value) * ocpu_count
            elif "annual flex" in model or "monthly flex" in model:
                result["annual_flex"] = float(value) * ocpu_count

        return result if "on_demand" in result else None

    @staticmethod
    def _parse_instance_type(instance_type: str) -> tuple[str, int]:
        """Parse 'VM.Standard.E4.Flex-4' into ('VM.Standard.E4.Flex', 4)."""
        if "-" in instance_type:
            parts = instance_type.rsplit("-", 1)
            try:
                return parts[0], int(parts[1])
            except (ValueError, IndexError):
                return instance_type, 1
        return instance_type, 1
