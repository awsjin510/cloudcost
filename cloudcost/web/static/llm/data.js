// GENERATED FILE — do not edit by hand.
// Regenerate with:  python -m cloudcost.llm.export
// Source of truth:  cloudcost/llm/catalog.py
//
// Quota values are platform DEFAULTS, not model limits; every one of them
// can be raised on request. Each row carries the document it came from.

const LLM_CONST = {"MAX_OUTPUT_TOKENS": 128000, "VERIFIED": "2026-09", "AMPLE_THRESHOLD": 0.7, "MAX_SUGGESTED_CACHE_RATE": 0.95, "PEAK_FACTORS": {"flat": 1.5, "normal": 3.0, "spiky": 6.0}, "ACTIVE_HOURS_PER_DAY": 8, "WORKING_DAYS_PER_MONTH": 22};

const LLM_MODELS = [
  {
    "model": "fable-5-1",
    "label": "Claude Fable 5.1",
    "pricing": {
      "input_per_mtok": 10.0,
      "output_per_mtok": 50.0,
      "cache_read_per_mtok": 0.25,
      "cache_write_5m_per_mtok": 12.5
    },
    "notes": [
      "快取讀取為輸入價的 0.025 倍，是所有模型中最低的，有做 prompt caching 時省下的比例最大"
    ]
  },
  {
    "model": "fable-5",
    "label": "Claude Fable 5",
    "pricing": {
      "input_per_mtok": 10.0,
      "output_per_mtok": 50.0,
      "cache_read_per_mtok": 1.0,
      "cache_write_5m_per_mtok": 12.5
    },
    "notes": [
      "快取讀取為輸入價的 0.1 倍，比 Fable 5.1 貴 4 倍"
    ]
  },
  {
    "model": "opus-5",
    "label": "Claude Opus 5",
    "pricing": {
      "input_per_mtok": 5.0,
      "output_per_mtok": 25.0,
      "cache_read_per_mtok": 0.5,
      "cache_write_5m_per_mtok": 6.25
    },
    "notes": [
      "單價為 Fable 的一半，配額普遍較寬鬆，多數情境是更划算的起點"
    ]
  },
  {
    "model": "sonnet-5",
    "label": "Claude Sonnet 5",
    "pricing": {
      "input_per_mtok": 2.0,
      "output_per_mtok": 10.0,
      "cache_read_per_mtok": 0.2,
      "cache_write_5m_per_mtok": 2.5
    },
    "notes": [
      "高流量生產工作負載的預設選擇，單價為 Fable 的五分之一"
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
    "max_tokens": 1000,
    "suggested_model": "sonnet-5",
    "messages_per_user_per_day": 12.0
  },
  {
    "scenario_id": "rag",
    "label": "知識庫問答",
    "blurb": "每次帶入檢索到的文件片段，提示詞偏長",
    "icon": "&#128218;",
    "input_tokens_per_request": 20000,
    "output_tokens_per_request": 2000,
    "cache_hit_rate": 0.5,
    "max_tokens": 4000,
    "suggested_model": "sonnet-5",
    "messages_per_user_per_day": 8.0
  },
  {
    "scenario_id": "summarize",
    "label": "文件摘要",
    "blurb": "一次讀入整份文件，輸出精簡，快取效益低",
    "icon": "&#128196;",
    "input_tokens_per_request": 30000,
    "output_tokens_per_request": 1500,
    "cache_hit_rate": 0.15,
    "max_tokens": 3000,
    "suggested_model": "sonnet-5",
    "messages_per_user_per_day": 4.0
  },
  {
    "scenario_id": "coding",
    "label": "程式開發代理",
    "blurb": "長對話多輪工具呼叫，前綴長但高度可快取",
    "icon": "&#129302;",
    "input_tokens_per_request": 60000,
    "output_tokens_per_request": 8000,
    "cache_hit_rate": 0.8,
    "max_tokens": 16000,
    "suggested_model": "fable-5-1",
    "messages_per_user_per_day": 60.0
  },
  {
    "scenario_id": "writing",
    "label": "內容生成",
    "blurb": "提示詞短、產出長，成本集中在 Output",
    "icon": "&#9998;",
    "input_tokens_per_request": 2000,
    "output_tokens_per_request": 4000,
    "cache_hit_rate": 0.25,
    "max_tokens": 8000,
    "suggested_model": "opus-5",
    "messages_per_user_per_day": 6.0
  }
];

const LLM_PLANS = [
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 500000.0}, "otpm": {"status": "enforced", "value": 100000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 1500000.0}, "otpm": {"status": "enforced", "value": 300000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "otpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "reserves_max_tokens": true, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "目前僅 Opus 4.7 有公布的 Mantle 預設值（20M 輸入 / 4M 輸出 TPM）", "可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html", "verified": "2026-09"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 0.0}, "itpm": {"status": "enforced", "value": 0.0}, "otpm": {"status": "enforced", "value": 0.0}, "reserves_max_tokens": false, "notes": ["隨用隨付訂閱的 Fable 預設配額為 0，部署前必須先申請", "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "reserves_max_tokens": false, "notes": ["Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
  {"model": "fable-5-1", "model_label": "Claude Fable 5.1", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）", "多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 500000.0}, "otpm": {"status": "enforced", "value": 100000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 1500000.0}, "otpm": {"status": "enforced", "value": 300000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍", "需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "otpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "reserves_max_tokens": true, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "目前僅 Opus 4.7 有公布的 Mantle 預設值（20M 輸入 / 4M 輸出 TPM）", "可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 0.0}, "itpm": {"status": "enforced", "value": 0.0}, "otpm": {"status": "enforced", "value": 0.0}, "reserves_max_tokens": false, "notes": ["隨用隨付訂閱的 Fable 預設配額為 0，部署前必須先申請", "Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 4000.0}, "itpm": {"status": "enforced", "value": 4000000.0}, "otpm": {"status": "enforced", "value": 800000.0}, "reserves_max_tokens": false, "notes": ["Fable 於 Foundry 目前為 Preview，僅有 Anthropic 託管版本", "配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
  {"model": "fable-5", "model_label": "Claude Fable 5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "reserves_max_tokens": false, "notes": ["Fable 5.1 與 Fable 5 共用同一個額度，拆流量不會變成兩倍（共用 anthropic-claude-fable 沿襲配額）", "多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "reserves_max_tokens": false, "notes": ["限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "reserves_max_tokens": false, "notes": [], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "reserves_max_tokens": false, "notes": ["需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "otpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "reserves_max_tokens": true, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "目前僅 Opus 4.7 有公布的 Mantle 預設值（20M 輸入 / 4M 輸出 TPM）", "可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 40.0}, "itpm": {"status": "enforced", "value": 40000.0}, "otpm": {"status": "enforced", "value": 8000.0}, "reserves_max_tokens": false, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "reserves_max_tokens": false, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2000.0}, "itpm": {"status": "enforced", "value": 20000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "reserves_max_tokens": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
  {"model": "opus-5", "model_label": "Claude Opus 5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "reserves_max_tokens": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "anthropic", "plan_id": "start", "platform_label": "Anthropic API", "plan_label": "Start 層級", "rpm": {"status": "enforced", "value": 1000.0}, "itpm": {"status": "enforced", "value": 2000000.0}, "otpm": {"status": "enforced", "value": 400000.0}, "reserves_max_tokens": false, "notes": ["限制掛在組織層級，可再往下分配給各 Workspace"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "anthropic", "plan_id": "build", "platform_label": "Anthropic API", "plan_label": "Build 層級", "rpm": {"status": "enforced", "value": 5000.0}, "itpm": {"status": "enforced", "value": 5000000.0}, "otpm": {"status": "enforced", "value": 1000000.0}, "reserves_max_tokens": false, "notes": [], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "anthropic", "plan_id": "scale", "platform_label": "Anthropic API", "plan_label": "Scale 層級", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "reserves_max_tokens": false, "notes": ["需要更高上限請走 Custom 層級洽談"], "source": "https://platform.claude.com/docs/en/api/rate-limits", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "bedrock", "plan_id": "mantle", "platform_label": "AWS Bedrock", "plan_label": "bedrock-mantle 端點", "rpm": {"status": "not_enforced", "note": "Mantle 端點不設 RPM 配額，僅以 ITPM / OTPM 節流"}, "itpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "otpm": {"status": "unpublished", "note": "Bedrock 僅對部分模型公布每帳號 TPM 配額，其餘由服務內部容量決定"}, "reserves_max_tokens": true, "notes": ["准入時預扣 input + max_tokens 的 ITPM，回應結束後退還未用部分", "與 bedrock-runtime 端點的配額完全獨立，兩邊需分開規劃", "目前僅 Opus 4.7 有公布的 Mantle 預設值（20M 輸入 / 4M 輸出 TPM）", "可在 Service Quotas 主控台搜尋 Bedrock Mantle 查到本帳號實際額度，並填入上方欄位"], "source": "https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "foundry", "plan_id": "payg", "platform_label": "Azure Foundry", "plan_label": "隨用隨付 (Global Standard)", "rpm": {"status": "enforced", "value": 40.0}, "itpm": {"status": "enforced", "value": 40000.0}, "otpm": {"status": "enforced", "value": 8000.0}, "reserves_max_tokens": false, "notes": ["隨用隨付的預設額度偏低，正式上線前通常仍需申請調升", "免費試用訂閱的預設額度同樣為 0"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "foundry", "plan_id": "enterprise", "platform_label": "Azure Foundry", "plan_label": "Enterprise / MCA-E (Global Standard)", "rpm": {"status": "enforced", "value": 10000.0}, "itpm": {"status": "enforced", "value": 10000000.0}, "otpm": {"status": "enforced", "value": 2000000.0}, "reserves_max_tokens": false, "notes": ["配額掛在訂閱層級，同型號的 Global Standard 部署跨區共用同一個額度池"], "source": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "vertex", "plan_id": "global", "platform_label": "GCP Vertex", "plan_label": "全域端點 (global)", "rpm": {"status": "enforced", "value": 2500.0}, "itpm": {"status": "enforced", "value": 25000000.0}, "otpm": {"status": "enforced", "value": 2500000.0}, "reserves_max_tokens": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "輸入 TPM 計入未快取與快取寫入的 token"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
  {"model": "sonnet-5", "model_label": "Claude Sonnet 5", "platform": "vertex", "plan_id": "multi_region", "platform_label": "GCP Vertex", "plan_label": "多區域端點 (us / eu)", "rpm": {"status": "enforced", "value": 1250.0}, "itpm": {"status": "enforced", "value": 12500000.0}, "otpm": {"status": "enforced", "value": 1250000.0}, "reserves_max_tokens": false, "notes": ["2026-05-26 之後推出的模型使用共用沿襲配額，同系列各版本共用同一個額度桶", "多區域端點配額與全域端點是獨立的額度池，兩者互不相通", "多區域端點另有 10% 價格溢價"], "source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/quotas", "verified": "2026-09"},
];

if (typeof module !== 'undefined') { module.exports = { LLM_CONST, LLM_MODELS, LLM_SCENARIOS, LLM_PLANS }; }
