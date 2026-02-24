"""Abstract base class for cloud provider cost calculators."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cloudcost.models.spec import CloudSpec, ProviderEstimate


class BaseCalculator(ABC):
    """Base interface for all cloud provider calculators."""

    @abstractmethod
    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        """Estimate costs for the given specification.

        Returns a ProviderEstimate with on-demand pricing (required)
        and optionally reserved / spot pricing.
        """
        ...
