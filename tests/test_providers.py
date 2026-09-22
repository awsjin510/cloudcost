"""Tests for cloud provider calculators."""

import pytest

from cloudcost.models.spec import CloudProvider, CloudSpec, PricingTier, Region, StorageType
from cloudcost.providers.aws import AWSCalculator, _DATA_TRANSFER_TIERS
from cloudcost.utils.pricing import calc_tiered_cost
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
        network_transfer_gb=500,
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
        # First 100 GB/month free
        cost = calc_tiered_cost(50, _DATA_TRANSFER_TIERS)
        assert cost == 0.0

        # Beyond the free allowance, egress is billed
        cost = calc_tiered_cost(500, _DATA_TRANSFER_TIERS)
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


class TestOracleApiParsing:
    """Unit tests for the OCI pricing API response parser (no network)."""

    _E4_OCPU_ITEM = {
        "partNumber": "B93113",
        "displayName": "Compute - Standard - E4 - OCPU",
        "metricName": "OCPU Per Hour",
        "currencyCodeLocalizations": [
            {"currencyCode": "USD", "prices": [{"model": "PAY_AS_YOU_GO", "value": 0.025}]}
        ],
    }
    _A1_OCPU_ITEM = {
        "partNumber": "B93297",
        "displayName": "Compute - Standard - A1 - OCPU",
        "currencyCodeLocalizations": [
            {
                "currencyCode": "USD",
                "prices": [
                    {"model": "PAY_AS_YOU_GO", "value": 0},
                    {"model": "PAY_AS_YOU_GO", "value": 0.01},
                ],
            }
        ],
    }

    def test_extract_payg_rate(self):
        assert OracleCalculator._extract_payg_rate(self._E4_OCPU_ITEM) == 0.025

    def test_extract_payg_rate_skips_free_tier_row(self):
        assert OracleCalculator._extract_payg_rate(self._A1_OCPU_ITEM) == 0.01

    def test_extract_payg_rate_missing(self):
        assert OracleCalculator._extract_payg_rate({"partNumber": "X"}) is None
        assert OracleCalculator._extract_payg_rate(
            {"currencyCodeLocalizations": [{"currencyCode": "EUR", "prices": [{"model": "PAY_AS_YOU_GO", "value": 1}]}]}
        ) is None

    def test_find_in_listing_excludes_other_products(self):
        items = [
            {"displayName": "Oracle Cloud VMware Solution - BM.Standard.E4.32 - Hourly Commit",
             "currencyCodeLocalizations": [{"currencyCode": "USD", "prices": [{"model": "PAY_AS_YOU_GO", "value": 9.25}]}]},
            {"displayName": "Compute - Dense I/O - E4 - OCPU",
             "currencyCodeLocalizations": [{"currencyCode": "USD", "prices": [{"model": "PAY_AS_YOU_GO", "value": 0.025}]}]},
            self._E4_OCPU_ITEM,
        ]
        rate = OracleCalculator._find_in_listing(items, ("compute", "standard", "e4", "ocpu"))
        assert rate == 0.025
        assert OracleCalculator._find_in_listing(items, ("compute", "standard", "x9", "ocpu")) is None
