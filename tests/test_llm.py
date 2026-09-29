"""Tests for the Claude capacity and cost planner."""

import json
import math

import pytest

from cloudcost.llm import (
    ModelLine,
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
            if p.cache_write_5m_per_mtok is not None:
                assert p.cache_write_5m_per_mtok > p.input_per_mtok

    def test_fable_5_1_cache_reads_are_far_cheaper_than_fable_5(self):
        """0.025x vs the standard 0.1x multiplier — a 4x difference."""
        assert get_model(LLMModel.FABLE_5_1).pricing.cache_read_per_mtok == 0.25
        assert get_model(LLMModel.FABLE_5).pricing.cache_read_per_mtok == 1.0

    def test_cache_read_multipliers_match_published_rates(self):
        for info in list_models(ModelLine.CLAUDE):
            p = info.pricing
            ratio = p.cache_read_per_mtok / p.input_per_mtok
            expected = {LLMModel.FABLE_5_1: 0.025, LLMModel.OPUS_5_5: 0.05}.get(info.model, 0.1)
            assert ratio == pytest.approx(expected)

    def test_plan_table_covers_every_model_and_platform(self):
        plans = list_plans()
        assert {p.platform for p in plans} == set(LLMPlatform)
        assert {p.model for p in plans} == set(LLMModel)

    def test_each_line_is_offered_where_the_vendors_say(self):
        def platforms(line):
            return {p.platform for m in list_models(line) for p in list_plans(m.model)}

        assert platforms(ModelLine.CLAUDE) == {LLMPlatform.ANTHROPIC, LLMPlatform.BEDROCK,
                                               LLMPlatform.FOUNDRY, LLMPlatform.VERTEX}
        # Proprietary GPT is on Bedrock and Azure, not Vertex; Gemini is Google-only.
        assert platforms(ModelLine.GPT) == {LLMPlatform.OPENAI, LLMPlatform.FOUNDRY, LLMPlatform.BEDROCK}
        assert platforms(ModelLine.GEMINI) == {LLMPlatform.GOOGLE_AI, LLMPlatform.VERTEX}

    def test_every_plan_cites_a_source_and_a_date(self):
        for plan in list_plans():
            assert plan.source.startswith("https://")
            assert plan.verified

    def test_filters_compose(self):
        plans = list_plans(model=LLMModel.OPUS_5, platform=LLMPlatform.VERTEX)
        assert len(plans) == 2
        assert all(p.model is LLMModel.OPUS_5 for p in plans)

    def test_bedrock_mantle_defaults_come_from_the_general_reference(self):
        """The slide's original AWS figures (2M / 200K) are Fable 5 on Mantle."""
        def mantle(model):
            return next(p for p in list_plans(model, LLMPlatform.BEDROCK) if p.plan_id == "mantle")

        assert (mantle(LLMModel.FABLE_5).itpm.value, mantle(LLMModel.FABLE_5).otpm.value) == (2_000_000, 200_000)
        assert (mantle(LLMModel.FABLE_5_1).itpm.value, mantle(LLMModel.FABLE_5_1).otpm.value) == (5_000_000, 500_000)
        assert mantle(LLMModel.OPUS_5_5).itpm.status is LimitStatus.UNPUBLISHED
        for model in (LLMModel.FABLE_5, LLMModel.OPUS_5_5):
            assert mantle(model).rpm.status is LimitStatus.NOT_ENFORCED
            assert mantle(model).reserves_max_tokens is True

    def test_bedrock_runtime_is_a_combined_quota_with_burndown(self):
        def runtime(model):
            return next(p for p in list_plans(model, LLMPlatform.BEDROCK) if p.plan_id == "runtime")

        assert runtime(LLMModel.OPUS_4_8).output_burndown == 15
        assert runtime(LLMModel.SONNET_5).output_burndown == 10
        assert runtime(LLMModel.HAIKU_4_5).output_burndown == 5
        assert runtime(LLMModel.GPT_6_SOL).output_burndown == 10
        for model in (LLMModel.SONNET_5, LLMModel.HAIKU_4_5):
            plan = runtime(model)
            assert plan.tpm is not None and plan.itpm is None and plan.otpm is None
            assert plan.tpm_reserves_max_tokens is True

    def test_sonnet_4_6_is_not_offered_on_mantle(self):
        assert {p.plan_id for p in list_plans(LLMModel.SONNET_4_6, LLMPlatform.BEDROCK)} == {"runtime"}

    def test_opus_5_start_tier_has_four_times_the_fable_itpm(self):
        def itpm(model):
            return next(
                p for p in list_plans(model, LLMPlatform.ANTHROPIC) if p.plan_id == "start"
            ).itpm.value

        assert itpm(LLMModel.OPUS_5) == 4 * itpm(LLMModel.FABLE_5_1)

    def test_vertex_multi_region_is_half_of_global(self):
        for info in list_models(ModelLine.CLAUDE):
            plans = {p.plan_id: p for p in list_plans(info.model, LLMPlatform.VERTEX)}
            if "multi_region" in plans:
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

    def test_unpublished_quota_is_unknown_not_a_pass(self):
        w = LLMWorkload(model=LLMModel.OPUS_5_5, apps=[AppWorkload(concurrent_users=100)])
        mantle = _plan(evaluate_workload(w, LLMPlatform.BEDROCK), "mantle")
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

    def test_suggests_the_closest_capability_model_that_fits(self, slide_workload):
        """From Fable, the next tier down is Opus; Opus 5.5 is the cheaper one."""
        start = _plan(evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC), "start")
        alt = next(a for a in start.actions if a.kind is ActionKind.SWITCH_MODEL)
        assert "Opus 5.5" in alt.text
        # A capability downgrade is never presented as a free win.
        assert alt.text.startswith("若 ")

    def test_never_suggests_a_more_capable_model_as_a_quota_fix(self):
        w = LLMWorkload(model=LLMModel.SONNET_5,
                        apps=[AppWorkload(concurrent_users=300, input_tokens_per_request=30_000)])
        for r in evaluate_workload(w).results:
            for a in r.actions:
                if a.kind is ActionKind.SWITCH_MODEL:
                    assert "Fable" not in a.text and "Opus" not in a.text

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

    def test_unknown_plan_asks_for_the_account_quota(self):
        w = LLMWorkload(model=LLMModel.OPUS_5_5, apps=[AppWorkload(concurrent_users=100)])
        mantle = _plan(evaluate_workload(w, LLMPlatform.BEDROCK), "mantle")
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
        from cloudcost.llm.catalog import list_scenarios, suggested_model

        for s in list_scenarios():
            w = size_from_scenario(s.scenario_id, users=100)
            assert w.model is suggested_model(s)
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



# ---------------------------------------------------------------------------
# Opus 5.5
# ---------------------------------------------------------------------------


class TestOpus55:
    def test_priced_below_opus_5(self):
        assert get_model(LLMModel.OPUS_5_5).pricing.input_per_mtok == 4.0
        assert get_model(LLMModel.OPUS_5_5).pricing.output_per_mtok == 20.0
        assert get_model(LLMModel.OPUS_5_5).pricing.cache_read_per_mtok == 0.20

    def test_quota_matches_opus_5_everywhere_but_bedrock_mantle(self):
        a = {(p.platform, p.plan_id): p for p in list_plans(LLMModel.OPUS_5_5)}
        b = {(p.platform, p.plan_id): p for p in list_plans(LLMModel.OPUS_5)}
        assert a.keys() == b.keys()
        # AWS publishes Opus 5's Mantle default but not Opus 5.5's.
        del a[(LLMPlatform.BEDROCK, "mantle")], b[(LLMPlatform.BEDROCK, "mantle")]
        for key in a:
            for dim in ("rpm", "itpm", "otpm"):
                assert getattr(a[key], dim) == getattr(b[key], dim), (key, dim)


# ---------------------------------------------------------------------------
# Thinking tokens
# ---------------------------------------------------------------------------


class TestThinking:
    def test_thinking_counts_toward_otpm(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100, output_tokens_per_request=2_000,
                                          thinking_tokens_per_request=3_000)])
        assert w.otpm == 100 * 5_000
        assert w.thinking_tpm == 100 * 3_000

    def test_thinking_is_billed_at_the_output_rate(self):
        base = LLMWorkload(apps=[AppWorkload(concurrent_users=100)])
        thinking = LLMWorkload(apps=[AppWorkload(concurrent_users=100, thinking_tokens_per_request=1_000)])
        delta = evaluate_workload(thinking).cost.per_request_usd - evaluate_workload(base).cost.per_request_usd
        # 1,000 thinking tokens at Fable 5.1's $50/MTok output rate
        assert delta == pytest.approx(0.05)

    def test_breakdown_separates_thinking(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100, thinking_tokens_per_request=2_000)])
        cost = evaluate_workload(w).cost
        assert cost.breakdown_per_1k["thinking"] == pytest.approx(100.0)
        assert sum(cost.breakdown_per_1k.values()) == pytest.approx(cost.per_1k_requests_usd, rel=1e-3)
        assert cost.thinking_share_pct == pytest.approx(25.0)

    def test_warns_when_max_tokens_would_truncate(self):
        w = LLMWorkload(apps=[AppWorkload(output_tokens_per_request=2_000, thinking_tokens_per_request=3_000)],
                        max_tokens=4_000)
        assert any("截斷" in x for x in evaluate_workload(w).warnings)

    def test_effort_scales_the_thinking_estimate(self):
        low = size_from_scenario("rag", users=10, effort="low")
        high = size_from_scenario("rag", users=10, effort="high")
        assert high.apps[0].thinking_tokens_per_request == 4 * low.apps[0].thinking_tokens_per_request

    def test_scenario_max_tokens_cover_reply_plus_thinking_at_top_effort(self):
        from cloudcost.llm.catalog import EFFORT_THINKING_FACTORS, list_scenarios

        top = max(EFFORT_THINKING_FACTORS.values())
        for s in list_scenarios():
            needed = s.output_tokens_per_request + s.thinking_tokens_per_request * top
            assert s.max_tokens >= needed, s.scenario_id


# ---------------------------------------------------------------------------
# Batch, comparison, sensitivity
# ---------------------------------------------------------------------------


class TestBatch:
    def test_batch_halves_the_bill(self):
        w = LLMWorkload(apps=[AppWorkload(concurrent_users=100)], monthly_requests=1_000_000)
        cost = evaluate_workload(w).cost
        assert cost.batch_per_1k_requests_usd == pytest.approx(cost.per_1k_requests_usd / 2)
        assert cost.batch_monthly_usd == pytest.approx(cost.monthly_usd / 2)

    def test_batch_is_suggested_only_for_work_that_can_wait(self):
        realtime = LLMWorkload(apps=[AppWorkload(concurrent_users=100)])
        deferred = realtime.model_copy(update={"batch_eligible": True})
        start_rt = _plan(evaluate_workload(realtime, LLMPlatform.ANTHROPIC), "start")
        start_bt = _plan(evaluate_workload(deferred, LLMPlatform.ANTHROPIC), "start")
        assert ActionKind.USE_BATCH not in {a.kind for a in start_rt.actions}
        assert ActionKind.USE_BATCH in {a.kind for a in start_bt.actions}

    def test_summarisation_scenario_is_batch_eligible(self):
        assert size_from_scenario("summarize", users=10).batch_eligible is True
        assert size_from_scenario("support", users=10).batch_eligible is False


class TestModelComparison:
    def test_every_model_is_compared_cheapest_first(self, slide_workload):
        rows = evaluate_workload(slide_workload).model_comparison
        assert {r.model for r in rows} == set(LLMModel)
        prices = [r.per_1k_requests_usd for r in rows]
        assert prices == sorted(prices)
        assert sum(r.is_selected for r in rows) == 1

    def test_comparison_uses_each_models_own_quota(self, slide_workload):
        rows = {r.model: r for r in evaluate_workload(slide_workload, LLMPlatform.ANTHROPIC).model_comparison}
        # Fable's Start and Build tiers are too small for this load; Opus 5.5 fits all three.
        assert rows[LLMModel.FABLE_5_1].fitting_plans == 1
        assert rows[LLMModel.OPUS_5_5].fitting_plans == 3


class TestSensitivity:
    def test_a_sharper_peak_never_fits_more_plans(self):
        for sid in ("support", "rag", "coding"):
            r = evaluate_workload(size_from_scenario(sid, users=400))
            stress = r.sensitivity[0]
            assert stress.multiplier == 2.0
            assert stress.fitting_plans <= r.fitting_plans



# ---------------------------------------------------------------------------
# Model lines and versions
# ---------------------------------------------------------------------------


class TestLines:
    def test_four_lines_in_picker_order(self):
        from cloudcost.llm import list_lines

        assert [l.line for l in list_lines()] == [ModelLine.CLAUDE, ModelLine.GPT, ModelLine.GEMINI, ModelLine.GROK]

    def test_every_line_resolves_every_capability_class(self):
        from cloudcost.llm import model_for

        for line in ModelLine:
            for cls in ("frontier", "strong", "balanced", "fast"):
                assert get_model(model_for(line, cls)).line is line

    def test_scenarios_pick_a_version_inside_the_chosen_line(self):
        w = size_from_scenario("support", users=100, line=ModelLine.GPT)
        assert get_model(w.model).line is ModelLine.GPT
        w = size_from_scenario("coding", users=100, line=ModelLine.GEMINI)
        assert w.model is LLMModel.GEMINI_3_1_PRO

    def test_api_ids_follow_each_vendors_convention(self):
        assert get_model(LLMModel.OPUS_5_5).api_id == "claude-opus-5-5"
        assert get_model(LLMModel.GPT_6_SOL).api_id == "gpt-6-sol"
        assert get_model(LLMModel.GEMINI_3_8_FLASH).api_id == "gemini-3.8-flash"

    def test_quota_advice_never_crosses_vendors(self):
        w = LLMWorkload(model=LLMModel.GPT_6_ASTRA, apps=[AppWorkload(concurrent_users=400)])
        for r in evaluate_workload(w).results:
            for a in r.actions:
                if a.kind is ActionKind.SWITCH_MODEL:
                    assert "GPT" in a.text and "Claude" not in a.text and "Gemini" not in a.text

    def test_comparison_covers_every_vendor(self, slide_workload):
        lines = {r.line for r in evaluate_workload(slide_workload).model_comparison}
        assert lines == set(ModelLine)


class TestOpenAI:
    def test_tpm_counts_cached_input_and_reserves_max_tokens(self):
        w = LLMWorkload(model=LLMModel.GPT_6_SOL, max_tokens=4_000,
                        apps=[AppWorkload(concurrent_users=100, cache_hit_rate=0.5,
                                          output_tokens_per_request=1_000)])
        t1 = _plan(evaluate_workload(w, LLMPlatform.OPENAI), "t1")
        # 100 rpm x (20,000 input incl. cached + 4,000 reserved)
        assert t1.tpm.demand == pytest.approx(2_400_000)
        assert t1.itpm is None and t1.otpm is None

    def test_long_prompts_are_billed_at_the_long_context_rate(self):
        short = LLMWorkload(model=LLMModel.GPT_6_SOL, apps=[AppWorkload(input_tokens_per_request=100_000)])
        long = LLMWorkload(model=LLMModel.GPT_6_SOL, apps=[AppWorkload(input_tokens_per_request=300_000)])
        # Input per token doubles above 272K; output rises 1.5x.
        s, l = evaluate_workload(short).cost, evaluate_workload(long).cost
        assert l.breakdown_per_1k["uncached_input"] == pytest.approx(s.breakdown_per_1k["uncached_input"] * 3 * 2)
        assert l.breakdown_per_1k["output"] == pytest.approx(s.breakdown_per_1k["output"] * 1.5)

    def test_azure_rpm_is_one_per_thousand_tpm(self):
        for p in list_plans(LLMModel.GPT_6_ASTRA, LLMPlatform.FOUNDRY):
            assert p.rpm.value == p.tpm.value / 1000

    def test_gpt_5_6_sol_promotional_price_is_flagged(self):
        assert any("促銷" in n for n in get_model(LLMModel.GPT_5_6_SOL).notes)


class TestGemini:
    def test_developer_api_spend_cap_is_evaluated(self):
        w = LLMWorkload(model=LLMModel.GEMINI_3_1_PRO, apps=[AppWorkload(concurrent_users=500)])
        r = evaluate_workload(w, LLMPlatform.GOOGLE_AI)
        t1 = _plan(r, "g_t1")
        per_minute = r.cost.per_peak_minute_usd
        assert t1.usd10m.demand == pytest.approx(per_minute * 10, rel=1e-3)
        assert t1.usd10m.limit == 10
        # RPM / TPM / RPD exist but Google no longer publishes the numbers.
        assert t1.rpm.status is LimitStatus.UNPUBLISHED
        assert t1.verdict in (Verdict.OVER, Verdict.TIGHT, Verdict.AMPLE)

    def test_vertex_paygo_baseline_is_soft(self):
        w = LLMWorkload(model=LLMModel.GEMINI_3_8_FLASH, apps=[AppWorkload(concurrent_users=100)])
        t1 = _plan(evaluate_workload(w, LLMPlatform.VERTEX), "vx_t1")
        assert t1.tpm.soft is True
        assert t1.rpm is None

    def test_pro_and_flash_get_different_baselines(self):
        def vx(model):
            return _plan(evaluate_workload(LLMWorkload(model=model, apps=[AppWorkload()]), LLMPlatform.VERTEX), "vx_t1")

        assert vx(LLMModel.GEMINI_3_1_PRO).tpm.limit == 500_000
        assert vx(LLMModel.GEMINI_3_8_FLASH).tpm.limit == 2_000_000

    def test_flash_2027_price_change_is_flagged(self):
        assert any("2027" in n for n in get_model(LLMModel.GEMINI_3_8_FLASH).notes)

    def test_daily_quota_needs_a_monthly_volume(self):
        w = LLMWorkload(model=LLMModel.GEMINI_3_8_FLASH, apps=[AppWorkload()])
        rpd = _plan(evaluate_workload(w, LLMPlatform.GOOGLE_AI), "g_t1").rpd
        assert rpd.demand_known is False


class TestGrok:
    def _report(self, model=LLMModel.GROK_4_7, platform=None, **kw):
        apps = kw.pop("apps", [AppWorkload(concurrent_users=100)])
        return evaluate_workload(LLMWorkload(model=model, apps=apps, **kw), platform)

    def test_requests_per_second_are_shown_per_minute(self):
        t0 = _plan(self._report(platform=LLMPlatform.XAI), "x_t0")
        assert t0.rpm.limit == 150 * 60
        assert t0.tpm.limit == 50_000_000
        # The smaller models have their own, lower profile.
        assert _plan(self._report(LLMModel.GROK_4_3, LLMPlatform.XAI), "x_t0").rpm.limit == 37 * 60

    def test_cached_input_still_counts_toward_xai_tpm(self):
        w = LLMWorkload(model=LLMModel.GROK_4_7,
                        apps=[AppWorkload(concurrent_users=100, cache_hit_rate=0.8)], max_tokens=4_000)
        t0 = _plan(evaluate_workload(w, LLMPlatform.XAI), "x_t0")
        # Actual output (not max_tokens) plus every input token, cached or not.
        assert t0.tpm.demand == pytest.approx(w.rpm * w.apps[0].input_tokens_per_request + w.otpm)

    def test_long_context_starts_at_the_threshold_itself(self):
        price = get_model(LLMModel.GROK_4_7).pricing
        assert price.rates_for(199_999) == (2, 6, 0.5)
        assert price.rates_for(200_000) == (4, 12, 1.0)
        # Gemini's threshold is exclusive: exactly 200K is still the base rate.
        assert get_model(LLMModel.GEMINI_3_1_PRO).pricing.rates_for(200_000)[0] == 2

    def test_models_without_a_batch_api_never_suggest_it(self):
        r = self._report(platform=LLMPlatform.XAI, batch_eligible=True, monthly_requests=100_000)
        assert r.cost.batch_discount_pct is None
        assert r.cost.batch_monthly_usd is None
        assert any("不支援 Batch API" in c for c in r.cost.caveats)
        assert all(a.kind is not ActionKind.USE_BATCH for p in r.results for a in p.actions)

    def test_grok_batch_is_twenty_percent_off(self):
        r = self._report(LLMModel.GROK_4_3, LLMPlatform.VERTEX, apps=[AppWorkload(concurrent_users=2_000)],
                         batch_eligible=True, monthly_requests=100_000)
        assert r.cost.batch_discount_pct == 20
        assert r.cost.batch_monthly_usd == pytest.approx(r.cost.monthly_usd * 0.8, rel=1e-3)
        vx = _plan(r, "vx_global")
        assert vx.verdict is Verdict.OVER
        batch = next(a for a in vx.actions if a.kind is ActionKind.USE_BATCH)
        assert "八折" in batch.text

    def test_vertex_default_is_small_and_shared(self):
        vx = _plan(self._report(LLMModel.GROK_4_6, LLMPlatform.VERTEX), "vx_global")
        assert (vx.rpm.limit, vx.itpm.limit, vx.otpm.limit) == (13, 188_000, 16_000)
        assert vx.verdict is Verdict.OVER

    def test_oci_points_to_its_own_console(self):
        oci = _plan(self._report(platform=LLMPlatform.OCI), "oci_ondemand")
        assert oci.verdict is Verdict.UNKNOWN
        assert "OCI 主控台" in oci.actions[0].text

    def test_bedrock_runtime_advice_does_not_mention_mantle(self):
        r = self._report(LLMModel.SONNET_5_5, LLMPlatform.BEDROCK)
        runtime = _plan(r, "runtime")
        assert runtime.verdict is Verdict.UNKNOWN
        assert "Mantle" not in runtime.actions[0].text

    def test_grok_on_bedrock_burns_output_one_to_one(self):
        from cloudcost.llm.catalog import list_plans

        runtime = next(p for p in list_plans(LLMModel.GROK_4_6, LLMPlatform.BEDROCK) if p.plan_id == "runtime")
        assert runtime.output_burndown == 1.0
        assert runtime.tpm.value == 10_000_000

    def test_azure_low_tier_is_blocked_until_requested(self):
        low = _plan(self._report(LLMModel.GROK_4_6, LLMPlatform.FOUNDRY), "az_low")
        assert low.verdict is Verdict.BLOCKED

    def test_platform_coverage_matches_the_vendors_docs(self):
        from cloudcost.llm.catalog import list_plans

        def platforms(model):
            return {p.platform for p in list_plans(model)}

        assert platforms(LLMModel.GROK_4_6) == {LLMPlatform.XAI, LLMPlatform.BEDROCK, LLMPlatform.FOUNDRY,
                                                LLMPlatform.VERTEX, LLMPlatform.OCI}
        assert platforms(LLMModel.GROK_4_7) == {LLMPlatform.XAI, LLMPlatform.OCI}
        assert platforms(LLMModel.GROK_BUILD_0_1) == {LLMPlatform.XAI}


def test_memory_and_file_features_are_flagged_as_excluded():
    """Tool-driven context (memory, file search, uploads) is outside the estimate; say so on every quote."""
    for model in (LLMModel.OPUS_5_5, LLMModel.GPT_6_SOL, LLMModel.GEMINI_3_8_FLASH, LLMModel.GROK_4_7):
        cost = evaluate_workload(LLMWorkload(model=model, apps=[AppWorkload()])).cost
        assert any("記憶或檔案功能" in c and "不包含" in c for c in cost.caveats), model


class TestCacheWrites:
    def _cost(self, model, write=0.2, hit=0.6):
        w = LLMWorkload(model=model, apps=[AppWorkload(concurrent_users=100, input_tokens_per_request=10_000,
                                                       cache_hit_rate=hit, cache_write_rate=write)],
                        monthly_requests=100_000)
        return evaluate_workload(w).cost

    def test_written_tokens_are_billed_at_the_write_price(self):
        with_writes, without = self._cost(LLMModel.OPUS_5_5), self._cost(LLMModel.OPUS_5_5, write=0)
        # 20% of 10K tokens move from $4 input to the $5 write rate: +$2 per 1K requests.
        assert with_writes.per_1k_requests_usd - without.per_1k_requests_usd == pytest.approx(2.0, abs=1e-6)
        assert with_writes.breakdown_per_1k["cache_write"] == pytest.approx(10.0)
        assert any("快取寫入依實際用量計入" in c for c in with_writes.caveats)

    def test_vendors_without_a_write_premium_bill_plain_input(self):
        with_writes, without = self._cost(LLMModel.GEMINI_3_8_FLASH), self._cost(LLMModel.GEMINI_3_8_FLASH, write=0)
        assert with_writes.per_1k_requests_usd == pytest.approx(without.per_1k_requests_usd)
        assert any("不另收費" in c for c in with_writes.caveats)

    def test_writes_still_count_toward_input_quota(self):
        """Anthropic ITPM counts uncached input and cache creation; only reads are free."""
        w = LLMWorkload(model=LLMModel.OPUS_5_5, apps=[AppWorkload(input_tokens_per_request=10_000,
                                                                   cache_hit_rate=0.6, cache_write_rate=0.2)])
        start = _plan(evaluate_workload(w, LLMPlatform.ANTHROPIC), "start")
        assert start.itpm.demand == pytest.approx(w.rpm * 4_000)

    def test_shares_cannot_exceed_the_prompt(self):
        with pytest.raises(Exception):
            AppWorkload(cache_hit_rate=0.8, cache_write_rate=0.3)
