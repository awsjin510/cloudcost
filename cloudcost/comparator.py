"""CloudCostComparator — parallel multi-cloud cost comparison engine."""

from __future__ import annotations

import asyncio
import logging

from cloudcost.models.spec import CloudProvider, CloudSpec, ComparisonResult, ProviderEstimate
from cloudcost.providers.aws import AWSCalculator
from cloudcost.providers.azure import AzureCalculator
from cloudcost.providers.gcp import GCPCalculator
from cloudcost.providers.oracle import OracleCalculator

logger = logging.getLogger(__name__)


class CloudCostComparator:
    """Query all four cloud providers in parallel and produce a comparison."""

    def __init__(self) -> None:
        self.aws_calculator = AWSCalculator()
        self.gcp_calculator = GCPCalculator()
        self.azure_calculator = AzureCalculator()
        self.oracle_calculator = OracleCalculator()

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

    @staticmethod
    async def _safe_estimate(
        label: str,
        calculator: AWSCalculator | GCPCalculator | AzureCalculator | OracleCalculator,
        spec: CloudSpec,
    ) -> ProviderEstimate | None:
        """Run a single provider estimate, catching errors gracefully."""
        try:
            return await calculator.estimate(spec)
        except Exception:
            logger.warning("Failed to estimate %s costs", label, exc_info=True)
            return None
