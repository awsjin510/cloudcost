"""Azure cost calculator using curated pricing tables.

Azure has a Retail Prices REST API, but for reliability this module
ships with embedded pricing tables that can be refreshed periodically.
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
# Azure VM on-demand pricing (USD/hour, East US baseline, Linux)
# ---------------------------------------------------------------------------
_AZURE_OD_PRICES: dict[str, float] = {
    "Standard_B1s": 0.0104,
    "Standard_B1ms": 0.0207,
    "Standard_B2s": 0.0416,
    "Standard_B2ms": 0.0832,
    "Standard_D2s_v5": 0.096,
    "Standard_D4s_v5": 0.192,
    "Standard_D8s_v5": 0.384,
    "Standard_D16s_v5": 0.768,
    "Standard_D32s_v5": 1.536,
    "Standard_D48s_v5": 2.304,
    "Standard_D64s_v5": 3.072,
    "Standard_F2s_v2": 0.085,
    "Standard_F4s_v2": 0.170,
    "Standard_F8s_v2": 0.340,
    "Standard_F16s_v2": 0.680,
    "Standard_E2s_v5": 0.126,
    "Standard_E4s_v5": 0.252,
    "Standard_E8s_v5": 0.504,
    "Standard_E16s_v5": 1.008,
}

# 1-year Reserved Instance discount ratio
_RI_1Y_DISCOUNT = 0.58

# Managed Disk pricing (USD per GB-month)
_DISK_PRICES: dict[str, float] = {
    "Premium_LRS": 0.132,
    "Standard_LRS": 0.040,
    "UltraSSD_LRS": 0.200,
}

# Bandwidth out pricing tiers (USD/GB)
_BANDWIDTH_TIERS: list[tuple[float, float]] = [
    (5, 0.00),  # first 5 GB free
    (10240, 0.087),
    (40960, 0.083),
    (102400, 0.07),
    (float("inf"), 0.05),
]

_REGION_MULTIPLIER: dict[str, float] = {
    "eastus": 1.00,
    "westus2": 1.00,
    "westeurope": 1.08,
    "japaneast": 1.25,
    "koreacentral": 1.22,
    "southeastasia": 1.12,
    "eastasia": 1.15,
}


class AzureCalculator(BaseCalculator):
    """Azure VM cost estimator using curated pricing tables."""

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        azure_region = get_provider_region(spec.region, CloudProvider.AZURE)
        instance = match_instance(spec, CloudProvider.AZURE)
        instance_type = instance["type"]

        warnings: list[str] = []

        base_hourly = _AZURE_OD_PRICES.get(instance_type)
        if base_hourly is None:
            base_hourly = 0.10
            warnings.append(f"No pricing data for {instance_type}, using estimate")

        multiplier = _REGION_MULTIPLIER.get(azure_region, 1.10)
        hourly_od = base_hourly * multiplier
        hourly_ri = hourly_od * _RI_1Y_DISCOUNT
        monthly_hours = spec.monthly_hours

        compute_od = hourly_od * monthly_hours
        compute_ri = hourly_ri * monthly_hours

        # Storage
        disk_type = "Premium_LRS"
        if spec.storage_type.value == "hdd":
            disk_type = "Standard_LRS"
        elif spec.storage_type.value == "nvme":
            disk_type = "UltraSSD_LRS"
        storage_monthly = spec.storage_gb * _DISK_PRICES.get(disk_type, 0.132)

        # Network
        network_monthly = self._calc_bandwidth(spec.network_transfer_gb)

        total_od = compute_od + storage_monthly + network_monthly
        total_ri = compute_ri + storage_monthly + network_monthly

        details_od = {
            "compute": round(compute_od, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
            "disk_type": disk_type,
        }
        details_ri = {
            "compute": round(compute_ri, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
            "disk_type": disk_type,
        }

        on_demand = PricingResult(
            provider=CloudProvider.AZURE,
            tier=PricingTier.ON_DEMAND,
            instance_type=instance_type,
            hourly_cost=round(hourly_od, 4),
            monthly_cost=round(total_od, 2),
            details=details_od,
        )
        reserved_1y = PricingResult(
            provider=CloudProvider.AZURE,
            tier=PricingTier.RESERVED_1Y,
            instance_type=instance_type,
            hourly_cost=round(hourly_ri, 4),
            monthly_cost=round(total_ri, 2),
            details=details_ri,
            notes=["Azure 1-Year Reserved VM Instance"],
        )

        return ProviderEstimate(
            provider=CloudProvider.AZURE,
            region_name=azure_region,
            matched_instance=instance_type,
            on_demand=on_demand,
            reserved_1y=reserved_1y,
            total_monthly_on_demand=round(total_od, 2),
            total_monthly_reserved_1y=round(total_ri, 2),
            warnings=warnings,
        )

    @staticmethod
    def _calc_bandwidth(gb: float) -> float:
        remaining = gb
        total = 0.0
        for tier_gb, rate in _BANDWIDTH_TIERS:
            chunk = min(remaining, tier_gb)
            total += chunk * rate
            remaining -= chunk
            if remaining <= 0:
                break
        return round(total, 2)
