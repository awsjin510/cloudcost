"""Tests for the Claude Fable 5 / 5.1 quota calculator."""

import pytest

from cloudcost.llm import (
    FABLE_MAX_OUTPUT_TOKENS,
    LimitStatus,
    LLMPlatform,
    LLMWorkload,
    Verdict,
    evaluate_workload,
    list_plans,
)


@pytest.fixture
def slide_workload():
    """The 100-user peak scenario: 20K in, 2K out, one request each per minute."""
    return LLMWorkload(
        concurrent_users=100,
        requests_per_user_per_minute=1.0,
        input_tokens_per_request=20_000,
        output_tokens_per_request=2_000,
    )


class TestDemandDerivation:
    def test_peak_demand(self, slide_workload):
        assert slide_workload.rpm == 100
        assert slide_workload.itpm == 2_000_000
        assert slide_workload.otpm == 200_000

    def test_cache_hits_cut_itpm_only(self):
        w = LLMWorkload(
            concurrent_users=100,
            input_tokens_per_request=20_000,
            output_tokens_per_request=2_000,
            cache_hit_rate=0.8,
        )
        # Only uncached input counts toward ITPM.
        assert w.itpm == pytest.approx(400_000)
        # RPM and OTPM are untouched by caching.
        assert w.rpm == 100
        assert w.otpm == 200_000

    def test_max_tokens_defaults_to_model_ceiling(self, slide_workload):
        assert slide_workload.max_tokens is None
        assert slide_workload.effective_max_tokens == FABLE_MAX_OUTPUT_TOKENS

    def test_reservation_adds_max_tokens_per_request(self):
        w = LLMWorkload(
            concurrent_users=100,
            input_tokens_per_request=20_000,
            output_tokens_per_request=2_000,
            max_tokens=4_000,
        )
        assert w.itpm == 2_000_000
        # Mantle admits on input + max_tokens: 100 x (20000 + 4000).
        assert w.itpm_with_reservation == 2_400_000

    def test_fractional_request_rate(self):
        w = LLMWorkload(concurrent_users=100, requests_per_user_per_minute=0.5)
        assert w.rpm == 50


class TestQuotaTable:
    def test_every_platform_present(self):
        platforms = {p.platform for p in list_plans()}
        assert platforms == set(LLMPlatform)

    def test_filter_by_platform(self):
        vertex = list_plans(LLMPlatform.VERTEX)
        assert vertex
        assert all(p.platform is LLMPlatform.VERTEX for p in vertex)

    def test_every_plan_cites_a_source(self):
        for plan in list_plans():
            assert plan.source.startswith("https://")
            assert plan.verified

    def test_bedrock_mantle_has_no_rpm_quota(self):
        mantle = next(p for p in list_plans(LLMPlatform.BEDROCK) if p.plan_id == "mantle")
        assert mantle.rpm.status is LimitStatus.NOT_ENFORCED
        assert mantle.itpm.status is LimitStatus.UNPUBLISHED
        assert mantle.reserves_max_tokens is True

    def test_vertex_multi_region_is_half_of_global(self):
        plans = {p.plan_id: p for p in list_plans(LLMPlatform.VERTEX)}
        assert plans["multi_region"].itpm.value * 2 == plans["global"].itpm.value
        assert plans["multi_region"].rpm.value * 2 == plans["global"].rpm.value


class TestEvaluation:
    def test_report_echoes_demand(self, slide_workload):
        report = evaluate_workload(slide_workload)
        assert report.required_rpm == 100
        assert report.required_itpm == 2_000_000
        assert report.required_otpm == 200_000

    def test_itpm_is_the_binding_dimension_for_rag(self, slide_workload):
        """A 20K-token prompt exhausts ITPM long before RPM becomes an issue."""
        report = evaluate_workload(slide_workload)
        scale = next(r for r in report.results if r.plan_id == "scale")
        assert scale.binding_dimension == "itpm"

    def test_anthropic_start_tier_is_over_quota(self, slide_workload):
        report = evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC)
        start = next(r for r in report.results if r.plan_id == "start")
        assert start.verdict is Verdict.OVER
        assert start.peak_load == pytest.approx(4.0)  # 2M needed vs 500K allowed

    def test_foundry_payg_is_blocked_not_merely_over(self, slide_workload):
        report = evaluate_workload(slide_workload, LLMPlatform.FOUNDRY)
        payg = next(r for r in report.results if r.plan_id == "payg")
        assert payg.verdict is Verdict.BLOCKED

    def test_foundry_enterprise_has_headroom(self, slide_workload):
        report = evaluate_workload(slide_workload, LLMPlatform.FOUNDRY)
        ent = next(r for r in report.results if r.plan_id == "enterprise")
        assert ent.verdict is Verdict.AMPLE
        assert ent.itpm.load == pytest.approx(0.5)

    def test_vertex_global_has_the_most_headroom(self, slide_workload):
        report = evaluate_workload(slide_workload, LLMPlatform.VERTEX)
        gl = next(r for r in report.results if r.plan_id == "global")
        assert gl.itpm.load == pytest.approx(0.1)
        assert gl.verdict is Verdict.AMPLE

    def test_unpublished_quota_yields_unknown_not_a_pass(self, slide_workload):
        report = evaluate_workload(slide_workload, LLMPlatform.BEDROCK)
        mantle = next(r for r in report.results if r.plan_id == "mantle")
        assert mantle.verdict is Verdict.UNKNOWN
        assert mantle.peak_load is None

    def test_bedrock_demand_includes_the_reservation(self, slide_workload):
        report = evaluate_workload(slide_workload, LLMPlatform.BEDROCK)
        mantle = next(r for r in report.results if r.plan_id == "mantle")
        # 100 x (20000 uncached + 128000 reserved)
        assert mantle.itpm.demand == pytest.approx(14_800_000)

    def test_caching_moves_a_tier_from_over_to_ample(self):
        cached = LLMWorkload(
            concurrent_users=100,
            input_tokens_per_request=20_000,
            output_tokens_per_request=2_000,
            cache_hit_rate=0.8,
        )
        report = evaluate_workload(cached, LLMPlatform.ANTHROPIC)
        build = next(r for r in report.results if r.plan_id == "build")
        # 400K uncached against a 1.5M ITPM ceiling.
        assert build.verdict is Verdict.AMPLE

    def test_tight_verdict_between_70_and_100_percent(self):
        w = LLMWorkload(
            concurrent_users=100,
            input_tokens_per_request=35_000,
            output_tokens_per_request=2_000,
        )
        report = evaluate_workload(w, LLMPlatform.ANTHROPIC)
        scale = next(r for r in report.results if r.plan_id == "scale")
        assert scale.itpm.load == pytest.approx(0.875)
        assert scale.verdict is Verdict.TIGHT

    def test_warns_when_caching_is_ignored(self, slide_workload):
        report = evaluate_workload(slide_workload)
        assert any("快取" in w for w in report.warnings)

    def test_max_tokens_warning_is_scoped_to_platforms_that_reserve(self):
        """Only Bedrock reserves max_tokens, so the tip is noise elsewhere."""
        w = LLMWorkload(concurrent_users=10)
        assert w.max_tokens is None
        assert any(
            "max_tokens" in x
            for x in evaluate_workload(w, LLMPlatform.BEDROCK).warnings
        )
        assert not any(
            "max_tokens" in x
            for x in evaluate_workload(w, LLMPlatform.VERTEX).warnings
        )

    def test_no_cache_warning_when_caching_is_modelled(self):
        w = LLMWorkload(concurrent_users=10, cache_hit_rate=0.5, max_tokens=2_000)
        report = evaluate_workload(w)
        assert not any("快取命中率設為 0" in x for x in report.warnings)


class TestValidation:
    def test_rejects_zero_users(self):
        with pytest.raises(ValueError):
            LLMWorkload(concurrent_users=0)

    def test_rejects_cache_rate_above_range(self):
        with pytest.raises(ValueError):
            LLMWorkload(cache_hit_rate=1.5)

    def test_rejects_output_beyond_model_ceiling(self):
        with pytest.raises(ValueError):
            LLMWorkload(output_tokens_per_request=FABLE_MAX_OUTPUT_TOKENS + 1)


class TestSerialization:
    """The report is served to browsers, which reject JSON's Infinity token."""

    def test_zero_quota_leaves_load_unset_rather_than_infinite(self, slide_workload):
        report = evaluate_workload(slide_workload, LLMPlatform.FOUNDRY)
        payg = next(r for r in report.results if r.plan_id == "payg")
        for dim in (payg.rpm, payg.itpm, payg.otpm):
            assert dim.limit == 0
            assert dim.load is None
        assert payg.verdict is Verdict.BLOCKED

    def test_report_is_strict_json(self, slide_workload):
        import json
        import math

        raw = evaluate_workload(slide_workload).model_dump_json()
        # parse_constant fires on Infinity / -Infinity / NaN
        parsed = json.loads(raw, parse_constant=lambda c: pytest.fail(f"non-finite: {c}"))

        def walk(node):
            if isinstance(node, dict):
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
            elif isinstance(node, float):
                assert math.isfinite(node)

        walk(parsed)
