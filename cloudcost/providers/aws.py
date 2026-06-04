"""AWS cost calculator using the AWS Price List Bulk API.

The module queries the public AWS pricing JSON endpoint for EC2 and
related services. No AWS credentials are needed — the Price List Bulk
API endpoints are publicly accessible.

Architecture:
  1. Fetch pricing JSON for EC2 in the target region.
  2. Filter by instance type, OS, tenancy=Shared, pre-installed SW=NA.
  3. Extract On-Demand and 1-yr Standard Reserved (No Upfront) prices.
  4. Add estimated storage (EBS) and data-transfer costs from known rate tables.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from cloudcost.models.naming import (
    get_provider_region,
    get_provider_storage_name,
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
# AWS pricing constants
# ---------------------------------------------------------------------------

# Public Pricing API endpoint (no auth needed)
AWS_PRICING_API = "https://pricing.us-east-1.amazonaws.com"

# Region-code to AWS "location" display name (used in pricing filters)
_REGION_DISPLAY: dict[str, str] = {
    "us-east-1": "US East (N. Virginia)",
    "us-west-2": "US West (Oregon)",
    "eu-west-1": "EU (Ireland)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "ap-northeast-2": "Asia Pacific (Seoul)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-east-1": "Asia Pacific (Hong Kong)",
    "ap-east-2": "Asia Pacific (Taipei)",
}

# EBS pricing per GB-month (approximate, varies slightly by region)
_EBS_PRICE_PER_GB_MONTH: dict[str, float] = {
    "gp3": 0.08,
    "gp2": 0.10,
    "io2": 0.125,
    "st1": 0.045,
    "sc1": 0.015,
}

# Data transfer out (to internet) pricing tiers (USD/GB).
# AWS provides 100 GB/month of free egress aggregated across regions/services
# (since Dec 2021), then $0.09/GB up to 10 TB, tapering for higher volumes.
# Pricing last verified: 2026-06 — https://aws.amazon.com/ec2/pricing/on-demand/
_DATA_TRANSFER_TIERS: list[tuple[float, float]] = [
    (100, 0.00),  # first 100 GB/month free
    (10140, 0.09),  # remainder of first 10 TB
    (40960, 0.085),  # next 40 TB
    (102400, 0.07),  # next 100 TB
    (float("inf"), 0.05),  # 150 TB+
]

# Fallback on-demand hourly prices (USD) when API is unreachable
_FALLBACK_PRICES: dict[str, float] = {
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "t3.xlarge": 0.1664,
    "t3.2xlarge": 0.3328,
    "m5.large": 0.096,
    "m5.xlarge": 0.192,
    "m5.2xlarge": 0.384,
    "m5.4xlarge": 0.768,
    "m5.8xlarge": 1.536,
    "m5.12xlarge": 2.304,
    "m5.16xlarge": 3.072,
    "c5.large": 0.085,
    "c5.xlarge": 0.170,
    "c5.2xlarge": 0.340,
    "c5.4xlarge": 0.680,
    "c5.9xlarge": 1.530,
    "r5.large": 0.126,
    "r5.xlarge": 0.252,
    "r5.2xlarge": 0.504,
    "r5.4xlarge": 1.008,
}

# Reserved 1-yr Standard No Upfront discount ratio vs On-Demand (approximate).
# 1-year No Upfront saves ~29% (you pay ~0.70 of on-demand); deeper discounts
# (~40%+) apply only to All Upfront or 3-year terms.
# Pricing last verified: 2026-06 — https://aws.amazon.com/ec2/pricing/reserved-instances/pricing/
_RESERVED_1Y_DISCOUNT = 0.70  # pay ~70% of on-demand


class AWSCalculator(BaseCalculator):
    """AWS EC2 cost estimator using the public Price List API."""

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        aws_region = get_provider_region(spec.region, CloudProvider.AWS)
        instance = match_instance(spec, CloudProvider.AWS)
        instance_type = instance["type"]

        warnings: list[str] = []

        # --- Compute pricing ---
        hourly_od = await self._fetch_on_demand_price(
            instance_type, aws_region, spec.os
        )
        if hourly_od is None:
            hourly_od = _FALLBACK_PRICES.get(instance_type, 0.10)
            warnings.append(
                f"Used fallback pricing for {instance_type} — API unreachable"
            )

        hourly_ri = hourly_od * _RESERVED_1Y_DISCOUNT
        monthly_hours = spec.monthly_hours

        compute_od = hourly_od * monthly_hours
        compute_ri = hourly_ri * monthly_hours

        # --- Storage pricing ---
        ebs_type = get_provider_storage_name(spec.storage_type, CloudProvider.AWS)
        storage_monthly = spec.storage_gb * _EBS_PRICE_PER_GB_MONTH.get(ebs_type, 0.08)

        # --- Network pricing ---
        network_monthly = calc_tiered_cost(spec.network_transfer_gb, _DATA_TRANSFER_TIERS)

        # --- Totals ---
        total_od = compute_od + storage_monthly + network_monthly
        total_ri = compute_ri + storage_monthly + network_monthly

        details_od = {
            "compute": round(compute_od, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
            "ebs_type": ebs_type,
        }
        details_ri = {
            "compute": round(compute_ri, 2),
            "storage": round(storage_monthly, 2),
            "network": round(network_monthly, 2),
            "ebs_type": ebs_type,
        }

        on_demand = PricingResult(
            provider=CloudProvider.AWS,
            tier=PricingTier.ON_DEMAND,
            instance_type=instance_type,
            hourly_cost=round(hourly_od, 4),
            monthly_cost=round(total_od, 2),
            details=details_od,
        )
        reserved_1y = PricingResult(
            provider=CloudProvider.AWS,
            tier=PricingTier.RESERVED_1Y,
            instance_type=instance_type,
            hourly_cost=round(hourly_ri, 4),
            monthly_cost=round(total_ri, 2),
            details=details_ri,
        )

        region_display = _REGION_DISPLAY.get(aws_region, aws_region)

        return ProviderEstimate(
            provider=CloudProvider.AWS,
            region_name=region_display,
            matched_instance=instance_type,
            on_demand=on_demand,
            reserved_1y=reserved_1y,
            total_monthly_on_demand=round(total_od, 2),
            total_monthly_reserved_1y=round(total_ri, 2),
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # AWS Price List Bulk API helpers
    # ------------------------------------------------------------------

    async def _fetch_on_demand_price(
        self, instance_type: str, region: str, os: str
    ) -> Optional[float]:
        """Query the AWS Pricing API for on-demand EC2 hourly price.

        Uses the GetProducts-style filter via the public JSON index.
        Falls back to None on any network/parse error.
        """
        try:
            client = await self._get_client()
            # Step 1: get the regional pricing index URL
            index_url = f"{AWS_PRICING_API}/offers/v1.0/aws/AmazonEC2/current/{region}/index.json"
            resp = await client.get(index_url)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()

            os_filter = "Linux" if os == "linux" else "Windows"

            # Step 2: scan products for the matching instance type
            for sku, product in data.get("products", {}).items():
                attrs = product.get("attributes", {})
                if (
                    attrs.get("instanceType") == instance_type
                    and attrs.get("operatingSystem") == os_filter
                    and attrs.get("tenancy") == "Shared"
                    and attrs.get("preInstalledSw") == "NA"
                    and attrs.get("capacitystatus") == "Used"
                ):
                    # Step 3: look up the On-Demand price
                    terms = data.get("terms", {}).get("OnDemand", {}).get(sku, {})
                    for _offer_key, offer in terms.items():
                        for _dim_key, dim in offer.get("priceDimensions", {}).items():
                            price_str = dim.get("pricePerUnit", {}).get("USD", "0")
                            price = float(price_str)
                            if price > 0:
                                return price
            return None

        except Exception:
            logger.warning(
                "Failed to fetch AWS pricing for %s in %s", instance_type, region,
                exc_info=True,
            )
            return None

