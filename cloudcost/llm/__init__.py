"""LLM platform capacity planning (Claude Fable 5 / 5.1 quota modelling)."""

from cloudcost.llm.quota import (
    FABLE_MAX_OUTPUT_TOKENS,
    LimitStatus,
    LLMPlatform,
    LLMWorkload,
    QuotaPlan,
    QuotaPlanResult,
    QuotaReport,
    Verdict,
    evaluate_workload,
    list_plans,
)

__all__ = [
    "FABLE_MAX_OUTPUT_TOKENS",
    "LimitStatus",
    "LLMPlatform",
    "LLMWorkload",
    "QuotaPlan",
    "QuotaPlanResult",
    "QuotaReport",
    "Verdict",
    "evaluate_workload",
    "list_plans",
]
