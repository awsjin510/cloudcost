"""AI-powered recommendation engine using the Claude API.

Analyzes multi-cloud cost comparison results and generates actionable
recommendations based on the user's usage scenario.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

import anthropic

from cloudcost.models.spec import ComparisonResult, GroupComparisonResult

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a cloud cost optimization expert. You will receive a JSON object \
containing cost estimates from four cloud providers (AWS, GCP, Azure, Oracle Cloud) \
along with a user-described usage scenario.

Your task is to provide a structured recommendation in **Traditional Chinese (繁體中文)** \
covering the following points:

1. **CP值最高方案** — Which provider offers the best cost-performance ratio and why.
2. **降低成本策略** — Which services can leverage Reserved Instances, Committed Use \
Discounts, Spot/Preemptible instances, or Annual Flex pricing to reduce costs.
3. **使用場景建議** — Tailored advice based on the described scenario \
(startup, enterprise, Taiwan-local needs, etc.).
4. **隱藏費用警示** — Hidden costs to watch out for: data transfer fees, \
support plans, cross-region replication, DNS queries, load balancer hours, \
managed NAT gateway, etc.

Keep the response concise (under 800 words), use bullet points, and include \
approximate dollar amounts where possible.
"""


async def generate_recommendation(
    result: ComparisonResult | GroupComparisonResult,
    api_key: Optional[str] = None,
) -> str:
    """Call the Claude API to generate a cost optimization recommendation.

    Args:
        result: The ComparisonResult from CloudCostComparator.
        api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.

    Returns:
        A recommendation string in Traditional Chinese.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return _fallback_recommendation(result)

    payload = _build_payload(result)

    try:
        client = anthropic.AsyncAnthropic(api_key=key)

        async with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": payload}],
        ) as stream:
            response = await stream.get_final_message()

        text = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        return text

    except Exception:
        logger.warning("Claude API call failed, using fallback", exc_info=True)
        return _fallback_recommendation(result)


def _build_payload(result: ComparisonResult | GroupComparisonResult) -> str:
    """Serialize the comparison result into a prompt-friendly JSON string."""
    if isinstance(result, GroupComparisonResult):
        return _build_group_payload(result)

    estimates_summary = []
    for est in result.estimates:
        entry = {
            "provider": est.provider.value,
            "region": est.region_name,
            "instance": est.matched_instance,
            "on_demand_monthly": est.total_monthly_on_demand,
            "reserved_1y_monthly": est.total_monthly_reserved_1y,
            "details": est.on_demand.details,
            "warnings": est.warnings,
        }
        estimates_summary.append(entry)

    data = {
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
            "description": result.spec.description,
        },
        "estimates": estimates_summary,
        "cheapest_on_demand": (
            result.cheapest_on_demand.value if result.cheapest_on_demand else None
        ),
        "cheapest_reserved": (
            result.cheapest_reserved.value if result.cheapest_reserved else None
        ),
    }

    return json.dumps(data, indent=2, ensure_ascii=False)


def _build_group_payload(result: GroupComparisonResult) -> str:
    """Serialize a GroupComparisonResult into a prompt-friendly JSON string."""
    group = result.group
    machines_summary = [
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

    estimates_summary = []
    for est in result.estimates:
        machine_details = [
            {
                "machine": md.machine.name or md.machine.id,
                "role": md.machine.role.value,
                "instance": md.matched_instance,
                "unit_on_demand": md.unit_monthly_on_demand,
                "quantity": md.machine.quantity,
                "subtotal_on_demand": md.subtotal_on_demand,
            }
            for md in est.machines
        ]
        estimates_summary.append({
            "provider": est.provider.value,
            "region": est.region_name,
            "total_machines": est.total_machines,
            "total_monthly_on_demand": est.total_monthly_on_demand,
            "total_monthly_reserved_1y": est.total_monthly_reserved_1y,
            "machine_details": machine_details,
            "warnings": est.warnings,
        })

    data = {
        "type": "workload_group",
        "group_name": group.name,
        "machines": machines_summary,
        "region": group.region,
        "os": group.os,
        "monthly_hours": group.monthly_hours,
        "estimates": estimates_summary,
        "cheapest_on_demand": (
            result.cheapest_on_demand.value if result.cheapest_on_demand else None
        ),
        "cheapest_reserved": (
            result.cheapest_reserved.value if result.cheapest_reserved else None
        ),
    }

    return json.dumps(data, indent=2, ensure_ascii=False)


def _fallback_recommendation(result: ComparisonResult | GroupComparisonResult) -> str:
    """Generate a basic recommendation without calling the Claude API."""
    lines = ["## 雲端成本比較摘要\n"]

    if not result.estimates:
        return "無法取得任何雲端供應商的報價。"

    if isinstance(result, GroupComparisonResult):
        total_qty = sum(m.quantity for m in result.group.machines)
        lines.append(f"*工作負載群組：{result.group.name}（共 {total_qty} 台機器）*\n")

    lines.append("### 各供應商月費 (On-Demand)\n")
    for est in sorted(result.estimates, key=lambda e: e.total_monthly_on_demand):
        marker = " ⬅ 最低" if est.provider == result.cheapest_on_demand else ""
        if isinstance(result, GroupComparisonResult):
            lines.append(
                f"- **{est.provider.value.upper()}**: "
                f"${est.total_monthly_on_demand:.2f}/月（{est.total_machines} 台）{marker}"
            )
        else:
            lines.append(
                f"- **{est.provider.value.upper()}** ({est.matched_instance}): "
                f"${est.total_monthly_on_demand:.2f}/月{marker}"
            )

    lines.append("\n### 各供應商月費 (1-Year Reserved)\n")
    for est in sorted(
        [e for e in result.estimates if e.total_monthly_reserved_1y is not None],
        key=lambda e: e.total_monthly_reserved_1y or float("inf"),
    ):
        marker = " ⬅ 最低" if est.provider == result.cheapest_reserved else ""
        if isinstance(result, GroupComparisonResult):
            lines.append(
                f"- **{est.provider.value.upper()}**: "
                f"${est.total_monthly_reserved_1y:.2f}/月{marker}"
            )
        else:
            lines.append(
                f"- **{est.provider.value.upper()}** ({est.matched_instance}): "
                f"${est.total_monthly_reserved_1y:.2f}/月{marker}"
            )

    lines.append("\n### 建議")
    if result.cheapest_on_demand:
        lines.append(
            f"\n- On-Demand 方案推薦：**{result.cheapest_on_demand.value.upper()}**"
        )
    if result.cheapest_reserved:
        lines.append(
            f"- Reserved 方案推薦：**{result.cheapest_reserved.value.upper()}**"
        )
    lines.append(
        "\n> 注意：以上為基本比較。設定 ANTHROPIC_API_KEY 環境變數即可啟用 AI 智能建議。"
    )

    return "\n".join(lines)
