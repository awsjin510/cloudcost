"""Tests for cloud provider calculators."""

import pytest

from cloudcost.models.spec import CloudProvider, CloudSpec, PricingTier, Region, StorageType
from cloudcost.providers.aws import AWSCalculator
from cloudcost.providers.azure import AzureCalculator
from cloudcost.providers.gcp import GCPCalculator
from cloudcost.providers.oracle import OracleCalculator


@pytest.fixture
def basic_spec():
    return CloudSpec(
        cpu_cores=4,
        ram_gb=16,
        storage_gb=100,
        storage_type=StorageType.SSD,
        network_transfer_gb=50,
        region=Region.US_EAST_1,
        monthly_hours=730,
        os="linux",
    )


@pytest.fixture
def tokyo_spec():
    return CloudSpec(
        cpu_cores=2,
        ram_gb=8,
        storage_gb=50,
        region=Region.AP_NORTHEAST_1,
    )


class TestAWSCalculator:
    @pytest.mark.asyncio
    async def test_estimate_basic(self, basic_spec):
        calc = AWSCalculator()
        est = await calc.estimate(basic_spec)

        assert est.provider == CloudProvider.AWS
        assert est.on_demand.tier == PricingTier.ON_DEMAND
        assert est.on_demand.hourly_cost > 0
        assert est.on_demand.monthly_cost > 0
        assert est.total_monthly_on_demand > 0
        assert est.reserved_1y is not None
        assert est.total_monthly_reserved_1y < est.total_monthly_on_demand

    @pytest.mark.asyncio
    async def test_storage_included(self, basic_spec):
        calc = AWSCalculator()
        est = await calc.estimate(basic_spec)
        assert est.on_demand.details["storage"] > 0

    @pytest.mark.asyncio
    async def test_network_included(self, basic_spec):
        calc = AWSCalculator()
        est = await calc.estimate(basic_spec)
        assert est.on_demand.details["network"] > 0

    @pytest.mark.asyncio
    async def test_data_transfer_calculation(self):
        # First 1 GB free
        cost = AWSCalculator._calc_data_transfer(0.5)
        assert cost == 0.0

        cost = AWSCalculator._calc_data_transfer(100)
        assert cost > 0


class TestGCPCalculator:
    @pytest.mark.asyncio
    async def test_estimate_basic(self, basic_spec):
        calc = GCPCalculator()
        est = await calc.estimate(basic_spec)

        assert est.provider == CloudProvider.GCP
        assert est.total_monthly_on_demand > 0
        assert est.reserved_1y is not None
        assert "CUD" in est.reserved_1y.notes[0]

    @pytest.mark.asyncio
    async def test_tokyo_region_multiplier(self, tokyo_spec):
        calc = GCPCalculator()
        est_tokyo = await calc.estimate(tokyo_spec)

        us_spec = CloudSpec(cpu_cores=2, ram_gb=8, storage_gb=50, region=Region.US_EAST_1)
        est_us = await calc.estimate(us_spec)

        # Tokyo should be more expensive than US
        assert est_tokyo.total_monthly_on_demand > est_us.total_monthly_on_demand


class TestAzureCalculator:
    @pytest.mark.asyncio
    async def test_estimate_basic(self, basic_spec):
        calc = AzureCalculator()
        est = await calc.estimate(basic_spec)

        assert est.provider == CloudProvider.AZURE
        assert est.total_monthly_on_demand > 0
        assert est.reserved_1y is not None
        assert est.total_monthly_reserved_1y < est.total_monthly_on_demand


class TestOracleCalculator:
    @pytest.mark.asyncio
    async def test_estimate_basic(self, basic_spec):
        calc = OracleCalculator()
        est = await calc.estimate(basic_spec)

        assert est.provider == CloudProvider.ORACLE
        assert est.total_monthly_on_demand > 0

    @pytest.mark.asyncio
    async def test_oracle_cheaper_than_others(self, basic_spec):
        """OCI is generally known for competitive pricing."""
        aws_est = await AWSCalculator().estimate(basic_spec)
        oci_est = await OracleCalculator().estimate(basic_spec)

        # OCI should generally be cheaper on compute
        assert oci_est.on_demand.details["compute"] < aws_est.on_demand.details["compute"]
