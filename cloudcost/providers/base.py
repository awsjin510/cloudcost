"""Abstract base class for cloud provider cost calculators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import httpx

from cloudcost.models.spec import CloudSpec, ProviderEstimate

_DEFAULT_TIMEOUT = 30.0


class BaseCalculator(ABC):
    """Base interface for all cloud provider calculators.

    Subclasses share a common HTTP client lifecycle: pass an existing
    ``httpx.AsyncClient`` for connection pooling, or let the base class
    create one lazily per-instance.
    """

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None) -> None:
        self._client = http_client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT)
        return self._client

    @abstractmethod
    async def estimate(self, spec: CloudSpec) -> ProviderEstimate:
        """Estimate costs for the given specification.

        Returns a ProviderEstimate with on-demand pricing (required)
        and optionally reserved / spot pricing.
        """
        ...
