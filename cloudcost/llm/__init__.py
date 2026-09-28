"""LLM capacity and cost planning for Claude deployments.

`catalog` holds the reference data (pricing, platform quotas); `planner`
turns a workload description into verdicts, costs and next actions.
"""

from cloudcost.llm.catalog import (
    MAX_OUTPUT_TOKENS,
    VERIFIED,
    Limit,
    LimitStatus,
    LLMModel,
    LLMPlatform,
    ModelInfo,
    ModelPricing,
    QuotaPlan,
    get_model,
    list_models,
    list_plans,
)
from cloudcost.llm.planner import (
    Action,
    ActionKind,
    AppWorkload,
    CostEstimate,
    DimensionResult,
    LLMWorkload,
    QuotaOverride,
    QuotaPlanResult,
    QuotaReport,
    Verdict,
    evaluate_workload,
)

__all__ = [
    "MAX_OUTPUT_TOKENS",
    "VERIFIED",
    "Action",
    "ActionKind",
    "AppWorkload",
    "CostEstimate",
    "DimensionResult",
    "LLMModel",
    "LLMPlatform",
    "LLMWorkload",
    "Limit",
    "LimitStatus",
    "ModelInfo",
    "ModelPricing",
    "QuotaOverride",
    "QuotaPlan",
    "QuotaPlanResult",
    "QuotaReport",
    "Verdict",
    "evaluate_workload",
    "get_model",
    "list_models",
    "list_plans",
]
