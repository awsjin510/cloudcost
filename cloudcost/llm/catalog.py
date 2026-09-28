"""Model catalogue: per-model pricing and per-platform default quotas.

Everything in this module is reference data transcribed from vendor
documentation, with the source URL and a verification date attached so a
stale figure can be traced back and re-checked.

Two things are deliberately kept apart:

*Pricing* is what a token costs. *Quota* is how many tokens per minute the
platform will accept. They come from different documents, change on
different schedules, and answer different questions.

Verified 2026-09 against:

  Pricing    https://platform.claude.com/docs/en/about-claude/pricing
  Anthropic  https://platform.claude.com/docs/en/api/rate-limits
  Bedrock    https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html
  Foundry    https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits
  Vertex     https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

VERIFIED = "2026-09-28"

#: Maximum output tokens for every model modelled here.
MAX_OUTPUT_TOKENS = 128_000

SRC_PRICING = "https://platform.claude.com/docs/en/about-claude/pricing"
SRC_ANTHROPIC = "https://platform.claude.com/docs/en/api/rate-limits"
SRC_BEDROCK = "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html"
SRC_FOUNDRY = (
    "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/"
    "concepts/claude-models-quotas-limits"
)
SRC_VERTEX = (
    "https://docs.cloud.google.com/gemini-enterprise-agent-platform/"
    "models/partner-models/claude/quotas"
)


class LLMModel(str, Enum):
    """Models with both published pricing and published platform quotas."""

    FABLE_5_1 = "fable-5-1"
    FABLE_5 = "fable-5"
    OPUS_5_5 = "opus-5-5"
    OPUS_5 = "opus-5"
    SONNET_5 = "sonnet-5"


class LLMPlatform(str, Enum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    FOUNDRY = "foundry"
    VERTEX = "vertex"


class LimitStatus(str, Enum):
    """Why a limit does or does not carry a number."""

    ENFORCED = "enforced"
    NOT_ENFORCED = "not_enforced"
    UNPUBLISHED = "unpublished"


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------


class ModelPricing(BaseModel):
    """USD per million tokens. First-party Claude API list price."""

    input_per_mtok: float
    output_per_mtok: float
    #: Cache hits are 0.1x base input on most models; Fable 5.1 is 0.025x and
    #: Opus 5.5 is 0.05x.
    cache_read_per_mtok: float
    #: Writing a prefix to the 5-minute cache costs 1.25x base input.
    cache_write_5m_per_mtok: float


class ModelInfo(BaseModel):
    model: LLMModel
    label: str
    #: Capability tier (higher = more capable). Used so a quota workaround
    #: never silently trades capability for price.
    tier: int
    pricing: ModelPricing
    notes: list[str] = Field(default_factory=list)

    @property
    def api_id(self) -> str:
        """Model ID on the Claude API, e.g. ``claude-opus-5-5``."""
        return f"claude-{self.model.value}"


_MODELS: list[ModelInfo] = [
    ModelInfo(
        model=LLMModel.FABLE_5_1,
        label="Claude Fable 5.1",
        tier=3,
        pricing=ModelPricing(
            input_per_mtok=10.0,
            output_per_mtok=50.0,
            cache_read_per_mtok=0.25,
            cache_write_5m_per_mtok=12.50,
        ),
        notes=[
            "快取讀取為輸入價的 0.025 倍，是所有模型中最低的，"
            "有做 prompt caching 時省下的比例最大",
        ],
    ),
    ModelInfo(
        model=LLMModel.FABLE_5,
        label="Claude Fable 5",
        tier=3,
        pricing=ModelPricing(
            input_per_mtok=10.0,
            output_per_mtok=50.0,
            cache_read_per_mtok=1.0,
            cache_write_5m_per_mtok=12.50,
        ),
        notes=["快取讀取為輸入價的 0.1 倍，比 Fable 5.1 貴 4 倍"],
    ),
    ModelInfo(
        model=LLMModel.OPUS_5_5,
        label="Claude Opus 5.5",
        tier=2,
        pricing=ModelPricing(
            input_per_mtok=4.0,
            output_per_mtok=20.0,
            cache_read_per_mtok=0.20,
            cache_write_5m_per_mtok=5.0,
        ),
        notes=["配額與 Opus 5 相同、單價便宜兩成，快取讀取為輸入價的 0.05 倍"],
    ),
    ModelInfo(
        model=LLMModel.OPUS_5,
        label="Claude Opus 5",
        tier=2,
        pricing=ModelPricing(
            input_per_mtok=5.0,
            output_per_mtok=25.0,
            cache_read_per_mtok=0.50,
            cache_write_5m_per_mtok=6.25,
        ),
        notes=["單價為 Fable 的一半；同配額下 Opus 5.5 更便宜，新專案建議直接評估 Opus 5.5"],
    ),
    ModelInfo(
        model=LLMModel.SONNET_5,
        label="Claude Sonnet 5",
        tier=1,
        pricing=ModelPricing(
            input_per_mtok=2.0,
            output_per_mtok=10.0,
            cache_read_per_mtok=0.20,
            cache_write_5m_per_mtok=2.50,
        ),
        notes=["高流量生產工作負載的預設選擇，單價為 Fable 的五分之一"],
    ),
]

_MODEL_BY_ID = {m.model: m for m in _MODELS}


def list_models() -> list[ModelInfo]:
    """All modelled models, cheapest cache read last."""
    return list(_MODELS)


def get_model(model: LLMModel) -> ModelInfo:
    return _MODEL_BY_ID[model]


# ---------------------------------------------------------------------------
# Quota
# ---------------------------------------------------------------------------


class Limit(BaseModel):
    """One quota dimension (RPM, ITPM or OTPM) for one plan."""

    status: LimitStatus
    value: Optional[float] = Field(
        default=None, description="Published ceiling per minute; None unless enforced"
    )
    note: str = ""


def _en(value: float) -> Limit:
    return Limit(status=LimitStatus.ENFORCED, value=value)


_NO_RPM = Limit(
    status=LimitStatus.NOT_ENFORCED,
    note="Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流",
)
_NO_TPM = Limit(
    status=LimitStatus.UNPUBLISHED,
    note="Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定",
)

_SHARED_FABLE = "Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍"


class QuotaPlan(BaseModel):
    """One platform's default quota for one model under one purchasing option."""

    model: LLMModel
    model_label: str
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
    verified: str = VERIFIED


# Plan shape, shared by every model on that plan.
# (platform, plan_id, platform_label, plan_label, source, reserves, notes)
_PLAN_SHAPES: list[tuple] = [
    (LLMPlatform.ANTHROPIC, "start", "Anthropic API", "Start 層級", SRC_ANTHROPIC, False,
     ["限制掛在組織層級，可再往下分配給各 Workspace"]),
    (LLMPlatform.ANTHROPIC, "build", "Anthropic API", "Build 層級", SRC_ANTHROPIC, False, []),
    (LLMPlatform.ANTHROPIC, "scale", "Anthropic API", "Scale 層級", SRC_ANTHROPIC, False,
     ["需要更高上限請走 Custom 層級洽談"]),
    (LLMPlatform.BEDROCK, "mantle", "AWS Bedrock", "bedrock-mantle 端點", SRC_BEDROCK, True,
     ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分",
      "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃",
      "目前僅 Opus 4.7 有公布的 Mantle 預設值（20M 輸入 / 4M 輸出 TPM）",
      "可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"]),
    (LLMPlatform.FOUNDRY, "payg", "Azure Foundry", "隨用隨付 (Global Standard)", SRC_FOUNDRY, False,
     ["免費試用訂閱的預設額度同樣為 0"]),
    (LLMPlatform.FOUNDRY, "enterprise", "Azure Foundry", "Enterprise / MCA-E (Global Standard)",
     SRC_FOUNDRY, False,
     ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"]),
    (LLMPlatform.VERTEX, "global", "GCP Vertex", "全域端點 (global)", SRC_VERTEX, False,
     ["輸入 TPM 計入未快取與快取寫入的 token"]),
    (LLMPlatform.VERTEX, "multi_region", "GCP Vertex", "多區域端點 (us / eu)", SRC_VERTEX, False,
     ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通",
      "多區域端點另有 10% 價格溢價"]),
]

# (rpm, itpm, otpm) per plan_id per model. None means "use the Limit object
# named in _SPECIAL" rather than a number.
_QUOTAS: dict[str, dict[LLMModel, tuple[float, float, float]]] = {
    "start": {
        LLMModel.FABLE_5_1: (1_000, 500_000, 100_000),
        LLMModel.FABLE_5: (1_000, 500_000, 100_000),
        LLMModel.OPUS_5_5: (1_000, 2_000_000, 400_000),
        LLMModel.OPUS_5: (1_000, 2_000_000, 400_000),
        LLMModel.SONNET_5: (1_000, 2_000_000, 400_000),
    },
    "build": {
        LLMModel.FABLE_5_1: (2_000, 1_500_000, 300_000),
        LLMModel.FABLE_5: (2_000, 1_500_000, 300_000),
        LLMModel.OPUS_5_5: (5_000, 5_000_000, 1_000_000),
        LLMModel.OPUS_5: (5_000, 5_000_000, 1_000_000),
        LLMModel.SONNET_5: (5_000, 5_000_000, 1_000_000),
    },
    "scale": {
        LLMModel.FABLE_5_1: (4_000, 4_000_000, 800_000),
        LLMModel.FABLE_5: (4_000, 4_000_000, 800_000),
        LLMModel.OPUS_5_5: (10_000, 10_000_000, 2_000_000),
        LLMModel.OPUS_5: (10_000, 10_000_000, 2_000_000),
        LLMModel.SONNET_5: (10_000, 10_000_000, 2_000_000),
    },
    "payg": {
        LLMModel.FABLE_5_1: (0, 0, 0),
        LLMModel.FABLE_5: (0, 0, 0),
        LLMModel.OPUS_5_5: (40, 40_000, 8_000),
        LLMModel.OPUS_5: (40, 40_000, 8_000),
        LLMModel.SONNET_5: (40, 40_000, 8_000),
    },
    "enterprise": {
        LLMModel.FABLE_5_1: (4_000, 4_000_000, 800_000),
        LLMModel.FABLE_5: (4_000, 4_000_000, 800_000),
        LLMModel.OPUS_5_5: (10_000, 10_000_000, 2_000_000),
        LLMModel.OPUS_5: (10_000, 10_000_000, 2_000_000),
        LLMModel.SONNET_5: (10_000, 10_000_000, 2_000_000),
    },
    "global": {
        LLMModel.FABLE_5_1: (2_000, 20_000_000, 2_000_000),
        LLMModel.FABLE_5: (2_000, 20_000_000, 2_000_000),
        LLMModel.OPUS_5_5: (2_000, 20_000_000, 2_000_000),
        LLMModel.OPUS_5: (2_000, 20_000_000, 2_000_000),
        LLMModel.SONNET_5: (2_500, 25_000_000, 2_500_000),
    },
    "multi_region": {
        LLMModel.FABLE_5_1: (1_000, 10_000_000, 1_000_000),
        LLMModel.FABLE_5: (1_000, 10_000_000, 1_000_000),
        LLMModel.OPUS_5_5: (1_000, 10_000_000, 1_000_000),
        LLMModel.OPUS_5: (1_000, 10_000_000, 1_000_000),
        LLMModel.SONNET_5: (1_250, 12_500_000, 1_250_000),
    },
    # Bedrock publishes no per-account quota for any of these models.
    "mantle": {},
}

# Per-(plan, model) extra notes.
_EXTRA_NOTES: dict[tuple[str, LLMModel], list[str]] = {}
for _plan in ("start", "build", "scale"):
    for _m in (LLMModel.FABLE_5_1, LLMModel.FABLE_5):
        _EXTRA_NOTES[(_plan, _m)] = [_SHARED_FABLE]
for _m in (LLMModel.FABLE_5_1, LLMModel.FABLE_5):
    for _plan in ("global", "multi_region"):
        _EXTRA_NOTES[(_plan, _m)] = [_SHARED_FABLE + "（共用 anthropic-claude-fable 沿襲配額）"]
    _EXTRA_NOTES[("payg", _m)] = [
        "隨用隨付訂閱的 Fable 預設配額為 0，部署前必須先申請",
        "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本",
    ]
    _EXTRA_NOTES[("enterprise", _m)] = [
        "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本"
    ]
for _plan in ("global", "multi_region"):
    _EXTRA_NOTES[(_plan, LLMModel.OPUS_5_5)] = [
        "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"
    ]
    _EXTRA_NOTES[(_plan, LLMModel.OPUS_5)] = [
        "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"
    ]
    _EXTRA_NOTES[(_plan, LLMModel.SONNET_5)] = [
        "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"
    ]
_EXTRA_NOTES[("payg", LLMModel.OPUS_5_5)] = [
    "隨用隨付的預設額度偏低，正式上線前通常仍需申請調升"
]
_EXTRA_NOTES[("payg", LLMModel.OPUS_5)] = [
    "隨用隨付的預設額度偏低，正式上線前通常仍需申請調升"
]
_EXTRA_NOTES[("payg", LLMModel.SONNET_5)] = [
    "隨用隨付的預設額度偏低，正式上線前通常仍需申請調升"
]


def _build_plans() -> list[QuotaPlan]:
    plans: list[QuotaPlan] = []
    for model_info in _MODELS:
        model = model_info.model
        for (platform, plan_id, p_label, plan_label, source, reserves, base_notes) in _PLAN_SHAPES:
            quotas = _QUOTAS[plan_id].get(model)
            if quotas is None:
                rpm, itpm, otpm = _NO_RPM, _NO_TPM, _NO_TPM
            else:
                rpm, itpm, otpm = (_en(quotas[0]), _en(quotas[1]), _en(quotas[2]))
            plans.append(
                QuotaPlan(
                    model=model,
                    model_label=model_info.label,
                    platform=platform,
                    plan_id=plan_id,
                    platform_label=p_label,
                    plan_label=plan_label,
                    rpm=rpm,
                    itpm=itpm,
                    otpm=otpm,
                    reserves_max_tokens=reserves,
                    notes=_EXTRA_NOTES.get((plan_id, model), []) + list(base_notes),
                    source=source,
                )
            )
    return plans


_PLANS: list[QuotaPlan] = _build_plans()


def list_plans(
    model: Optional[LLMModel] = None, platform: Optional[LLMPlatform] = None
) -> list[QuotaPlan]:
    """The quota table, optionally narrowed to one model and/or platform."""
    out = _PLANS
    if model is not None:
        out = [p for p in out if p.model == model]
    if platform is not None:
        out = [p for p in out if p.platform == platform]
    return list(out)

# ---------------------------------------------------------------------------
# Usage scenarios
# ---------------------------------------------------------------------------
#
# A salesperson knows "500 客服人員，每人一天用 10 次". They do not know how
# many tokens their prompt is, and nobody reasons in requests per minute. These
# profiles carry the token shape so the form can ask only what a customer can
# actually answer, and derive the rest.
#
# The token figures are PLANNING ESTIMATES for sizing conversations, not
# measurements of any particular deployment. Every one of them is editable in
# the advanced panel, and a real deployment should replace them with counts
# from the token counting endpoint.


class UsageScenario(BaseModel):
    """A recognisable deployment shape with a typical token profile."""

    scenario_id: str
    label: str
    blurb: str
    icon: str
    input_tokens_per_request: int
    output_tokens_per_request: int
    #: Share of the prompt that is a fixed, cacheable prefix.
    cache_hit_rate: float
    #: Must cover visible output AND thinking: thinking counts toward max_tokens.
    max_tokens: int
    #: The model this shape usually starts on.
    suggested_model: LLMModel
    #: Messages per user per day, as a starting point.
    messages_per_user_per_day: float
    #: Thinking tokens per request at effort "high". Every modelled model thinks
    #: by default and bills thinking as output, so leaving this out would
    #: understate the most expensive token type. PLANNING ESTIMATE: calibrate
    #: against `usage.output_tokens` from a few real requests.
    thinking_tokens_per_request: int = 0
    #: Effort level this shape usually runs at.
    default_effort: str = "high"
    #: Work that can wait for an asynchronous result (Batch API, 50% off).
    batch_friendly: bool = False


_SCENARIOS: list[UsageScenario] = [
    UsageScenario(
        scenario_id="support",
        label="客服對話",
        blurb="固定話術 + 短問答，前綴幾乎每次相同",
        icon="&#128172;",
        input_tokens_per_request=4_000,
        output_tokens_per_request=500,
        cache_hit_rate=0.60,
        max_tokens=3_000,
        suggested_model=LLMModel.SONNET_5,
        messages_per_user_per_day=12,
        thinking_tokens_per_request=800,
        default_effort="medium",
    ),
    UsageScenario(
        scenario_id="rag",
        label="知識庫問答",
        blurb="每次帶入檢索到的文件片段，提示詞偏長",
        icon="&#128218;",
        input_tokens_per_request=20_000,
        output_tokens_per_request=2_000,
        cache_hit_rate=0.50,
        max_tokens=8_000,
        suggested_model=LLMModel.SONNET_5,
        messages_per_user_per_day=8,
        thinking_tokens_per_request=2_500,
        default_effort="high",
    ),
    UsageScenario(
        scenario_id="summarize",
        label="文件摘要",
        blurb="一次讀入整份文件，輸出精簡，快取效益低",
        icon="&#128196;",
        input_tokens_per_request=30_000,
        output_tokens_per_request=1_500,
        cache_hit_rate=0.15,
        max_tokens=6_000,
        suggested_model=LLMModel.SONNET_5,
        messages_per_user_per_day=4,
        thinking_tokens_per_request=1_500,
        default_effort="medium",
        batch_friendly=True,
    ),
    UsageScenario(
        scenario_id="coding",
        label="程式開發代理",
        blurb="長對話多輪工具呼叫，前綴長但高度可快取",
        icon="&#129302;",
        input_tokens_per_request=60_000,
        output_tokens_per_request=8_000,
        cache_hit_rate=0.80,
        max_tokens=32_000,
        suggested_model=LLMModel.FABLE_5_1,
        messages_per_user_per_day=60,
        thinking_tokens_per_request=6_000,
        default_effort="xhigh",
    ),
    UsageScenario(
        scenario_id="writing",
        label="內容生成",
        blurb="提示詞短、產出長，成本集中在 Output",
        icon="&#9998;",
        input_tokens_per_request=2_000,
        output_tokens_per_request=4_000,
        cache_hit_rate=0.25,
        max_tokens=12_000,
        suggested_model=LLMModel.OPUS_5,
        messages_per_user_per_day=6,
        thinking_tokens_per_request=2_000,
        default_effort="high",
    ),
]

_SCENARIO_BY_ID = {s.scenario_id: s for s in _SCENARIOS}


def list_scenarios() -> list[UsageScenario]:
    return list(_SCENARIOS)


def get_scenario(scenario_id: str) -> UsageScenario:
    return _SCENARIO_BY_ID[scenario_id]


# How sharply a day's traffic piles into the busiest minute. Quota is a
# per-minute ceiling, so this factor is what decides whether a deployment is
# throttled — it matters more than the daily total.
PEAK_FACTORS: dict[str, float] = {
    "flat": 1.5,      # 背景批次、排程作業
    "normal": 3.0,    # 一般上班時間使用
    "spiky": 6.0,     # 活動檔期、早會後、上課時間
}

# How much of a scenario's "high" thinking estimate each effort level spends.
# Relative planning factors, not published figures: effort changes how much
# the model thinks, and the only reliable number is a measured one.
EFFORT_THINKING_FACTORS: dict[str, float] = {
    "low": 0.25,
    "medium": 0.5,
    "high": 1.0,
    "xhigh": 1.5,
}

#: Batch API list-price discount on input and output (first-party).
BATCH_DISCOUNT = 0.50

#: Hours per day over which the daily volume is assumed to be spread.
ACTIVE_HOURS_PER_DAY = 8

#: Working days per month, used for the monthly volume suggestion.
WORKING_DAYS_PER_MONTH = 22
