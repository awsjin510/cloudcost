"""Standardized naming conversion layer: maps generic specs to provider-specific names."""

from __future__ import annotations

from .spec import CloudProvider, CloudSpec, DatabaseType, Region, StorageType

# ---------------------------------------------------------------------------
# Region mapping: normalized region -> provider-specific region code
# ---------------------------------------------------------------------------
REGION_MAP: dict[Region, dict[CloudProvider, str]] = {
    Region.US_EAST_1: {
        CloudProvider.AWS: "us-east-1",
        CloudProvider.GCP: "us-east1",
        CloudProvider.AZURE: "eastus",
        CloudProvider.ORACLE: "us-ashburn-1",
    },
    Region.US_WEST_2: {
        CloudProvider.AWS: "us-west-2",
        CloudProvider.GCP: "us-west1",
        CloudProvider.AZURE: "westus2",
        CloudProvider.ORACLE: "us-phoenix-1",
    },
    Region.AP_NORTHEAST_1: {
        CloudProvider.AWS: "ap-northeast-1",
        CloudProvider.GCP: "asia-northeast1",
        CloudProvider.AZURE: "japaneast",
        CloudProvider.ORACLE: "ap-tokyo-1",
    },
    Region.AP_NORTHEAST_2: {
        CloudProvider.AWS: "ap-northeast-2",
        CloudProvider.GCP: "asia-northeast3",
        CloudProvider.AZURE: "koreacentral",
        CloudProvider.ORACLE: "ap-seoul-1",
    },
    Region.AP_SOUTHEAST_1: {
        CloudProvider.AWS: "ap-southeast-1",
        CloudProvider.GCP: "asia-southeast1",
        CloudProvider.AZURE: "southeastasia",
        CloudProvider.ORACLE: "ap-singapore-1",
    },
    Region.AP_EAST_1: {
        CloudProvider.AWS: "ap-east-1",
        CloudProvider.GCP: "asia-east2",
        CloudProvider.AZURE: "eastasia",
        CloudProvider.ORACLE: "ap-singapore-1",
    },
    Region.AP_EAST_2: {
        CloudProvider.AWS: "ap-east-2",
        CloudProvider.GCP: "asia-east1",
        CloudProvider.AZURE: "taiwannorth",
        CloudProvider.ORACLE: "ap-singapore-1",
    },
    Region.EU_WEST_1: {
        CloudProvider.AWS: "eu-west-1",
        CloudProvider.GCP: "europe-west1",
        CloudProvider.AZURE: "westeurope",
        CloudProvider.ORACLE: "eu-amsterdam-1",
    },
}

# ---------------------------------------------------------------------------
# Instance family matching: find the best instance type for a given spec
# ---------------------------------------------------------------------------

# AWS EC2 instance catalog (representative subset)
AWS_INSTANCE_CATALOG: list[dict] = [
    {"type": "t3.micro", "vcpu": 2, "ram": 1.0},
    {"type": "t3.small", "vcpu": 2, "ram": 2.0},
    {"type": "t3.medium", "vcpu": 2, "ram": 4.0},
    {"type": "t3.large", "vcpu": 2, "ram": 8.0},
    {"type": "t3.xlarge", "vcpu": 4, "ram": 16.0},
    {"type": "t3.2xlarge", "vcpu": 8, "ram": 32.0},
    {"type": "m5.large", "vcpu": 2, "ram": 8.0},
    {"type": "m5.xlarge", "vcpu": 4, "ram": 16.0},
    {"type": "m5.2xlarge", "vcpu": 8, "ram": 32.0},
    {"type": "m5.4xlarge", "vcpu": 16, "ram": 64.0},
    {"type": "m5.8xlarge", "vcpu": 32, "ram": 128.0},
    {"type": "m5.12xlarge", "vcpu": 48, "ram": 192.0},
    {"type": "m5.16xlarge", "vcpu": 64, "ram": 256.0},
    {"type": "c5.large", "vcpu": 2, "ram": 4.0},
    {"type": "c5.xlarge", "vcpu": 4, "ram": 8.0},
    {"type": "c5.2xlarge", "vcpu": 8, "ram": 16.0},
    {"type": "c5.4xlarge", "vcpu": 16, "ram": 32.0},
    {"type": "c5.9xlarge", "vcpu": 36, "ram": 72.0},
    {"type": "r5.large", "vcpu": 2, "ram": 16.0},
    {"type": "r5.xlarge", "vcpu": 4, "ram": 32.0},
    {"type": "r5.2xlarge", "vcpu": 8, "ram": 64.0},
    {"type": "r5.4xlarge", "vcpu": 16, "ram": 128.0},
]

GCP_INSTANCE_CATALOG: list[dict] = [
    {"type": "e2-micro", "vcpu": 0.25, "ram": 1.0},
    {"type": "e2-small", "vcpu": 0.5, "ram": 2.0},
    {"type": "e2-medium", "vcpu": 1, "ram": 4.0},
    {"type": "e2-standard-2", "vcpu": 2, "ram": 8.0},
    {"type": "e2-standard-4", "vcpu": 4, "ram": 16.0},
    {"type": "e2-standard-8", "vcpu": 8, "ram": 32.0},
    {"type": "e2-standard-16", "vcpu": 16, "ram": 64.0},
    {"type": "e2-standard-32", "vcpu": 32, "ram": 128.0},
    {"type": "n2-standard-2", "vcpu": 2, "ram": 8.0},
    {"type": "n2-standard-4", "vcpu": 4, "ram": 16.0},
    {"type": "n2-standard-8", "vcpu": 8, "ram": 32.0},
    {"type": "n2-standard-16", "vcpu": 16, "ram": 64.0},
    {"type": "n2-standard-32", "vcpu": 32, "ram": 128.0},
    {"type": "n2-standard-48", "vcpu": 48, "ram": 192.0},
    {"type": "n2-standard-64", "vcpu": 64, "ram": 256.0},
    {"type": "c2-standard-4", "vcpu": 4, "ram": 16.0},
    {"type": "c2-standard-8", "vcpu": 8, "ram": 32.0},
    {"type": "c2-standard-16", "vcpu": 16, "ram": 64.0},
    {"type": "n2-highmem-2", "vcpu": 2, "ram": 16.0},
    {"type": "n2-highmem-4", "vcpu": 4, "ram": 32.0},
    {"type": "n2-highmem-8", "vcpu": 8, "ram": 64.0},
    {"type": "n2-highmem-16", "vcpu": 16, "ram": 128.0},
]

AZURE_INSTANCE_CATALOG: list[dict] = [
    {"type": "Standard_B1s", "vcpu": 1, "ram": 1.0},
    {"type": "Standard_B1ms", "vcpu": 1, "ram": 2.0},
    {"type": "Standard_B2s", "vcpu": 2, "ram": 4.0},
    {"type": "Standard_B2ms", "vcpu": 2, "ram": 8.0},
    {"type": "Standard_D2s_v5", "vcpu": 2, "ram": 8.0},
    {"type": "Standard_D4s_v5", "vcpu": 4, "ram": 16.0},
    {"type": "Standard_D8s_v5", "vcpu": 8, "ram": 32.0},
    {"type": "Standard_D16s_v5", "vcpu": 16, "ram": 64.0},
    {"type": "Standard_D32s_v5", "vcpu": 32, "ram": 128.0},
    {"type": "Standard_D48s_v5", "vcpu": 48, "ram": 192.0},
    {"type": "Standard_D64s_v5", "vcpu": 64, "ram": 256.0},
    {"type": "Standard_F2s_v2", "vcpu": 2, "ram": 4.0},
    {"type": "Standard_F4s_v2", "vcpu": 4, "ram": 8.0},
    {"type": "Standard_F8s_v2", "vcpu": 8, "ram": 16.0},
    {"type": "Standard_F16s_v2", "vcpu": 16, "ram": 32.0},
    {"type": "Standard_E2s_v5", "vcpu": 2, "ram": 16.0},
    {"type": "Standard_E4s_v5", "vcpu": 4, "ram": 32.0},
    {"type": "Standard_E8s_v5", "vcpu": 8, "ram": 64.0},
    {"type": "Standard_E16s_v5", "vcpu": 16, "ram": 128.0},
]

# OCI: 1 OCPU = 2 vCPU (x86).  vcpu below = real vCPU count (2 × OCPU).
# Default RAM: E4 & Std3 = 16 GB/OCPU, Optimized3 = 14 GB/OCPU.
ORACLE_INSTANCE_CATALOG: list[dict] = [
    {"type": "VM.Standard.E4.Flex-1", "vcpu": 2, "ram": 16.0},
    {"type": "VM.Standard.E4.Flex-2", "vcpu": 4, "ram": 32.0},
    {"type": "VM.Standard.E4.Flex-4", "vcpu": 8, "ram": 64.0},
    {"type": "VM.Standard.E4.Flex-8", "vcpu": 16, "ram": 128.0},
    {"type": "VM.Standard.E4.Flex-16", "vcpu": 32, "ram": 256.0},
    {"type": "VM.Standard3.Flex-2", "vcpu": 4, "ram": 32.0},
    {"type": "VM.Standard3.Flex-4", "vcpu": 8, "ram": 64.0},
    {"type": "VM.Standard3.Flex-8", "vcpu": 16, "ram": 128.0},
    {"type": "VM.Standard3.Flex-16", "vcpu": 32, "ram": 256.0},
    {"type": "VM.Optimized3.Flex-2", "vcpu": 4, "ram": 28.0},
    {"type": "VM.Optimized3.Flex-4", "vcpu": 8, "ram": 56.0},
    {"type": "VM.Optimized3.Flex-8", "vcpu": 16, "ram": 112.0},
]

PROVIDER_CATALOGS: dict[CloudProvider, list[dict]] = {
    CloudProvider.AWS: AWS_INSTANCE_CATALOG,
    CloudProvider.GCP: GCP_INSTANCE_CATALOG,
    CloudProvider.AZURE: AZURE_INSTANCE_CATALOG,
    CloudProvider.ORACLE: ORACLE_INSTANCE_CATALOG,
}

# ---------------------------------------------------------------------------
# Storage type mapping
# ---------------------------------------------------------------------------
STORAGE_TYPE_MAP: dict[StorageType, dict[CloudProvider, str]] = {
    StorageType.SSD: {
        CloudProvider.AWS: "gp3",
        CloudProvider.GCP: "pd-ssd",
        CloudProvider.AZURE: "Premium_LRS",
        CloudProvider.ORACLE: "Block Volume (SSD)",
    },
    StorageType.HDD: {
        CloudProvider.AWS: "st1",
        CloudProvider.GCP: "pd-standard",
        CloudProvider.AZURE: "Standard_LRS",
        CloudProvider.ORACLE: "Block Volume (HDD)",
    },
    StorageType.NVME: {
        CloudProvider.AWS: "io2",
        CloudProvider.GCP: "pd-extreme",
        CloudProvider.AZURE: "UltraSSD_LRS",
        CloudProvider.ORACLE: "Block Volume (Ultra High Performance)",
    },
}

# ---------------------------------------------------------------------------
# Database engine mapping
# ---------------------------------------------------------------------------
DATABASE_MAP: dict[DatabaseType, dict[CloudProvider, str]] = {
    DatabaseType.MYSQL: {
        CloudProvider.AWS: "Amazon RDS for MySQL",
        CloudProvider.GCP: "Cloud SQL for MySQL",
        CloudProvider.AZURE: "Azure Database for MySQL",
        CloudProvider.ORACLE: "MySQL Database Service",
    },
    DatabaseType.POSTGRESQL: {
        CloudProvider.AWS: "Amazon RDS for PostgreSQL",
        CloudProvider.GCP: "Cloud SQL for PostgreSQL",
        CloudProvider.AZURE: "Azure Database for PostgreSQL",
        CloudProvider.ORACLE: "PostgreSQL Database Service",
    },
    DatabaseType.MARIADB: {
        CloudProvider.AWS: "Amazon RDS for MariaDB",
        CloudProvider.GCP: "Cloud SQL for MySQL",  # GCP uses MySQL-compatible
        CloudProvider.AZURE: "Azure Database for MariaDB",
        CloudProvider.ORACLE: "MySQL Database Service",
    },
    DatabaseType.MSSQL: {
        CloudProvider.AWS: "Amazon RDS for SQL Server",
        CloudProvider.GCP: "Cloud SQL for SQL Server",
        CloudProvider.AZURE: "Azure SQL Database",
        CloudProvider.ORACLE: "N/A",
    },
    DatabaseType.ORACLE: {
        CloudProvider.AWS: "Amazon RDS for Oracle",
        CloudProvider.GCP: "N/A",
        CloudProvider.AZURE: "N/A",
        CloudProvider.ORACLE: "Oracle Autonomous Database",
    },
    DatabaseType.NONE: {
        CloudProvider.AWS: "",
        CloudProvider.GCP: "",
        CloudProvider.AZURE: "",
        CloudProvider.ORACLE: "",
    },
}


def get_provider_region(region: Region, provider: CloudProvider) -> str:
    """Convert a normalized region to a provider-specific region code."""
    mapping = REGION_MAP.get(region)
    if not mapping or provider not in mapping:
        raise ValueError(
            f"Region {region.value} not mapped for provider {provider.value}"
        )
    return mapping[provider]


def get_provider_storage_name(
    storage_type: StorageType, provider: CloudProvider
) -> str:
    """Get the provider-specific storage product name."""
    return STORAGE_TYPE_MAP[storage_type][provider]


def get_provider_database_name(
    db_type: DatabaseType, provider: CloudProvider
) -> str:
    """Get the provider-specific managed database service name."""
    return DATABASE_MAP[db_type][provider]


def match_instance(spec: CloudSpec, provider: CloudProvider) -> dict:
    """Find the smallest instance that meets or exceeds the requested spec.

    Matching strategy:
      1. Filter instances where vcpu >= spec.cpu_cores AND ram >= spec.ram_gb
      2. Sort by (vcpu, ram) ascending — pick the tightest fit
      3. Return the best match, or raise ValueError if nothing fits
    """
    catalog = PROVIDER_CATALOGS[provider]
    candidates = [
        inst
        for inst in catalog
        if inst["vcpu"] >= spec.cpu_cores and inst["ram"] >= spec.ram_gb
    ]
    if not candidates:
        raise ValueError(
            f"No {provider.value} instance found for "
            f"{spec.cpu_cores} vCPU / {spec.ram_gb} GB RAM"
        )
    candidates.sort(key=lambda x: (x["vcpu"], x["ram"]))
    return candidates[0]
