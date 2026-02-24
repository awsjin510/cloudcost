"""Shared helpers for constructing domain objects from raw user input.

Centralises the conversion of raw strings/numbers (from CLI args, web forms,
or API request bodies) into validated Pydantic models, so that the logic
lives in exactly one place instead of being repeated in each entry point.
"""

from __future__ import annotations

from cloudcost.models.spec import CloudSpec, DatabaseType, Region, StorageType


def build_cloud_spec(
    *,
    cpu_cores: int,
    ram_gb: float,
    storage_gb: float = 0,
    storage_type: str = "ssd",
    network_transfer_gb: float = 0,
    database_type: str = "none",
    region: str = "us-east-1",
    monthly_hours: float = 730,
    os: str = "linux",
    description: str = "",
) -> CloudSpec:
    """Construct a validated CloudSpec from raw user-supplied values.

    All string enum parameters (storage_type, database_type, region) are
    converted to their respective enum types here, so callers never have
    to import or reference those enums directly.
    """
    return CloudSpec(
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        storage_gb=storage_gb,
        storage_type=StorageType(storage_type),
        network_transfer_gb=network_transfer_gb,
        database_type=DatabaseType(database_type),
        region=Region(region),
        monthly_hours=monthly_hours,
        os=os,
        description=description,
    )
