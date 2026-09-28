"""Tests for the Claude capacity and cost planner."""

import json
import math

import pytest

from cloudcost.llm import (
    MAX_OUTPUT_TOKENS,
    ActionKind,
    AppWorkload,
    LimitStatus,
    LLMModel,
    LLMPlatform,
    LLMWorkload,
    QuotaOverride,
    Verdict,
    evaluate_workload,
    get_model,
    list_models,
    list_plans,
)
from cloudcost.llm.planner import size_from_scenario


@pytest.fixture
def slide_workload():
    """100 users, one request each per peak minute, 20K in / 2K out, no cache."""
    return LLMWorkload(apps=[AppWorkload(concurrent_users=100)])


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------


class TestCatalogue:
    def test_every_model_is_priced(self):
        for info in list_models():
            p = info.pricing
            assert p.input_per_mtok > 0
            assert p.output_per_mtok > p.input_per_mtok
            assert p.cache_read_per_mtok < p.input_per_mtok
            assert p.cache_write_5m_per_mtok > p.input_per_mtok

    def test_fable_5_1_cache_reads_are_far_cheaper_than_fable_5(self):
        """0.025x vs the standard 0.1x multiplier — a 4x difference."""
        assert get_model(LLMModel.FABLE_5_1).pricing.cache_read_per_mtok == 0.25
        assert get_model(LLMModel.FABLE_5).pricing.cache_read_per_mtok == 1.0

    def test_cache_read_multipliers_match_published_rates(self):
        for info in list_models():
            p = info.pricing
            ratio = p.cache_read_per_mtok / p.input_per_mtok
            expected = 0.025 if info.model is LLMModel.FABLE_5_1 else 0.1
            assert ratio == pytest.approx(expected)

    def test_plan_table_covers_every_model_and_platform(self):
        plans = list_plans()
        assert len(plans) == len(list(LLMModel)) * 8
        assert {p.platform for p in plans} == set(LLMPlatform)
        assert {p.model for p in plans} == set(LLMModel)

    def test_every_plan_cites_a_source_and_a_date(self):
        for plan in list_plans():
            assert plan.source.startswith("https://")
            assert plan.verified

    def test_filters_compose(self):
        plans = list_plans(model=LLMModel.OPUS_5, platform=LLMPlatform.VERTEX)
        assert len(plans) == 2
        assert all(p.model is LLMModel.OPUS_5 for p in plans)

    def test_bedrock_publishes_no_quota_for_any_model(self):
        for plan in list_plans(platform=LLMPlatform.BEDROCK):
            assert plan.rpm.status is LimitStatus.NOT_ENFORCED
            assert plan.itpm.status is LimitStatus.UNPUBLISHED
            assert plan.reserves_max_tokens is True

    def test_opus_5_start_tier_has_four_times_the_fable_itpm(self):
        def itpm(model):
            return next(
                p for p in list_plans(model, LLMPlatform.ANTHROPIC) if p.plan_id == "start"
            ).itpm.value

        assert itpm(LLMModel.OPUS_5) == 4 * itpm(LLMModel.FABLE_5_1)

    def test_vertex_multi_region_is_half_of_global(self):
        for model in LLMModel:
            plans = {p.plan_id: p for p in list_plans(model, LLMPlatform.VERTEX)}
            assert plans["multi_region"].itpm.value * 2 == plans["global"].itpm.value

    def test_foundry_payg_blocks_fable_but_not_opus(self):
        payg = {
            p.model: p
            for p in list_plans(platform=LLMPlatform.FOUNDRY)
            if p.plan_id == "payg"
        }
        assert payg[LLMModel.FABLE_5_1].itpm.value == 0
        assert payg[LLMModel.OPUS_5].itpm.value > 0


# ---------------------------------------------------------------------------
# Demand
# ---------------------------------------------------------------------------


class TestDemand:
    def test_peak_demand(self, slide_workload):
        assert slide_workload.rpm == 100
        assert slide_workload.itpm == 2_000_000
        assert slide_workload.otpm == 200_000

    def test_cache_hits_cut_itpm_but_not_rpm_or_otpm(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100, cache_hit_rate=0.8)])
        assert w.itpm == pytest.approx(400_000)
        assert w.cached_itpm == pytest.approx(1_600_000)
        assert w.rpm == 100
        assert w.otpm == 200_000

    def test_several_apps_share_one_quota_bucket(self):
        w = LLMWorkload(
            apps=[
                AppWorkload(name="A", concurrent_users=100),
                AppWorkload(name="B", concurrent_users=50),
            ]
        )
        assert w.total_users == 150
        assert w.rpm == 150
        assert w.itpm == 3_000_000

    def test_max_tokens_defaults_to_the_model_ceiling(self, slide_workload):
        assert slide_workload.effective_max_tokens == MAX_OUTPUT_TOKENS

    def test_mantle_reserves_max_tokens_per_request(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100)], max_tokens=4_000)
        assert w.itpm == 2_000_000
        assert w.itpm_with_reservation == 2_400_000


# ---------------------------------------------------------------------------
# Cost
# ---------------------------------------------------------------------------


class TestCost:
    def test_uncached_cost_matches_list_price(self, slide_workload):
        # 20K in @ $10/MTok + 2K out @ $50/MTok = $0.20 + $0.10 per request
        cost = evaluate_workload(slide_workload).cost
        assert cost.per_request_usd == pytest.approx(0.30)
        assert cost.per_1k_requests_usd == pytest.approx(300.0)

    def test_caching_shows_up_as_a_saving(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100, cache_hit_rate=0.8)])
        cost = evaluate_workload(w).cost
        # 4K uncached @ $10 + 16K cached @ $0.25 + 2K out @ $50 = $0.144
        assert cost.per_1k_requests_usd == pytest.approx(144.0)
        assert cost.per_1k_requests_without_cache_usd == pytest.approx(300.0)
        assert cost.cache_saving_pct == pytest.approx(52.0, abs=0.1)

    def test_no_saving_reported_when_caching_is_off(self, slide_workload):
        cost = evaluate_workload(slide_workload).cost
        assert cost.cache_saving_pct == 0
        assert cost.per_1k_requests_usd == cost.per_1k_requests_without_cache_usd

    def test_breakdown_sums_to_the_total(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100, cache_hit_rate=0.5)])
        cost = evaluate_workload(w).cost
        assert sum(cost.breakdown_per_1k.values()) == pytest.approx(
            cost.per_1k_requests_usd, rel=1e-3
        )

    def test_monthly_cost_only_when_volume_is_given(self, slide_workload):
        assert evaluate_workload(slide_workload).cost.monthly_usd is None
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100)], monthly_requests=1_000_000)
        assert evaluate_workload(w).cost.monthly_usd == pytest.approx(300_000)

    def test_sonnet_is_five_times_cheaper_than_fable(self):
        def per_1k(model):
            w = LLMWorkload(model=model, apps=[AppWorkload(concurrent_users=100)])
            return evaluate_workload(w).cost.per_1k_requests_usd

        assert per_1k(LLMModel.FABLE_5_1) == pytest.approx(5 * per_1k(LLMModel.SONNET_5))

    def test_cost_states_which_platforms_it_does_not_cover(self, slide_workload):
        caveats = " ".join(evaluate_workload(slide_workload).cost.caveats)
        assert "Bedrock" in caveats and "Vertex" in caveats


# ---------------------------------------------------------------------------
# Verdicts and headroom
# ---------------------------------------------------------------------------


class TestVerdicts:
    def test_start_tier_is_over_for_a_rag_workload(self, slide_workload):
        start = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "start")
        assert start.verdict is Verdict.OVER
        assert start.itpm.load == pytest.approx(4.0)

    def test_foundry_payg_is_blocked_not_merely_over(self, slide_workload):
        payg = _plan(evaluate_workload(slide_workload, LLMPlatform.FOUNDRY), "payg")
        assert payg.verdict is Verdict.BLOCKED
        assert payg.max_users == 0

    def test_unpublished_quota_is_unknown_not_a_pass(self, slide_workload):
        mantle = _plan(evaluate_workload(slide_workload, LLMPlatform.BEDROCK), "mantle")
        assert mantle.verdict is Verdict.UNKNOWN
        assert mantle.peak_load is None
        assert mantle.max_users is None

    def test_tight_sits_between_70_and_100_percent(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100, input_tokens_per_request=35_000)])
        scale = _plan(evaluate_workload(w, LLMPlatform.ANTHROPIC), "scale")
        assert scale.itpm.load == pytest.approx(0.875)
        assert scale.verdict is Verdict.TIGHT

    def test_headroom_is_reported_in_users(self, slide_workload):
        r = evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC)
        # Scale allows 4M ITPM against 2M demand, so twice the scenario fits.
        assert _plan(r, "scale").max_users == 200
        assert _plan(r, "start").max_users == 25

    def test_headroom_scales_the_whole_mix_for_several_apps(self):
        w = LLMWorkload(
            apps=[
                AppWorkload(name="A", concurrent_users=60, input_tokens_per_request=20_000),
                AppWorkload(name="B", concurrent_users=40, input_tokens_per_request=5_000),
            ]
        )
        scale = _plan(evaluate_workload(w, LLMPlatform.ANTHROPIC), "scale")
        assert scale.max_users is not None
        assert scale.max_users > w.total_users

    def test_output_can_be_the_bottleneck_rather_than_input(self):
        """Long generations exhaust OTPM while ITPM still has room."""
        w = LLMWorkload(
            apps=[
                AppWorkload(
                    concurrent_users=20,
                    requests_per_user_per_minute=3,
                    input_tokens_per_request=60_000,
                    output_tokens_per_request=8_000,
                    cache_hit_rate=0.8,
                )
            ]
        )
        build = _plan(evaluate_workload(w, LLMPlatform.ANTHROPIC), "build")
        assert build.binding_dimension == "otpm"


# ---------------------------------------------------------------------------
# Account quota overrides
# ---------------------------------------------------------------------------


class TestAccountQuota:
    def test_override_turns_unknown_into_a_verdict(self):
        w = LLMWorkload(
            apps=[AppWorkload(concurrent_users=100)],
            max_tokens=4_000,
            account_quotas=[QuotaOverride(plan_id="mantle", itpm=20_000_000, otpm=4_000_000)],
        )
        mantle = _plan(evaluate_workload(w, LLMPlatform.BEDROCK), "mantle")
        assert mantle.verdict is Verdict.AMPLE
        assert mantle.itpm.limit == 20_000_000
        assert mantle.itpm.from_account is True
        # RPM is still genuinely not enforced on this endpoint.
        assert mantle.rpm.status is LimitStatus.NOT_ENFORCED

    def test_override_applies_to_only_the_named_plan(self):
        w = LLMWorkload(
            apps=[AppWorkload(concurrent_users=100)],
            account_quotas=[
                QuotaOverride(plan_id="start", itpm=9_000_000, otpm=9_000_000)
            ],
        )
        r = evaluate_workload(w, LLMPlatform.ANTHROPIC)
        assert _plan(r, "start").verdict is Verdict.AMPLE
        assert _plan(r, "start").itpm.from_account is True
        # Build keeps its published defaults and stays over quota.
        assert _plan(r, "build").itpm.from_account is False
        assert _plan(r, "build").verdict is Verdict.OVER

    def test_overriding_one_dimension_does_not_rescue_the_others(self):
        """Raising ITPM alone leaves OTPM at its published ceiling."""
        w = LLMWorkload(
            apps=[AppWorkload(concurrent_users=100)],
            account_quotas=[QuotaOverride(plan_id="start", itpm=9_000_000)],
        )
        start = _plan(evaluate_workload(w, LLMPlatform.ANTHROPIC), "start")
        assert start.itpm.load < 1
        assert start.otpm.load == pytest.approx(2.0)
        assert start.verdict is Verdict.OVER
        assert start.binding_dimension == "otpm"

    def test_partial_override_keeps_the_published_default(self):
        w = LLMWorkload(
            apps=[AppWorkload(concurrent_users=100)],
            account_quotas=[QuotaOverride(plan_id="start", itpm=9_000_000)],
        )
        start = _plan(evaluate_workload(w, LLMPlatform.ANTHROPIC), "start")
        assert start.itpm.limit == 9_000_000
        assert start.rpm.limit == 1_000  # untouched published default


# ---------------------------------------------------------------------------
# Next actions
# ---------------------------------------------------------------------------


def _kinds(result):
    return {a.kind for a in result.actions}


class TestActions:
    def test_over_quota_names_the_numbers_to_request(self, slide_workload):
        start = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "start")
        req = next(a for a in start.actions if a.kind is ActionKind.REQUEST_QUOTA)
        assert "2,000,000" in req.text and "500,000" in req.text

    def test_suggests_a_plan_on_the_same_platform_that_fits(self, slide_workload):
        start = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "start")
        switch = next(a for a in start.actions if a.kind is ActionKind.SWITCH_PLAN)
        assert "Scale" in switch.text

    def test_suggests_a_model_with_a_looser_quota(self, slide_workload):
        start = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "start")
        alt = next(a for a in start.actions if a.kind is ActionKind.SWITCH_MODEL)
        assert "Opus 5" in alt.text

    def test_break_even_cache_rate_is_offered_when_itpm_alone_is_over(self, slide_workload):
        build = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "build")
        # 1.5M ceiling against 2M raw input: 25% cached is enough.
        cache = next(a for a in build.actions if a.kind is ActionKind.RAISE_CACHE)
        assert "25%" in cache.text

    def test_no_cache_advice_when_output_is_also_over(self, slide_workload):
        """Caching does nothing for OTPM, so suggesting it would mislead."""
        start = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "start")
        assert start.otpm.load > 1
        assert ActionKind.RAISE_CACHE not in _kinds(start)

    def test_unknown_plan_asks_for_the_account_quota(self, slide_workload):
        mantle = _plan(evaluate_workload(slide_workload, LLMPlatform.BEDROCK), "mantle")
        assert ActionKind.ENTER_ACCOUNT_QUOTA in _kinds(mantle)
        assert ActionKind.SET_MAX_TOKENS in _kinds(mantle)

    def test_a_comfortable_plan_needs_no_actions(self, slide_workload):
        scale = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "scale")
        assert scale.verdict is Verdict.AMPLE
        assert scale.actions == []


# ---------------------------------------------------------------------------
# Report shape
# ---------------------------------------------------------------------------


class TestReport:
    def test_warns_about_unused_caching(self, slide_workload):
        assert any("快取" in w for w in evaluate_workload(slide_workload).warnings)

    def test_max_tokens_warning_is_scoped_to_platforms_that_reserve(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=10)])
        assert any("max_tokens" in x for x in evaluate_workload(w, LLMPlatform.BEDROCK).warnings)
        assert not any("max_tokens" in x for x in evaluate_workload(w, LLMPlatform.VERTEX).warnings)

    def test_assumptions_name_the_burst_limitation(self, slide_workload):
        text = " ".join(evaluate_workload(slide_workload).assumptions)
        assert "token bucket" in text
        assert "共用" in text

    def test_report_is_strict_json(self, slide_workload):
        raw = evaluate_workload(slide_workload).model_dump_json()
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


class TestValidation:
    def test_rejects_zero_users(self):
        with pytest.raises(ValueError):
            AppWorkload(concurrent_users=0)

    def test_rejects_cache_rate_out_of_range(self):
        with pytest.raises(ValueError):
            AppWorkload(cache_hit_rate=1.5)

    def test_rejects_output_beyond_the_model_ceiling(self):
        with pytest.raises(ValueError):
            AppWorkload(output_tokens_per_request=MAX_OUTPUT_TOKENS + 1)

    def test_requires_at_least_one_app(self):
        with pytest.raises(ValueError):
            LLMWorkload(apps=[])


def _plan(report, plan_id):
    return next(r for r in report.results if r.plan_id == plan_id)


# ---------------------------------------------------------------------------
# Scenario-based sizing
# ---------------------------------------------------------------------------


class TestScenarioSizing:
    def test_every_scenario_is_usable_as_a_starting_point(self):
        from cloudcost.llm.catalog import list_scenarios

        for s in list_scenarios():
            w = size_from_scenario(s.scenario_id, users=100)
            assert w.model is s.suggested_model
            assert w.apps[0].input_tokens_per_request == s.input_tokens_per_request
            assert w.max_tokens == s.max_tokens
            report = evaluate_workload(w)
            assert report.required_rpm > 0
            assert report.cost.monthly_usd is not None

    def test_daily_usage_becomes_peak_minute_demand(self):
        """500 people at 10 messages a day, spread over 8h, tripled at peak."""
        w = size_from_scenario("support", users=500, messages_per_user_per_day=10,
                               peak_profile="normal")
        # 10 / (8*60) * 3 = 0.0625 requests per user per peak minute
        assert w.apps[0].requests_per_user_per_minute == pytest.approx(0.0625)
        assert w.rpm == pytest.approx(31.25)

    def test_peak_profile_is_the_load_bearing_assumption(self):
        base = dict(scenario_id="support", users=500, messages_per_user_per_day=10)
        flat = size_from_scenario(**base, peak_profile="flat")
        spiky = size_from_scenario(**base, peak_profile="spiky")
        # Same daily volume, four times the peak-minute demand.
        assert spiky.rpm == pytest.approx(4 * flat.rpm)
        assert spiky.monthly_requests == flat.monthly_requests

    def test_monthly_volume_follows_the_daily_rate(self):
        w = size_from_scenario("rag", users=100, messages_per_user_per_day=8)
        assert w.monthly_requests == 100 * 8 * 22

    def test_unknown_peak_profile_falls_back_to_normal(self):
        a = size_from_scenario("rag", users=10, peak_profile="nonsense")
        b = size_from_scenario("rag", users=10, peak_profile="normal")
        assert a.rpm == pytest.approx(b.rpm)

    def test_model_can_be_overridden(self):
        w = size_from_scenario("support", users=10, model=LLMModel.FABLE_5_1)
        assert w.model is LLMModel.FABLE_5_1

    def test_a_modest_support_deployment_fits_on_defaults(self):
        """The headline case a salesperson brings: it should just work."""
        w = size_from_scenario("support", users=500, messages_per_user_per_day=10)
        report = evaluate_workload(w)
        fitting = [r for r in report.results if r.verdict in (Verdict.AMPLE, Verdict.TIGHT)]
        assert len(fitting) >= 5
        assert report.cost.monthly_usd < 5_000
