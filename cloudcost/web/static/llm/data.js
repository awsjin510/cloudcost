// GENERATED FILE — do not edit by hand.
// Regenerate with:  python -m cloudcost.llm.export
// Source of truth:  cloudcost/llm/catalog.py
//
// Quota values are platform DEFAULTS, not model limits; every one of them
// can be raised on request. Each row carries the document it came from.

const LLM_CONST = {"MAX_OUTPUT_TOKENS": 128000, "VERIFIED": "2026-09-29", "AMPLE_THRESHOLD": 0.7, "MAX_SUGGESTED_CACHE_RATE": 0.95, "PEAK_FACTORS": {"flat": 1.5, "normal": 3.0, "spiky": 6.0}, "ACTIVE_HOURS_PER_DAY": 8, "WORKING_DAYS_PER_MONTH": 22, "EFFORT_THINKING_FACTORS": {"low": 0.25, "medium": 0.5, "high": 1.0, "xhigh": 1.5}, "MODEL_CLASSES": ["frontier", "strong", "balanced", "fast"], "DIMS": ["rpm", "itpm", "otpm", "tpm", "rpd", "usd10m"]};

const LLM_LINES = [
  {
    "line": "claude",
    "label": "Claude",
    "vendor": "Anthropic",
    "price_caveat": "以 Anthropic 官方第一方定價計算。Claude in Microsoft Foundry 同樣採標準 API 費率（以 CCU 計價開立帳單）；Amazon Bedrock 與 Google Vertex 為合作夥伴自訂定價，實際金額請以該平台價目表為準"
  },
  {
    "line": "gpt",
    "label": "GPT",
    "vendor": "OpenAI",
    "price_caveat": "以 OpenAI 官方 API 牌價計算。Azure OpenAI Global Standard 與 Bedrock 全域跨區推論同樣採 OpenAI 牌價；Azure Data Zone 與 Bedrock 區域內推論另加 10%"
  },
  {
    "line": "gemini",
    "label": "Gemini",
    "vendor": "Google",
    "price_caveat": "以 Gemini API 付費層牌價計算，與 Vertex 全域端點價格相同；Vertex 區域端點另加 10%。Gemini 的明確快取另按儲存時數收費，此處未計入"
  },
  {
    "line": "grok",
    "label": "Grok",
    "vendor": "xAI",
    "price_caveat": "以 xAI 官方 API 牌價計算。Bedrock 全域跨區、Azure Global Standard、Vertex 全域端點與 OCI 標準處理同樣採 xAI 牌價；Bedrock 區域內與 Azure Data Zone 另加 10%，OCI 優先處理（priority）為兩倍"
  }
];

const LLM_MODELS = [
  {
    "model": "fable-5-1",
    "label": "Claude Fable 5.1",
    "line": "claude",
    "version_label": "Fable 5.1",
    "model_class": "frontier",
    "tier": 3,
    "api_id": "claude-fable-5-1",
    "pricing": {
      "input_per_mtok": 10.0,
      "output_per_mtok": 50.0,
      "cache_read_per_mtok": 0.25,
      "cache_write_5m_per_mtok": 12.5,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "快取讀取為輸入價的 0.025 倍，是所有模型中最低的，有做 prompt caching 時省下的比例最大"
    ]
  },
  {
    "model": "fable-5",
    "label": "Claude Fable 5",
    "line": "claude",
    "version_label": "Fable 5",
    "model_class": "frontier",
    "tier": 3,
    "api_id": "claude-fable-5",
    "pricing": {
      "input_per_mtok": 10.0,
      "output_per_mtok": 50.0,
      "cache_read_per_mtok": 1.0,
      "cache_write_5m_per_mtok": 12.5,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "快取讀取為輸入價的 0.1 倍，比 Fable 5.1 貴 4 倍"
    ]
  },
  {
    "model": "opus-5-5",
    "label": "Claude Opus 5.5",
    "line": "claude",
    "version_label": "Opus 5.5",
    "model_class": "strong",
    "tier": 2,
    "api_id": "claude-opus-5-5",
    "pricing": {
      "input_per_mtok": 4.0,
      "output_per_mtok": 20.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": 5.0,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "配額與 Opus 5 相同、單價便宜兩成，快取讀取為輸入價的 0.05 倍"
    ]
  },
  {
    "model": "opus-5",
    "label": "Claude Opus 5",
    "line": "claude",
    "version_label": "Opus 5",
    "model_class": "strong",
    "tier": 2,
    "api_id": "claude-opus-5",
    "pricing": {
      "input_per_mtok": 5.0,
      "output_per_mtok": 25.0,
      "cache_read_per_mtok": 0.5,
      "cache_write_5m_per_mtok": 6.25,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "單價為 Fable 的一半；同配額下 Opus 5.5 更便宜，新專案建議直接評估 Opus 5.5"
    ]
  },
  {
    "model": "sonnet-5-5",
    "label": "Claude Sonnet 5.5",
    "line": "claude",
    "version_label": "Sonnet 5.5",
    "model_class": "balanced",
    "tier": 1,
    "api_id": "claude-sonnet-5-5",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 10.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": 2.5,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "目前的 Sonnet，高流量生產工作負載的預設選擇，單價與 Sonnet 5 相同、為 Fable 的五分之一",
      "與 Sonnet 5 各自獨立計算配額"
    ]
  },
  {
    "model": "sonnet-5",
    "label": "Claude Sonnet 5",
    "line": "claude",
    "version_label": "Sonnet 5",
    "model_class": "balanced",
    "tier": 1,
    "api_id": "claude-sonnet-5",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 10.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": 2.5,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "前一代 Sonnet，單價與 Sonnet 5.5 相同；新專案建議直接評估 Sonnet 5.5"
    ]
  },
  {
    "model": "opus-4-8",
    "label": "Claude Opus 4.8",
    "line": "claude",
    "version_label": "Opus 4.8",
    "model_class": "strong",
    "tier": 2,
    "api_id": "claude-opus-4-8",
    "pricing": {
      "input_per_mtok": 5.0,
      "output_per_mtok": 25.0,
      "cache_read_per_mtok": 0.5,
      "cache_write_5m_per_mtok": 6.25,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "前一代 Opus，單價與 Opus 5 相同；新專案建議直接評估 Opus 5.5"
    ]
  },
  {
    "model": "sonnet-4-6",
    "label": "Claude Sonnet 4.6",
    "line": "claude",
    "version_label": "Sonnet 4.6",
    "model_class": "balanced",
    "tier": 1,
    "api_id": "claude-sonnet-4-6",
    "pricing": {
      "input_per_mtok": 3.0,
      "output_per_mtok": 15.0,
      "cache_read_per_mtok": 0.3,
      "cache_write_5m_per_mtok": 3.75,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "前一代 Sonnet，單價比 Sonnet 5 高；使用較舊的 tokenizer，同樣文字的 token 數約少三成"
    ]
  },
  {
    "model": "haiku-4-5",
    "label": "Claude Haiku 4.5",
    "line": "claude",
    "version_label": "Haiku 4.5",
    "model_class": "fast",
    "tier": 0,
    "api_id": "claude-haiku-4-5",
    "pricing": {
      "input_per_mtok": 1.0,
      "output_per_mtok": 5.0,
      "cache_read_per_mtok": 0.1,
      "cache_write_5m_per_mtok": 1.25,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "Claude 最便宜的版本，適合高流量的簡單任務；上下文上限 200K"
    ]
  },
  {
    "model": "gpt-6-astra",
    "label": "GPT-6 Astra",
    "line": "gpt",
    "version_label": "GPT-6 Astra",
    "model_class": "frontier",
    "tier": 4,
    "api_id": "gpt-6-astra",
    "pricing": {
      "input_per_mtok": 10.0,
      "output_per_mtok": 50.0,
      "cache_read_per_mtok": 1.0,
      "cache_write_5m_per_mtok": 12.5,
      "long_context_threshold": 272000,
      "long_input_per_mtok": 20.0,
      "long_output_per_mtok": 75.0,
      "long_cache_read_per_mtok": 2.0,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "OpenAI 目前最強的旗艦，一律會推理、無法關閉",
      "提示詞超過 272K tokens 時整筆改按長上下文費率"
    ]
  },
  {
    "model": "gpt-6-sol",
    "label": "GPT-6 Sol",
    "line": "gpt",
    "version_label": "GPT-6 Sol",
    "model_class": "balanced",
    "tier": 3,
    "api_id": "gpt-6-sol",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 10.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": 2.5,
      "long_context_threshold": 272000,
      "long_input_per_mtok": 4.0,
      "long_output_per_mtok": 15.0,
      "long_cache_read_per_mtok": 0.4,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "GPT-6 的中階版本，偏重程式與代理工作，預設推理強度 medium"
    ]
  },
  {
    "model": "gpt-6-luna",
    "label": "GPT-6 Luna",
    "line": "gpt",
    "version_label": "GPT-6 Luna",
    "model_class": "fast",
    "tier": 1,
    "api_id": "gpt-6-luna",
    "pricing": {
      "input_per_mtok": 0.1,
      "output_per_mtok": 0.5,
      "cache_read_per_mtok": 0.01,
      "cache_write_5m_per_mtok": 0.125,
      "long_context_threshold": 272000,
      "long_input_per_mtok": 0.2,
      "long_output_per_mtok": 0.75,
      "long_cache_read_per_mtok": 0.02,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "GPT-6 的低成本、高流量版本"
    ]
  },
  {
    "model": "gpt-5.6-sol",
    "label": "GPT-5.6 Sol",
    "line": "gpt",
    "version_label": "GPT-5.6 Sol",
    "model_class": "strong",
    "tier": 3,
    "api_id": "gpt-5.6-sol",
    "pricing": {
      "input_per_mtok": 4.0,
      "output_per_mtok": 20.0,
      "cache_read_per_mtok": 0.4,
      "cache_write_5m_per_mtok": 5.0,
      "long_context_threshold": 272000,
      "long_input_per_mtok": 8.0,
      "long_output_per_mtok": 30.0,
      "long_cache_read_per_mtok": 0.8,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "前一代旗艦；$4 / $20 為促銷價，官方保證至少維持到 2026-11-21，報價時請留意"
    ]
  },
  {
    "model": "gpt-5.6-terra",
    "label": "GPT-5.6 Terra",
    "line": "gpt",
    "version_label": "GPT-5.6 Terra",
    "model_class": "balanced",
    "tier": 2,
    "api_id": "gpt-5.6-terra",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 12.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": 2.5,
      "long_context_threshold": 272000,
      "long_input_per_mtok": 4.0,
      "long_output_per_mtok": 18.0,
      "long_cache_read_per_mtok": 0.4,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "相當於舊的 mini 級距"
    ]
  },
  {
    "model": "gpt-5.6-luna",
    "label": "GPT-5.6 Luna",
    "line": "gpt",
    "version_label": "GPT-5.6 Luna",
    "model_class": "fast",
    "tier": 1,
    "api_id": "gpt-5.6-luna",
    "pricing": {
      "input_per_mtok": 0.2,
      "output_per_mtok": 1.2,
      "cache_read_per_mtok": 0.02,
      "cache_write_5m_per_mtok": 0.25,
      "long_context_threshold": 272000,
      "long_input_per_mtok": 0.4,
      "long_output_per_mtok": 1.8,
      "long_cache_read_per_mtok": 0.04,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "相當於舊的 nano 級距"
    ]
  },
  {
    "model": "gpt-5.5",
    "label": "GPT-5.5",
    "line": "gpt",
    "version_label": "GPT-5.5",
    "model_class": "strong",
    "tier": 3,
    "api_id": "gpt-5.5",
    "pricing": {
      "input_per_mtok": 5.0,
      "output_per_mtok": 30.0,
      "cache_read_per_mtok": 0.5,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 272000,
      "long_input_per_mtok": 10.0,
      "long_output_per_mtok": 45.0,
      "long_cache_read_per_mtok": 1.0,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "較舊但仍常用的旗艦，沒有快取寫入費"
    ]
  },
  {
    "model": "gemini-3.1-pro-preview",
    "label": "Gemini 3.1 Pro",
    "line": "gemini",
    "version_label": "3.1 Pro (Preview)",
    "model_class": "frontier",
    "tier": 3,
    "api_id": "gemini-3.1-pro-preview",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 12.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 4.0,
      "long_output_per_mtok": 18.0,
      "long_cache_read_per_mtok": 0.4,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "目前唯一的 Pro，仍為 Preview 且沒有免費層",
      "提示詞超過 200K tokens 時整筆改按長上下文費率"
    ]
  },
  {
    "model": "gemini-3.8-flash",
    "label": "Gemini 3.8 Flash",
    "line": "gemini",
    "version_label": "3.8 Flash",
    "model_class": "balanced",
    "tier": 2,
    "api_id": "gemini-3.8-flash",
    "pricing": {
      "input_per_mtok": 0.75,
      "output_per_mtok": 3.75,
      "cache_read_per_mtok": 0.075,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "此價格維持到 2026-12-31；2027-01-01 起調為 $1.50 / $7.50，年約報價請特別留意"
    ]
  },
  {
    "model": "gemini-3.5-flash-lite",
    "label": "Gemini 3.5 Flash-Lite",
    "line": "gemini",
    "version_label": "3.5 Flash-Lite",
    "model_class": "fast",
    "tier": 1,
    "api_id": "gemini-3.5-flash-lite",
    "pricing": {
      "input_per_mtok": 0.3,
      "output_per_mtok": 2.5,
      "cache_read_per_mtok": 0.03,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "Google 建議新專案使用的輕量版本之一，思考預設為最低"
    ]
  },
  {
    "model": "gemini-3.1-flash-lite",
    "label": "Gemini 3.1 Flash-Lite",
    "line": "gemini",
    "version_label": "3.1 Flash-Lite",
    "model_class": "fast",
    "tier": 1,
    "api_id": "gemini-3.1-flash-lite",
    "pricing": {
      "input_per_mtok": 0.25,
      "output_per_mtok": 1.5,
      "cache_read_per_mtok": 0.025,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "目前最便宜的 Gemini；音訊輸入另計 $0.50"
    ]
  },
  {
    "model": "gemini-2.5-pro",
    "label": "Gemini 2.5 Pro",
    "line": "gemini",
    "version_label": "2.5 Pro",
    "model_class": "frontier",
    "tier": 3,
    "api_id": "gemini-2.5-pro",
    "pricing": {
      "input_per_mtok": 1.25,
      "output_per_mtok": 10.0,
      "cache_read_per_mtok": 0.125,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 2.5,
      "long_output_per_mtok": 15.0,
      "long_cache_read_per_mtok": 0.25,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "前一代 Pro，僅限過去用過的專案使用，新專案無法啟用"
    ]
  },
  {
    "model": "gemini-2.5-flash",
    "label": "Gemini 2.5 Flash",
    "line": "gemini",
    "version_label": "2.5 Flash",
    "model_class": "balanced",
    "tier": 2,
    "api_id": "gemini-2.5-flash",
    "pricing": {
      "input_per_mtok": 0.3,
      "output_per_mtok": 2.5,
      "cache_read_per_mtok": 0.03,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": null,
      "long_input_per_mtok": null,
      "long_output_per_mtok": null,
      "long_cache_read_per_mtok": null,
      "long_context_inclusive": false,
      "batch_discount": 0.5
    },
    "notes": [
      "前一代 Flash，僅限過去用過的專案使用，新專案無法啟用"
    ]
  },
  {
    "model": "grok-4.7",
    "label": "Grok 4.7",
    "line": "grok",
    "version_label": "Grok 4.7",
    "model_class": "frontier",
    "tier": 4,
    "api_id": "grok-4.7",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 6.0,
      "cache_read_per_mtok": 0.5,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 4.0,
      "long_output_per_mtok": 12.0,
      "long_cache_read_per_mtok": 1.0,
      "long_context_inclusive": true,
      "batch_discount": null
    },
    "notes": [
      "xAI 目前最強的模型，官方建議程式與一般對話都用它；一律會推理，預設推理強度 high",
      "不支援 Batch API；提示詞達 200K tokens 時整筆改按兩倍費率"
    ]
  },
  {
    "model": "grok-4.6",
    "label": "Grok 4.6",
    "line": "grok",
    "version_label": "Grok 4.6",
    "model_class": "strong",
    "tier": 3,
    "api_id": "grok-4.6",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 6.0,
      "cache_read_per_mtok": 0.5,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 4.0,
      "long_output_per_mtok": 12.0,
      "long_cache_read_per_mtok": 1.0,
      "long_context_inclusive": true,
      "batch_discount": null
    },
    "notes": [
      "前一代旗艦，單價與 4.7 相同；新專案建議直接評估 4.7",
      "目前唯一同時上架 Bedrock、Azure、Vertex 與 OCI 的 Grok"
    ]
  },
  {
    "model": "grok-4.5",
    "label": "Grok 4.5",
    "line": "grok",
    "version_label": "Grok 4.5",
    "model_class": "strong",
    "tier": 3,
    "api_id": "grok-4.5",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 6.0,
      "cache_read_per_mtok": 0.3,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 4.0,
      "long_output_per_mtok": 12.0,
      "long_cache_read_per_mtok": 0.6,
      "long_context_inclusive": true,
      "batch_discount": null
    },
    "notes": [
      "偏重程式與代理工作，快取讀取比 4.6／4.7 便宜（$0.30）",
      "只在 xAI API 提供"
    ]
  },
  {
    "model": "grok-4.3",
    "label": "Grok 4.3",
    "line": "grok",
    "version_label": "Grok 4.3",
    "model_class": "balanced",
    "tier": 2,
    "api_id": "grok-4.3",
    "pricing": {
      "input_per_mtok": 1.25,
      "output_per_mtok": 2.5,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 2.5,
      "long_output_per_mtok": 5.0,
      "long_cache_read_per_mtok": 0.4,
      "long_context_inclusive": true,
      "batch_discount": 0.2
    },
    "notes": [
      "1M context，推理強度可設 none 到 xhigh（預設 low）",
      "支援 Batch API，打八折"
    ]
  },
  {
    "model": "grok-4.20-0309-reasoning",
    "label": "Grok 4.20 Reasoning",
    "line": "grok",
    "version_label": "Grok 4.20 Reasoning",
    "model_class": "balanced",
    "tier": 2,
    "api_id": "grok-4.20-0309-reasoning",
    "pricing": {
      "input_per_mtok": 1.25,
      "output_per_mtok": 2.5,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 2.5,
      "long_output_per_mtok": 5.0,
      "long_cache_read_per_mtok": 0.4,
      "long_context_inclusive": true,
      "batch_discount": 0.2
    },
    "notes": [
      "單價與 4.3 相同；xAI 官方建議新專案改用 4.3",
      "支援 Batch API，打八折"
    ]
  },
  {
    "model": "grok-4.20-0309-non-reasoning",
    "label": "Grok 4.20 Non-reasoning",
    "line": "grok",
    "version_label": "Grok 4.20 Non-reasoning",
    "model_class": "fast",
    "tier": 1,
    "api_id": "grok-4.20-0309-non-reasoning",
    "pricing": {
      "input_per_mtok": 1.25,
      "output_per_mtok": 2.5,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 2.5,
      "long_output_per_mtok": 5.0,
      "long_cache_read_per_mtok": 0.4,
      "long_context_inclusive": true,
      "batch_discount": 0.2
    },
    "notes": [
      "不推理、延遲最低，適合分類與摘要這類大量簡單工作",
      "支援 Batch API，打八折"
    ]
  },
  {
    "model": "grok-build-0.1",
    "label": "Grok Build 0.1",
    "line": "grok",
    "version_label": "Grok Build 0.1",
    "model_class": "fast",
    "tier": 1,
    "api_id": "grok-build-0.1",
    "pricing": {
      "input_per_mtok": 1.0,
      "output_per_mtok": 2.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": null,
      "long_context_threshold": 200000,
      "long_input_per_mtok": 2.0,
      "long_output_per_mtok": 4.0,
      "long_cache_read_per_mtok": 0.4,
      "long_context_inclusive": true,
      "batch_discount": null
    },
    "notes": [
      "xAI 的程式專用模型（取代已退役的 grok-code-fast-1），也是最便宜的 Grok",
      "256K context，只在 xAI API 提供"
    ]
  }
];

const LLM_SCENARIOS = [
  {
    "scenario_id": "support",
    "label": "客服對話",
    "blurb": "固定話術 + 短問答，前綴幾乎每次相同",
    "icon": "&#128172;",
    "input_tokens_per_request": 4000,
    "output_tokens_per_request": 500,
    "cache_hit_rate": 0.6,
    "max_tokens": 3000,
    "suggested_class": "balanced",
    "messages_per_user_per_day": 12.0,
    "thinking_tokens_per_request": 800,
    "default_effort": "medium",
    "batch_friendly": false
  },
  {
    "scenario_id": "rag",
    "label": "知識庫問答",
    "blurb": "每次帶入檢索到的文件片段，提示詞偏長",
    "icon": "&#128218;",
    "input_tokens_per_request": 20000,
    "output_tokens_per_request": 2000,
    "cache_hit_rate": 0.5,
    "max_tokens": 8000,
    "suggested_class": "balanced",
    "messages_per_user_per_day": 8.0,
    "thinking_tokens_per_request": 2500,
    "default_effort": "high",
    "batch_friendly": false
  },
  {
    "scenario_id": "summarize",
    "label": "文件摘要",
    "blurb": "一次讀入整份文件，輸出精簡，快取效益低",
    "icon": "&#128196;",
    "input_tokens_per_request": 30000,
    "output_tokens_per_request": 1500,
    "cache_hit_rate": 0.15,
    "max_tokens": 6000,
    "suggested_class": "balanced",
    "messages_per_user_per_day": 4.0,
    "thinking_tokens_per_request": 1500,
    "default_effort": "medium",
    "batch_friendly": true
  },
  {
    "scenario_id": "coding",
    "label": "程式開發代理",
    "blurb": "長對話多輪工具呼叫，前綴長但高度可快取",
    "icon": "&#129302;",
    "input_tokens_per_request": 60000,
    "output_tokens_per_request": 8000,
    "cache_hit_rate": 0.8,
    "max_tokens": 32000,
    "suggested_class": "frontier",
    "messages_per_user_per_day": 60.0,
    "thinking_tokens_per_request": 6000,
    "default_effort": "xhigh",
    "batch_friendly": false
  },
  {
    "scenario_id": "writing",
    "label": "內容生成",
    "blurb": "提示詞短、產出長，成本集中在 Output",
    "icon": "&#9998;",
    "input_tokens_per_request": 2000,
    "output_tokens_per_request": 4000,
    "cache_hit_rate": 0.25,
    "max_tokens": 12000,
    "suggested_class": "strong",
    "messages_per_user_per_day": 6.0,
    "thinking_tokens_per_request": 2000,
    "default_effort": "high",
    "batch_friendly": false
  }
];

const LLM_PLANS = [
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 500000.0}, "otpm": {"status": "enforced", "value": 100000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 1500000.0}, "otpm": {"status": "enforced", "value": 300000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 500000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown）", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 0.0}, "itpm": {"status": "enforced", "value": 0.0}, "otpm": {"status": "enforced", "value": 0.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付訂閱的 Fable 預設配額為 0，部署前必須先申請", "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", "Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 500000.0}, "otpm": {"status": "enforced", "value": 100000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 1500000.0}, "otpm": {"status": "enforced", "value": 300000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 200000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token；AWS 未明列此模型，比照 Fable 5.1 估算", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 0.0}, "itpm": {"status": "enforced", "value": 0.0}, "otpm": {"status": "enforced", "value": 0.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付訂閱的 Fable 預設配額為 0，部署前必須先申請", "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", "Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": [], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "otpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "AWS 配額總表未列出此模型的 Mantle 預設值，可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 30000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown）", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 40.0}, "itpm": {"status": "enforced", "value": 40000.0}, "otpm": {"status": "enforced", "value": 8000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "opus-5-5", "model_label": "Claude Opus 5.5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": [], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 30000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown）", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 40.0}, "itpm": {"status": "enforced", "value": 40000.0}, "otpm": {"status": "enforced", "value": 8000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": [], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "otpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "AWS 配額總表未列出此模型的 Mantle 預設值，可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token；AWS 未明列此模型，比照 Sonnet 5 估算", "快取讀取不計入配額", "AWS 配額總表尚未列出此模型的 bedrock-runtime 預設值，可在 Service Quotas 主控台查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 40.0}, "itpm": {"status": "enforced", "value": 40000.0}, "otpm": {"status": "enforced", "value": 8000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2500.0}, "itpm": {"status": "enforced", "value": 25000000.0}, "otpm": {"status": "enforced", "value": 2500000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "sonnet-5-5", "model_label": "Claude Sonnet 5.5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1250.0}, "itpm": {"status": "enforced", "value": 12500000.0}, "otpm": {"status": "enforced", "value": 1250000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": [], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 3000000.0}, "otpm": {"status": "enforced", "value": 300000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 6000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown）", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 40.0}, "itpm": {"status": "enforced", "value": 40000.0}, "otpm": {"status": "enforced", "value": 8000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2500.0}, "itpm": {"status": "enforced", "value": 25000000.0}, "otpm": {"status": "enforced", "value": 2500000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1250.0}, "itpm": {"status": "enforced", "value": 12500000.0}, "otpm": {"status": "enforced", "value": 1250000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", "2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Opus 4.x 各版本（4.8／4.7／4.6／4.5）共用同一個額度", "限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Opus 4.x 各版本（4.8／4.7／4.6／4.5）共用同一個額度"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Opus 4.x 各版本（4.8／4.7／4.6／4.5）共用同一個額度", "需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 30000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 15.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 15 個配額 token（burndown）", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 40.0}, "itpm": {"status": "enforced", "value": 40000.0}, "otpm": {"status": "enforced", "value": 8000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["Google 同時把 Opus 4.8 列在各模型配額表與共用沿襲配額的範例中，實際採哪一種請以主控台為準", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "opus-4-8", "model_label": "Claude Opus 4.8", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價", "Google 同時把 Opus 4.8 列在各模型配額表與共用沿襲配額的範例中，實際採哪一種請以主控台為準"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "sonnet-4-6", "model_label": "Claude Sonnet 4.6", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Sonnet 4.x 各版本（4.6／4.5）共用同一個額度", "限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-4-6", "model_label": "Claude Sonnet 4.6", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Sonnet 4.x 各版本（4.6／4.5）共用同一個額度"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-4-6", "model_label": "Claude Sonnet 4.6", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["Sonnet 4.x 各版本（4.6／4.5）共用同一個額度", "需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "sonnet-4-6", "model_label": "Claude Sonnet 4.6", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 6000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 5.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 5 個配額 token（burndown）", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "sonnet-4-6", "model_label": "Claude Sonnet 4.6", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 80.0}, "itpm": {"status": "enforced", "value": 80000.0}, "otpm": {"status": "enforced", "value": 16000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "sonnet-4-6", "model_label": "Claude Sonnet 4.6", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "sonnet-4-6", "model_label": "Claude Sonnet 4.6", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 1500.0}, "itpm": {"status": "enforced", "value": 1500000.0}, "otpm": {"status": "enforced", "value": 150000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["此模型採各模型獨立配額", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": [], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "otpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "AWS 配額總表未列出此模型的 Mantle 預設值，可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 5000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 5.0, "list_priced": false, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 5 個配額 token（burndown）", "快取讀取不計入配額"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 80.0}, "itpm": {"status": "enforced", "value": 80000.0}, "otpm": {"status": "enforced", "value": 16000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09-29"},
  {"model": "haiku-4-5", "model_label": "Claude Haiku 4.5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2500.0}, "itpm": {"status": "enforced", "value": 2500000.0}, "otpm": {"status": "enforced", "value": 250000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["此模型採各模型獨立配額", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "openai", "plan_id": "t1", "platform_label": "OpenAI API", "plan_label": "Tier 1（累計付款 $5 起）", "rpm": {"status": "enforced", "value": 500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "openai", "plan_id": "t3", "platform_label": "OpenAI API", "plan_label": "Tier 3（累計付款 $100 起）", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "openai", "plan_id": "t5", "platform_label": "OpenAI API", "plan_label": "Tier 5（累計付款 $1,000 起）", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 40000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "foundry", "plan_id": "az_t1", "platform_label": "Azure OpenAI", "plan_label": "Tier 1 (Global Standard)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "foundry", "plan_id": "az_t3", "platform_label": "Azure OpenAI", "plan_label": "Tier 3 (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "foundry", "plan_id": "az_t6", "platform_label": "Azure OpenAI", "plan_label": "Tier 6 (Global Standard)", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 15000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 1000000.0}, "otpm": {"status": "enforced", "value": 100000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升", "區域內推論比 OpenAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-6-astra", "model_label": "GPT-6 Astra", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": true, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown，出自 AWS 模型卡與 burndown 說明頁）", "全域跨區推論以 OpenAI 牌價計費"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "openai", "plan_id": "t1", "platform_label": "OpenAI API", "plan_label": "Tier 1（累計付款 $5 起）", "rpm": {"status": "enforced", "value": 500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "openai", "plan_id": "t3", "platform_label": "OpenAI API", "plan_label": "Tier 3（累計付款 $100 起）", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "openai", "plan_id": "t5", "platform_label": "OpenAI API", "plan_label": "Tier 5（累計付款 $1,000 起）", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 40000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "foundry", "plan_id": "az_t1", "platform_label": "Azure OpenAI", "plan_label": "Tier 1 (Global Standard)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "foundry", "plan_id": "az_t3", "platform_label": "Azure OpenAI", "plan_label": "Tier 3 (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "foundry", "plan_id": "az_t6", "platform_label": "Azure OpenAI", "plan_label": "Tier 6 (Global Standard)", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 15000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "otpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "AWS 配額總表未列出此模型的 Mantle 預設值，實際額度依帳號而定", "區域內推論比 OpenAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-6-sol", "model_label": "GPT-6 Sol", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": true, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown，出自 AWS 模型卡與 burndown 說明頁）", "全域跨區推論以 OpenAI 牌價計費"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "openai", "plan_id": "t1", "platform_label": "OpenAI API", "plan_label": "Tier 1（累計付款 $5 起）", "rpm": {"status": "enforced", "value": 500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "openai", "plan_id": "t3", "platform_label": "OpenAI API", "plan_label": "Tier 3（累計付款 $100 起）", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "openai", "plan_id": "t5", "platform_label": "OpenAI API", "plan_label": "Tier 5（累計付款 $1,000 起）", "rpm": {"status": "enforced", "value": 30000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 180000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "foundry", "plan_id": "az_t1", "platform_label": "Azure OpenAI", "plan_label": "Tier 1 (Global Standard)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "foundry", "plan_id": "az_t3", "platform_label": "Azure OpenAI", "plan_label": "Tier 3 (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "foundry", "plan_id": "az_t6", "platform_label": "Azure OpenAI", "plan_label": "Tier 6 (Global Standard)", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 15000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "otpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "AWS 配額總表未列出此模型的 Mantle 預設值，實際額度依帳號而定", "區域內推論比 OpenAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-6-luna", "model_label": "GPT-6 Luna", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": true, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown，出自 AWS 模型卡與 burndown 說明頁）", "全域跨區推論以 OpenAI 牌價計費"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "openai", "plan_id": "t1", "platform_label": "OpenAI API", "plan_label": "Tier 1（累計付款 $5 起）", "rpm": {"status": "enforced", "value": 500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "openai", "plan_id": "t3", "platform_label": "OpenAI API", "plan_label": "Tier 3（累計付款 $100 起）", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "openai", "plan_id": "t5", "platform_label": "OpenAI API", "plan_label": "Tier 5（累計付款 $1,000 起）", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 40000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "foundry", "plan_id": "az_t1", "platform_label": "Azure OpenAI", "plan_label": "Tier 1 (Global Standard)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "foundry", "plan_id": "az_t3", "platform_label": "Azure OpenAI", "plan_label": "Tier 3 (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "foundry", "plan_id": "az_t6", "platform_label": "Azure OpenAI", "plan_label": "Tier 6 (Global Standard)", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 15000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升", "區域內推論比 OpenAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-5.6-sol", "model_label": "GPT-5.6 Sol", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": true, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown，出自 AWS 模型卡與 burndown 說明頁）", "全域跨區推論以 OpenAI 牌價計費"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "openai", "plan_id": "t1", "platform_label": "OpenAI API", "plan_label": "Tier 1（累計付款 $5 起）", "rpm": {"status": "enforced", "value": 500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "openai", "plan_id": "t3", "platform_label": "OpenAI API", "plan_label": "Tier 3（累計付款 $100 起）", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "openai", "plan_id": "t5", "platform_label": "OpenAI API", "plan_label": "Tier 5（累計付款 $1,000 起）", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 40000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "foundry", "plan_id": "az_t1", "platform_label": "Azure OpenAI", "plan_label": "Tier 1 (Global Standard)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "foundry", "plan_id": "az_t3", "platform_label": "Azure OpenAI", "plan_label": "Tier 3 (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "foundry", "plan_id": "az_t6", "platform_label": "Azure OpenAI", "plan_label": "Tier 6 (Global Standard)", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 15000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升", "區域內推論比 OpenAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-5.6-terra", "model_label": "GPT-5.6 Terra", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 20000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": true, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown，出自 AWS 模型卡與 burndown 說明頁）", "全域跨區推論以 OpenAI 牌價計費"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "openai", "plan_id": "t1", "platform_label": "OpenAI API", "plan_label": "Tier 1（累計付款 $5 起）", "rpm": {"status": "enforced", "value": 500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "openai", "plan_id": "t3", "platform_label": "OpenAI API", "plan_label": "Tier 3（累計付款 $100 起）", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "openai", "plan_id": "t5", "platform_label": "OpenAI API", "plan_label": "Tier 5（累計付款 $1,000 起）", "rpm": {"status": "enforced", "value": 30000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 180000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "foundry", "plan_id": "az_t1", "platform_label": "Azure OpenAI", "plan_label": "Tier 1 (Global Standard)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "foundry", "plan_id": "az_t3", "platform_label": "Azure OpenAI", "plan_label": "Tier 3 (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "foundry", "plan_id": "az_t6", "platform_label": "Azure OpenAI", "plan_label": "Tier 6 (Global Standard)", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 15000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升", "區域內推論比 OpenAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-5.6-luna", "model_label": "GPT-5.6 Luna", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 20000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 10.0, "list_priced": true, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "每 1 個 output token 消耗 10 個配額 token（burndown，出自 AWS 模型卡與 burndown 說明頁）", "全域跨區推論以 OpenAI 牌價計費"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gpt-5.5", "model_label": "GPT-5.5", "platform": "openai", "plan_id": "t1", "platform_label": "OpenAI API", "plan_label": "Tier 1（累計付款 $5 起）", "rpm": {"status": "enforced", "value": 500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.5", "model_label": "GPT-5.5", "platform": "openai", "plan_id": "t3", "platform_label": "OpenAI API", "plan_label": "Tier 3（累計付款 $100 起）", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.5", "model_label": "GPT-5.5", "platform": "openai", "plan_id": "t5", "platform_label": "OpenAI API", "plan_label": "Tier 5（累計付款 $1,000 起）", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 40000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["限制掛在組織與專案層級，同一組織的應用共用", "TPM 為輸入加輸出合併計算，准入時以提示詞加 max_tokens 估算；官方措辭有歧義，此處採保守算法", "快取的輸入 token 仍計入 TPM", "輸入流量超過約 1M TPM 後，每 15 分鐘最多成長 50%，否則可能收到 429"], "source": "https://developers.openai.com/api/docs/models", "verified": "2026-09-29"},
  {"model": "gpt-5.5", "model_label": "GPT-5.5", "platform": "foundry", "plan_id": "az_t1", "platform_label": "Azure OpenAI", "plan_label": "Tier 1 (Global Standard)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.5", "model_label": "GPT-5.5", "platform": "foundry", "plan_id": "az_t3", "platform_label": "Azure OpenAI", "plan_label": "Tier 3 (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.5", "model_label": "GPT-5.5", "platform": "foundry", "plan_id": "az_t6", "platform_label": "Azure OpenAI", "plan_label": "Tier 6 (Global Standard)", "rpm": {"status": "enforced", "value": 15000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 15000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 依使用量、合約關係（EA／MCA-E 較高）與付款紀錄自動指派層級，對照表未公開", "RPM 為每 1,000 TPM 1 次（依層級表推算），並以 1–10 秒視窗執行，短時間突發可能被擋", "TPM 在請求到達時以提示詞加 max_tokens 估算扣除，快取的輸入仍計入", "免費層（Tier 0）沒有任何額度"], "source": "https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits", "verified": "2026-09-29"},
  {"model": "gpt-5.5", "model_label": "GPT-5.5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "數值出自 AWS 配額總表（General Reference），皆可申請調升", "區域內推論比 OpenAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "gemini-3.1-pro-preview", "model_label": "Gemini 3.1 Pro", "platform": "google_ai", "plan_id": "g_t1", "platform_label": "Gemini API", "plan_label": "Tier 1（已綁定帳單）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 10.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $10，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.1-pro-preview", "model_label": "Gemini 3.1 Pro", "platform": "google_ai", "plan_id": "g_t2", "platform_label": "Gemini API", "plan_label": "Tier 2（已付 $100 且滿 3 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 50.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $50，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.1-pro-preview", "model_label": "Gemini 3.1 Pro", "platform": "google_ai", "plan_id": "g_t3", "platform_label": "Gemini API", "plan_label": "Tier 3（已付 $1,000 且滿 30 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 200.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $200，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.1-pro-preview", "model_label": "Gemini 3.1 Pro", "platform": "vertex", "plan_id": "vx_t1", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 1（30 天消費 $10–$250）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.1-pro-preview", "model_label": "Gemini 3.1 Pro", "platform": "vertex", "plan_id": "vx_t2", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 2（30 天消費 $250–$2K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.1-pro-preview", "model_label": "Gemini 3.1 Pro", "platform": "vertex", "plan_id": "vx_t3", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 3（30 天消費 $2K–$50K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.1-pro-preview", "model_label": "Gemini 3.1 Pro", "platform": "vertex", "plan_id": "vx_t4", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 4（30 天消費 $50K 以上）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.8-flash", "model_label": "Gemini 3.8 Flash", "platform": "google_ai", "plan_id": "g_t1", "platform_label": "Gemini API", "plan_label": "Tier 1（已綁定帳單）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 10.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $10，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.8-flash", "model_label": "Gemini 3.8 Flash", "platform": "google_ai", "plan_id": "g_t2", "platform_label": "Gemini API", "plan_label": "Tier 2（已付 $100 且滿 3 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 50.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $50，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.8-flash", "model_label": "Gemini 3.8 Flash", "platform": "google_ai", "plan_id": "g_t3", "platform_label": "Gemini API", "plan_label": "Tier 3（已付 $1,000 且滿 30 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 200.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $200，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.8-flash", "model_label": "Gemini 3.8 Flash", "platform": "vertex", "plan_id": "vx_t1", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 1（30 天消費 $10–$250）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.8-flash", "model_label": "Gemini 3.8 Flash", "platform": "vertex", "plan_id": "vx_t2", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 2（30 天消費 $250–$2K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.8-flash", "model_label": "Gemini 3.8 Flash", "platform": "vertex", "plan_id": "vx_t3", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 3（30 天消費 $2K–$50K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.8-flash", "model_label": "Gemini 3.8 Flash", "platform": "vertex", "plan_id": "vx_t4", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 4（30 天消費 $50K 以上）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.5-flash-lite", "model_label": "Gemini 3.5 Flash-Lite", "platform": "google_ai", "plan_id": "g_t1", "platform_label": "Gemini API", "plan_label": "Tier 1（已綁定帳單）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 10.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $10，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.5-flash-lite", "model_label": "Gemini 3.5 Flash-Lite", "platform": "google_ai", "plan_id": "g_t2", "platform_label": "Gemini API", "plan_label": "Tier 2（已付 $100 且滿 3 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 50.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $50，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.5-flash-lite", "model_label": "Gemini 3.5 Flash-Lite", "platform": "google_ai", "plan_id": "g_t3", "platform_label": "Gemini API", "plan_label": "Tier 3（已付 $1,000 且滿 30 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 200.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $200，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.5-flash-lite", "model_label": "Gemini 3.5 Flash-Lite", "platform": "vertex", "plan_id": "vx_t1", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 1（30 天消費 $10–$250）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.5-flash-lite", "model_label": "Gemini 3.5 Flash-Lite", "platform": "vertex", "plan_id": "vx_t2", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 2（30 天消費 $250–$2K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.5-flash-lite", "model_label": "Gemini 3.5 Flash-Lite", "platform": "vertex", "plan_id": "vx_t3", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 3（30 天消費 $2K–$50K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.5-flash-lite", "model_label": "Gemini 3.5 Flash-Lite", "platform": "vertex", "plan_id": "vx_t4", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 4（30 天消費 $50K 以上）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.1-flash-lite", "model_label": "Gemini 3.1 Flash-Lite", "platform": "google_ai", "plan_id": "g_t1", "platform_label": "Gemini API", "plan_label": "Tier 1（已綁定帳單）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 10.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $10，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.1-flash-lite", "model_label": "Gemini 3.1 Flash-Lite", "platform": "google_ai", "plan_id": "g_t2", "platform_label": "Gemini API", "plan_label": "Tier 2（已付 $100 且滿 3 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 50.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $50，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.1-flash-lite", "model_label": "Gemini 3.1 Flash-Lite", "platform": "google_ai", "plan_id": "g_t3", "platform_label": "Gemini API", "plan_label": "Tier 3（已付 $1,000 且滿 30 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 200.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $200，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-3.1-flash-lite", "model_label": "Gemini 3.1 Flash-Lite", "platform": "vertex", "plan_id": "vx_t1", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 1（30 天消費 $10–$250）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.1-flash-lite", "model_label": "Gemini 3.1 Flash-Lite", "platform": "vertex", "plan_id": "vx_t2", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 2（30 天消費 $250–$2K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.1-flash-lite", "model_label": "Gemini 3.1 Flash-Lite", "platform": "vertex", "plan_id": "vx_t3", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 3（30 天消費 $2K–$50K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-3.1-flash-lite", "model_label": "Gemini 3.1 Flash-Lite", "platform": "vertex", "plan_id": "vx_t4", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 4（30 天消費 $50K 以上）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-pro", "model_label": "Gemini 2.5 Pro", "platform": "google_ai", "plan_id": "g_t1", "platform_label": "Gemini API", "plan_label": "Tier 1（已綁定帳單）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 10.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $10，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-2.5-pro", "model_label": "Gemini 2.5 Pro", "platform": "google_ai", "plan_id": "g_t2", "platform_label": "Gemini API", "plan_label": "Tier 2（已付 $100 且滿 3 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 50.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $50，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-2.5-pro", "model_label": "Gemini 2.5 Pro", "platform": "google_ai", "plan_id": "g_t3", "platform_label": "Gemini API", "plan_label": "Tier 3（已付 $1,000 且滿 30 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 200.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $200，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-2.5-pro", "model_label": "Gemini 2.5 Pro", "platform": "vertex", "plan_id": "vx_t1", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 1（30 天消費 $10–$250）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 500000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-pro", "model_label": "Gemini 2.5 Pro", "platform": "vertex", "plan_id": "vx_t2", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 2（30 天消費 $250–$2K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 1000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-pro", "model_label": "Gemini 2.5 Pro", "platform": "vertex", "plan_id": "vx_t3", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 3（30 天消費 $2K–$50K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-pro", "model_label": "Gemini 2.5 Pro", "platform": "vertex", "plan_id": "vx_t4", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 4（30 天消費 $50K 以上）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-flash", "model_label": "Gemini 2.5 Flash", "platform": "google_ai", "plan_id": "g_t1", "platform_label": "Gemini API", "plan_label": "Tier 1（已綁定帳單）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 10.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $10，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-2.5-flash", "model_label": "Gemini 2.5 Flash", "platform": "google_ai", "plan_id": "g_t2", "platform_label": "Gemini API", "plan_label": "Tier 2（已付 $100 且滿 3 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 50.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $50，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-2.5-flash", "model_label": "Gemini 2.5 Flash", "platform": "google_ai", "plan_id": "g_t3", "platform_label": "Gemini API", "plan_label": "Tier 3（已付 $1,000 且滿 30 天）", "rpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "itpm": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "otpm": null, "tpm": null, "rpd": {"status": "unpublished", "note": "Google 已不公開各模型的數字，請登入 AI Studio 查看專案的實際額度"}, "usd10m": {"status": "enforced", "value": 200.0}, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["RPM、TPM（輸入）、RPD 仍會限制，但 Google 已不公開各模型數字，需登入 AI Studio 查看", "官方公開的只有每 10 分鐘滾動消費上限 $200，超過會收到 429", "限制以專案為單位，不是 API 金鑰；RPD 於太平洋時間午夜重置"], "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "verified": "2026-09-29"},
  {"model": "gemini-2.5-flash", "model_label": "Gemini 2.5 Flash", "platform": "vertex", "plan_id": "vx_t1", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 1（30 天消費 $10–$250）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 2000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-flash", "model_label": "Gemini 2.5 Flash", "platform": "vertex", "plan_id": "vx_t2", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 2（30 天消費 $250–$2K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 4000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-flash", "model_label": "Gemini 2.5 Flash", "platform": "vertex", "plan_id": "vx_t3", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 3（30 天消費 $2K–$50K）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "gemini-2.5-flash", "model_label": "Gemini 2.5 Flash", "platform": "vertex", "plan_id": "vx_t4", "platform_label": "GCP Vertex", "plan_label": "Standard PayGo Tier 4（30 天消費 $50K 以上）", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000000.0, "soft": true}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["基準 TPM 依組織過去 30 天的 Vertex 總消費決定，並非硬上限；超出部分以盡力方式服務，可能被節流", "官方未說明基準 TPM 是否計入輸出，此處保守以輸入加輸出計算", "不設 RPM；數值以送往全域端點為準，區域端點另加 10% 價格", "需要保證容量可改買 Provisioned Throughput"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo", "verified": "2026-09-29"},
  {"model": "grok-4.7", "model_label": "Grok 4.7", "platform": "xai", "plan_id": "x_t0", "platform_label": "xAI API", "plan_label": "Tier 0（預設）", "rpm": {"status": "enforced", "value": 9000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 150 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.7", "model_label": "Grok 4.7", "platform": "xai", "plan_id": "x_t2", "platform_label": "xAI API", "plan_label": "Tier 2（累計消費 $250 起）", "rpm": {"status": "enforced", "value": 12480.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 60000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 208 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.7", "model_label": "Grok 4.7", "platform": "xai", "plan_id": "x_t4", "platform_label": "xAI API", "plan_label": "Tier 4（累計消費 $5,000 起）", "rpm": {"status": "enforced", "value": 30000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 100000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 500 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.7", "model_label": "Grok 4.7", "platform": "oci", "plan_id": "oci_ondemand", "platform_label": "Oracle OCI", "plan_label": "Generative AI 隨選 (On-Demand)", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "OCI 只公布調額用的限制名稱，未公布預設 TPM"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["OCI 的 Grok 只提供隨選模式，沒有專屬 AI 叢集", "OCI 尚未公布此模型的限制名稱與預設值", "標準處理採 xAI 牌價；優先處理（priority）單價兩倍，僅在回應帶 service_tier: priority 時計費"], "source": "https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "xai", "plan_id": "x_t0", "platform_label": "xAI API", "plan_label": "Tier 0（預設）", "rpm": {"status": "enforced", "value": 9000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 150 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "xai", "plan_id": "x_t2", "platform_label": "xAI API", "plan_label": "Tier 2（累計消費 $250 起）", "rpm": {"status": "enforced", "value": 12480.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 60000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 208 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "xai", "plan_id": "x_t4", "platform_label": "xAI API", "plan_label": "Tier 4（累計消費 $5,000 起）", "rpm": {"status": "enforced", "value": 30000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 100000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 500 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "otpm": {"status": "unpublished", "note": "AWS 配額總表未列出此模型的預設值，實際額度依帳號而定"}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": true, "tpm_reserves_max_tokens": false, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": false, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "AWS 配額總表未列出此模型的 Mantle 預設值，實際額度依帳號而定", "Mantle 僅提供區域內推論，比 xAI 牌價另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "bedrock", "plan_id": "runtime", "platform_label": "AWS Bedrock", "plan_label": "bedrock-runtime（全域跨區）", "rpm": {"status": "not_enforced", "note": "AWS 未對此模型在 bedrock-runtime 設定 RPM 配額，僅以 TPM 節流"}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": false, "output_burndown": 1.0, "list_priced": true, "notes": ["TPM 為輸入加輸出合併計算；准入時預扣 input + max_tokens，完成後按實際用量重算", "AWS 說明頁：未列名的模型 output burndown 為 1:1", "全域跨區推論以 xAI 牌價計費；美國跨區與區域內另加 10%"], "source": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "foundry", "plan_id": "az_low", "platform_label": "Azure Foundry", "plan_label": "Low 層級 (Global Standard)", "rpm": {"status": "enforced", "value": 0.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 0.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 上的 Grok 4.6 目前為 Preview，context 200K、單次輸出上限 128K", "層級依訂閱與部署設定決定，官方未公開對照表", "Azure 未說明 Grok 的計量方式，此處沿用 Azure 的一般算法：以提示詞加 max_tokens 估算扣除", "此層級預設為 0，部署前必須先申請"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "foundry", "plan_id": "az_medium", "platform_label": "Azure Foundry", "plan_label": "Medium 層級 (Global Standard)", "rpm": {"status": "enforced", "value": 50.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 上的 Grok 4.6 目前為 Preview，context 200K、單次輸出上限 128K", "層級依訂閱與部署設定決定，官方未公開對照表", "Azure 未說明 Grok 的計量方式，此處沿用 Azure 的一般算法：以提示詞加 max_tokens 估算扣除"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "foundry", "plan_id": "az_high", "platform_label": "Azure Foundry", "plan_label": "High 層級 (Global Standard)", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 5000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 上的 Grok 4.6 目前為 Preview，context 200K、單次輸出上限 128K", "層級依訂閱與部署設定決定，官方未公開對照表", "Azure 未說明 Grok 的計量方式，此處沿用 Azure 的一般算法：以提示詞加 max_tokens 估算扣除"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "vertex", "plan_id": "vx_global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 13.0}, "itpm": {"status": "enforced", "value": 188000.0}, "otpm": {"status": "enforced", "value": 16000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Grok 在 Vertex 只有一個全域配額，全域端點與美國多區域端點共用同一個額度", "快取讀取是否計入輸入 TPM 官方未說明，此處保守計入", "預設額度偏低，正式上線前通常需要申請調升"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/grok", "verified": "2026-09-29"},
  {"model": "grok-4.6", "model_label": "Grok 4.6", "platform": "oci", "plan_id": "oci_ondemand", "platform_label": "Oracle OCI", "plan_label": "Generative AI 隨選 (On-Demand)", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "OCI 只公布調額用的限制名稱，未公布預設 TPM"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["OCI 的 Grok 只提供隨選模式，沒有專屬 AI 叢集", "調額時在 Limits 申請 grok-4-6-tokens-per-minute-count", "標準處理採 xAI 牌價；優先處理（priority）單價兩倍，僅在回應帶 service_tier: priority 時計費"], "source": "https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm", "verified": "2026-09-29"},
  {"model": "grok-4.5", "model_label": "Grok 4.5", "platform": "xai", "plan_id": "x_t0", "platform_label": "xAI API", "plan_label": "Tier 0（預設）", "rpm": {"status": "enforced", "value": 9000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 50000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 150 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.5", "model_label": "Grok 4.5", "platform": "xai", "plan_id": "x_t2", "platform_label": "xAI API", "plan_label": "Tier 2（累計消費 $250 起）", "rpm": {"status": "enforced", "value": 12480.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 60000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 208 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.5", "model_label": "Grok 4.5", "platform": "xai", "plan_id": "x_t4", "platform_label": "xAI API", "plan_label": "Tier 4（累計消費 $5,000 起）", "rpm": {"status": "enforced", "value": 30000.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 100000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 500 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.3", "model_label": "Grok 4.3", "platform": "xai", "plan_id": "x_t0", "platform_label": "xAI API", "plan_label": "Tier 0（預設）", "rpm": {"status": "enforced", "value": 2220.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 37 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.3", "model_label": "Grok 4.3", "platform": "xai", "plan_id": "x_t2", "platform_label": "xAI API", "plan_label": "Tier 2（累計消費 $250 起）", "rpm": {"status": "enforced", "value": 4500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 25000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 75 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.3", "model_label": "Grok 4.3", "platform": "xai", "plan_id": "x_t4", "platform_label": "xAI API", "plan_label": "Tier 4（累計消費 $5,000 起）", "rpm": {"status": "enforced", "value": 12480.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 85000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 208 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.3", "model_label": "Grok 4.3", "platform": "foundry", "plan_id": "az_gs", "platform_label": "Azure Foundry", "plan_label": "Global Standard", "rpm": {"status": "unpublished", "note": "Azure 只公布 Grok 4.6 的配額，此模型需在 Foundry 入口網站查看"}, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "Azure 只公布 Grok 4.6 的配額，此模型需在 Foundry 入口網站查看"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 上為 Preview，context 約 200K–262K、單次輸出上限 8,192 tokens", "Data Zone Standard (US) 比 xAI 牌價另加 10%"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok", "verified": "2026-09-29"},
  {"model": "grok-4.3", "model_label": "Grok 4.3", "platform": "vertex", "plan_id": "vx_global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 100.0}, "itpm": {"status": "enforced", "value": 540000.0}, "otpm": {"status": "enforced", "value": 80000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["此模型在 Vertex 仍為 Preview", "Grok 在 Vertex 只有一個全域配額，全域端點與美國多區域端點共用同一個額度", "快取讀取是否計入輸入 TPM 官方未說明，此處保守計入", "預設額度偏低，正式上線前通常需要申請調升"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/grok", "verified": "2026-09-29"},
  {"model": "grok-4.3", "model_label": "Grok 4.3", "platform": "oci", "plan_id": "oci_ondemand", "platform_label": "Oracle OCI", "plan_label": "Generative AI 隨選 (On-Demand)", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "OCI 只公布調額用的限制名稱，未公布預設 TPM"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["OCI 的 Grok 只提供隨選模式，沒有專屬 AI 叢集", "調額時在 Limits 申請 grok-4-3-tokens-per-minute-count", "標準處理採 xAI 牌價；優先處理（priority）單價兩倍，僅在回應帶 service_tier: priority 時計費"], "source": "https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-reasoning", "model_label": "Grok 4.20 Reasoning", "platform": "xai", "plan_id": "x_t0", "platform_label": "xAI API", "plan_label": "Tier 0（預設）", "rpm": {"status": "enforced", "value": 2220.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 37 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-reasoning", "model_label": "Grok 4.20 Reasoning", "platform": "xai", "plan_id": "x_t2", "platform_label": "xAI API", "plan_label": "Tier 2（累計消費 $250 起）", "rpm": {"status": "enforced", "value": 4500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 25000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 75 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-reasoning", "model_label": "Grok 4.20 Reasoning", "platform": "xai", "plan_id": "x_t4", "platform_label": "xAI API", "plan_label": "Tier 4（累計消費 $5,000 起）", "rpm": {"status": "enforced", "value": 12480.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 85000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 208 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-reasoning", "model_label": "Grok 4.20 Reasoning", "platform": "foundry", "plan_id": "az_gs", "platform_label": "Azure Foundry", "plan_label": "Global Standard", "rpm": {"status": "unpublished", "note": "Azure 只公布 Grok 4.6 的配額，此模型需在 Foundry 入口網站查看"}, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "Azure 只公布 Grok 4.6 的配額，此模型需在 Foundry 入口網站查看"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 上為 Preview，context 約 200K–262K、單次輸出上限 8,192 tokens", "Data Zone Standard (US) 比 xAI 牌價另加 10%"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-reasoning", "model_label": "Grok 4.20 Reasoning", "platform": "vertex", "plan_id": "vx_global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 100.0}, "itpm": {"status": "enforced", "value": 540000.0}, "otpm": {"status": "enforced", "value": 80000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Grok 在 Vertex 只有一個全域配額，全域端點與美國多區域端點共用同一個額度", "快取讀取是否計入輸入 TPM 官方未說明，此處保守計入", "預設額度偏低，正式上線前通常需要申請調升"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/grok", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-reasoning", "model_label": "Grok 4.20 Reasoning", "platform": "oci", "plan_id": "oci_ondemand", "platform_label": "Oracle OCI", "plan_label": "Generative AI 隨選 (On-Demand)", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "OCI 只公布調額用的限制名稱，未公布預設 TPM"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["OCI 的 Grok 只提供隨選模式，沒有專屬 AI 叢集", "調額時在 Limits 申請 grok-4-2-reasoning-tokens-per-minute-count", "標準處理採 xAI 牌價；優先處理（priority）單價兩倍，僅在回應帶 service_tier: priority 時計費"], "source": "https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-non-reasoning", "model_label": "Grok 4.20 Non-reasoning", "platform": "xai", "plan_id": "x_t0", "platform_label": "xAI API", "plan_label": "Tier 0（預設）", "rpm": {"status": "enforced", "value": 2220.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 37 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-non-reasoning", "model_label": "Grok 4.20 Non-reasoning", "platform": "xai", "plan_id": "x_t2", "platform_label": "xAI API", "plan_label": "Tier 2（累計消費 $250 起）", "rpm": {"status": "enforced", "value": 4500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 25000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 75 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-non-reasoning", "model_label": "Grok 4.20 Non-reasoning", "platform": "xai", "plan_id": "x_t4", "platform_label": "xAI API", "plan_label": "Tier 4（累計消費 $5,000 起）", "rpm": {"status": "enforced", "value": 12480.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 85000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 208 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-non-reasoning", "model_label": "Grok 4.20 Non-reasoning", "platform": "foundry", "plan_id": "az_gs", "platform_label": "Azure Foundry", "plan_label": "Global Standard", "rpm": {"status": "unpublished", "note": "Azure 只公布 Grok 4.6 的配額，此模型需在 Foundry 入口網站查看"}, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "Azure 只公布 Grok 4.6 的配額，此模型需在 Foundry 入口網站查看"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": true, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Azure 上為 Preview，context 約 200K–262K、單次輸出上限 8,192 tokens", "Data Zone Standard (US) 比 xAI 牌價另加 10%"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-non-reasoning", "model_label": "Grok 4.20 Non-reasoning", "platform": "vertex", "plan_id": "vx_global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 100.0}, "itpm": {"status": "enforced", "value": 540000.0}, "otpm": {"status": "enforced", "value": 80000.0}, "tpm": null, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["Grok 在 Vertex 只有一個全域配額，全域端點與美國多區域端點共用同一個額度", "快取讀取是否計入輸入 TPM 官方未說明，此處保守計入", "預設額度偏低，正式上線前通常需要申請調升"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/grok", "verified": "2026-09-29"},
  {"model": "grok-4.20-0309-non-reasoning", "model_label": "Grok 4.20 Non-reasoning", "platform": "oci", "plan_id": "oci_ondemand", "platform_label": "Oracle OCI", "plan_label": "Generative AI 隨選 (On-Demand)", "rpm": null, "itpm": null, "otpm": null, "tpm": {"status": "unpublished", "note": "OCI 只公布調額用的限制名稱，未公布預設 TPM"}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["OCI 的 Grok 只提供隨選模式，沒有專屬 AI 叢集", "調額時在 Limits 申請 grok-4-2-non-reasoning-tokens-per-minute-count", "標準處理採 xAI 牌價；優先處理（priority）單價兩倍，僅在回應帶 service_tier: priority 時計費"], "source": "https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm", "verified": "2026-09-29"},
  {"model": "grok-build-0.1", "model_label": "Grok Build 0.1", "platform": "xai", "plan_id": "x_t0", "platform_label": "xAI API", "plan_label": "Tier 0（預設）", "rpm": {"status": "enforced", "value": 2220.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 10000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 37 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-build-0.1", "model_label": "Grok Build 0.1", "platform": "xai", "plan_id": "x_t2", "platform_label": "xAI API", "plan_label": "Tier 2（累計消費 $250 起）", "rpm": {"status": "enforced", "value": 4500.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 25000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 75 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
  {"model": "grok-build-0.1", "model_label": "Grok Build 0.1", "platform": "xai", "plan_id": "x_t4", "platform_label": "xAI API", "plan_label": "Tier 4（累計消費 $5,000 起）", "rpm": {"status": "enforced", "value": 12480.0}, "itpm": null, "otpm": null, "tpm": {"status": "enforced", "value": 85000000.0}, "rpd": null, "usd10m": null, "reserves_max_tokens": false, "tpm_reserves_max_tokens": false, "input_cached_counts": true, "output_burndown": 1.0, "list_priced": true, "notes": ["每秒 208 次請求", "xAI 以「每秒請求數」限制：每秒上限為 RPM ÷ 60，同一秒內湧入仍會被擋，此處換算為每分鐘顯示", "TPM 計入輸入、輸出、思考與快取讀取的所有 token，快取不會省配額", "層級依 2026-01-01 起的累計消費自動升級且永不降級；限制以團隊為單位、各模型分開計算"], "source": "https://docs.x.ai/developers/rate-limits", "verified": "2026-09-29"},
];

if (typeof module !== 'undefined') { module.exports = { LLM_CONST, LLM_LINES, LLM_MODELS, LLM_SCENARIOS, LLM_PLANS }; }
