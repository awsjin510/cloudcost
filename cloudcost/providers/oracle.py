"""Oracle Cloud Infrastructure (OCI) cost calculator using the public pricing API.

The module queries Oracle's public pricing JSON endpoint used by the
official OCI Cost Estimator. No authentication is needed.

Pricing source: https://www.oracle.com/cloud/costestimator.html
API endpoint:   https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/

Architecture:
  1. Look up the shape family's OCPU and memory SKUs by part number
     (``?partNumber=`` query — the ``/products/<part>`` path form is
     blocked by Oracle's edge and returns 403).
  2. If the part-number lookup fails, scan the full product listing by
     display name instead.
  3. Extract the Pay-As-You-Go rate; the API only publishes PAYG, so the
     Annual Flex tier is derived from the published discount ratio.
  4. Fall back to embedded pricing tables if API is unreachable.

Response shape (verified 2026-09)::

    {"lastUpdated": "...", "items": [{
        "partNumber": "B93113",
        "displayName": "Compute - Standard - E4 - OCPU",
        "metricName": "OCPU Per Hour",
        "currencyCodeLocalizations": [{
            "currencyCode": "USD",
            "prices": [{"model": "PAY_AS_YOU_GO", "value": 0.025}]
        }]
    }]}
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from cloudcost.models.naming import (
    ORACLE_INSTANCE_CATALOG,
    get_provider_region,
    match_instance,
)
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

# Shape family -> (OCPU part number, memory part number).
# Verified against the public pricing listing 2026-09 (lastUpdated 2026-09-09).
_OCI_FAMILY_PARTS: dict[str, tuple[str, str]] = {
    "VM.Standard.E4.Flex": ("B93113", "B93114"),  # Compute - Standard - E4 - OCPU / Memory
    "VM.Standard3.Flex": ("B94176", "B94177"),    # Compute - Standard - X9 - OCPU / Memory
    "VM.Optimized3.Flex": ("B93311", "B93312"),   # Compute - Optimized - X9 - OCPU / Memory
}

# Display-name keywords used to locate the same SKUs in the full listing
# when the part-number lookup returns nothing.
_OCI_FAMILY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "VM.Standard.E4.Flex": ("compute", "standard", "e4"),
    "VM.Standard3.Flex": ("compute", "standard", "x9"),
    "VM.Optimized3.Flex": ("compute", "optimized", "x9"),
}
_OCI_LISTING_EXCLUDE: tuple[str, ...] = ("cloud@customer", "vmware", "gpu", "dense i/o")

# ---------------------------------------------------------------------------
# Fallback OCPU rates (USD per OCPU per hour) when API is unreachable.
# OCI Flex shapes charge OCPU and memory separately.
# ---------------------------------------------------------------------------
_FALLBACK_OCPU_RATES: dict[str, float] = {
    "VM.Standard.E4.Flex": 0.025,      # E4 (AMD EPYC)
    "VM.Standard3.Flex": 0.04,         # Standard3 (Intel Xeon)
    "VM.Optimized3.Flex": 0.054,       # Optimized3 (Intel Xeon HPC)
}

# Memory is priced the same across all OCI Flex shapes
_MEMORY_RATE_PER_GB_HOUR = 0.0015  # USD per GB per hour

# OCI doesn't have traditional reserved instances in the same way;
# Annual Flex (Universal Credits) pricing runs at roughly 66% of
# Pay-As-You-Go list price (~34% discount). Larger negotiated commits can
# go deeper, but 0.66 reflects the standard published ratio.
_FALLBACK_ANNUAL_FLEX_DISCOUNT = 0.66

# Regions used as a nearest alternative when Oracle has no direct presence.
# A warning is shown to the user whenever one of these is selected.
_OCI_FALLBACK_REGIONS: set[str] = {"ap-singapore-1"}

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


def _parse_shape(instance_type: str) -> tuple[str, int]:
    """Parse 'VM.Standard.E4.Flex-4' into ('VM.Standard.E4.Flex', 4)."""
    if "-" in instance_type:
        parts = instance_type.rsplit("-", 1)
        try:
            return parts[0], int(parts[1])
        except (ValueError, IndexError):
            return instance_type, 1
    return instance_type, 1


# Estimated hourly OCPU cost per catalog shape, used to steer instance
# matching toward the cheapest family (memory is billed identically across
# Flex shapes and on the requested RAM, so it does not affect the ranking).
_CATALOG_OCPU_COSTS: dict[str, float] = {
    inst["type"]: _FALLBACK_OCPU_RATES.get(_parse_shape(inst["type"])[0], 0.025)
    * _parse_shape(inst["type"])[1]
    for inst in ORACLE_INSTANCE_CATALOG
}


class OracleCalculator(BaseCalculator):
    """OCI cost estimator using the public Oracle pricing API."""

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        oci_region = get_provider_region(spec.region, CloudProvider.ORACLE)
        instance = match_instance(spec, CloudProvider.ORACLE, _CATALOG_OCPU_COSTS)
        instance_type = instance["type"]

        warnings: list[str] = []

        if spec.os == "windows":
            warnings.append(
                "Windows licensing is not modeled for OCI — prices are Linux-based"
            )

        if oci_region in _OCI_FALLBACK_REGIONS:
            warnings.append(
                f"Oracle Cloud has no {spec.region.value} region; "
                f"using {oci_region} pricing as nearest alternative"
            )

        base_family, ocpu_count = self._parse_instance_type(instance_type)

        # --- OCPU + memory rates (try API first, then fallback) ---
        api_prices = await self._fetch_compute_price(instance_type)

        if api_prices:
            ocpu_rate = api_prices["ocpu_rate"]
            memory_rate = api_prices.get("memory_rate", _MEMORY_RATE_PER_GB_HOUR)
        else:
            # Fallback to embedded rates
            ocpu_rate = _FALLBACK_OCPU_RATES.get(base_family, 0.025)
            memory_rate = _MEMORY_RATE_PER_GB_HOUR
            warnings.append(
                f"Used fallback pricing for {instance_type} — OCI API unreachable"
            )

        # OCI Flex shapes charge OCPU and memory separately. Bill the
        # user-requested RAM (spec.ram_gb): Flex shapes charge for exactly
        # the RAM you allocate, not the catalog entry.
        memory_hourly = spec.ram_gb * memory_rate
        ocpu_hourly_od = ocpu_rate * ocpu_count
        # The public API only publishes Pay-As-You-Go; Annual Flex is derived.
        ocpu_hourly_annual = ocpu_hourly_od * _FALLBACK_ANNUAL_FLEX_DISCOUNT

        # Total hourly = OCPU + memory
        hourly_od = ocpu_hourly_od + memory_hourly
        hourly_annual = ocpu_hourly_annual + memory_hourly

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
        """Query OCI's public pricing API for a Flex shape's unit rates.

        Returns ``{"ocpu_rate": <USD per OCPU-hour>, "memory_rate": <USD
        per GB-hour>}`` (memory_rate may be absent), or None when the API
        is unreachable or the family is unknown.
        """
        base_family, _ = self._parse_instance_type(instance_type)
        parts = _OCI_FAMILY_PARTS.get(base_family)
        if parts is None:
            return None

        try:
            client = await self._get_client()
            ocpu_part, memory_part = parts

            ocpu_rate = await self._fetch_part_rate(client, ocpu_part)
            memory_rate = await self._fetch_part_rate(client, memory_part)

            if ocpu_rate is None or memory_rate is None:
                # Part numbers occasionally rotate; fall back to scanning
                # the full listing by display name.
                items = await self._fetch_listing(client)
                keywords = _OCI_FAMILY_KEYWORDS.get(base_family, ())
                if ocpu_rate is None:
                    ocpu_rate = self._find_in_listing(items, keywords + ("ocpu",))
                if memory_rate is None:
                    memory_rate = self._find_in_listing(items, keywords + ("memory",))

            if ocpu_rate is None:
                return None

            result: dict[str, float] = {"ocpu_rate": ocpu_rate}
            if memory_rate is not None:
                result["memory_rate"] = memory_rate
            return result

        except Exception:
            logger.warning(
                "Failed to fetch OCI pricing for %s",
                instance_type,
                exc_info=True,
            )
            return None

    @classmethod
    async def _fetch_part_rate(cls, client, part_number: str) -> Optional[float]:
        """Look up one SKU by part number and return its PAYG rate."""
        resp = await client.get(
            OCI_PRICING_API,
            params={"partNumber": part_number, "currencyCode": "USD"},
        )
        resp.raise_for_status()
        # The API returns ``"items": null`` for unknown part numbers.
        for item in resp.json().get("items") or []:
            rate = cls._extract_payg_rate(item)
            if rate is not None:
                return rate
        return None

    @staticmethod
    async def _fetch_listing(client) -> list[dict[str, Any]]:
        """Fetch the full product listing (a few hundred items, unpaginated)."""
        resp = await client.get(OCI_PRICING_API, params={"currencyCode": "USD"})
        resp.raise_for_status()
        return resp.json().get("items") or []

    @classmethod
    def _find_in_listing(
        cls, items: list[dict[str, Any]], keywords: tuple[str, ...]
    ) -> Optional[float]:
        """Return the PAYG rate of the first item whose displayName has every keyword."""
        for item in items:
            name = str(item.get("displayName", "")).lower()
            if any(bad in name for bad in _OCI_LISTING_EXCLUDE):
                continue
            if all(kw in name for kw in keywords):
                rate = cls._extract_payg_rate(item)
                if rate is not None:
                    return rate
        return None

    @staticmethod
    def _extract_payg_rate(item: dict[str, Any]) -> Optional[float]:
        """Extract the USD Pay-As-You-Go unit rate from an API item.

        Prices live under ``currencyCodeLocalizations[].prices[]`` with
        ``model == "PAY_AS_YOU_GO"``. Some SKUs list a zero-priced free-tier
        row followed by the paid rate, so the highest non-zero value wins.
        """
        best: Optional[float] = None
        for loc in item.get("currencyCodeLocalizations", []) or []:
            if loc.get("currencyCode", "USD") != "USD":
                continue
            for price in loc.get("prices", []) or []:
                model = str(price.get("model", "")).upper().replace(" ", "_")
                if model not in ("PAY_AS_YOU_GO", "PAYG"):
                    continue
                try:
                    value = float(price.get("value", 0))
                except (TypeError, ValueError):
                    continue
                if value > 0 and (best is None or value > best):
                    best = value
        return best

    @staticmethod
    def _parse_instance_type(instance_type: str) -> tuple[str, int]:
        """Parse 'VM.Standard.E4.Flex-4' into ('VM.Standard.E4.Flex', 4)."""
        return _parse_shape(instance_type)
