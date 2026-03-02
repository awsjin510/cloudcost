"""AI-powered recommendation engine using the Claude API.

Analyzes multi-cloud cost comparison results and generates actionable
recommendations based on the user's usage scenario.
"""

from __future__ import annotations

import json
import logging
import os

import anthropic

from cloudcost.models.spec import ComparisonResult, GroupComparisonResult

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-5"
_MAX_TOKENS = 2048

_SYSTEM_PROMPT = """\
You are a cloud cost optimization expert. You will receive a JSON object \
containing cost estimates from four cloud providers (AWS, GCP, Azure, Oracle Cloud).

The top-level field "usage_scenario" describes the user's actual use case. \
**This is the most important input for personalising your response.** \
If it is non-empty, every section of your answer must reflect that scenario. \
If it is empty, give generic advice.

Your task is to provide a structured recommendation in **Traditional Chinese (繁體中文)** \
covering the following points:

1. **CP值最高方案** — Which provider offers the best cost-performance ratio and why, \
   taking the usage scenario into account.
2. **降低成本策略** — Which services can leverage Reserved Instances, Committed Use \
Discounts, Spot/Preemptible instances, or Annual Flex pricing to reduce costs.
3. **使用場景建議** — Tailored advice that directly addresses the described scenario \
(startup, enterprise, Taiwan-local needs, etc.). \
If a usage_scenario is provided, explicitly reference it and give specific advice \
for that scenario. If no scenario is given, give general advice.
4. **隱藏費用警示** — Hidden costs to watch out for: data transfer fees, \
support plans, cross-region replication, DNS queries, load balancer hours, \
managed NAT gateway, etc.

Keep the response concise (under 800 words), use bullet points, and include \
approximate dollar amounts where possible.
"""

_FALLBACK_FOOTER = (
    "\n> 注意：以上為基本比較，場景描述無法在此模式下影響建議內容。"
    "設定 ANTHROPIC_API_KEY 環境變數即可啟用場景化 AI 智能建議。"
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_recommendation(
    result: ComparisonResult | GroupComparisonResult,
    api_key: str | None = None,
) -> str:
    """Return a Traditional-Chinese cost optimisation recommendation.

    Falls back to a price-only summary when the Claude API is unavailable.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return _fallback_recommendation(result)

    try:
        return await _call_claude(_build_payload(result), key)
    except Exception:
        logger.warning("Claude API call failed, using fallback", exc_info=True)
        return _fallback_recommendation(result)


# ---------------------------------------------------------------------------
# Claude API call
# ---------------------------------------------------------------------------


async def _call_claude(payload: str, api_key: str) -> str:
    """Send *payload* to Claude and return the first text block."""
    client = anthropic.AsyncAnthropic(api_key=api_key)
    async with client.messages.stream(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": payload}],
    ) as stream:
        response = await stream.get_final_message()
    return next((b.text for b in response.content if b.type == "text"), "")


# ---------------------------------------------------------------------------
# Payload builders
# ---------------------------------------------------------------------------


def _build_payload(result: ComparisonResult | GroupComparisonResult) -> str:
    """Dispatch to the appropriate payload builder."""
    if isinstance(result, GroupComparisonResult):
        return _build_group_payload(result)
    return _build_single_payload(result)


def _build_single_payload(result: ComparisonResult) -> str:
    """Serialize a single-machine ComparisonResult for Claude."""
    estimates = [
        {
            "provider": est.provider.value,
            "region": est.region_name,
            "instance": est.matched_instance,
            "on_demand_monthly": est.total_monthly_on_demand,
            "reserved_1y_monthly": est.total_monthly_reserved_1y,
            "details": est.on_demand.details,
            "warnings": est.warnings,
        }
        for est in result.estimates
    ]
    data = {
        "usage_scenario": result.spec.description,
        "spec": {
            "cpu_cores": result.spec.cpu_cores,
            "ram_gb": result.spec.ram_gb,
            "storage_gb": result.spec.storage_gb,
            "storage_type": result.spec.storage_type.value,
            "network_transfer_gb": result.spec.network_transfer_gb,
            "database_type": result.spec.database_type.value,
            "region": result.spec.region.value,
            "monthly_hours": result.spec.monthly_hours,
            "os": result.spec.os,
        },
        "estimates": estimates,
        "cheapest_on_demand": (
            result.cheapest_on_demand.value if result.cheapest_on_demand else None
        ),
        "cheapest_reserved": (
            result.cheapest_reserved.value if result.cheapest_reserved else None
        ),
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def _build_group_payload(result: GroupComparisonResult) -> str:
    """Serialize a GroupComparisonResult for Claude."""
    group = result.group
    machines = [
        {
            "name": m.name or m.id,
            "role": m.role.value,
            "cpu": m.cpu,
            "ram": m.ram,
            "storage": m.storage,
            "quantity": m.quantity,
        }
        for m in group.machines
    ]
    estimates = [
        {
            "provider": est.provider.value,
            "region": est.region_name,
            "total_machines": est.total_machines,
            "total_monthly_on_demand": est.total_monthly_on_demand,
            "total_monthly_reserved_1y": est.total_monthly_reserved_1y,
            "machine_details": [
                {
                    "machine": md.machine.name or md.machine.id,
                    "role": md.machine.role.value,
                    "instance": md.matched_instance,
                    "unit_on_demand": md.unit_monthly_on_demand,
                    "quantity": md.machine.quantity,
                    "subtotal_on_demand": md.subtotal_on_demand,
                }
                for md in est.machines
            ],
            "warnings": est.warnings,
        }
        for est in result.estimates
    ]
    data = {
        "usage_scenario": group.description,
        "type": "workload_group",
        "group_name": group.name,
        "machines": machines,
        "region": group.region,
        "os": group.os,
        "monthly_hours": group.monthly_hours,
        "estimates": estimates,
        "cheapest_on_demand": (
            result.cheapest_on_demand.value if result.cheapest_on_demand else None
        ),
        "cheapest_reserved": (
            result.cheapest_reserved.value if result.cheapest_reserved else None
        ),
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Fallback (no API key or API error)
# ---------------------------------------------------------------------------


def _fallback_recommendation(result: ComparisonResult | GroupComparisonResult) -> str:
    """Generate a price-only summary when the Claude API is unavailable."""
    if not result.estimates:
        return "無法取得任何雲端供應商的報價。"

    lines: list[str] = ["## 雲端成本比較摘要\n"]

    if isinstance(result, GroupComparisonResult):
        lines.extend(_group_header(result))
    else:
        lines.extend(_single_header(result))

    lines.extend(_price_table(result))
    lines.extend(_recommendation_lines(result))
    lines.append(_FALLBACK_FOOTER)
    return "\n".join(lines)


def _single_header(result: ComparisonResult) -> list[str]:
    if result.spec.description:
        return [f"**使用場景**：{result.spec.description}\n"]
    return []


def _group_header(result: GroupComparisonResult) -> list[str]:
    total_qty = sum(m.quantity for m in result.group.machines)
    return [f"*工作負載群組：{result.group.name}（共 {total_qty} 台機器）*\n"]


def _price_table(result: ComparisonResult | GroupComparisonResult) -> list[str]:
    is_group = isinstance(result, GroupComparisonResult)
    lines: list[str] = ["### 各供應商月費 (On-Demand)\n"]

    for est in sorted(result.estimates, key=lambda e: e.total_monthly_on_demand):
        marker = " ⬅ 最低" if est.provider == result.cheapest_on_demand else ""
        name = est.provider.value.upper()
        if is_group:
            lines.append(
                f"- **{name}**: "
                f"${est.total_monthly_on_demand:.2f}/月（{est.total_machines} 台）{marker}"
            )
        else:
            lines.append(
                f"- **{name}** ({est.matched_instance}): "
                f"${est.total_monthly_on_demand:.2f}/月{marker}"
            )

    with_reserved = [e for e in result.estimates if e.total_monthly_reserved_1y is not None]
    if with_reserved:
        lines.append("\n### 各供應商月費 (1-Year Reserved)\n")
        for est in sorted(with_reserved, key=lambda e: e.total_monthly_reserved_1y or float("inf")):
            marker = " ⬅ 最低" if est.provider == result.cheapest_reserved else ""
            name = est.provider.value.upper()
            if is_group:
                lines.append(f"- **{name}**: ${est.total_monthly_reserved_1y:.2f}/月{marker}")
            else:
                lines.append(
                    f"- **{name}** ({est.matched_instance}): "
                    f"${est.total_monthly_reserved_1y:.2f}/月{marker}"
                )

    return lines


def _recommendation_lines(result: ComparisonResult | GroupComparisonResult) -> list[str]:
    lines: list[str] = ["\n### 建議"]
    if result.cheapest_on_demand:
        lines.append(f"\n- On-Demand 方案推薦：**{result.cheapest_on_demand.value.upper()}**")
    if result.cheapest_reserved:
        lines.append(f"- Reserved 方案推薦：**{result.cheapest_reserved.value.upper()}**")
    return lines
