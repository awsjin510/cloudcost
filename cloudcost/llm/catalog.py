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

VERIFIED = "2026-09-29"

#: Maximum output tokens for every model modelled here.
MAX_OUTPUT_TOKENS = 128_000

SRC_PRICING = "https://platform.claude.com/docs/en/about-claude/pricing"
SRC_ANTHROPIC = "https://platform.claude.com/docs/en/api/rate-limits"
SRC_BEDROCK = "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html"
#: The authoritative per-model Bedrock defaults (Mantle and runtime) live in the
#: General Reference, not the user guide, which lists only Opus 4.7.
SRC_BEDROCK_GR = "https://docs.aws.amazon.com/general/latest/gr/bedrock.html"
SRC_BEDROCK_BURNDOWN = "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html"
SRC_OPENAI_PRICING = "https://developers.openai.com/api/docs/pricing"
SRC_OPENAI_MODELS = "https://developers.openai.com/api/docs/models"
SRC_OPENAI_RATE = "https://developers.openai.com/api/docs/guides/rate-limits"
SRC_AZURE_OPENAI = "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits"
SRC_GEMINI_PRICING = "https://ai.google.dev/gemini-api/docs/pricing"
SRC_GEMINI_RATE = "https://ai.google.dev/gemini-api/docs/rate-limits"
SRC_VERTEX_PAYGO = "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo"
SRC_XAI_MODELS = "https://docs.x.ai/developers/models"
SRC_XAI_RATE = "https://docs.x.ai/developers/rate-limits"
SRC_AZURE_GROK = "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok"
SRC_VERTEX_GROK = "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/grok"
SRC_OCI_GROK = "https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm"
SRC_BEDROCK_GROK = "https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-xai-grok-4-6.html"
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
    SONNET_5_5 = "sonnet-5-5"
    SONNET_5 = "sonnet-5"
    OPUS_4_8 = "opus-4-8"
    SONNET_4_6 = "sonnet-4-6"
    HAIKU_4_5 = "haiku-4-5"
    GPT_6_ASTRA = "gpt-6-astra"
    GPT_6_SOL = "gpt-6-sol"
    GPT_6_LUNA = "gpt-6-luna"
    GPT_5_6_SOL = "gpt-5.6-sol"
    GPT_5_6_TERRA = "gpt-5.6-terra"
    GPT_5_6_LUNA = "gpt-5.6-luna"
    GPT_5_5 = "gpt-5.5"
    GEMINI_3_1_PRO = "gemini-3.1-pro-preview"
    GEMINI_3_8_FLASH = "gemini-3.8-flash"
    GEMINI_3_5_FLASH_LITE = "gemini-3.5-flash-lite"
    GEMINI_3_1_FLASH_LITE = "gemini-3.1-flash-lite"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GROK_4_7 = "grok-4.7"
    GROK_4_6 = "grok-4.6"
    GROK_4_5 = "grok-4.5"
    GROK_4_3 = "grok-4.3"
    GROK_4_20_REASONING = "grok-4.20-0309-reasoning"
    GROK_4_20_NON_REASONING = "grok-4.20-0309-non-reasoning"
    GROK_BUILD_0_1 = "grok-build-0.1"


class LLMPlatform(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE_AI = "google_ai"
    BEDROCK = "bedrock"
    FOUNDRY = "foundry"
    VERTEX = "vertex"
    XAI = "xai"
    OCI = "oci"


class ModelLine(str, Enum):
    """A vendor's product line — the first choice in the model picker."""

    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    GROK = "grok"


class LineInfo(BaseModel):
    line: ModelLine
    label: str
    vendor: str
    #: Where the catalogue's list price comes from, stated on every estimate.
    price_caveat: str
    #: Whether this vendor's usage "input" count already includes cached tokens,
    #: which decides how measured usage is split when calibrating.
    usage_input_includes_cache: bool = True
    #: How the vendor's usage fields map onto the calibration form.
    usage_hint: str = ""


_LINES: dict[ModelLine, LineInfo] = {
    ModelLine.CLAUDE: LineInfo(
        line=ModelLine.CLAUDE, label="Claude", vendor="Anthropic",
        price_caveat="以 Anthropic 官方第一方定價計算。Claude in Microsoft Foundry 同樣採標準 API 費率"
        "（以 CCU 計價開立帳單）；Amazon Bedrock 與 Google Vertex 為合作夥伴自訂定價，"
        "實際金額請以該平台價目表為準",
        usage_input_includes_cache=False,
        usage_hint="Anthropic 的 Input（input_tokens）不含快取，快取讀取（cache_read_input_tokens）與寫入"
        "（cache_creation_input_tokens）另列；Output（output_tokens）已含思考",
    ),
    ModelLine.GPT: LineInfo(
        line=ModelLine.GPT, label="GPT", vendor="OpenAI",
        price_caveat="以 OpenAI 官方 API 牌價計算。Azure OpenAI Global Standard 與 Bedrock 全域跨區推論"
        "同樣採 OpenAI 牌價；Azure Data Zone 與 Bedrock 區域內推論另加 10%",
        usage_hint="OpenAI 的 Input（input_tokens）已包含快取讀取（cached_tokens）；Output（output_tokens）已含推理",
    ),
    ModelLine.GEMINI: LineInfo(
        line=ModelLine.GEMINI, label="Gemini", vendor="Google",
        price_caveat="以 Gemini API 付費層牌價計算，與 Vertex 全域端點價格相同；Vertex 區域端點另加 10%。"
        "Gemini 的明確快取另按儲存時數收費，此處未計入",
        usage_hint="Gemini 的 Input（promptTokenCount）已包含快取（cachedContentTokenCount）；"
        "思考（thoughtsTokenCount）不含在 Output 中，請另填在「思考」欄",
    ),
    ModelLine.GROK: LineInfo(
        line=ModelLine.GROK, label="Grok", vendor="xAI",
        price_caveat="以 xAI 官方 API 牌價計算。Bedrock 全域跨區、Azure Global Standard、Vertex 全域端點與 "
        "OCI 標準處理同樣採 xAI 牌價；Bedrock 區域內與 Azure Data Zone 另加 10%，OCI 優先處理（priority）為兩倍",
        usage_hint="xAI 的 Input（prompt_tokens）已包含快取（cached_tokens）；若主控台把推理（reasoning_tokens）"
        "與 Output 分開列出，請另填在「思考」欄",
    ),
}


def list_lines() -> list[LineInfo]:
    """Lines that have at least one modelled model, in display order."""
    present = {m.line for m in _MODELS}
    return [info for line, info in _LINES.items() if line in present]


def get_line(line: ModelLine) -> LineInfo:
    return _LINES[line]


#: Capability classes, most to least capable. Scenarios name a class and the
#: picker resolves it to a concrete version within whichever line is chosen.
MODEL_CLASSES = ("frontier", "strong", "balanced", "fast")


class LimitStatus(str, Enum):
    """Why a limit does or does not carry a number."""

    ENFORCED = "enforced"
    NOT_ENFORCED = "not_enforced"
    UNPUBLISHED = "unpublished"


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------


class ModelPricing(BaseModel):
    """USD per million tokens at the vendor's own first-party list price."""

    input_per_mtok: float
    output_per_mtok: float
    #: Price of an input token served from the prompt/context cache.
    cache_read_per_mtok: float
    #: Explicit cache-write premium, where the vendor charges one.
    cache_write_5m_per_mtok: Optional[float] = None
    #: Some vendors bill the whole request at a higher rate once the prompt
    #: exceeds a length threshold.
    long_context_threshold: Optional[int] = None
    long_input_per_mtok: Optional[float] = None
    long_output_per_mtok: Optional[float] = None
    long_cache_read_per_mtok: Optional[float] = None
    #: True when the long rate starts at the threshold itself ("reaches 200K")
    #: rather than above it ("> 200K").
    long_context_inclusive: bool = False
    #: Batch API discount on list price; None when the model has no Batch API.
    batch_discount: Optional[float] = 0.50

    def is_long(self, prompt_tokens: int) -> bool:
        if self.long_context_threshold is None:
            return False
        if self.long_context_inclusive:
            return prompt_tokens >= self.long_context_threshold
        return prompt_tokens > self.long_context_threshold

    def rates_for(self, prompt_tokens: int) -> tuple[float, float, float]:
        """(input, output, cache read) for a request of this prompt size."""
        if self.is_long(prompt_tokens):
            return (
                self.long_input_per_mtok if self.long_input_per_mtok is not None else self.input_per_mtok,
                self.long_output_per_mtok if self.long_output_per_mtok is not None else self.output_per_mtok,
                self.long_cache_read_per_mtok if self.long_cache_read_per_mtok is not None else self.cache_read_per_mtok,
            )
        return self.input_per_mtok, self.output_per_mtok, self.cache_read_per_mtok


class ModelInfo(BaseModel):
    model: LLMModel
    label: str
    line: ModelLine = ModelLine.CLAUDE
    #: Short label for the version picker, e.g. "Opus 5.5".
    version_label: str = ""
    #: One of MODEL_CLASSES; lets a scenario name "a balanced model" and get
    #: the right version in whichever line the user picked.
    model_class: str = "balanced"
    #: Capability tier within the line (higher = more capable). Used so a
    #: quota workaround never silently trades capability for price.
    tier: int
    pricing: ModelPricing
    notes: list[str] = Field(default_factory=list)

    @property
    def api_id(self) -> str:
        """The vendor's own API model ID, e.g. ``claude-opus-5-5``."""
        return f"claude-{self.model.value}" if self.line is ModelLine.CLAUDE else self.model.value


_MODELS: list[ModelInfo] = [
    ModelInfo(
        model=LLMModel.FABLE_5_1,
        version_label="Fable 5.1",
        model_class="frontier",
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
        version_label="Fable 5",
        model_class="frontier",
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
        version_label="Opus 5.5",
        model_class="strong",
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
        version_label="Opus 5",
        model_class="strong",
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
        model=LLMModel.SONNET_5_5,
        version_label="Sonnet 5.5",
        model_class="balanced",
        label="Claude Sonnet 5.5",
        tier=1,
        pricing=ModelPricing(
            input_per_mtok=2.0,
            output_per_mtok=10.0,
            cache_read_per_mtok=0.20,
            cache_write_5m_per_mtok=2.50,
        ),
        notes=["目前的 Sonnet，高流量生產工作負載的預設選擇，單價與 Sonnet 5 相同、為 Fable 的五分之一",
               "與 Sonnet 5 各自獨立計算配額"],
    ),
    ModelInfo(
        model=LLMModel.SONNET_5,
        version_label="Sonnet 5",
        model_class="balanced",
        label="Claude Sonnet 5",
        tier=1,
        pricing=ModelPricing(
            input_per_mtok=2.0,
            output_per_mtok=10.0,
            cache_read_per_mtok=0.20,
            cache_write_5m_per_mtok=2.50,
        ),
        notes=["前一代 Sonnet，單價與 Sonnet 5.5 相同；新專案建議直接評估 Sonnet 5.5"],
    ),
]

# Claude 4.x, verified 2026-09-29 against pricing.md.
_MODELS += [
    ModelInfo(
        model=LLMModel.OPUS_4_8, label="Claude Opus 4.8", version_label="Opus 4.8",
        model_class="strong", tier=2,
        pricing=ModelPricing(input_per_mtok=5.0, output_per_mtok=25.0,
                             cache_read_per_mtok=0.50, cache_write_5m_per_mtok=6.25),
        notes=["前一代 Opus，單價與 Opus 5 相同；新專案建議直接評估 Opus 5.5"],
    ),
    ModelInfo(
        model=LLMModel.SONNET_4_6, label="Claude Sonnet 4.6", version_label="Sonnet 4.6",
        model_class="balanced", tier=1,
        pricing=ModelPricing(input_per_mtok=3.0, output_per_mtok=15.0,
                             cache_read_per_mtok=0.30, cache_write_5m_per_mtok=3.75),
        notes=["前一代 Sonnet，單價比 Sonnet 5 高；使用較舊的 tokenizer，同樣文字的 token 數約少三成"],
    ),
    ModelInfo(
        model=LLMModel.HAIKU_4_5, label="Claude Haiku 4.5", version_label="Haiku 4.5",
        model_class="fast", tier=0,
        pricing=ModelPricing(input_per_mtok=1.0, output_per_mtok=5.0,
                             cache_read_per_mtok=0.10, cache_write_5m_per_mtok=1.25),
        notes=["Claude 最便宜的版本，適合高流量的簡單任務；上下文上限 200K"],
    ),
]

# OpenAI GPT and Google Gemini, verified 2026-09-29 (see the plan section for sources).
_MODELS += [
    ModelInfo(
        model=LLMModel.GPT_6_ASTRA, label="GPT-6 Astra", version_label="GPT-6 Astra", line=ModelLine.GPT,
        model_class="frontier", tier=4,
        pricing=ModelPricing(input_per_mtok=10, output_per_mtok=50, cache_read_per_mtok=1, cache_write_5m_per_mtok=12.5,
                             long_context_threshold=272_000, long_input_per_mtok=20, long_output_per_mtok=75, long_cache_read_per_mtok=2),
        notes=['OpenAI 目前最強的旗艦，一律會推理、無法關閉', '提示詞超過 272K tokens 時整筆改按長上下文費率'],
    ),
    ModelInfo(
        model=LLMModel.GPT_6_SOL, label="GPT-6 Sol", version_label="GPT-6 Sol", line=ModelLine.GPT,
        model_class="balanced", tier=3,
        pricing=ModelPricing(input_per_mtok=2, output_per_mtok=10, cache_read_per_mtok=0.2, cache_write_5m_per_mtok=2.5,
                             long_context_threshold=272_000, long_input_per_mtok=4, long_output_per_mtok=15, long_cache_read_per_mtok=0.4),
        notes=['GPT-6 的中階版本，偏重程式與代理工作，預設推理強度 medium'],
    ),
    ModelInfo(
        model=LLMModel.GPT_6_LUNA, label="GPT-6 Luna", version_label="GPT-6 Luna", line=ModelLine.GPT,
        model_class="fast", tier=1,
        pricing=ModelPricing(input_per_mtok=0.1, output_per_mtok=0.5, cache_read_per_mtok=0.01, cache_write_5m_per_mtok=0.125,
                             long_context_threshold=272_000, long_input_per_mtok=0.2, long_output_per_mtok=0.75, long_cache_read_per_mtok=0.02),
        notes=['GPT-6 的低成本、高流量版本'],
    ),
    ModelInfo(
        model=LLMModel.GPT_5_6_SOL, label="GPT-5.6 Sol", version_label="GPT-5.6 Sol", line=ModelLine.GPT,
        model_class="strong", tier=3,
        pricing=ModelPricing(input_per_mtok=4, output_per_mtok=20, cache_read_per_mtok=0.4, cache_write_5m_per_mtok=5,
                             long_context_threshold=272_000, long_input_per_mtok=8, long_output_per_mtok=30, long_cache_read_per_mtok=0.8),
        notes=['前一代旗艦；$4 / $20 為促銷價，官方保證至少維持到 2026-11-21，報價時請留意'],
    ),
    ModelInfo(
        model=LLMModel.GPT_5_6_TERRA, label="GPT-5.6 Terra", version_label="GPT-5.6 Terra", line=ModelLine.GPT,
        model_class="balanced", tier=2,
        pricing=ModelPricing(input_per_mtok=2, output_per_mtok=12, cache_read_per_mtok=0.2, cache_write_5m_per_mtok=2.5,
                             long_context_threshold=272_000, long_input_per_mtok=4, long_output_per_mtok=18, long_cache_read_per_mtok=0.4),
        notes=['相當於舊的 mini 級距'],
    ),
    ModelInfo(
        model=LLMModel.GPT_5_6_LUNA, label="GPT-5.6 Luna", version_label="GPT-5.6 Luna", line=ModelLine.GPT,
        model_class="fast", tier=1,
        pricing=ModelPricing(input_per_mtok=0.2, output_per_mtok=1.2, cache_read_per_mtok=0.02, cache_write_5m_per_mtok=0.25,
                             long_context_threshold=272_000, long_input_per_mtok=0.4, long_output_per_mtok=1.8, long_cache_read_per_mtok=0.04),
        notes=['相當於舊的 nano 級距'],
    ),
    ModelInfo(
        model=LLMModel.GPT_5_5, label="GPT-5.5", version_label="GPT-5.5", line=ModelLine.GPT,
        model_class="strong", tier=3,
        pricing=ModelPricing(input_per_mtok=5, output_per_mtok=30, cache_read_per_mtok=0.5,
                             long_context_threshold=272_000, long_input_per_mtok=10, long_output_per_mtok=45, long_cache_read_per_mtok=1),
        notes=['較舊但仍常用的旗艦，沒有快取寫入費'],
    ),
    ModelInfo(
        model=LLMModel.GEMINI_3_1_PRO, label="Gemini 3.1 Pro", version_label="3.1 Pro (Preview)", line=ModelLine.GEMINI,
        model_class="frontier", tier=3,
        pricing=ModelPricing(input_per_mtok=2, output_per_mtok=12, cache_read_per_mtok=0.2,
                             long_context_threshold=200_000, long_input_per_mtok=4, long_output_per_mtok=18, long_cache_read_per_mtok=0.4),
        notes=['目前唯一的 Pro，仍為 Preview 且沒有免費層', '提示詞超過 200K tokens 時整筆改按長上下文費率'],
    ),
    ModelInfo(
        model=LLMModel.GEMINI_3_8_FLASH, label="Gemini 3.8 Flash", version_label="3.8 Flash", line=ModelLine.GEMINI,
        model_class="balanced", tier=2,
        pricing=ModelPricing(input_per_mtok=0.75, output_per_mtok=3.75, cache_read_per_mtok=0.075),
        notes=['此價格維持到 2026-12-31；2027-01-01 起調為 $1.50 / $7.50，年約報價請特別留意'],
    ),
    ModelInfo(
        model=LLMModel.GEMINI_3_5_FLASH_LITE, label="Gemini 3.5 Flash-Lite", version_label="3.5 Flash-Lite", line=ModelLine.GEMINI,
        model_class="fast", tier=1,
        pricing=ModelPricing(input_per_mtok=0.3, output_per_mtok=2.5, cache_read_per_mtok=0.03),
        notes=['Google 建議新專案使用的輕量版本之一，思考預設為最低'],
    ),
    ModelInfo(
        model=LLMModel.GEMINI_3_1_FLASH_LITE, label="Gemini 3.1 Flash-Lite", version_label="3.1 Flash-Lite", line=ModelLine.GEMINI,
        model_class="fast", tier=1,
        pricing=ModelPricing(input_per_mtok=0.25, output_per_mtok=1.5, cache_read_per_mtok=0.025),
        notes=['目前最便宜的 Gemini；音訊輸入另計 $0.50'],
    ),
    ModelInfo(
        model=LLMModel.GEMINI_2_5_PRO, label="Gemini 2.5 Pro", version_label="2.5 Pro", line=ModelLine.GEMINI,
        model_class="frontier", tier=3,
        pricing=ModelPricing(input_per_mtok=1.25, output_per_mtok=10, cache_read_per_mtok=0.125,
                             long_context_threshold=200_000, long_input_per_mtok=2.5, long_output_per_mtok=15, long_cache_read_per_mtok=0.25),
        notes=['前一代 Pro，僅限過去用過的專案使用，新專案無法啟用'],
    ),
    ModelInfo(
        model=LLMModel.GEMINI_2_5_FLASH, label="Gemini 2.5 Flash", version_label="2.5 Flash", line=ModelLine.GEMINI,
        model_class="balanced", tier=2,
        pricing=ModelPricing(input_per_mtok=0.3, output_per_mtok=2.5, cache_read_per_mtok=0.03),
        notes=['前一代 Flash，僅限過去用過的專案使用，新專案無法啟用'],
    ),
]

# xAI Grok, verified 2026-09-29 against docs.x.ai models and per-model pages.
_MODELS += [
    ModelInfo(
        model=LLMModel.GROK_4_7, label="Grok 4.7", version_label="Grok 4.7", line=ModelLine.GROK,
        model_class="frontier", tier=4,
        pricing=ModelPricing(input_per_mtok=2, output_per_mtok=6, cache_read_per_mtok=0.5,
                             long_context_threshold=200_000, long_context_inclusive=True,
                             long_input_per_mtok=4, long_output_per_mtok=12,
                             long_cache_read_per_mtok=1, batch_discount=None),
        notes=['xAI 目前最強的模型，官方建議程式與一般對話都用它；一律會推理，預設推理強度 high', '不支援 Batch API；提示詞達 200K tokens 時整筆改按兩倍費率'],
    ),
    ModelInfo(
        model=LLMModel.GROK_4_6, label="Grok 4.6", version_label="Grok 4.6", line=ModelLine.GROK,
        model_class="strong", tier=3,
        pricing=ModelPricing(input_per_mtok=2, output_per_mtok=6, cache_read_per_mtok=0.5,
                             long_context_threshold=200_000, long_context_inclusive=True,
                             long_input_per_mtok=4, long_output_per_mtok=12,
                             long_cache_read_per_mtok=1, batch_discount=None),
        notes=['前一代旗艦，單價與 4.7 相同；新專案建議直接評估 4.7', '目前唯一同時上架 Bedrock、Azure、Vertex 與 OCI 的 Grok'],
    ),
    ModelInfo(
        model=LLMModel.GROK_4_5, label="Grok 4.5", version_label="Grok 4.5", line=ModelLine.GROK,
        model_class="strong", tier=3,
        pricing=ModelPricing(input_per_mtok=2, output_per_mtok=6, cache_read_per_mtok=0.3,
                             long_context_threshold=200_000, long_context_inclusive=True,
                             long_input_per_mtok=4, long_output_per_mtok=12,
                             long_cache_read_per_mtok=0.6, batch_discount=None),
        notes=['偏重程式與代理工作，快取讀取比 4.6／4.7 便宜（$0.30）', '只在 xAI API 提供'],
    ),
    ModelInfo(
        model=LLMModel.GROK_4_3, label="Grok 4.3", version_label="Grok 4.3", line=ModelLine.GROK,
        model_class="balanced", tier=2,
        pricing=ModelPricing(input_per_mtok=1.25, output_per_mtok=2.5, cache_read_per_mtok=0.2,
                             long_context_threshold=200_000, long_context_inclusive=True,
                             long_input_per_mtok=2.5, long_output_per_mtok=5,
                             long_cache_read_per_mtok=0.4, batch_discount=0.2),
        notes=['1M context，推理強度可設 none 到 xhigh（預設 low）', '支援 Batch API，打八折'],
    ),
    ModelInfo(
        model=LLMModel.GROK_4_20_REASONING, label="Grok 4.20 Reasoning", version_label="Grok 4.20 Reasoning", line=ModelLine.GROK,
        model_class="balanced", tier=2,
        pricing=ModelPricing(input_per_mtok=1.25, output_per_mtok=2.5, cache_read_per_mtok=0.2,
                             long_context_threshold=200_000, long_context_inclusive=True,
                             long_input_per_mtok=2.5, long_output_per_mtok=5,
                             long_cache_read_per_mtok=0.4, batch_discount=0.2),
        notes=['單價與 4.3 相同；xAI 官方建議新專案改用 4.3', '支援 Batch API，打八折'],
    ),
    ModelInfo(
        model=LLMModel.GROK_4_20_NON_REASONING, label="Grok 4.20 Non-reasoning", version_label="Grok 4.20 Non-reasoning", line=ModelLine.GROK,
        model_class="fast", tier=1,
        pricing=ModelPricing(input_per_mtok=1.25, output_per_mtok=2.5, cache_read_per_mtok=0.2,
                             long_context_threshold=200_000, long_context_inclusive=True,
                             long_input_per_mtok=2.5, long_output_per_mtok=5,
                             long_cache_read_per_mtok=0.4, batch_discount=0.2),
        notes=['不推理、延遲最低，適合分類與摘要這類大量簡單工作', '支援 Batch API，打八折'],
    ),
    ModelInfo(
        model=LLMModel.GROK_BUILD_0_1, label="Grok Build 0.1", version_label="Grok Build 0.1", line=ModelLine.GROK,
        model_class="fast", tier=1,
        pricing=ModelPricing(input_per_mtok=1, output_per_mtok=2, cache_read_per_mtok=0.2,
                             long_context_threshold=200_000, long_context_inclusive=True,
                             long_input_per_mtok=2, long_output_per_mtok=4,
                             long_cache_read_per_mtok=0.4, batch_discount=None),
        notes=['xAI 的程式專用模型（取代已退役的 grok-code-fast-1），也是最便宜的 Grok', '256K context，只在 xAI API 提供'],
    ),
]

_MODEL_BY_ID = {m.model: m for m in _MODELS}


def list_models(line: Optional[ModelLine] = None) -> list[ModelInfo]:
    """Modelled models, optionally one line's, newest first within a line."""
    return [m for m in _MODELS if line is None or m.line is line]


def model_for(line: ModelLine, model_class: str) -> LLMModel:
    """The first model of `model_class` in `line`, or the nearest class."""
    candidates = list_models(line)
    if not candidates:
        raise KeyError(line)
    want = MODEL_CLASSES.index(model_class) if model_class in MODEL_CLASSES else 2
    ranked = sorted(
        candidates,
        key=lambda m: (abs(MODEL_CLASSES.index(m.model_class) - want),
                       MODEL_CLASSES.index(m.model_class) > want,
                       candidates.index(m)),
    )
    return ranked[0].model


def get_model(model: LLMModel) -> ModelInfo:
    return _MODEL_BY_ID[model]


# ---------------------------------------------------------------------------
# Quota
# ---------------------------------------------------------------------------


class Limit(BaseModel):
    """One quota dimension (RPM, ITPM, OTPM, ...) for one plan."""

    status: LimitStatus
    value: Optional[float] = Field(
        default=None, description="Published ceiling per minute; None unless enforced"
    )
    #: A baseline the platform may exceed on a best-effort basis, not a hard cap.
    soft: bool = False
    note: str = ""


def _en(value: float) -> Limit:
    return Limit(status=LimitStatus.ENFORCED, value=value)


_NO_RPM = Limit(
    status=LimitStatus.NOT_ENFORCED,
    note="Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流",
)
_NO_RPM_RUNTIME = Limit(
    status=LimitStatus.NOT_ENFORCED,
    note="AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流",
)
_NO_TPM = Limit(
    status=LimitStatus.UNPUBLISHED,
    note="AWS 配額總表未列出此模型的預設值，實際額度依帳號而定",
)

_SHARED_FABLE = "Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍"
_SHARED_OPUS4 = "Opus 4.x 各版本（4.8／4.7／4.6／4.5）共用同一個額度"
_SHARED_SONNET4 = "Sonnet 4.x 各版本（4.6／4.5）共用同一個額度"
_LINEAGE = "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"
_PAYG_LOW = "隨用隨付的預設額度偏低，正式上線前通常仍需申請調升"


class QuotaPlan(BaseModel):
    """One platform's default quota for one model under one purchasing option.

    Platforms meter differently, so every dimension is optional and a plan
    carries only the ones its platform enforces:

    rpm   requests per minute
    itpm  input tokens per minute
    otpm  output tokens per minute (thinking included)
    tpm   input + output tokens per minute, as one combined ceiling
    rpd   requests per day
    """

    model: LLMModel
    model_label: str
    platform: LLMPlatform
    plan_id: str
    platform_label: str
    plan_label: str
    rpm: Optional[Limit] = None
    itpm: Optional[Limit] = None
    otpm: Optional[Limit] = None
    tpm: Optional[Limit] = None
    rpd: Optional[Limit] = None
    #: Spend ceiling in USD per rolling 10 minutes (Gemini Developer API).
    usd10m: Optional[Limit] = None
    #: Bedrock Mantle admits on input + max_tokens rather than input alone.
    reserves_max_tokens: bool = False
    #: Combined TPM is charged on max_tokens at admission, not actual output.
    tpm_reserves_max_tokens: bool = False
    #: Whether cache reads count toward input-based limits on this platform.
    input_cached_counts: bool = False
    #: Output tokens consume this many units of a combined TPM quota.
    output_burndown: float = 1.0
    #: Whether the model's catalogue (first-party) price applies here.
    list_priced: bool = True
    notes: list[str] = Field(default_factory=list)
    source: str
    verified: str = VERIFIED


_PLANS: list[QuotaPlan] = []


def _add(model: LLMModel, platform: LLMPlatform, plan_id: str, platform_label: str,
         plan_label: str, source: str, notes=(), **kw) -> None:
    _PLANS.append(QuotaPlan(
        model=model, model_label=_MODEL_BY_ID[model].label, platform=platform,
        plan_id=plan_id, platform_label=platform_label, plan_label=plan_label,
        source=source, notes=list(notes), **kw,
    ))


def _en3(values) -> dict:
    return {"rpm": _en(values[0]), "itpm": _en(values[1]), "otpm": _en(values[2])}


# ---------------------------------------------------------------------------
# Claude
# ---------------------------------------------------------------------------

_CLAUDE_ORDER = (
    LLMModel.FABLE_5_1, LLMModel.FABLE_5, LLMModel.OPUS_5_5, LLMModel.OPUS_5,
    LLMModel.SONNET_5_5, LLMModel.SONNET_5, LLMModel.OPUS_4_8, LLMModel.SONNET_4_6, LLMModel.HAIKU_4_5,
)
_FABLE = (LLMModel.FABLE_5_1, LLMModel.FABLE_5)

# Anthropic API: (rpm, itpm, otpm) per tier.
_CLAUDE_TIERS = {
    **{m: {"start": (1_000, 500_000, 100_000), "build": (2_000, 1_500_000, 300_000),
           "scale": (4_000, 4_000_000, 800_000)} for m in _FABLE},
    **{m: {"start": (1_000, 2_000_000, 400_000), "build": (5_000, 5_000_000, 1_000_000),
           "scale": (10_000, 10_000_000, 2_000_000)} for m in _CLAUDE_ORDER if m not in _FABLE},
}
_CLAUDE_TIER_NOTES = {
    LLMModel.FABLE_5_1: [_SHARED_FABLE], LLMModel.FABLE_5: [_SHARED_FABLE],
    LLMModel.OPUS_4_8: [_SHARED_OPUS4], LLMModel.SONNET_4_6: [_SHARED_SONNET4],
}

# Foundry Global Standard: ((payg rpm, itpm, otpm), (enterprise rpm, itpm, otpm)).
_CLAUDE_FOUNDRY = {
    LLMModel.FABLE_5_1: ((0, 0, 0), (4_000, 4_000_000, 800_000)),
    LLMModel.FABLE_5: ((0, 0, 0), (4_000, 4_000_000, 800_000)),
    LLMModel.OPUS_5_5: ((40, 40_000, 8_000), (10_000, 10_000_000, 2_000_000)),
    LLMModel.OPUS_5: ((40, 40_000, 8_000), (10_000, 10_000_000, 2_000_000)),
    LLMModel.SONNET_5_5: ((40, 40_000, 8_000), (10_000, 10_000_000, 2_000_000)),
    LLMModel.SONNET_5: ((40, 40_000, 8_000), (10_000, 10_000_000, 2_000_000)),
    LLMModel.OPUS_4_8: ((40, 40_000, 8_000), (10_000, 10_000_000, 2_000_000)),
    LLMModel.SONNET_4_6: ((80, 80_000, 16_000), (10_000, 10_000_000, 2_000_000)),
    LLMModel.HAIKU_4_5: ((80, 80_000, 16_000), (10_000, 10_000_000, 2_000_000)),
}

# Vertex: ((global qpm, input tpm, output tpm), (multi-region ...) or None).
_CLAUDE_VERTEX = {
    LLMModel.FABLE_5_1: ((2_000, 20_000_000, 2_000_000), (1_000, 10_000_000, 1_000_000)),
    LLMModel.FABLE_5: ((2_000, 20_000_000, 2_000_000), (1_000, 10_000_000, 1_000_000)),
    LLMModel.OPUS_5_5: ((2_000, 20_000_000, 2_000_000), (1_000, 10_000_000, 1_000_000)),
    LLMModel.OPUS_5: ((2_000, 20_000_000, 2_000_000), (1_000, 10_000_000, 1_000_000)),
    LLMModel.SONNET_5_5: ((2_500, 25_000_000, 2_500_000), (1_250, 12_500_000, 1_250_000)),
    LLMModel.SONNET_5: ((2_500, 25_000_000, 2_500_000), (1_250, 12_500_000, 1_250_000)),
    LLMModel.OPUS_4_8: ((2_000, 20_000_000, 2_000_000), (1_000, 10_000_000, 1_000_000)),
    LLMModel.SONNET_4_6: ((1_500, 1_500_000, 150_000), None),
    LLMModel.HAIKU_4_5: ((2_500, 2_500_000, 250_000), None),
}

# Bedrock, from the AWS General Reference quota table.
# mantle: (itpm, otpm), None = offered but unpublished, "absent" = not offered.
# runtime (global cross-Region profile): (tpm or None = unpublished, rpm or None, output burndown).
_CLAUDE_BEDROCK = {
    LLMModel.FABLE_5_1: ((5_000_000, 500_000), (10_000_000, None, 10.0)),
    LLMModel.FABLE_5: ((2_000_000, 200_000), (4_000_000, None, 10.0)),
    LLMModel.OPUS_5_5: (None, (30_000_000, None, 10.0)),
    LLMModel.OPUS_5: ((20_000_000, 2_000_000), (30_000_000, None, 10.0)),
    LLMModel.SONNET_5_5: (None, (None, None, 10.0)),
    LLMModel.SONNET_5: ((3_000_000, 300_000), (6_000_000, None, 10.0)),
    LLMModel.OPUS_4_8: ((20_000_000, 2_000_000), (30_000_000, None, 15.0)),
    LLMModel.SONNET_4_6: ("absent", (6_000_000, 10_000, 5.0)),
    LLMModel.HAIKU_4_5: (None, (5_000_000, 10_000, 5.0)),
}
#: Models the burndown page does not name yet, and the sibling whose rate we assume.
_BURNDOWN_ASSUMED = {LLMModel.FABLE_5: "Fable 5.1", LLMModel.SONNET_5_5: "Sonnet 5"}

_MANTLE_COMMON = ("准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分",
                  "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃")


def _build_claude() -> None:
    for model in _CLAUDE_ORDER:
        tier_notes = _CLAUDE_TIER_NOTES.get(model, [])
        tiers = _CLAUDE_TIERS[model]
        _add(model, LLMPlatform.ANTHROPIC, "start", "Anthropic API", "Start 層級", SRC_ANTHROPIC,
             (*tier_notes, "限制掛在組織層級，可再往下分配給各 Workspace"), **_en3(tiers["start"]))
        _add(model, LLMPlatform.ANTHROPIC, "build", "Anthropic API", "Build 層級", SRC_ANTHROPIC,
             tuple(tier_notes), **_en3(tiers["build"]))
        _add(model, LLMPlatform.ANTHROPIC, "scale", "Anthropic API", "Scale 層級", SRC_ANTHROPIC,
             (*tier_notes, "需要更高上限請走 Custom 層級洽談"), **_en3(tiers["scale"]))

        mantle, (tpm, rpm, burndown) = _CLAUDE_BEDROCK[model]
        if mantle is None:
            _add(model, LLMPlatform.BEDROCK, "mantle", "AWS Bedrock", "bedrock-mantle 端點", SRC_BEDROCK_GR,
                 (*_MANTLE_COMMON, "AWS 配額總表未列出此模型的 Mantle 預設值，可在 Service Quotas "
                  "主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"),
                 rpm=_NO_RPM, itpm=_NO_TPM, otpm=_NO_TPM, reserves_max_tokens=True, list_priced=False)
        elif mantle != "absent":
            _add(model, LLMPlatform.BEDROCK, "mantle", "AWS Bedrock", "bedrock-mantle 端點", SRC_BEDROCK_GR,
                 (*_MANTLE_COMMON, "數值出自 AWS 配額總表（General Reference），皆可申請調升"),
                 rpm=_NO_RPM, itpm=_en(mantle[0]), otpm=_en(mantle[1]),
                 reserves_max_tokens=True, list_priced=False)
        burn = (f"每 1 個 output token 消耗 {burndown:g} 個配額 token；AWS 未明列此模型，"
                f"比照 {_BURNDOWN_ASSUMED[model]} 估算"
                if model in _BURNDOWN_ASSUMED
                else f"每 1 個 output token 消耗 {burndown:g} 個配額 token（burndown）")
        unpublished = (() if tpm is not None else
                       ("AWS 配額總表尚未列出此模型的 bedrock-runtime 預設值，可在 Service Quotas "
                        "主控台查到本帳號實際額度，並填入上方欄位",))
        _add(model, LLMPlatform.BEDROCK, "runtime", "AWS Bedrock", "bedrock-runtime（全域跨區）", SRC_BEDROCK_GR,
             ("TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算",
              burn, "快取讀取不計入配額", *unpublished),
             rpm=_en(rpm) if rpm is not None else _NO_RPM_RUNTIME, tpm=_en(tpm) if tpm is not None else _NO_TPM,
             tpm_reserves_max_tokens=True, output_burndown=burndown, list_priced=False)

        payg, ent = _CLAUDE_FOUNDRY[model]
        fable = model in _FABLE
        preview = ("Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本",) if fable else ()
        _add(model, LLMPlatform.FOUNDRY, "payg", "Azure Foundry", "隨用隨付 (Global Standard)", SRC_FOUNDRY,
             (("隨用隨付訂閱的 Fable 預設配額為 0，部署前必須先申請", *preview) if fable else (_PAYG_LOW,))
             + ("免費試用訂閱的預設額度同樣為 0",), **_en3(payg))
        _add(model, LLMPlatform.FOUNDRY, "enterprise", "Azure Foundry", "Enterprise / MCA-E (Global Standard)",
             SRC_FOUNDRY, (*preview, "配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"),
             **_en3(ent))

        g, mr = _CLAUDE_VERTEX[model]
        if fable:
            lineage = (_SHARED_FABLE + "（共用 anthropic-claude-fable 沿襲配額）",)
        elif model in (LLMModel.OPUS_5_5, LLMModel.OPUS_5, LLMModel.SONNET_5_5, LLMModel.SONNET_5):
            lineage = (_LINEAGE,)
        elif model is LLMModel.OPUS_4_8:
            lineage = ("Google 同時把 Opus 4.8 列在各模型配額表與共用沿襲配額的範例中，"
                       "實際採哪一種請以主控台為準",)
        else:
            lineage = ("此模型採各模型獨立配額",)
        _add(model, LLMPlatform.VERTEX, "global", "GCP Vertex", "全域端點 (global)", SRC_VERTEX,
             (*lineage, "輸入 TPM 計入未快取與快取寫入的 token"), list_priced=False, **_en3(g))
        if mr is not None:
            _add(model, LLMPlatform.VERTEX, "multi_region", "GCP Vertex", "多區域端點 (us / eu)", SRC_VERTEX,
                 ("多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", *lineage),
                 list_priced=False, **_en3(mr))


_build_claude()


# ---------------------------------------------------------------------------
# OpenAI GPT
# ---------------------------------------------------------------------------
# Verified 2026-09-29: developers.openai.com pricing and per-model pages,
# learn.microsoft.com Azure OpenAI quotas (updated 2026-08-20), AWS General
# Reference and the AWS GPT-6 model card (10x runtime burndown).

# OpenAI API rate limits: {tier: (rpm, tpm)}. Two published profiles.
_GPT_PROFILE_A = {"t1": (500, 500_000), "t3": (5_000, 2_000_000), "t5": (15_000, 40_000_000)}
_GPT_PROFILE_B = {"t1": (500, 500_000), "t3": (5_000, 4_000_000), "t5": (30_000, 180_000_000)}
_GPT_TIERS = {
    LLMModel.GPT_6_ASTRA: _GPT_PROFILE_A, LLMModel.GPT_6_SOL: _GPT_PROFILE_A,
    LLMModel.GPT_6_LUNA: _GPT_PROFILE_B, LLMModel.GPT_5_6_SOL: _GPT_PROFILE_A,
    LLMModel.GPT_5_6_TERRA: _GPT_PROFILE_A, LLMModel.GPT_5_6_LUNA: _GPT_PROFILE_B,
    LLMModel.GPT_5_5: _GPT_PROFILE_A,
}
_GPT_TIER_LABELS = {"t1": ("Tier 1", "累計付款 $5 起"), "t3": ("Tier 3", "累計付款 $100 起"),
                    "t5": ("Tier 5", "累計付款 $1,000 起")}

# Azure OpenAI Global Standard default TPM by quota tier (all seven models).
_AZURE_GPT_TIERS = {"az_t1": ("Tier 1", 1_000_000), "az_t3": ("Tier 3", 4_000_000),
                    "az_t6": ("Tier 6", 15_000_000)}

# Bedrock: mantle (itpm, otpm) / None unpublished / "absent"; runtime tpm or None.
_GPT_BEDROCK = {
    LLMModel.GPT_6_ASTRA: ((1_000_000, 100_000), 4_000_000),
    LLMModel.GPT_6_SOL: (None, 2_000_000),
    LLMModel.GPT_6_LUNA: (None, 4_000_000),
    LLMModel.GPT_5_6_SOL: ((10_000_000, 1_000_000), 10_000_000),
    LLMModel.GPT_5_6_TERRA: ((20_000_000, 2_000_000), 20_000_000),
    LLMModel.GPT_5_6_LUNA: ((20_000_000, 2_000_000), 20_000_000),
    LLMModel.GPT_5_5: ((10_000_000, 1_000_000), None),
}

_OPENAI_TPM_NOTES = (
    "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法",
    "快取的輸入 token 仍計入 TPM",
    "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429",
)


def _build_gpt() -> None:
    for model, tiers in _GPT_TIERS.items():
        for tier_id, (rpm, tpm) in tiers.items():
            name, how = _GPT_TIER_LABELS[tier_id]
            _add(model, LLMPlatform.OPENAI, tier_id, "OpenAI API", f"{name}（{how}）", SRC_OPENAI_MODELS,
                 ("限制掛在組織與專案層級，同一組織的應用共用", *_OPENAI_TPM_NOTES),
                 rpm=_en(rpm), tpm=_en(tpm), tpm_reserves_max_tokens=True, input_cached_counts=True)

        for plan_id, (name, tpm) in _AZURE_GPT_TIERS.items():
            _add(model, LLMPlatform.FOUNDRY, plan_id, "Azure OpenAI", f"{name} (Global Standard)", SRC_AZURE_OPENAI,
                 ("Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開",
                  "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋",
                  "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入",
                  "免費層（Tier 0）沒有任何額度"),
                 rpm=_en(tpm / 1000), tpm=_en(tpm), tpm_reserves_max_tokens=True, input_cached_counts=True)

        mantle, runtime = _GPT_BEDROCK[model]
        if mantle is None:
            _add(model, LLMPlatform.BEDROCK, "mantle", "AWS Bedrock", "bedrock-mantle 端點", SRC_BEDROCK_GR,
                 (*_MANTLE_COMMON, "AWS 配額總表未列出此模型的 Mantle 預設值，實際額度依帳號而定",
                  "區域內推論比 OpenAI 牌價另加 10%"),
                 rpm=_NO_RPM, itpm=_NO_TPM, otpm=_NO_TPM, reserves_max_tokens=True, list_priced=False)
        elif mantle != "absent":
            _add(model, LLMPlatform.BEDROCK, "mantle", "AWS Bedrock", "bedrock-mantle 端點", SRC_BEDROCK_GR,
                 (*_MANTLE_COMMON, "數值出自 AWS 配額總表（General Reference），皆可申請調升",
                  "區域內推論比 OpenAI 牌價另加 10%"),
                 rpm=_NO_RPM, itpm=_en(mantle[0]), otpm=_en(mantle[1]),
                 reserves_max_tokens=True, list_priced=False)
        if runtime is not None:
            _add(model, LLMPlatform.BEDROCK, "runtime", "AWS Bedrock", "bedrock-runtime（全域跨區）", SRC_BEDROCK_GR,
                 ("TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算",
                  "每 1 個 output token 消耗 10 個配額 token（burndown，出自 AWS 模型卡與 burndown 說明頁）",
                  "全域跨區推論以 OpenAI 牌價計費"),
                 rpm=_NO_RPM_RUNTIME, tpm=_en(runtime), tpm_reserves_max_tokens=True, output_burndown=10.0)


# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------
# Verified 2026-09-29: ai.google.dev pricing (2026-09-24) and rate limits
# (2026-09-02), Vertex Standard PayGo (2026-09-28). Google no longer
# publishes per-model RPM/TPM/RPD for the Developer API.

_GEMINI_ORDER = (LLMModel.GEMINI_3_1_PRO, LLMModel.GEMINI_3_8_FLASH, LLMModel.GEMINI_3_5_FLASH_LITE,
                 LLMModel.GEMINI_3_1_FLASH_LITE, LLMModel.GEMINI_2_5_PRO, LLMModel.GEMINI_2_5_FLASH)
_GEMINI_PRO = {LLMModel.GEMINI_3_1_PRO, LLMModel.GEMINI_2_5_PRO}

# Developer API: the only published ceiling is spend per rolling 10 minutes.
_GEMINI_API_TIERS = {"g_t1": ("Tier 1", "已綁定帳單", 10), "g_t2": ("Tier 2", "已付 $100 且滿 3 天", 50),
                     "g_t3": ("Tier 3", "已付 $1,000 且滿 30 天", 200)}

# Vertex Standard PayGo baseline TPM by 30-day spend tier: (label, pro, flash).
_VERTEX_PAYGO = {"vx_t1": ("Tier 1", "$10–$250", 500_000, 2_000_000),
                 "vx_t2": ("Tier 2", "$250–$2K", 1_000_000, 4_000_000),
                 "vx_t3": ("Tier 3", "$2K–$50K", 2_000_000, 10_000_000),
                 "vx_t4": ("Tier 4", "$50K 以上", 10_000_000, 50_000_000)}

_GEMINI_UNPUBLISHED = Limit(
    status=LimitStatus.UNPUBLISHED,
    note="Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度",
)


def _build_gemini() -> None:
    for model in _GEMINI_ORDER:
        for plan_id, (name, how, cap) in _GEMINI_API_TIERS.items():
            _add(model, LLMPlatform.GOOGLE_AI, plan_id, "Gemini API", f"{name}（{how}）", SRC_GEMINI_RATE,
                 ("RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看",
                  f"官方公開的只有每 10 分鐘滾動消費上限 ${cap}，超過會收到 429",
                  "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"),
                 rpm=_GEMINI_UNPUBLISHED, itpm=_GEMINI_UNPUBLISHED, rpd=_GEMINI_UNPUBLISHED,
                 usd10m=_en(cap), input_cached_counts=True)
        for plan_id, (name, spend, pro, flash) in _VERTEX_PAYGO.items():
            tpm = pro if model in _GEMINI_PRO else flash
            _add(model, LLMPlatform.VERTEX, plan_id, "GCP Vertex",
                 f"Standard PayGo {name}（30 天消費 {spend}）", SRC_VERTEX_PAYGO,
                 ("基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流",
                  "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算",
                  "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格",
                  "需要保證容量可改買 Provisioned Throughput"),
                 tpm=Limit(status=LimitStatus.ENFORCED, value=tpm, soft=True), input_cached_counts=True)


_build_gpt()
_build_gemini()


# ---------------------------------------------------------------------------
# xAI Grok
# ---------------------------------------------------------------------------
# Verified 2026-09-29: docs.x.ai rate limits (per-tier RPS / TPM) and models,
# AWS General Reference and Grok 4.6 model card, Azure Foundry "Use Grok
# models", Vertex Grok model pages, OCI Generative AI pretrained models and
# the Oracle price list API. xAI meters requests per second; the planner
# works per minute, so RPS is shown as RPS x 60.

_GROK_ORDER = (LLMModel.GROK_4_7, LLMModel.GROK_4_6, LLMModel.GROK_4_5, LLMModel.GROK_4_3,
               LLMModel.GROK_4_20_REASONING, LLMModel.GROK_4_20_NON_REASONING, LLMModel.GROK_BUILD_0_1)
_GROK_FLAGSHIP = {LLMModel.GROK_4_7, LLMModel.GROK_4_6, LLMModel.GROK_4_5}

# xAI API: {tier: (rps, tpm)} for the two published profiles.
_XAI_FLAGSHIP = {"x_t0": (150, 50_000_000), "x_t2": (208, 60_000_000), "x_t4": (500, 100_000_000)}
_XAI_STANDARD = {"x_t0": (37, 10_000_000), "x_t2": (75, 25_000_000), "x_t4": (208, 85_000_000)}
_XAI_TIER_LABELS = {"x_t0": "Tier 0（預設）", "x_t2": "Tier 2（累計消費 $250 起）",
                    "x_t4": "Tier 4（累計消費 $5,000 起）"}

# Azure Foundry (Grok 4.6 only publishes numbers): {plan: (label, rpm, tpm)}.
_AZURE_GROK_46 = {"az_low": ("Low 層級", 0, 0), "az_medium": ("Medium 層級", 50, 50_000),
                  "az_high": ("High 層級", 5_000, 5_000_000)}
_AZURE_GROK_OTHER = (LLMModel.GROK_4_3, LLMModel.GROK_4_20_REASONING, LLMModel.GROK_4_20_NON_REASONING)

# Vertex (global quota shared with the US multi-region endpoint): (qpm, input tpm, output tpm).
_VERTEX_GROK = {
    LLMModel.GROK_4_6: (13, 188_000, 16_000),
    LLMModel.GROK_4_3: (100, 540_000, 80_000),
    LLMModel.GROK_4_20_REASONING: (100, 540_000, 80_000),
    LLMModel.GROK_4_20_NON_REASONING: (100, 540_000, 80_000),
}
_VERTEX_GROK_PREVIEW = {LLMModel.GROK_4_3}

# OCI on-demand: the TPM limit name to raise; no default is published.
_OCI_GROK = {
    LLMModel.GROK_4_7: None,
    LLMModel.GROK_4_6: "grok-4-6-tokens-per-minute-count",
    LLMModel.GROK_4_3: "grok-4-3-tokens-per-minute-count",
    LLMModel.GROK_4_20_REASONING: "grok-4-2-reasoning-tokens-per-minute-count",
    LLMModel.GROK_4_20_NON_REASONING: "grok-4-2-non-reasoning-tokens-per-minute-count",
}

_XAI_NOTES = (
    "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示",
    "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額",
    "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算",
)


def _build_grok() -> None:
    for model in _GROK_ORDER:
        tiers = _XAI_FLAGSHIP if model in _GROK_FLAGSHIP else _XAI_STANDARD
        for plan_id, (rps, tpm) in tiers.items():
            _add(model, LLMPlatform.XAI, plan_id, "xAI API", _XAI_TIER_LABELS[plan_id], SRC_XAI_RATE,
                 (f"每秒 {rps:,} 次請求", *_XAI_NOTES),
                 rpm=_en(rps * 60), tpm=_en(tpm), input_cached_counts=True)

        if model is LLMModel.GROK_4_6:
            _add(model, LLMPlatform.BEDROCK, "mantle", "AWS Bedrock", "bedrock-mantle 端點", SRC_BEDROCK_GR,
                 (*_MANTLE_COMMON, "AWS 配額總表未列出此模型的 Mantle 預設值，實際額度依帳號而定",
                  "Mantle 僅提供區域內推論，比 xAI 牌價另加 10%"),
                 rpm=_NO_RPM, itpm=_NO_TPM, otpm=_NO_TPM, reserves_max_tokens=True, list_priced=False)
            _add(model, LLMPlatform.BEDROCK, "runtime", "AWS Bedrock", "bedrock-runtime（全域跨區）", SRC_BEDROCK_GR,
                 ("TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算",
                  "AWS 說明頁：未列名的模型 output burndown 為 1:1",
                  "全域跨區推論以 xAI 牌價計費；美國跨區與區域內另加 10%"),
                 rpm=_NO_RPM_RUNTIME, tpm=_en(10_000_000), tpm_reserves_max_tokens=True)

            for plan_id, (label, rpm, tpm) in _AZURE_GROK_46.items():
                _add(model, LLMPlatform.FOUNDRY, plan_id, "Azure Foundry", f"{label} (Global Standard)", SRC_AZURE_GROK,
                     ("Azure 上的 Grok 4.6 目前為 Preview，context 200K、單次輸出上限 128K",
                      "層級依訂閱與部署設定決定，官方未公開對照表",
                      "Azure 未說明 Grok 的計量方式，此處沿用 Azure 的一般算法：以提示詞加 max_tokens 估算扣除",
                      *(("此層級預設為 0，部署前必須先申請",) if tpm == 0 else ())),
                     rpm=_en(rpm), tpm=_en(tpm), tpm_reserves_max_tokens=True, input_cached_counts=True)
        elif model in _AZURE_GROK_OTHER:
            azure_unpublished = Limit(status=LimitStatus.UNPUBLISHED,
                                      note="Azure 只公布 Grok 4.6 的配額，此模型需在 Foundry 入口網站查看")
            _add(model, LLMPlatform.FOUNDRY, "az_gs", "Azure Foundry", "Global Standard", SRC_AZURE_GROK,
                 ("Azure 上為 Preview，context 約 200K–262K、單次輸出上限 8,192 tokens",
                  "Data Zone Standard (US) 比 xAI 牌價另加 10%"),
                 rpm=azure_unpublished, tpm=azure_unpublished, tpm_reserves_max_tokens=True,
                 input_cached_counts=True)

        if model in _VERTEX_GROK:
            preview = ("此模型在 Vertex 仍為 Preview",) if model in _VERTEX_GROK_PREVIEW else ()
            _add(model, LLMPlatform.VERTEX, "vx_global", "GCP Vertex", "全域端點 (global)", SRC_VERTEX_GROK,
                 (*preview, "Grok 在 Vertex 只有一個全域配額，全域端點與美國多區域端點共用同一個額度",
                  "快取讀取是否計入輸入 TPM 官方未說明，此處保守計入",
                  "預設額度偏低，正式上線前通常需要申請調升"),
                 input_cached_counts=True, **_en3(_VERTEX_GROK[model]))

        if model in _OCI_GROK:
            limit_name = _OCI_GROK[model]
            how = (f"調額時在 Limits 申請 {limit_name}" if limit_name
                   else "OCI 尚未公布此模型的限制名稱與預設值")
            _add(model, LLMPlatform.OCI, "oci_ondemand", "Oracle OCI", "Generative AI 隨選 (On-Demand)", SRC_OCI_GROK,
                 ("OCI 的 Grok 只提供隨選模式，沒有專屬 AI 叢集", how,
                  "標準處理採 xAI 牌價；優先處理（priority）單價兩倍，僅在回應帶 service_tier: priority 時計費"),
                 tpm=Limit(status=LimitStatus.UNPUBLISHED,
                           note="OCI 只公布調額用的限制名稱，未公布預設 TPM"),
                 input_cached_counts=True)


_build_grok()


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
    #: The capability class this shape usually starts on.
    suggested_class: str
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
        suggested_class="balanced",
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
        suggested_class="balanced",
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
        suggested_class="balanced",
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
        suggested_class="frontier",
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
        suggested_class="strong",
        messages_per_user_per_day=6,
        thinking_tokens_per_request=2_000,
        default_effort="high",
    ),
]

_SCENARIO_BY_ID = {s.scenario_id: s for s in _SCENARIOS}


def suggested_model(scenario: "UsageScenario", line: ModelLine = ModelLine.CLAUDE) -> LLMModel:
    """The scenario's starting model within a line."""
    return model_for(line, scenario.suggested_class)


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

#: Hours per day over which the daily volume is assumed to be spread.
ACTIVE_HOURS_PER_DAY = 8

#: Working days per month, used for the monthly volume suggestion.
WORKING_DAYS_PER_MONTH = 22
