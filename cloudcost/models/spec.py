"""Cloud specification data models and standardized naming conversion layer."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class StorageType(str, Enum):
    SSD = "ssd"
    HDD = "hdd"
    NVME = "nvme"


class DatabaseType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MARIADB = "mariadb"
    MSSQL = "mssql"
    ORACLE = "oracle"
    NONE = "none"


class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ORACLE = "oracle"


class PricingTier(str, Enum):
    ON_DEMAND = "on_demand"
    RESERVED_1Y = "reserved_1y"
    RESERVED_3Y = "reserved_3y"
    SPOT = "spot"


class Region(str, Enum):
    # Asia Pacific
    AP_NORTHEAST_1 = "ap-northeast-1"  # Tokyo
    AP_NORTHEAST_2 = "ap-northeast-2"  # Seoul
    AP_SOUTHEAST_1 = "ap-southeast-1"  # Singapore
    AP_EAST_1 = "ap-east-1"  # Hong Kong
    # US
    US_EAST_1 = "us-east-1"  # N. Virginia
    US_WEST_2 = "us-west-2"  # Oregon
    # Europe
    EU_WEST_1 = "eu-west-1"  # Ireland


class CloudSpec(BaseModel):
    """Standardized cloud resource specification."""

    cpu_cores: int = Field(ge=1, le=512, description="Number of CPU cores (vCPU)")
    ram_gb: float = Field(ge=0.5, le=12288, description="RAM in GB")
    storage_gb: float = Field(default=0, ge=0, le=65536, description="Storage size in GB")
    storage_type: StorageType = Field(default=StorageType.SSD, description="Storage type")
    network_transfer_gb: float = Field(
        default=0, ge=0, description="Monthly outbound network transfer in GB"
    )
    database_type: DatabaseType = Field(
        default=DatabaseType.NONE, description="Managed database engine type"
    )
    region: Region = Field(
        default=Region.US_EAST_1, description="Deployment region (normalized)"
    )
    monthly_hours: float = Field(
        default=730, ge=0, le=744, description="Expected usage hours per month"
    )
    os: str = Field(default="linux", description="Operating system (linux/windows)")
    description: str = Field(
        default="", description="Free-form usage scenario description"
    )

    @field_validator("os")
    @classmethod
    def normalize_os(cls, v: str) -> str:
        v = v.strip().lower()
        if v in ("linux", "ubuntu", "amazon linux", "rhel", "centos", "debian"):
            return "linux"
        if v in ("windows", "windows server", "win"):
            return "windows"
        return v


class PricingResult(BaseModel):
    """Pricing result for a single provider and tier."""

    provider: CloudProvider
    tier: PricingTier
    instance_type: str = Field(description="Provider-specific instance/VM name")
    hourly_cost: float = Field(ge=0, description="Cost per hour in USD")
    monthly_cost: float = Field(ge=0, description="Cost per month in USD")
    currency: str = Field(default="USD")
    details: dict = Field(
        default_factory=dict,
        description="Breakdown: compute, storage, network, database, etc.",
    )
    notes: list[str] = Field(default_factory=list)


class ProviderEstimate(BaseModel):
    """Full estimate from a single cloud provider."""

    provider: CloudProvider
    region_name: str = Field(description="Provider-specific region display name")
    matched_instance: str
    on_demand: PricingResult
    reserved_1y: Optional[PricingResult] = None
    spot: Optional[PricingResult] = None
    total_monthly_on_demand: float = Field(
        ge=0, description="Total monthly cost (compute + storage + network + db)"
    )
    total_monthly_reserved_1y: Optional[float] = None
    warnings: list[str] = Field(default_factory=list)


class ComparisonResult(BaseModel):
    """Aggregated comparison across all providers."""

    spec: CloudSpec
    estimates: list[ProviderEstimate]
    cheapest_on_demand: Optional[CloudProvider] = None
    cheapest_reserved: Optional[CloudProvider] = None
    recommendation: str = Field(default="", description="AI-generated recommendation")


# ---------------------------------------------------------------------------
# Workload Group (multi-machine combination) models
# ---------------------------------------------------------------------------


class MachineRole(str, Enum):
    WEB = "web"
    API = "api"
    DB = "db"
    CACHE = "cache"
    WORKER = "worker"


class MachineItem(BaseModel):
    """A single machine specification within a workload group."""

    id: str = Field(description="Unique identifier for this machine row")
    name: str = Field(default="", description="Human-readable machine label")
    cpu: int = Field(ge=1, le=512, description="Number of vCPUs")
    ram: float = Field(ge=0.5, le=12288, description="RAM in GB")
    storage: float = Field(default=0, ge=0, le=65536, description="Storage in GB")
    quantity: int = Field(default=1, ge=1, le=1000, description="Number of instances")
    role: MachineRole = Field(default=MachineRole.WEB, description="Machine role")


class WorkloadGroup(BaseModel):
    """A group of machines representing a complete environment."""

    name: str = Field(default="My Workload", description="Group name")
    machines: list[MachineItem] = Field(min_length=1)
    region: str = Field(default="us-east-1")
    storage_type: str = Field(default="ssd")
    os: str = Field(default="linux")
    monthly_hours: float = Field(default=730, ge=0, le=744)
    description: str = Field(default="", description="Free-form usage scenario description")


class MachineEstimateDetail(BaseModel):
    """Cost estimate for a single machine item within a group, for one provider."""

    machine: MachineItem
    matched_instance: str
    unit_monthly_on_demand: float
    unit_monthly_reserved_1y: Optional[float] = None
    subtotal_on_demand: float = Field(description="unit cost * quantity")
    subtotal_reserved_1y: Optional[float] = None
    details: dict = Field(default_factory=dict)


class GroupProviderEstimate(BaseModel):
    """Full estimate from one provider for an entire workload group."""

    provider: CloudProvider
    region_name: str
    machines: list[MachineEstimateDetail]
    total_monthly_on_demand: float
    total_monthly_reserved_1y: Optional[float] = None
    total_machines: int = Field(description="Sum of all machine quantities")
    warnings: list[str] = Field(default_factory=list)


class GroupComparisonResult(BaseModel):
    """Aggregated comparison of a workload group across all providers."""

    group: WorkloadGroup
    estimates: list[GroupProviderEstimate]
    cheapest_on_demand: Optional[CloudProvider] = None
    cheapest_reserved: Optional[CloudProvider] = None
    recommendation: str = Field(default="")
