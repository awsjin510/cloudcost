"""Tests for CloudCostComparator."""

import pytest

from cloudcost.comparator import CloudCostComparator
from cloudcost.models.spec import CloudSpec, MachineItem, MachineRole, Region, StorageType, WorkloadGroup


@pytest.fixture
def comparator():
    return CloudCostComparator()


@pytest.fixture
def standard_spec():
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


class TestCloudCostComparator:
    @pytest.mark.asyncio
    async def test_compare_returns_all_providers(self, comparator, standard_spec):
        result = await comparator.compare(standard_spec)

        assert len(result.estimates) == 4
        providers = {e.provider.value for e in result.estimates}
        assert providers == {"aws", "gcp", "azure", "oracle"}

    @pytest.mark.asyncio
    async def test_cheapest_on_demand_set(self, comparator, standard_spec):
        result = await comparator.compare(standard_spec)
        assert result.cheapest_on_demand is not None

    @pytest.mark.asyncio
    async def test_cheapest_reserved_set(self, comparator, standard_spec):
        result = await comparator.compare(standard_spec)
        assert result.cheapest_reserved is not None

    @pytest.mark.asyncio
    async def test_spec_preserved(self, comparator, standard_spec):
        result = await comparator.compare(standard_spec)
        assert result.spec == standard_spec

    @pytest.mark.asyncio
    async def test_all_estimates_positive(self, comparator, standard_spec):
        result = await comparator.compare(standard_spec)
        for est in result.estimates:
            assert est.total_monthly_on_demand > 0
            assert est.on_demand.hourly_cost > 0

    @pytest.mark.asyncio
    async def test_compare_group(self, comparator):
        group = WorkloadGroup(
            name="Test Group",
            machines=[
                MachineItem(id="web", name="Web", cpu=2, ram=4, quantity=2, role=MachineRole.WEB),
                MachineItem(id="db", name="DB", cpu=4, ram=16, storage=200, quantity=1, role=MachineRole.DB),
            ],
            region="us-east-1",
        )
        result = await comparator.compare_group(group)

        assert len(result.estimates) == 4
        assert result.cheapest_on_demand is not None

        for est in result.estimates:
            assert est.total_machines == 3
            assert len(est.machines) == 2
            assert est.total_monthly_on_demand > 0

            # Verify subtotals add up to total
            calc_total = sum(m.subtotal_on_demand for m in est.machines)
            assert abs(calc_total - est.total_monthly_on_demand) < 0.01

            # Verify subtotal = unit * quantity
            for md in est.machines:
                expected = md.unit_monthly_on_demand * md.machine.quantity
                assert abs(md.subtotal_on_demand - expected) < 0.01

    @pytest.mark.asyncio
    async def test_compare_group_preserves_group(self, comparator):
        group = WorkloadGroup(
            name="My Group",
            machines=[
                MachineItem(id="m1", cpu=2, ram=8, quantity=5, role=MachineRole.WORKER),
            ],
            region="us-east-1",
        )
        result = await comparator.compare_group(group)
        assert result.group == group
        assert result.group.name == "My Group"

    @pytest.mark.asyncio
    async def test_tokyo_region(self, comparator):
        spec = CloudSpec(
            cpu_cores=2,
            ram_gb=8,
            region=Region.AP_NORTHEAST_1,
        )
        result = await comparator.compare(spec)
        assert len(result.estimates) == 4
