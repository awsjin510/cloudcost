"""Shared pricing calculation utilities.

Provides common functions used across all cloud provider calculators
to avoid duplicating the same logic in each provider module.
"""

from __future__ import annotations


def calc_tiered_cost(amount: float, tiers: list[tuple[float, float]]) -> float:
    """Calculate cost using tiered pricing.

    Each tier is a (capacity, rate) tuple where:
    - capacity: how many units this tier covers (use float('inf') for the last tier)
    - rate: price per unit for this tier

    Example tiers for AWS data transfer:
        [(1, 0.00), (9999, 0.09), (40000, 0.085), (float('inf'), 0.05)]

    Args:
        amount: Total number of units to price.
        tiers:  List of (capacity, rate_per_unit) tuples in ascending order.

    Returns:
        Total cost rounded to 2 decimal places.
    """
    remaining = amount
    total = 0.0
    for tier_capacity, rate in tiers:
        chunk = min(remaining, tier_capacity)
        total += chunk * rate
        remaining -= chunk
        if remaining <= 0:
            break
    return round(total, 2)
