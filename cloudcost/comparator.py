"""CloudCostComparator — parallel multi-cloud cost comparison engine."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from cloudcost.models.spec import (
    CloudProvider,
    CloudSpec,
    ComparisonResult,
    GroupComparisonResult,
    GroupProviderEstimate,
    MachineEstimateDetail,
    ProviderEstimate,
    Region,
    StorageType,
    WorkloadGroup,
)
from cloudcost.providers.aws import AWSCalculator
from cloudcost.providers.azure import AzureCalculator
from cloudcost.providers.base import BaseCalculator
from cloudcost.providers.gcp import GCPCalculator
from cloudcost.providers.oracle import OracleCalculator

logger = logging.getLogger(__name__)


class CloudCostComparator:
    """Query all four cloud providers in parallel and produce a comparison.

    Uses a single shared httpx.AsyncClient across all provider calculators
    for connection pooling and reduced overhead.

    Can be used as an async context manager to ensure proper cleanup::

        async with CloudCostComparator() as comparator:
            result = await comparator.compare(spec)
    """

    def __init__(self) -> None:
        self._http_client = httpx.AsyncClient(timeout=30.0)
        self.aws_calculator = AWSCalculator(http_client=self._http_client)
        self.gcp_calculator = GCPCalculator(http_client=self._http_client)
        self.azure_calculator = AzureCalculator(http_client=self._http_client)
        self.oracle_calculator = OracleCalculator(http_client=self._http_client)

    async def aclose(self) -> None:
        """Close the shared HTTP client and release connections."""
        await self._http_client.aclose()

    async def __aenter__(self) -> CloudCostComparator:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def compare(self, spec: CloudSpec) -> ComparisonResult:
        """Run all provider estimators concurrently and return aggregated results."""
        tasks = [
            self._safe_estimate("AWS", self.aws_calculator, spec),
            self._safe_estimate("GCP", self.gcp_calculator, spec),
            self._safe_estimate("Azure", self.azure_calculator, spec),
            self._safe_estimate("Oracle", self.oracle_calculator, spec),
        ]
        raw_results: list[ProviderEstimate | None] = await asyncio.gather(*tasks)

        estimates = [r for r in raw_results if r is not None]

        result = ComparisonResult(spec=spec, estimates=estimates)

        # Determine cheapest options
        if estimates:
            by_od = sorted(estimates, key=lambda e: e.total_monthly_on_demand)
            result.cheapest_on_demand = by_od[0].provider

            reserved = [e for e in estimates if e.total_monthly_reserved_1y is not None]
            if reserved:
                by_ri = sorted(reserved, key=lambda e: e.total_monthly_reserved_1y or float("inf"))
                result.cheapest_reserved = by_ri[0].provider

        return result

    async def compare_group(self, group: WorkloadGroup) -> GroupComparisonResult:
        """Compare costs for a workload group across all providers.

        For each machine in the group, a CloudSpec is created and estimated
        against all providers.  Results are then pivoted by provider so each
        provider has a full machine-by-machine breakdown plus totals.
        """
        # Build a CloudSpec per unique machine and run comparisons
        per_machine_results: list[tuple[Any, ComparisonResult]] = []
        for machine in group.machines:
            spec = CloudSpec(
                cpu_cores=machine.cpu,
                ram_gb=machine.ram,
                storage_gb=machine.storage,
                storage_type=StorageType(group.storage_type),
                region=Region(group.region),
                monthly_hours=group.monthly_hours,
                os=group.os,
            )
            result = await self.compare(spec)
            per_machine_results.append((machine, result))

        # Pivot: group by provider
        provider_data: dict[CloudProvider, dict] = {}

        for machine, comparison in per_machine_results:
            for est in comparison.estimates:
                if est.provider not in provider_data:
                    provider_data[est.provider] = {
                        "region_name": est.region_name,
                        "machines": [],
                        "total_od": 0.0,
                        "total_ri": 0.0,
                        "has_ri": True,
                        "total_qty": 0,
                        "warnings": [],
                    }
                pd = provider_data[est.provider]

                unit_od = est.total_monthly_on_demand
                unit_ri = est.total_monthly_reserved_1y
                sub_od = unit_od * machine.quantity
                sub_ri = (unit_ri * machine.quantity) if unit_ri is not None else None

                pd["machines"].append(
                    MachineEstimateDetail(
                        machine=machine,
                        matched_instance=est.matched_instance,
                        unit_monthly_on_demand=unit_od,
                        unit_monthly_reserved_1y=unit_ri,
                        subtotal_on_demand=sub_od,
                        subtotal_reserved_1y=sub_ri,
                        details=est.on_demand.details,
                    )
                )
                pd["total_od"] += sub_od
                if unit_ri is not None:
                    pd["total_ri"] += unit_ri * machine.quantity
                else:
                    pd["has_ri"] = False
                pd["total_qty"] += machine.quantity
                pd["warnings"].extend(est.warnings)

        # Build GroupProviderEstimate list
        estimates: list[GroupProviderEstimate] = []
        for provider, pd in provider_data.items():
            estimates.append(
                GroupProviderEstimate(
                    provider=provider,
                    region_name=pd["region_name"],
                    machines=pd["machines"],
                    total_monthly_on_demand=pd["total_od"],
                    total_monthly_reserved_1y=pd["total_ri"] if pd["has_ri"] else None,
                    total_machines=pd["total_qty"],
                    warnings=list(dict.fromkeys(pd["warnings"])),  # deduplicate
                )
            )

        result = GroupComparisonResult(group=group, estimates=estimates)

        if estimates:
            by_od = sorted(estimates, key=lambda e: e.total_monthly_on_demand)
            result.cheapest_on_demand = by_od[0].provider

            reserved = [e for e in estimates if e.total_monthly_reserved_1y is not None]
            if reserved:
                by_ri = sorted(
                    reserved, key=lambda e: e.total_monthly_reserved_1y or float("inf")
                )
                result.cheapest_reserved = by_ri[0].provider

        return result

    @staticmethod
    async def _safe_estimate(
        label: str,
        calculator: BaseCalculator,
        spec: CloudSpec,
    ) -> ProviderEstimate | None:
        """Run a single provider estimate, catching errors gracefully."""
        try:
            return await calculator.estimate(spec)
        except Exception:
            logger.warning("Failed to estimate %s costs", label, exc_info=True)
            return None
