"""GCP cost calculator using publicly known pricing tables.

GCP does not have a simple unauthenticated bulk pricing API like AWS,
so this module uses curated pricing tables for Compute Engine, Persistent
Disk, and network egress. The tables are based on published GCP pricing
pages and can be updated periodically.
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
# GCP on-demand pricing (USD/hour, us-east1 baseline, Linux)
# ---------------------------------------------------------------------------
_GCP_OD_PRICES: dict[str, float] = {
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

# 1-year CUD discount ratio (approximate)
_CUD_1Y_DISCOUNT = 0.63

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

# Regional price multipliers relative to us-east1
_REGION_MULTIPLIER: dict[str, float] = {
    "us-east1": 1.00,
    "us-west1": 1.00,
    "europe-west1": 1.10,
    "asia-northeast1": 1.22,
    "asia-northeast3": 1.22,
    "asia-southeast1": 1.13,
    "asia-east2": 1.16,
}


class GCPCalculator(BaseCalculator):
    """GCP Compute Engine cost estimator using curated pricing tables."""

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        gcp_region = get_provider_region(spec.region, CloudProvider.GCP)
        instance = match_instance(spec, CloudProvider.GCP)
        instance_type = instance["type"]

        warnings: list[str] = []

        # Compute pricing
        base_hourly = _GCP_OD_PRICES.get(instance_type)
        if base_hourly is None:
            base_hourly = 0.10
            warnings.append(f"No pricing data for {instance_type}, using estimate")

        multiplier = _REGION_MULTIPLIER.get(gcp_region, 1.15)
        hourly_od = base_hourly * multiplier
        hourly_cud = hourly_od * _CUD_1Y_DISCOUNT
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
        network_monthly = self._calc_egress(spec.network_transfer_gb)

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

    @staticmethod
    def _calc_egress(gb: float) -> float:
        remaining = gb
        total = 0.0
        for tier_gb, rate in _EGRESS_TIERS:
            chunk = min(remaining, tier_gb)
            total += chunk * rate
            remaining -= chunk
            if remaining <= 0:
                break
        return round(total, 2)
