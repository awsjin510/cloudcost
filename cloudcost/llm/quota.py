"""Claude Fable 5 / 5.1 platform quota data and capacity calculator.

Answers the question a customer actually asks before a deployment:
"we expect N users at peak — is the default quota on this platform enough?"

Three demand figures drive every platform's throttling decision:

  RPM   requests per minute
  ITPM  *uncached* input tokens per minute
  OTPM  output tokens per minute

Two facts make a naive spreadsheet wrong, and both are modelled here:

1. Cache reads are free of ITPM on all four platforms. Only tokens after
   the last cache breakpoint plus cache *writes* count, so a workload with
   a large cached system prompt / RAG prefix needs far less ITPM than its
   raw prompt size suggests.
2. Amazon Bedrock's Messages-API endpoint (``bedrock-mantle``) reserves
   ``input_tokens + max_tokens`` against ITPM when it *admits* a request,
   and refunds the unused remainder afterwards. A request is therefore
   throttled on what it *might* generate, not on what it does. When
   ``max_tokens`` is omitted the model maximum (128K) is reserved.

Quota values below are platform *defaults*, not physical model limits.
Every one of them can be raised on request. Verified 2026-09 against:

  Anthropic  https://platform.claude.com/docs/en/api/rate-limits
  Bedrock    https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html
  Foundry    https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits
  Vertex     https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Maximum output tokens for the Fable 5 family. Bedrock Mantle reserves this
#: much ITPM per request when the caller omits ``max_tokens``.
FABLE_MAX_OUTPUT_TOKENS = 128_000

#: Load ratio at or below which a plan is considered comfortable.
_AMPLE_THRESHOLD = 0.70

#: Verified 2026-09. Quota data covers the Fable 5 family as a whole: every
#: platform either shares one bucket across Fable 5 and 5.1 or publishes
#: identical defaults for both.
QUOTA_VERIFIED = "2026-09"


class LLMPlatform(str, Enum):
    """Platform serving Claude Fable 5 / 5.1."""

    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    FOUNDRY = "foundry"
    VERTEX = "vertex"


class LimitStatus(str, Enum):
    """Why a limit does or does not carry a number."""

    #: A published numeric ceiling applies.
    ENFORCED = "enforced"
    #: The platform does not apply this limit type at all.
    NOT_ENFORCED = "not_enforced"
    #: A limit applies but the platform publishes no default value.
    UNPUBLISHED = "unpublished"


class Verdict(str, Enum):
    """Capacity verdict for one plan against one workload."""

    #: Comfortably within the default quota.
    AMPLE = "ample"
    #: Fits, but with little headroom.
    TIGHT = "tight"
    #: Demand exceeds the default quota.
    OVER = "over"
    #: Default quota is zero — the plan cannot serve any traffic as-is.
    BLOCKED = "blocked"
    #: No published quota to compare against.
    UNKNOWN = "unknown"


class Limit(BaseModel):
    """One quota dimension (RPM, ITPM or OTPM) for one plan."""

    status: LimitStatus
    value: Optional[float] = Field(
        default=None, description="Published ceiling per minute; None unless enforced"
    )
    note: str = ""


class QuotaPlan(BaseModel):
    """A platform's default quota under one purchasing / endpoint option."""

    platform: LLMPlatform
    plan_id: str
    platform_label: str
    plan_label: str
    rpm: Limit
    itpm: Limit
    otpm: Limit
    #: Bedrock Mantle admits on input + max_tokens rather than input alone.
    reserves_max_tokens: bool = False
    notes: list[str] = Field(default_factory=list)
    source: str
    verified: str = QUOTA_VERIFIED


def _enforced(value: float) -> Limit:
    return Limit(status=LimitStatus.ENFORCED, value=value)


_UNPUBLISHED_TPM = Limit(
    status=LimitStatus.UNPUBLISHED,
    note="Bedrock publishes per-account TPM quotas only for selected models; "
    "Fable throughput is governed by internal service capacity",
)

_ANTHROPIC_SRC = "https://platform.claude.com/docs/en/api/rate-limits"
_BEDROCK_SRC = "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html"
_FOUNDRY_SRC = (
    "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/"
    "concepts/claude-models-quotas-limits"
)
_VERTEX_SRC = (
    "https://docs.cloud.google.com/gemini-enterprise-agent-platform/"
    "models/partner-models/claude/quotas"
)

_SHARED_FABLE_BUCKET = (
    "Fable 5.1 and Fable 5 draw on one shared limit — split traffic does not double it"
)

# ---------------------------------------------------------------------------
# Quota table
# ---------------------------------------------------------------------------

_PLANS: list[QuotaPlan] = [
    # --- Anthropic Claude API (first party) --------------------------------
    QuotaPlan(
        platform=LLMPlatform.ANTHROPIC,
        plan_id="start",
        platform_label="Anthropic API",
        plan_label="Start 層級",
        rpm=_enforced(1_000),
        itpm=_enforced(500_000),
        otpm=_enforced(100_000),
        notes=[_SHARED_FABLE_BUCKET, "組織層級限制，可跨 Workspace 分配"],
        source=_ANTHROPIC_SRC,
    ),
    QuotaPlan(
        platform=LLMPlatform.ANTHROPIC,
        plan_id="build",
        platform_label="Anthropic API",
        plan_label="Build 層級",
        rpm=_enforced(2_000),
        itpm=_enforced(1_500_000),
        otpm=_enforced(300_000),
        notes=[_SHARED_FABLE_BUCKET],
        source=_ANTHROPIC_SRC,
    ),
    QuotaPlan(
        platform=LLMPlatform.ANTHROPIC,
        plan_id="scale",
        platform_label="Anthropic API",
        plan_label="Scale 層級",
        rpm=_enforced(4_000),
        itpm=_enforced(4_000_000),
        otpm=_enforced(800_000),
        notes=[_SHARED_FABLE_BUCKET, "需要更高上限請走 Custom 層級洽談"],
        source=_ANTHROPIC_SRC,
    ),
    # --- Amazon Bedrock ----------------------------------------------------
    QuotaPlan(
        platform=LLMPlatform.BEDROCK,
        plan_id="mantle",
        platform_label="AWS Bedrock",
        plan_label="bedrock-mantle 端點",
        rpm=Limit(
            status=LimitStatus.NOT_ENFORCED,
            note="Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流",
        ),
        itpm=_UNPUBLISHED_TPM,
        otpm=_UNPUBLISHED_TPM,
        reserves_max_tokens=True,
        notes=[
            "准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分",
            "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃",
            "目前僅 Opus 4.7 有公布的 Mantle 預設值 (20M 輸入 / 4M 輸出 TPM)",
        ],
        source=_BEDROCK_SRC,
    ),
    # --- Microsoft Foundry -------------------------------------------------
    QuotaPlan(
        platform=LLMPlatform.FOUNDRY,
        plan_id="payg",
        platform_label="Azure Foundry",
        plan_label="隨用隨付 (Global Standard)",
        rpm=_enforced(0),
        itpm=_enforced(0),
        otpm=_enforced(0),
        notes=[
            "隨用隨付訂閱的 Fable 預設配額為 0，部署前必須先申請",
            "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本",
        ],
        source=_FOUNDRY_SRC,
    ),
    QuotaPlan(
        platform=LLMPlatform.FOUNDRY,
        plan_id="enterprise",
        platform_label="Azure Foundry",
        plan_label="Enterprise / MCA-E (Global Standard)",
        rpm=_enforced(4_000),
        itpm=_enforced(4_000_000),
        otpm=_enforced(800_000),
        notes=[
            "配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池",
            "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本",
        ],
        source=_FOUNDRY_SRC,
    ),
    # --- Google Vertex AI --------------------------------------------------
    QuotaPlan(
        platform=LLMPlatform.VERTEX,
        plan_id="global",
        platform_label="GCP Vertex",
        plan_label="全域端點 (global)",
        rpm=_enforced(2_000),
        itpm=_enforced(20_000_000),
        otpm=_enforced(2_000_000),
        notes=[
            _SHARED_FABLE_BUCKET + "（共用 anthropic-claude-fable 沿襲配額）",
            "輸入 TPM 計入未快取與快取寫入的 token",
        ],
        source=_VERTEX_SRC,
    ),
    QuotaPlan(
        platform=LLMPlatform.VERTEX,
        plan_id="multi_region",
        platform_label="GCP Vertex",
        plan_label="多區域端點 (us / eu)",
        rpm=_enforced(1_000),
        itpm=_enforced(10_000_000),
        otpm=_enforced(1_000_000),
        notes=[
            "多區域端點配額為全域端點的一半，且兩者額度互不相通",
            _SHARED_FABLE_BUCKET + "（共用 anthropic-claude-fable 沿襲配額）",
        ],
        source=_VERTEX_SRC,
    ),
]


def list_plans(platform: Optional[LLMPlatform] = None) -> list[QuotaPlan]:
    """Return the quota table, optionally filtered to one platform."""
    if platform is None:
        return list(_PLANS)
    return [p for p in _PLANS if p.platform == platform]


# ---------------------------------------------------------------------------
# Workload model
# ---------------------------------------------------------------------------


class LLMWorkload(BaseModel):
    """Peak-minute demand description for a Claude deployment."""

    concurrent_users: int = Field(
        default=100, ge=1, le=1_000_000, description="Users active during the peak minute"
    )
    requests_per_user_per_minute: float = Field(
        default=1.0, gt=0, le=600, description="Requests each user sends per peak minute"
    )
    input_tokens_per_request: int = Field(
        default=20_000,
        ge=1,
        le=1_000_000,
        description="Total prompt size: system prompt + history + RAG context",
    )
    output_tokens_per_request: int = Field(
        default=2_000, ge=1, le=FABLE_MAX_OUTPUT_TOKENS, description="Generated tokens"
    )
    cache_hit_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=0.95,
        description="Share of the prompt served from prompt cache; cache reads are ITPM-free",
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=FABLE_MAX_OUTPUT_TOKENS,
        description="Requested max_tokens; drives Bedrock Mantle's ITPM reservation",
    )

    # -- derived demand ----------------------------------------------------

    @property
    def rpm(self) -> float:
        """Requests per minute at peak."""
        return self.concurrent_users * self.requests_per_user_per_minute

    @property
    def uncached_input_per_request(self) -> float:
        """Prompt tokens that actually count toward ITPM."""
        return self.input_tokens_per_request * (1.0 - self.cache_hit_rate)

    @property
    def itpm(self) -> float:
        """Uncached input tokens per minute."""
        return self.rpm * self.uncached_input_per_request

    @property
    def otpm(self) -> float:
        """Output tokens per minute."""
        return self.rpm * self.output_tokens_per_request

    @property
    def effective_max_tokens(self) -> int:
        """What Bedrock Mantle reserves per request when admitting it."""
        return self.max_tokens if self.max_tokens is not None else FABLE_MAX_OUTPUT_TOKENS

    @property
    def itpm_with_reservation(self) -> float:
        """ITPM as Bedrock Mantle counts it: uncached input plus reserved output."""
        return self.rpm * (self.uncached_input_per_request + self.effective_max_tokens)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


class DimensionResult(BaseModel):
    """Demand vs. limit for one quota dimension."""

    demand: float
    limit: Optional[float] = None
    status: LimitStatus
    #: demand / limit; None when there is nothing to divide by.
    load: Optional[float] = None
    note: str = ""


class QuotaPlanResult(BaseModel):
    """How one workload lands against one plan's default quota."""

    platform: LLMPlatform
    plan_id: str
    platform_label: str
    plan_label: str
    rpm: DimensionResult
    itpm: DimensionResult
    otpm: DimensionResult
    verdict: Verdict
    #: Highest load ratio across the enforced dimensions.
    peak_load: Optional[float] = None
    #: Dimension driving the verdict ("rpm" / "itpm" / "otpm").
    binding_dimension: Optional[str] = None
    notes: list[str] = Field(default_factory=list)
    source: str
    verified: str


class QuotaReport(BaseModel):
    """Full evaluation of one workload across every known plan."""

    workload: LLMWorkload
    required_rpm: float
    required_itpm: float
    required_otpm: float
    results: list[QuotaPlanResult]
    warnings: list[str] = Field(default_factory=list)


def _evaluate_dimension(demand: float, limit: Limit) -> DimensionResult:
    if limit.status is not LimitStatus.ENFORCED or limit.value is None:
        return DimensionResult(
            demand=round(demand, 2), status=limit.status, note=limit.note
        )
    # A zero default quota has no meaningful ratio: infinity does not survive
    # JSON (browsers reject the token), so the BLOCKED verdict carries the
    # meaning instead and the ratio stays unset.
    load = None if limit.value == 0 else demand / limit.value
    return DimensionResult(
        demand=round(demand, 2),
        limit=limit.value,
        status=limit.status,
        load=load,
        note=limit.note,
    )


def _verdict_for(loads: dict[str, float], any_zero_limit: bool) -> Verdict:
    if any_zero_limit:
        return Verdict.BLOCKED
    if not loads:
        return Verdict.UNKNOWN
    worst = max(loads.values())
    if worst > 1.0:
        return Verdict.OVER
    if worst > _AMPLE_THRESHOLD:
        return Verdict.TIGHT
    return Verdict.AMPLE


def _evaluate_plan(workload: LLMWorkload, plan: QuotaPlan) -> QuotaPlanResult:
    # Bedrock Mantle admits on input + max_tokens; everyone else on input alone.
    itpm_demand = (
        workload.itpm_with_reservation if plan.reserves_max_tokens else workload.itpm
    )

    rpm = _evaluate_dimension(workload.rpm, plan.rpm)
    itpm = _evaluate_dimension(itpm_demand, plan.itpm)
    otpm = _evaluate_dimension(workload.otpm, plan.otpm)

    loads = {
        name: dim.load
        for name, dim in (("rpm", rpm), ("itpm", itpm), ("otpm", otpm))
        if dim.load is not None
    }
    any_zero_limit = any(
        dim.status is LimitStatus.ENFORCED and dim.limit == 0
        for dim in (rpm, itpm, otpm)
    )

    verdict = _verdict_for(loads, any_zero_limit)
    peak_load: Optional[float] = None
    binding: Optional[str] = None
    if loads:
        binding = max(loads, key=lambda k: loads[k])
        peak_load = round(loads[binding], 4)

    notes = list(plan.notes)
    if plan.reserves_max_tokens:
        if workload.max_tokens is None:
            notes.insert(
                0,
                f"未指定 max_tokens，Mantle 每次請求預扣模型上限 "
                f"{FABLE_MAX_OUTPUT_TOKENS:,} tokens 的 ITPM",
            )
        else:
            notes.insert(
                0,
                f"ITPM 需求已含每次請求預扣的 max_tokens {workload.max_tokens:,} tokens",
            )

    return QuotaPlanResult(
        platform=plan.platform,
        plan_id=plan.plan_id,
        platform_label=plan.platform_label,
        plan_label=plan.plan_label,
        rpm=rpm,
        itpm=itpm,
        otpm=otpm,
        verdict=verdict,
        peak_load=peak_load,
        binding_dimension=binding,
        notes=notes,
        source=plan.source,
        verified=plan.verified,
    )


def evaluate_workload(
    workload: LLMWorkload, platform: Optional[LLMPlatform] = None
) -> QuotaReport:
    """Evaluate a workload against every published Fable 5 / 5.1 default quota."""
    plans = list_plans(platform)
    results = [_evaluate_plan(workload, plan) for plan in plans]

    warnings: list[str] = []
    if workload.cache_hit_rate == 0:
        warnings.append(
            "快取命中率設為 0：若 System Prompt 或 RAG context 有做 prompt caching，"
            "實際 ITPM 需求會顯著低於此估算"
        )
    # Only worth raising when a plan that actually reserves max_tokens is in scope.
    if workload.max_tokens is None and any(p.reserves_max_tokens for p in plans):
        warnings.append(
            f"未指定 max_tokens：Bedrock Mantle 會按模型上限 "
            f"{FABLE_MAX_OUTPUT_TOKENS:,} tokens 預扣 ITPM，設定實際值可大幅降低被節流的機會"
        )
    if any(r.verdict is Verdict.UNKNOWN for r in results):
        warnings.append(
            "部分平台未公布 Fable 預設配額，實際額度請以該帳號的配額主控台為準"
        )

    return QuotaReport(
        workload=workload,
        required_rpm=round(workload.rpm, 2),
        required_itpm=round(workload.itpm, 2),
        required_otpm=round(workload.otpm, 2),
        results=results,
        warnings=warnings,
    )
