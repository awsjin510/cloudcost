"""Oracle Cloud Infrastructure (OCI) cost calculator.

OCI uses a simpler pricing model with generally lower list prices
compared to the hyperscalers. This module uses curated pricing tables.
"""

from __future__ import annotations

from cloudcost.models.naming import get_provider_region, match_instance
from cloudcost.models.spec import (
    CloudProvider,
    CloudSpec,
    PricingResult,
    PricingTier,
    ProviderEstimate,
)

from .base import BaseCalculator

# ---------------------------------------------------------------------------
# OCI Compute on-demand pricing (USD/hour)
# ---------------------------------------------------------------------------
_OCI_OD_PRICES: dict[str, float] = {
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
_ANNUAL_FLEX_DISCOUNT = 0.50

# Block Volume pricing (USD per GB-month)
_BLOCK_VOLUME_PRICES: dict[str, float] = {
    "ssd": 0.0255,
    "hdd": 0.0255,  # OCI balanced is same price
    "nvme": 0.0340,
}

# Network egress: first 10 TB/month free, then $0.0085/GB
_FREE_EGRESS_GB = 10240  # 10 TB
_EGRESS_RATE = 0.0085


class OracleCalculator(BaseCalculator):
    """OCI cost estimator using curated pricing tables."""

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        oci_region = get_provider_region(spec.region, CloudProvider.ORACLE)
        instance = match_instance(spec, CloudProvider.ORACLE)
        instance_type = instance["type"]

        warnings: list[str] = []

        base_hourly = _OCI_OD_PRICES.get(instance_type)
        if base_hourly is None:
            base_hourly = 0.03
            warnings.append(f"No pricing data for {instance_type}, using estimate")

        hourly_od = base_hourly
        hourly_annual = hourly_od * _ANNUAL_FLEX_DISCOUNT
        monthly_hours = spec.monthly_hours

        compute_od = hourly_od * monthly_hours
        compute_annual = hourly_annual * monthly_hours

        # Storage
        storage_key = spec.storage_type.value
        storage_rate = _BLOCK_VOLUME_PRICES.get(storage_key, 0.0255)
        storage_monthly = spec.storage_gb * storage_rate

        # Network — OCI has generous free tier
        if spec.network_transfer_gb <= _FREE_EGRESS_GB:
            network_monthly = 0.0
        else:
            network_monthly = (
                spec.network_transfer_gb - _FREE_EGRESS_GB
            ) * _EGRESS_RATE

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
