"""Tests for Pydantic data models and naming conversion layer."""

import pytest

from cloudcost.models.naming import (
    get_provider_database_name,
    get_provider_region,
    get_provider_storage_name,
    match_instance,
)
from cloudcost.models.spec import (
    CloudProvider,
    CloudSpec,
    DatabaseType,
    MachineItem,
    MachineRole,
    PricingResult,
    PricingTier,
    Region,
    StorageType,
    WorkloadGroup,
)


class TestCloudSpec:
    def test_defaults(self):
        spec = CloudSpec(cpu_cores=2, ram_gb=8)
        assert spec.storage_type == StorageType.SSD
        assert spec.region == Region.US_EAST_1
        assert spec.monthly_hours == 730
        assert spec.os == "linux"

    def test_os_normalization(self):
        spec = CloudSpec(cpu_cores=1, ram_gb=1, os="Windows Server")
        assert spec.os == "windows"

        spec2 = CloudSpec(cpu_cores=1, ram_gb=1, os="Ubuntu")
        assert spec2.os == "linux"

    def test_validation_cpu_min(self):
        with pytest.raises(Exception):
            CloudSpec(cpu_cores=0, ram_gb=1)

    def test_validation_ram_min(self):
        with pytest.raises(Exception):
            CloudSpec(cpu_cores=1, ram_gb=0.1)


class TestRegionMapping:
    def test_us_east_1_all_providers(self):
        assert get_provider_region(Region.US_EAST_1, CloudProvider.AWS) == "us-east-1"
        assert get_provider_region(Region.US_EAST_1, CloudProvider.GCP) == "us-east1"
        assert get_provider_region(Region.US_EAST_1, CloudProvider.AZURE) == "eastus"
        assert get_provider_region(Region.US_EAST_1, CloudProvider.ORACLE) == "us-ashburn-1"

    def test_ap_northeast_1(self):
        assert get_provider_region(Region.AP_NORTHEAST_1, CloudProvider.AWS) == "ap-northeast-1"
        assert get_provider_region(Region.AP_NORTHEAST_1, CloudProvider.GCP) == "asia-northeast1"


class TestStorageMapping:
    def test_ssd_mapping(self):
        assert get_provider_storage_name(StorageType.SSD, CloudProvider.AWS) == "gp3"
        assert get_provider_storage_name(StorageType.SSD, CloudProvider.GCP) == "pd-ssd"

    def test_hdd_mapping(self):
        assert get_provider_storage_name(StorageType.HDD, CloudProvider.AWS) == "st1"


class TestDatabaseMapping:
    def test_postgresql_mapping(self):
        name = get_provider_database_name(DatabaseType.POSTGRESQL, CloudProvider.AWS)
        assert "PostgreSQL" in name

    def test_none_mapping(self):
        name = get_provider_database_name(DatabaseType.NONE, CloudProvider.AWS)
        assert name == ""


class TestInstanceMatching:
    def test_match_2vcpu_8gb_aws(self):
        spec = CloudSpec(cpu_cores=2, ram_gb=8)
        inst = match_instance(spec, CloudProvider.AWS)
        assert inst["vcpu"] >= 2
        assert inst["ram"] >= 8

    def test_match_4vcpu_16gb_gcp(self):
        spec = CloudSpec(cpu_cores=4, ram_gb=16)
        inst = match_instance(spec, CloudProvider.GCP)
        assert inst["vcpu"] >= 4
        assert inst["ram"] >= 16

    def test_match_smallest_fit(self):
        spec = CloudSpec(cpu_cores=2, ram_gb=8)
        inst = match_instance(spec, CloudProvider.AWS)
        # Should pick t3.large (2 vCPU, 8 GB) or m5.large (2 vCPU, 8 GB)
        assert inst["vcpu"] == 2
        assert inst["ram"] == 8.0

    def test_no_match_raises(self):
        spec = CloudSpec(cpu_cores=512, ram_gb=12288)
        with pytest.raises(ValueError, match="No aws instance found"):
            match_instance(spec, CloudProvider.AWS)


class TestMachineItem:
    def test_defaults(self):
        m = MachineItem(id="m1", cpu=2, ram=8)
        assert m.quantity == 1
        assert m.role == MachineRole.WEB
        assert m.storage == 0

    def test_all_roles(self):
        for role in MachineRole:
            m = MachineItem(id="m1", cpu=1, ram=1, role=role)
            assert m.role == role

    def test_validation_cpu_min(self):
        with pytest.raises(Exception):
            MachineItem(id="m1", cpu=0, ram=1)

    def test_validation_quantity_min(self):
        with pytest.raises(Exception):
            MachineItem(id="m1", cpu=1, ram=1, quantity=0)


class TestWorkloadGroup:
    def test_creation(self):
        machines = [
            MachineItem(id="web", name="Web Server", cpu=2, ram=4, quantity=3, role=MachineRole.WEB),
            MachineItem(id="db", name="DB Server", cpu=4, ram=32, quantity=1, role=MachineRole.DB),
        ]
        group = WorkloadGroup(name="Prod", machines=machines, region="us-east-1")
        assert len(group.machines) == 2
        assert group.name == "Prod"
        assert sum(m.quantity for m in group.machines) == 4

    def test_empty_machines_rejected(self):
        with pytest.raises(Exception):
            WorkloadGroup(name="Empty", machines=[])


class TestPricingResult:
    def test_creation(self):
        pr = PricingResult(
            provider=CloudProvider.AWS,
            tier=PricingTier.ON_DEMAND,
            instance_type="m5.large",
            hourly_cost=0.096,
            monthly_cost=70.08,
        )
        assert pr.currency == "USD"
        assert pr.monthly_cost == 70.08
