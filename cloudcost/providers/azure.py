"""Azure cost calculator using the Azure Retail Prices REST API.

The module queries the public Azure Retail Prices API for VM pricing.
No authentication is needed — the API is publicly accessible.

API docs: https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices

Architecture:
  1. Query Azure Retail Prices API with OData filters for VM size + region.
  2. Extract On-Demand (Consumption) and 1-yr Reserved prices.
  3. Add estimated Managed Disk and bandwidth costs from known rate tables.
  4. Fall back to embedded pricing tables if API is unreachable.
"""

from __future__ import annotations

import logging
from typing import Optional

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
# Azure Retail Prices API
# ---------------------------------------------------------------------------
AZURE_PRICING_API = "https://prices.azure.com/api/retail/prices"
API_VERSION = "2023-01-01-preview"

# ---------------------------------------------------------------------------
# Fallback VM on-demand pricing (USD/hour, East US baseline, Linux)
# Used when API is unreachable
# ---------------------------------------------------------------------------
_FALLBACK_PRICES: dict[str, float] = {
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
    "Standard_F2s_v2": 0.0846,
    "Standard_F4s_v2": 0.169,
    "Standard_F8s_v2": 0.340,
    "Standard_F16s_v2": 0.680,
    "Standard_E2s_v5": 0.126,
    "Standard_E4s_v5": 0.252,
    "Standard_E8s_v5": 0.504,
    "Standard_E16s_v5": 1.008,
}

# Fallback 1-year Reserved Instance discount ratio
_FALLBACK_RI_1Y_DISCOUNT = 0.58

# Fallback region multipliers (used only when API is unreachable)
_FALLBACK_REGION_MULTIPLIER: dict[str, float] = {
    "eastus": 1.00,
    "westus2": 1.00,
    "westeurope": 1.08,
    "japaneast": 1.25,
    "koreacentral": 1.22,
    "southeastasia": 1.12,
    "eastasia": 1.15,
}

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


class AzureCalculator(BaseCalculator):
    """Azure VM cost estimator using the Azure Retail Prices API."""

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        azure_region = get_provider_region(spec.region, CloudProvider.AZURE)
        instance = match_instance(spec, CloudProvider.AZURE)
        instance_type = instance["type"]

        warnings: list[str] = []

        # --- Compute pricing (try API first, then fallback) ---
        api_prices = await self._fetch_vm_prices(instance_type, azure_region, spec.os)

        if api_prices:
            hourly_od = api_prices["on_demand"]
            hourly_ri = api_prices.get("reserved_1y")
            if hourly_ri is None:
                hourly_ri = hourly_od * _FALLBACK_RI_1Y_DISCOUNT
                warnings.append("Reserved pricing unavailable from API — using estimated discount")
        else:
            # Fallback to embedded tables
            base_hourly = _FALLBACK_PRICES.get(instance_type, 0.10)
            multiplier = _FALLBACK_REGION_MULTIPLIER.get(azure_region, 1.10)
            hourly_od = base_hourly * multiplier
            hourly_ri = hourly_od * _FALLBACK_RI_1Y_DISCOUNT
            warnings.append(
                f"Used fallback pricing for {instance_type} — Azure API unreachable"
            )

        monthly_hours = spec.monthly_hours
        compute_od = hourly_od * monthly_hours
        compute_ri = hourly_ri * monthly_hours

        # --- Storage pricing ---
        disk_type = "Premium_LRS"
        if spec.storage_type.value == "hdd":
            disk_type = "Standard_LRS"
        elif spec.storage_type.value == "nvme":
            disk_type = "UltraSSD_LRS"
        storage_monthly = spec.storage_gb * _DISK_PRICES.get(disk_type, 0.132)

        # --- Network pricing ---
        network_monthly = calc_tiered_cost(spec.network_transfer_gb, _BANDWIDTH_TIERS)

        # --- Totals ---
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

    # ------------------------------------------------------------------
    # Azure Retail Prices API helpers
    # ------------------------------------------------------------------

    async def _fetch_vm_prices(
        self, instance_type: str, region: str, os: str
    ) -> Optional[dict[str, float]]:
        """Query Azure Retail Prices API for VM hourly pricing.

        Returns dict with 'on_demand' and optionally 'reserved_1y' keys,
        or None if API is unreachable.
        """
        try:
            client = await self._get_client()

            os_filter = "Linux" if os == "linux" else "Windows"

            # Fetch On-Demand (Consumption) pricing
            od_filter = (
                f"serviceName eq 'Virtual Machines' "
                f"and armRegionName eq '{region}' "
                f"and armSkuName eq '{instance_type}' "
                f"and priceType eq 'Consumption'"
            )
            params = {
                "api-version": API_VERSION,
                "$filter": od_filter,
                "currencyCode": "USD",
            }
            resp = await client.get(AZURE_PRICING_API, params=params)
            resp.raise_for_status()
            data = resp.json()

            hourly_od = self._extract_hourly_price(data, os_filter)
            if hourly_od is None:
                return None

            result: dict[str, float] = {"on_demand": hourly_od}

            # Fetch Reserved 1Y pricing
            ri_filter = (
                f"serviceName eq 'Virtual Machines' "
                f"and armRegionName eq '{region}' "
                f"and armSkuName eq '{instance_type}' "
                f"and priceType eq 'Reservation' "
                f"and reservationTerm eq '1 Year'"
            )
            params_ri = {
                "api-version": API_VERSION,
                "$filter": ri_filter,
                "currencyCode": "USD",
            }
            resp_ri = await client.get(AZURE_PRICING_API, params=params_ri)
            resp_ri.raise_for_status()
            data_ri = resp_ri.json()

            hourly_ri = self._extract_reserved_hourly(data_ri, os_filter)
            if hourly_ri is not None:
                result["reserved_1y"] = hourly_ri

            return result

        except Exception:
            logger.warning(
                "Failed to fetch Azure pricing for %s in %s",
                instance_type,
                region,
                exc_info=True,
            )
            return None

    @staticmethod
    def _extract_hourly_price(data: dict, os_filter: str) -> Optional[float]:
        """Extract hourly on-demand price from API response."""
        for item in data.get("Items", []):
            product_name = item.get("productName", "")
            meter_name = item.get("meterName", "")
            # Filter for the correct OS and exclude Spot/Low Priority
            if os_filter in product_name and "Spot" not in meter_name and "Low Priority" not in meter_name:
                unit_of_measure = item.get("unitOfMeasure", "")
                if "Hour" in unit_of_measure:
                    price = item.get("retailPrice", 0)
                    if price > 0:
                        return float(price)
        return None

    @staticmethod
    def _extract_reserved_hourly(data: dict, os_filter: str) -> Optional[float]:
        """Extract hourly reserved price from API response.

        Reserved prices are typically returned as monthly or yearly totals.
        We convert to hourly for consistency.
        """
        for item in data.get("Items", []):
            product_name = item.get("productName", "")
            if os_filter in product_name:
                unit_of_measure = item.get("unitOfMeasure", "")
                price = item.get("retailPrice", 0)
                if price > 0:
                    if "Hour" in unit_of_measure:
                        return float(price)
                    elif "1 Year" in unit_of_measure:
                        # Convert annual price to hourly (8760 hours/year)
                        return float(price) / 8760
                    elif "1 Month" in unit_of_measure:
                        return float(price) / 730
        return None

