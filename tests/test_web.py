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
        # Result data is embedded as JSON for client-side rendering
        body = resp.text.lower()
        assert "aws" in body
        assert "gcp" in body
        assert "azure" in body
        assert "oracle" in body


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
    async def test_api_compare_group(self, client):
        resp = await client.post(
            "/api/compare-group",
            json={
                "name": "Test Workload",
                "machines": [
                    {"id": "web1", "name": "Web", "cpu": 2, "ram": 4, "storage": 50, "quantity": 2, "role": "web"},
                    {"id": "db1", "name": "DB", "cpu": 4, "ram": 16, "storage": 200, "quantity": 1, "role": "db"},
                ],
                "region": "us-east-1",
                "include_ai": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["estimates"]) == 4
        assert data["cheapest_on_demand"] is not None
        # Each provider should have 2 machine entries
        for est in data["estimates"]:
            assert len(est["machines"]) == 2
            assert est["total_machines"] == 3  # 2 + 1
            assert est["total_monthly_on_demand"] > 0
            # Verify subtotals: web has quantity=2 so subtotal = unit * 2
            web_machine = next(m for m in est["machines"] if m["machine"]["id"] == "web1")
            assert abs(web_machine["subtotal_on_demand"] - web_machine["unit_monthly_on_demand"] * 2) < 0.01

    @pytest.mark.asyncio
    async def test_api_compare_group_single_machine(self, client):
        resp = await client.post(
            "/api/compare-group",
            json={
                "machines": [
                    {"id": "m1", "cpu": 4, "ram": 16, "quantity": 1, "role": "api"},
                ],
                "region": "us-east-1",
                "include_ai": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        providers = {e["provider"] for e in data["estimates"]}
        assert providers == {"aws", "gcp", "azure", "oracle"}
        for est in data["estimates"]:
            assert est["total_machines"] == 1

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


class TestLLMQuotaAPI:
    @pytest.mark.asyncio
    async def test_model_catalogue(self, client):
        resp = await client.get("/api/llm-quota/models")
        assert resp.status_code == 200
        models = resp.json()
        assert {m["model"] for m in models} == {"fable-5-1", "fable-5", "opus-5", "sonnet-5"}
        assert all(m["pricing"]["input_per_mtok"] > 0 for m in models)

    @pytest.mark.asyncio
    async def test_quota_plan_table(self, client):
        resp = await client.get("/api/llm-quota/plans")
        assert resp.status_code == 200
        plans = resp.json()
        assert len(plans) == 32
        assert {p["platform"] for p in plans} == {"anthropic", "bedrock", "foundry", "vertex"}
        assert all(p["source"].startswith("https://") for p in plans)

    @pytest.mark.asyncio
    async def test_quota_plan_table_filters_compose(self, client):
        resp = await client.get(
            "/api/llm-quota/plans", params={"model": "opus-5", "platform": "vertex"}
        )
        assert resp.status_code == 200
        plans = resp.json()
        assert len(plans) == 2
        assert all(p["model"] == "opus-5" and p["platform"] == "vertex" for p in plans)

    @pytest.mark.asyncio
    async def test_evaluate_workload(self, client):
        resp = await client.post(
            "/api/llm-quota",
            json={
                "model": "fable-5-1",
                "apps": [
                    {
                        "name": "RAG",
                        "concurrent_users": 100,
                        "requests_per_user_per_minute": 1,
                        "input_tokens_per_request": 20000,
                        "output_tokens_per_request": 2000,
                        "cache_hit_rate": 0,
                    }
                ],
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["required_rpm"] == 100
        assert body["required_itpm"] == 2_000_000
        assert body["required_otpm"] == 200_000
        assert body["cost"]["per_1k_requests_usd"] == 300.0

        by_plan = {r["plan_id"]: r for r in body["results"]}
        assert by_plan["start"]["verdict"] == "over"
        assert by_plan["scale"]["verdict"] == "ample"
        assert by_plan["scale"]["max_users"] == 200
        assert by_plan["payg"]["verdict"] == "blocked"
        assert by_plan["mantle"]["verdict"] == "unknown"
        # Over-quota plans must come with concrete next steps.
        assert {a["kind"] for a in by_plan["start"]["actions"]} >= {
            "request_quota",
            "switch_plan",
        }

    @pytest.mark.asyncio
    async def test_several_apps_are_summed(self, client):
        resp = await client.post(
            "/api/llm-quota",
            json={
                "apps": [
                    {"name": "A", "concurrent_users": 100},
                    {"name": "B", "concurrent_users": 50},
                ]
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_users"] == 150
        assert body["required_rpm"] == 150

    @pytest.mark.asyncio
    async def test_account_quota_resolves_an_unknown_plan(self, client):
        resp = await client.post(
            "/api/llm-quota",
            params={"platform": "bedrock"},
            json={
                "apps": [{"concurrent_users": 100}],
                "max_tokens": 4000,
                "account_quotas": [
                    {"plan_id": "mantle", "itpm": 20000000, "otpm": 4000000}
                ],
            },
        )
        assert resp.status_code == 200
        mantle = resp.json()["results"][0]
        assert mantle["verdict"] == "ample"
        assert mantle["itpm"]["from_account"] is True

    @pytest.mark.asyncio
    async def test_response_carries_no_infinities(self, client):
        """Browsers reject JSON's Infinity token, so a zero quota must not emit one."""
        import json

        resp = await client.post("/api/llm-quota", json={"apps": [{"concurrent_users": 100}]})
        assert resp.status_code == 200
        json.loads(resp.text, parse_constant=lambda c: pytest.fail(f"non-finite: {c}"))

    @pytest.mark.asyncio
    async def test_rejects_invalid_workload(self, client):
        resp = await client.post("/api/llm-quota", json={"apps": [{"concurrent_users": 0}]})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_index_page_serves_the_shared_planner_assets(self, client):
        resp = await client.get("/")
        assert 'data-mode="llm"' in resp.text
        for asset in ("/static/llm/style.css", "/static/llm/data.js",
                      "/static/llm/render.js", "/static/llm/form.js"):
            assert asset in resp.text
        assert "/api/llm-quota" in resp.text

    @pytest.mark.asyncio
    async def test_shared_assets_are_served(self, client):
        for path in ("style.css", "data.js", "render.js", "form.js"):
            resp = await client.get(f"/static/llm/{path}")
            assert resp.status_code == 200, path
            assert len(resp.text) > 500
