"""Tests for the FastAPI web application."""

import pytest
from httpx import ASGITransport, AsyncClient

from cloudcost.web.app import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestWebUI:
    @pytest.mark.asyncio
    async def test_index_page(self, client):
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "CloudCost" in resp.text
        assert "CPU" in resp.text

    @pytest.mark.asyncio
    async def test_compare_form(self, client):
        resp = await client.post(
            "/compare",
            data={
                "cpu_cores": "4",
                "ram_gb": "16",
                "storage_gb": "100",
                "storage_type": "ssd",
                "network_transfer_gb": "50",
                "database_type": "none",
                "region": "us-east-1",
                "monthly_hours": "730",
                "os_type": "linux",
                "description": "",
            },
        )
        assert resp.status_code == 200
        assert "AWS" in resp.text
        assert "GCP" in resp.text
        assert "AZURE" in resp.text
        assert "ORACLE" in resp.text


class TestAPI:
    @pytest.mark.asyncio
    async def test_api_compare(self, client):
        resp = await client.post(
            "/api/compare",
            json={
                "cpu_cores": 2,
                "ram_gb": 8,
                "storage_gb": 50,
                "region": "us-east-1",
                "include_ai": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["estimates"]) == 4
        assert data["cheapest_on_demand"] is not None

    @pytest.mark.asyncio
    async def test_api_compare_tokyo(self, client):
        resp = await client.post(
            "/api/compare",
            json={
                "cpu_cores": 4,
                "ram_gb": 16,
                "region": "ap-northeast-1",
                "include_ai": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        providers = {e["provider"] for e in data["estimates"]}
        assert providers == {"aws", "gcp", "azure", "oracle"}
