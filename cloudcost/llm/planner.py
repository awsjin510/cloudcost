"""Capacity and cost planner for Claude deployments.

Answers, in the order a customer actually asks them:

  1. "100 個使用者，配額夠不夠？"   -> verdict per plan
  2. "不夠的話怎麼辦？"             -> concrete, costed next actions
  3. "那一個月多少錢？"             -> cost at the modelled load
  4. "這個方案還能再撐多少人？"     -> headroom expressed in users

Three rules make a naive spreadsheet wrong, and all three are modelled:

* Cache reads never count toward ITPM on any platform, and they are billed
  at a small fraction of the input rate (0.025x on Fable 5.1). Caching is
  therefore both a capacity lever and the largest cost lever.
* ``bedrock-mantle`` reserves ``input + max_tokens`` of ITPM when it
  *admits* a request and refunds the remainder afterwards, so a request is
  throttled on what it might generate. Omitting ``max_tokens`` reserves the
  full 128K model ceiling.
* Quota is shared per organisation / subscription, not per application.
  Several apps on one account draw from one bucket, so they are summed.

Everything here is peak-minute arithmetic. Bursts *inside* the peak minute
are not modelled: platforms use a continuously replenishing token bucket,
so a minute's worth of traffic delivered in five seconds can still throttle.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from cloudcost.llm.catalog import (
    ACTIVE_HOURS_PER_DAY,
    BATCH_DISCOUNT,
    EFFORT_THINKING_FACTORS,
    MAX_OUTPUT_TOKENS,
    PEAK_FACTORS,
    WORKING_DAYS_PER_MONTH,
    Limit,
    LimitStatus,
    LLMModel,
    LLMPlatform,
    QuotaPlan,
    get_model,
    get_scenario,
    list_models,
    list_plans,
)

#: Load ratio at or below which a plan is considered comfortable.
AMPLE_THRESHOLD = 0.70

#: Highest cache hit rate worth suggesting as a remedy.
MAX_SUGGESTED_CACHE_RATE = 0.95


class Verdict(str, Enum):
    AMPLE = "ample"
    TIGHT = "tight"
    OVER = "over"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class ActionKind(str, Enum):
    REQUEST_QUOTA = "request_quota"
    SWITCH_PLAN = "switch_plan"
    SWITCH_MODEL = "switch_model"
    RAISE_CACHE = "raise_cache"
    SET_MAX_TOKENS = "set_max_tokens"
    ENTER_ACCOUNT_QUOTA = "enter_account_quota"
    USE_BATCH = "use_batch"


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------


class AppWorkload(BaseModel):
    """One application's peak-minute demand profile."""

    name: str = Field(default="主要應用", max_length=60)
    concurrent_users: int = Field(default=100, ge=1, le=1_000_000)
    requests_per_user_per_minute: float = Field(default=1.0, gt=0, le=600)
    input_tokens_per_request: int = Field(
        default=20_000, ge=1, le=1_000_000,
        description="System prompt + history + RAG context",
    )
    output_tokens_per_request: int = Field(
        default=2_000, ge=1, le=MAX_OUTPUT_TOKENS, description="Visible reply tokens"
    )
    thinking_tokens_per_request: int = Field(
        default=0, ge=0, le=MAX_OUTPUT_TOKENS,
        description="Thinking tokens; billed as output and counted toward OTPM",
    )
    cache_hit_rate: float = Field(
        default=0.0, ge=0.0, le=0.95,
        description="Share of the prompt served from cache; cache reads are ITPM-free",
    )

    @property
    def rpm(self) -> float:
        return self.concurrent_users * self.requests_per_user_per_minute

    @property
    def uncached_input_per_request(self) -> float:
        return self.input_tokens_per_request * (1.0 - self.cache_hit_rate)

    @property
    def cached_input_per_request(self) -> float:
        return self.input_tokens_per_request * self.cache_hit_rate

    @property
    def billed_output_per_request(self) -> int:
        """Everything generated: the reply plus the thinking behind it."""
        return self.output_tokens_per_request + self.thinking_tokens_per_request


class QuotaOverride(BaseModel):
    """An account's real quota, read from that platform's own console.

    Published defaults are a starting point; a mature account rarely still
    has them. Any dimension left unset falls back to the published default.
    """

    plan_id: str
    rpm: Optional[float] = Field(default=None, ge=0)
    itpm: Optional[float] = Field(default=None, ge=0)
    otpm: Optional[float] = Field(default=None, ge=0)


class LLMWorkload(BaseModel):
    """A full sizing scenario: one model, one or more applications."""

    model: LLMModel = LLMModel.FABLE_5_1
    apps: list[AppWorkload] = Field(default_factory=lambda: [AppWorkload()], min_length=1, max_length=20)
    max_tokens: Optional[int] = Field(
        default=None, ge=1, le=MAX_OUTPUT_TOKENS,
        description="Requested max_tokens; drives Bedrock Mantle's ITPM reservation",
    )
    monthly_requests: Optional[int] = Field(
        default=None, ge=0, le=10_000_000_000,
        description="Monthly request volume, used only for the monthly cost estimate",
    )
    account_quotas: list[QuotaOverride] = Field(default_factory=list, max_length=40)
    batch_eligible: bool = Field(
        default=False, description="Work can wait for an asynchronous (Batch API) result"
    )

    # -- aggregate demand --------------------------------------------------

    @property
    def total_users(self) -> int:
        return sum(a.concurrent_users for a in self.apps)

    @property
    def rpm(self) -> float:
        return sum(a.rpm for a in self.apps)

    @property
    def itpm(self) -> float:
        """Uncached input tokens per minute — what counts toward ITPM."""
        return sum(a.rpm * a.uncached_input_per_request for a in self.apps)

    @property
    def cached_itpm(self) -> float:
        """Cache-read tokens per minute — billed, but ITPM-free."""
        return sum(a.rpm * a.cached_input_per_request for a in self.apps)

    @property
    def otpm(self) -> float:
        """Generated tokens per minute, thinking included: OTPM counts all of it."""
        return sum(a.rpm * a.billed_output_per_request for a in self.apps)

    @property
    def thinking_tpm(self) -> float:
        return sum(a.rpm * a.thinking_tokens_per_request for a in self.apps)

    @property
    def effective_max_tokens(self) -> int:
        return self.max_tokens if self.max_tokens is not None else MAX_OUTPUT_TOKENS

    @property
    def itpm_with_reservation(self) -> float:
        """ITPM as bedrock-mantle counts it: uncached input plus reserved output."""
        return self.itpm + self.rpm * self.effective_max_tokens

    def override_for(self, plan_id: str) -> Optional[QuotaOverride]:
        for o in self.account_quotas:
            if o.plan_id == plan_id:
                return o
        return None


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


class DimensionResult(BaseModel):
    demand: float
    limit: Optional[float] = None
    status: LimitStatus
    #: demand / limit; unset when there is nothing meaningful to divide by.
    load: Optional[float] = None
    #: True when `limit` came from the user's own account rather than the doc.
    from_account: bool = False
    note: str = ""


class CostEstimate(BaseModel):
    """First-party Claude API list price at the modelled load."""

    per_request_usd: float
    per_1k_requests_usd: float
    per_peak_minute_usd: float
    monthly_usd: Optional[float] = None
    #: What the same traffic would cost with no prompt caching at all.
    per_1k_requests_without_cache_usd: float
    cache_saving_pct: float
    breakdown_per_1k: dict[str, float]
    #: Share of the bill that is thinking tokens.
    thinking_share_pct: float = 0.0
    #: Same traffic through the Batch API (first-party, 50% off).
    batch_per_1k_requests_usd: float = 0.0
    batch_monthly_usd: Optional[float] = None
    caveats: list[str] = Field(default_factory=list)


class Action(BaseModel):
    kind: ActionKind
    text: str


class QuotaPlanResult(BaseModel):
    model: LLMModel
    model_label: str
    platform: LLMPlatform
    plan_id: str
    platform_label: str
    plan_label: str
    rpm: DimensionResult
    itpm: DimensionResult
    otpm: DimensionResult
    verdict: Verdict
    peak_load: Optional[float] = None
    binding_dimension: Optional[str] = None
    #: How many times the whole scenario fits; None when nothing is published.
    headroom_multiple: Optional[float] = None
    #: Scenario scaled up proportionally, expressed in users.
    max_users: Optional[int] = None
    actions: list[Action] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    source: str
    verified: str


class ModelComparison(BaseModel):
    """The same scenario priced and sized on one model."""

    model: LLMModel
    label: str
    per_1k_requests_usd: float
    monthly_usd: Optional[float] = None
    fitting_plans: int
    total_plans: int
    best_max_users: Optional[int] = None
    is_selected: bool = False


class Sensitivity(BaseModel):
    """How the answer holds up if the peak is sharper than assumed."""

    label: str
    multiplier: float
    fitting_plans: int
    total_plans: int


class QuotaReport(BaseModel):
    workload: LLMWorkload
    model_label: str
    total_users: int
    required_rpm: float
    required_itpm: float
    required_otpm: float
    cached_itpm: float
    cost: CostEstimate
    results: list[QuotaPlanResult]
    fitting_plans: int = 0
    model_comparison: list[ModelComparison] = Field(default_factory=list)
    sensitivity: list[Sensitivity] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def _resolve(limit: Limit, override: Optional[float]) -> tuple[Limit, bool]:
    """Apply an account-specific value on top of a published default."""
    if override is None:
        return limit, False
    return Limit(status=LimitStatus.ENFORCED, value=override, note=limit.note), True


def _evaluate_dimension(
    demand: float, limit: Limit, override: Optional[float]
) -> DimensionResult:
    resolved, from_account = _resolve(limit, override)
    if resolved.status is not LimitStatus.ENFORCED or resolved.value is None:
        return DimensionResult(
            demand=round(demand, 2), status=resolved.status, note=resolved.note
        )
    # A zero quota has no meaningful ratio: infinity is not valid JSON, so the
    # BLOCKED verdict carries the meaning and the ratio stays unset.
    load = None if resolved.value == 0 else demand / resolved.value
    return DimensionResult(
        demand=round(demand, 2),
        limit=resolved.value,
        status=resolved.status,
        load=load,
        from_account=from_account,
        note=resolved.note,
    )


def _plan_dims(
    workload: LLMWorkload, plan: QuotaPlan
) -> dict[str, DimensionResult]:
    override = workload.override_for(plan.plan_id)
    itpm_demand = (
        workload.itpm_with_reservation if plan.reserves_max_tokens else workload.itpm
    )
    return {
        "rpm": _evaluate_dimension(workload.rpm, plan.rpm, override.rpm if override else None),
        "itpm": _evaluate_dimension(itpm_demand, plan.itpm, override.itpm if override else None),
        "otpm": _evaluate_dimension(workload.otpm, plan.otpm, override.otpm if override else None),
    }


def _verdict_for(dims: dict[str, DimensionResult]) -> tuple[Verdict, Optional[str], Optional[float]]:
    if any(d.status is LimitStatus.ENFORCED and d.limit == 0 for d in dims.values()):
        return Verdict.BLOCKED, None, None
    loads = {k: d.load for k, d in dims.items() if d.load is not None}
    if not loads:
        return Verdict.UNKNOWN, None, None
    binding = max(loads, key=lambda k: loads[k])
    peak = loads[binding]
    if peak > 1.0:
        verdict = Verdict.OVER
    elif peak > AMPLE_THRESHOLD:
        verdict = Verdict.TIGHT
    else:
        verdict = Verdict.AMPLE
    return verdict, binding, round(peak, 4)


def _fits(workload: LLMWorkload, plan: QuotaPlan) -> bool:
    verdict, _, _ = _verdict_for(_plan_dims(workload, plan))
    return verdict in (Verdict.AMPLE, Verdict.TIGHT)


def _headroom(dims: dict[str, DimensionResult]) -> Optional[float]:
    """How many times over the whole scenario fits inside this plan."""
    ratios = [
        d.limit / d.demand
        for d in dims.values()
        if d.status is LimitStatus.ENFORCED and d.limit is not None and d.demand > 0
    ]
    return min(ratios) if ratios else None


def _breakeven_cache_rate(workload: LLMWorkload, itpm_limit: float) -> Optional[float]:
    """Cache hit rate at which uncached input drops to the ITPM ceiling.

    Only meaningful when ITPM is what blows the budget: raising the cache
    rate does nothing for RPM or OTPM.
    """
    raw_input_tpm = sum(a.rpm * a.input_tokens_per_request for a in workload.apps)
    if raw_input_tpm <= 0 or itpm_limit <= 0:
        return None
    needed = 1.0 - (itpm_limit / raw_input_tpm)
    if needed <= 0 or needed > MAX_SUGGESTED_CACHE_RATE:
        return None
    return round(needed, 3)


def _fmt(n: float) -> str:
    return f"{int(round(n)):,}"


def _build_actions(
    workload: LLMWorkload, plan: QuotaPlan, dims: dict[str, DimensionResult], verdict: Verdict
) -> list[Action]:
    actions: list[Action] = []

    if verdict is Verdict.UNKNOWN:
        actions.append(
            Action(
                kind=ActionKind.ENTER_ACCOUNT_QUOTA,
                text="此平台未公布預設值。請到 Service Quotas 主控台搜尋 "
                "Bedrock Mantle 查出本帳號的輸入／輸出 TPM，填入上方「我的帳號配額」即可得到判讀",
            )
        )
        if workload.max_tokens is None:
            actions.append(
                Action(
                    kind=ActionKind.SET_MAX_TOKENS,
                    text=f"設定 max_tokens 可大幅降低 ITPM 需求：目前按模型上限 "
                    f"{_fmt(MAX_OUTPUT_TOKENS)} 預扣，佔 ITPM 需求的絕大部分",
                )
            )
        return actions

    if verdict not in (Verdict.OVER, Verdict.BLOCKED):
        return actions

    # 1. The exact numbers to put in the increase request.
    shortfalls = [
        f"{name.upper()} {_fmt(d.demand)}（目前 {_fmt(d.limit)}）"
        for name, d in dims.items()
        if d.status is LimitStatus.ENFORCED and d.limit is not None and d.demand > d.limit
    ]
    if shortfalls:
        actions.append(
            Action(
                kind=ActionKind.REQUEST_QUOTA,
                text="提報調升至：" + "、".join(shortfalls),
            )
        )

    # 2. A plan on the same platform that already fits.
    same_platform = [
        p
        for p in list_plans(model=plan.model, platform=plan.platform)
        if p.plan_id != plan.plan_id and _fits(workload, p)
    ]
    if same_platform:
        actions.append(
            Action(
                kind=ActionKind.SWITCH_PLAN,
                text=f"改用「{same_platform[0].plan_label}」即可容納，無需另外申請",
            )
        )

    # 3. The same plan on a model with a looser quota.
    # Never trade capability for quota silently: consider only models at or
    # below the current tier, keep as much capability as possible, and break
    # ties on price.
    current = get_model(plan.model)
    alt_models = [
        p
        for p in list_plans(platform=plan.platform)
        if p.plan_id == plan.plan_id
        and p.model != plan.model
        and get_model(p.model).tier <= current.tier
        and _fits(workload, p)
    ]
    alt_models.sort(
        key=lambda p: (
            -get_model(p.model).tier,
            get_model(p.model).pricing.input_per_mtok,
            get_model(p.model).pricing.output_per_mtok,
        )
    )
    if alt_models:
        alt = alt_models[0]
        info = get_model(alt.model)
        cheaper = "，單價也更低" if info.pricing.input_per_mtok < current.pricing.input_per_mtok else ""
        prefix = f"若 {alt.model_label} 的能力足夠，" if info.tier < current.tier else ""
        actions.append(
            Action(
                kind=ActionKind.SWITCH_MODEL,
                text=f"{prefix}同一方案改用 {alt.model_label} 就塞得下{cheaper}",
            )
        )

    # 4. Caching, but only when ITPM alone is the problem.
    over_dims = {
        name
        for name, d in dims.items()
        if d.status is LimitStatus.ENFORCED and d.limit is not None and d.demand > d.limit
    }
    itpm = dims["itpm"]
    if over_dims == {"itpm"} and itpm.limit and not plan.reserves_max_tokens:
        rate = _breakeven_cache_rate(workload, itpm.limit)
        if rate is not None:
            actions.append(
                Action(
                    kind=ActionKind.RAISE_CACHE,
                    text=f"把快取命中率提高到 {rate * 100:.0f}% 就能塞進現有額度，"
                    f"不必申請調額（目前 {max(a.cache_hit_rate for a in workload.apps) * 100:.0f}%）",
                )
            )

    if workload.batch_eligible:
        actions.append(
            Action(
                kind=ActionKind.USE_BATCH,
                text="這類工作可以非即時處理：改走批次 API 不佔即時配額，且費用打五折",
            )
        )

    if plan.reserves_max_tokens and workload.max_tokens is None:
        actions.append(
            Action(
                kind=ActionKind.SET_MAX_TOKENS,
                text=f"設定 max_tokens：目前按模型上限 {_fmt(MAX_OUTPUT_TOKENS)} 預扣 ITPM",
            )
        )
    return actions


def _evaluate_plan(workload: LLMWorkload, plan: QuotaPlan) -> QuotaPlanResult:
    dims = _plan_dims(workload, plan)
    verdict, binding, peak = _verdict_for(dims)
    headroom = _headroom(dims)

    max_users = None
    if headroom is not None and workload.total_users > 0:
        max_users = int(math.floor(workload.total_users * headroom))

    notes = list(plan.notes)
    if plan.reserves_max_tokens:
        notes.insert(
            0,
            f"ITPM 需求已含每次請求預扣的 max_tokens {_fmt(workload.effective_max_tokens)} tokens"
            if workload.max_tokens is not None
            else f"未指定 max_tokens，每次請求預扣模型上限 {_fmt(MAX_OUTPUT_TOKENS)} tokens 的 ITPM",
        )

    return QuotaPlanResult(
        model=plan.model,
        model_label=plan.model_label,
        platform=plan.platform,
        plan_id=plan.plan_id,
        platform_label=plan.platform_label,
        plan_label=plan.plan_label,
        rpm=dims["rpm"],
        itpm=dims["itpm"],
        otpm=dims["otpm"],
        verdict=verdict,
        peak_load=peak,
        binding_dimension=binding,
        headroom_multiple=round(headroom, 4) if headroom is not None else None,
        max_users=max_users,
        actions=_build_actions(workload, plan, dims, verdict),
        notes=notes,
        source=plan.source,
        verified=plan.verified,
    )


# ---------------------------------------------------------------------------
# Cost
# ---------------------------------------------------------------------------


def _estimate_cost(workload: LLMWorkload) -> CostEstimate:
    price = get_model(workload.model).pricing
    per_m = 1_000_000.0

    uncached_usd = workload.itpm * price.input_per_mtok / per_m
    cache_read_usd = workload.cached_itpm * price.cache_read_per_mtok / per_m
    thinking_usd = workload.thinking_tpm * price.output_per_mtok / per_m
    reply_usd = (workload.otpm - workload.thinking_tpm) * price.output_per_mtok / per_m
    per_minute = uncached_usd + cache_read_usd + reply_usd + thinking_usd

    rpm = workload.rpm
    per_request = per_minute / rpm if rpm else 0.0
    per_1k = per_request * 1000

    # Same traffic with caching switched off: every input token at full rate.
    raw_input_tpm = sum(a.rpm * a.input_tokens_per_request for a in workload.apps)
    no_cache_minute = (raw_input_tpm * price.input_per_mtok + workload.otpm * price.output_per_mtok) / per_m
    no_cache_per_1k = (no_cache_minute / rpm * 1000) if rpm else 0.0
    saving_pct = (
        (no_cache_per_1k - per_1k) / no_cache_per_1k * 100 if no_cache_per_1k > 0 else 0.0
    )

    def per_1k_of(usd: float) -> float:
        return round(usd / rpm * 1000, 4) if rpm else 0.0

    batch_per_request = per_request * (1 - BATCH_DISCOUNT)

    caveats = [
        "以 Anthropic 官方第一方定價計算。Claude in Microsoft Foundry 同樣採標準 API 費率"
        "（以 CCU 計價開立帳單）；Amazon Bedrock 與 Google Vertex 為合作夥伴自訂定價，"
        "實際金額請以該平台價目表為準",
        "思考 token 一律按 Output 計費，即使畫面不顯示也會收費。此處的思考量是規劃估計，"
        "請以實際請求回傳的 usage.output_tokens 校正",
        "假設快取在穩定流量下由讀取持續續期，因此未計入快取寫入費用"
        f"（首次寫入為輸入價的 1.25 倍，約 ${price.cache_write_5m_per_mtok:g}/MTok）",
    ]

    return CostEstimate(
        per_request_usd=round(per_request, 6),
        per_1k_requests_usd=round(per_1k, 4),
        per_peak_minute_usd=round(per_minute, 4),
        monthly_usd=(
            round(per_request * workload.monthly_requests, 2)
            if workload.monthly_requests is not None
            else None
        ),
        per_1k_requests_without_cache_usd=round(no_cache_per_1k, 4),
        cache_saving_pct=round(saving_pct, 1),
        breakdown_per_1k={
            "uncached_input": per_1k_of(uncached_usd),
            "cache_read": per_1k_of(cache_read_usd),
            "output": per_1k_of(reply_usd),
            "thinking": per_1k_of(thinking_usd),
        },
        thinking_share_pct=round(thinking_usd / per_minute * 100, 1) if per_minute else 0.0,
        batch_per_1k_requests_usd=round(batch_per_request * 1000, 4),
        batch_monthly_usd=(
            round(batch_per_request * workload.monthly_requests, 2)
            if workload.monthly_requests is not None
            else None
        ),
        caveats=caveats,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_FITS = (Verdict.AMPLE, Verdict.TIGHT)


def _scaled(workload: LLMWorkload, multiplier: float) -> LLMWorkload:
    """The same scenario with every app's peak rate multiplied."""
    apps = [
        a.model_copy(update={"requests_per_user_per_minute": a.requests_per_user_per_minute * multiplier})
        for a in workload.apps
    ]
    return workload.model_copy(update={"apps": apps})


def _count_fitting(workload: LLMWorkload, platform: Optional[LLMPlatform]) -> tuple[int, int]:
    plans = list_plans(model=workload.model, platform=platform)
    fitting = sum(1 for p in plans if _fits(workload, p))
    return fitting, len(plans)


def compare_models(
    workload: LLMWorkload, platform: Optional[LLMPlatform] = None
) -> list[ModelComparison]:
    """Price and size the same scenario on every model, cheapest first.

    Thinking and output volumes are held constant across models: real
    per-model differences exist but are not published, so the comparison
    isolates what *is* known — price and quota.
    """
    rows: list[ModelComparison] = []
    for info in list_models():
        variant = workload.model_copy(update={"model": info.model})
        cost = _estimate_cost(variant)
        results = [_evaluate_plan(variant, p) for p in list_plans(info.model, platform)]
        fitting = [r for r in results if r.verdict in _FITS]
        caps = [r.max_users for r in fitting if r.max_users is not None]
        rows.append(
            ModelComparison(
                model=info.model,
                label=info.label,
                per_1k_requests_usd=cost.per_1k_requests_usd,
                monthly_usd=cost.monthly_usd,
                fitting_plans=len(fitting),
                total_plans=len(results),
                best_max_users=max(caps) if caps else None,
                is_selected=info.model == workload.model,
            )
        )
    rows.sort(key=lambda r: (r.per_1k_requests_usd, r.label))
    return rows


def evaluate_workload(
    workload: LLMWorkload, platform: Optional[LLMPlatform] = None
) -> QuotaReport:
    """Evaluate a scenario against every published default quota for its model."""
    plans = list_plans(model=workload.model, platform=platform)
    results = [_evaluate_plan(workload, p) for p in plans]
    fitting = sum(1 for r in results if r.verdict in _FITS)

    warnings: list[str] = []
    if all(a.cache_hit_rate == 0 for a in workload.apps):
        warnings.append(
            "快取命中率設為 0：System Prompt 與固定 RAG 前綴通常可以快取，"
            "開啟後 ITPM 需求與費用會同時下降"
        )
    if workload.max_tokens is None and any(p.reserves_max_tokens for p in plans):
        warnings.append(
            f"未指定 max_tokens：Bedrock Mantle 會按模型上限 {_fmt(MAX_OUTPUT_TOKENS)} "
            "tokens 預扣 ITPM，設定實際值可大幅降低被節流的機會"
        )
    if workload.max_tokens is not None:
        needed = max(a.billed_output_per_request for a in workload.apps)
        if workload.max_tokens < needed:
            warnings.append(
                f"max_tokens {_fmt(workload.max_tokens)} 小於單次回覆加思考的 {_fmt(needed)} tokens："
                "思考也計入 max_tokens，回應會被截斷，請調高"
            )
    if any(r.verdict is Verdict.UNKNOWN for r in results):
        warnings.append(
            "部分平台未公布預設配額。可在該平台的配額主控台查出本帳號實際額度後填入上方欄位"
        )

    stressed = _scaled(workload, 2.0)
    stress_fit, stress_total = _count_fitting(stressed, platform)

    assumptions = [
        "所有數字皆為尖峰 1 分鐘的平均值。平台採持續補充的 token bucket，"
        "同樣的量在幾秒內灌完仍可能被節流，實務上請預留突發餘裕",
        "配額為組織／訂閱層級共用。多個應用跑在同一個帳號上會共用同一個額度，此處已加總",
        "思考 token 計入 Output 費用與 OTPM。思考量隨 effort 與題目難度變動，此處為規劃估計",
        "情境的 token 量、每人每天次數與尖峰係數為規劃估計，不是任何實際部署的量測值",
        f"配額資料驗證：{results[0].verified if results else ''}。"
        "以上皆為平台預設值，非模型本體物理上限，均可提報申請調升",
    ]

    return QuotaReport(
        workload=workload,
        model_label=get_model(workload.model).label,
        total_users=workload.total_users,
        required_rpm=round(workload.rpm, 2),
        required_itpm=round(workload.itpm, 2),
        required_otpm=round(workload.otpm, 2),
        cached_itpm=round(workload.cached_itpm, 2),
        cost=_estimate_cost(workload),
        results=results,
        fitting_plans=fitting,
        model_comparison=compare_models(workload, platform),
        sensitivity=[
            Sensitivity(
                label="尖峰再集中一倍",
                multiplier=2.0,
                fitting_plans=stress_fit,
                total_plans=stress_total,
            )
        ],
        warnings=warnings,
        assumptions=assumptions,
    )


# ---------------------------------------------------------------------------
# Scenario-based sizing
# ---------------------------------------------------------------------------


def size_from_scenario(
    scenario_id: str,
    users: int,
    messages_per_user_per_day: Optional[float] = None,
    peak_profile: str = "normal",
    model: Optional[LLMModel] = None,
    effort: Optional[str] = None,
) -> LLMWorkload:
    """Build a workload from the three things a customer can actually answer.

    Nobody knows their prompt's token count, and nobody plans in requests per
    minute — but everyone knows roughly how many people will use the thing and
    how often. This turns that into the peak-minute figures quota is measured
    in, using the scenario's token profile.

    The peak factor is the load-bearing assumption. Quota is a per-minute
    ceiling, so how sharply a day's traffic piles into the busiest minute
    matters more than the daily total does.
    """
    scenario = get_scenario(scenario_id)
    per_day = (
        messages_per_user_per_day
        if messages_per_user_per_day is not None
        else scenario.messages_per_user_per_day
    )
    factor = PEAK_FACTORS.get(peak_profile, PEAK_FACTORS["normal"])
    level = effort if effort in EFFORT_THINKING_FACTORS else scenario.default_effort
    thinking = round(scenario.thinking_tokens_per_request * EFFORT_THINKING_FACTORS[level])

    # Spread the day over its active hours, then concentrate it by the factor.
    peak_rpm_per_user = per_day / (ACTIVE_HOURS_PER_DAY * 60) * factor

    return LLMWorkload(
        model=model or scenario.suggested_model,
        apps=[
            AppWorkload(
                name=scenario.label,
                concurrent_users=users,
                requests_per_user_per_minute=max(0.0001, peak_rpm_per_user),
                input_tokens_per_request=scenario.input_tokens_per_request,
                output_tokens_per_request=scenario.output_tokens_per_request,
                thinking_tokens_per_request=thinking,
                cache_hit_rate=scenario.cache_hit_rate,
            )
        ],
        max_tokens=scenario.max_tokens,
        monthly_requests=round(users * per_day * WORKING_DAYS_PER_MONTH),
        batch_eligible=scenario.batch_friendly,
    )
