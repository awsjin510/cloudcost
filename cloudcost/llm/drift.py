"""Detect drift between the planner's catalogue and the vendors' own pages.

No vendor publishes default quotas or list prices for these models through
an API (checked 2026-09-28/29: the AWS Price List only reaches Claude 3, the
Azure Retail Prices API has no Claude rows, Google no longer publishes Gemini
API limits at all). The documentation pages themselves are the authoritative
source, and they are machine-readable enough to parse, so this module fetches
them — Anthropic, AWS General Reference, Microsoft Learn, OpenAI model pages,
Google pricing and Vertex PayGo — parses the tables, and reports every place
the catalogue disagrees, including models the vendors list that the
catalogue does not know about yet.

Run weekly from CI (.github/workflows/llm-drift.yml)::

    python -m cloudcost.llm.drift            # human-readable, exit 1 on drift
    python -m cloudcost.llm.drift --markdown # issue body

A finding is not automatically a bug in the catalogue: a vendor may have
reworded a table. Either way a person should look, which is the point.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass, field
from typing import Callable, Optional

from cloudcost.llm.catalog import (
    SRC_ANTHROPIC,
    SRC_AZURE_OPENAI,
    SRC_BEDROCK_GR,
    SRC_FOUNDRY,
    SRC_GEMINI_PRICING,
    SRC_OPENAI_MODELS,
    SRC_OPENAI_PRICING,
    SRC_PRICING,
    SRC_VERTEX,
    SRC_VERTEX_PAYGO,
    LimitStatus,
    LLMModel,
    LLMPlatform,
    ModelLine,
    get_model,
    list_models,
    list_plans,
)

# Markdown variants of the Anthropic pages parse far more reliably than HTML.
URLS = {
    "anthropic_rate_limits": SRC_ANTHROPIC + ".md",
    "anthropic_pricing": SRC_PRICING + ".md",
    "foundry": SRC_FOUNDRY,
    "vertex": SRC_VERTEX + "?hl=en",
    # The General Reference, not the user guide: only it lists every model.
    "bedrock_gr": SRC_BEDROCK_GR,
    "openai_pricing": SRC_OPENAI_PRICING + ".md",
    "azure_openai": SRC_AZURE_OPENAI,
    "gemini_pricing": SRC_GEMINI_PRICING + ".md.txt",
    "vertex_paygo": SRC_VERTEX_PAYGO + "?hl=en",
}

# Labels the vendors list that the planner deliberately does not model
# (older generations, gated research models). Anything outside this set and
# outside the catalogue is reported as a new model.
_ANTHROPIC_KNOWN_OTHER = (
    "claude mythos", "claude opus 4", "claude sonnet 4", "claude haiku 3",
)
_FOUNDRY_KNOWN_OTHER = (
    "claude-mythos", "claude-opus-4", "claude-sonnet-4", "claude-haiku-3",
)
_VERTEX_KNOWN_OTHER = (
    "claude mythos", "claude opus 4", "claude sonnet 4", "claude haiku 3",
    "claude 3", "claude opus 3", "claude sonnet 3",
)


@dataclass
class Finding:
    source: str
    kind: str          # mismatch | new_model | missing | parse_error | now_published
    subject: str
    expected: str = ""
    actual: str = ""

    def line(self) -> str:
        detail = f"：工具 {self.expected}，官方 {self.actual}" if self.expected or self.actual else ""
        return f"[{self.source}] {self.kind} {self.subject}{detail}"


@dataclass
class DriftReport:
    findings: list[Finding] = field(default_factory=list)
    checked: dict[str, int] = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        return not self.findings


def _num(text: str) -> Optional[float]:
    m = re.search(r"[\d][\d,]*(?:\.\d+)?", text or "")
    return float(m.group(0).replace(",", "")) if m else None


def _strip(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment)).strip()


def _fmt(v: Optional[float]) -> str:
    if v is None:
        return "—"
    return f"{v:,.2f}".rstrip("0").rstrip(".") if v % 1 else f"{int(v):,}"


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_anthropic_rate_limits(md: str) -> dict[str, dict[str, tuple[float, float, float]]]:
    """{normalised label: {tier: (rpm, itpm, otpm)}} from the tier tabs."""
    out: dict[str, dict[str, tuple[float, float, float]]] = {}
    for tier in ("Start", "Build", "Scale"):
        m = re.search(rf'<Tab title="{tier} tier">(.*?)</Tab>', md, re.S)
        if not m:
            continue
        for line in m.group(1).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or not cells[0].startswith("Claude"):
                continue
            label = re.sub(r"\s*\(.*$", "", cells[0])
            label = re.sub(r"(\.x)\d$", r"\1", label).strip()   # "Fable 5.x1" -> "Fable 5.x"
            values = tuple(_num(c) for c in cells[1:4])
            if None in values:
                continue
            out.setdefault(label, {})[tier.lower()] = values  # type: ignore[assignment]
    return out


def parse_anthropic_pricing(md: str) -> dict[str, tuple[float, float, float, float]]:
    """{label: (input, 5m cache write, cache read, output)} from the model table."""
    out: dict[str, tuple[float, float, float, float]] = {}
    m = re.search(r"## Model pricing(.*?)\n## ", md, re.S)
    section = m.group(1) if m else ""
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not cells[0].startswith("Claude"):
            continue
        label = re.sub(r"\s*\(.*$", "", cells[0]).strip()
        values = (_num(cells[1]), _num(cells[2]), _num(cells[4]), _num(cells[5]))
        if None not in values:
            out[label] = values  # type: ignore[assignment]
    return out


def parse_foundry(page: str) -> dict[str, dict[str, tuple[float, float, float]]]:
    """{subscription: {model id: (rpm, itpm, otpm)}} for Global Standard rows."""
    out: dict[str, dict[str, tuple[float, float, float]]] = {}
    tables = re.findall(r"<table.*?</table>", page, re.S)
    for name, table in zip(("payg", "enterprise", "free"), tables):
        rows: dict[str, tuple[float, float, float]] = {}
        for tr in re.findall(r"<tr>(.*?)</tr>", table, re.S):
            cells = [_strip(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            if len(cells) >= 7 and cells[0].startswith("claude-") and cells[1] == "Global Standard":
                vals = tuple(_num(c) for c in cells[4:7])
                if None not in vals:
                    rows[cells[0]] = vals  # type: ignore[assignment]
        out[name] = rows
    return out


def parse_vertex(page: str) -> dict[str, dict[str, Optional[tuple[float, float, float]]]]:
    """{model label: {"global" | "multi_region": (qpm, input tpm, output tpm) or None}}."""
    out: dict[str, dict[str, Optional[tuple[float, float, float]]]] = {}
    current = None
    for tr in re.findall(r"<tr>(.*?)</tr>", page, re.S):
        tds = re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S)
        if not tds:
            continue
        if "rowspan" in tds[0][0]:
            name = _strip(tds[0][1])
            current = name.replace(" on Google Cloud", "").strip() if name.startswith("Claude") else None
            tds = tds[1:]
        if current is None or len(tds) < 2:
            continue
        region = _strip(tds[0][1]).lower()
        key = "global" if "global" in region else ("multi_region" if "multi" in region else None)
        if key is None:
            continue
        body = tds[1][1]
        qpm = re.search(r"QPM:\s*([\d,]+)", body)
        itpm = re.search(r"Input TPM:\s*([\d,]+)", body)
        otpm = re.search(r"Output TPM:\s*([\d,]+)", body)
        vals = None
        if qpm and itpm and otpm:
            vals = tuple(float(x.group(1).replace(",", "")) for x in (qpm, itpm, otpm))
        # Several multi-region rows (us, eu) share values; keep the first.
        out.setdefault(current, {}).setdefault(key, vals)  # type: ignore[arg-type]
    return out


def parse_bedrock_gr(page: str) -> dict[str, float]:
    """{quota name: default value} from the AWS General Reference Bedrock table."""
    out: dict[str, float] = {}
    for tr in re.findall(r"<tr>(.*?)</tr>", page, re.S):
        cells = [" ".join(_strip(c).split()) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) >= 2:
            v = _num(cells[1])
            if v is not None:
                out[cells[0]] = v
    return out


def parse_openai_model_page(md: str) -> dict:
    """Pricing and Standard rate-limit tiers from a developers.openai.com model page."""
    out: dict = {"pricing": {}, "tiers": {}}
    m = re.search(r"### Text tokens(.*?)(?:\n### |\n## )", md, re.S)
    for line in (m.group(1) if m else "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] in ("Input", "Cached input", "Cache writes", "Output"):
            out["pricing"][cells[0]] = _num(cells[1])
    # The first tier table under "Rate limits"; its sub-heading varies
    # ("Standard" on most pages, "default" on the Luna pages).
    m = re.search(r"## Rate limits(.*?)(?:\n## |\Z)", md, re.S)
    for line in (m.group(1) if m else "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith("Tier "):
            key = cells[0].lower().replace(" ", "")
            if key not in out["tiers"]:
                out["tiers"][key] = (_num(cells[1]), _num(cells[2]))
    return out


def parse_openai_pricing_ids(md: str) -> set[str]:
    """Every GPT text model ID the pricing page lists."""
    return set(re.findall(r"\b(gpt-\d+(?:\.\d+)?(?:-[a-z]+)?)\b", md))


def parse_openai_pricing(md: str) -> dict[str, tuple[Optional[float], ...]]:
    """{model id: (input, cached, cache write, output, long input, long cached, long write, long output)}.

    Read from the "Standard pricing data" table, which carries short- and
    long-context prices for every model; some per-model pages omit rows.
    """
    out: dict[str, tuple[Optional[float], ...]] = {}
    m = re.search(r"### Standard pricing data\s*\n(.*?)(?:\n### |\n## |\Z)", md, re.S)
    for line in (m.group(1) if m else "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 9 or not cells[0].startswith("gpt-"):
            continue
        mid = re.sub(r"\s*\(.*\)$", "", cells[0])
        out[mid] = tuple(None if c in ("-", "") else _num(c) for c in cells[1:9])
    return out


def parse_azure_openai(page: str) -> dict[int, dict[str, tuple[float, float]]]:
    """{tier number: {model id: (rpm, tpm)}} for Global Standard rows."""
    out: dict[int, dict[str, tuple[float, float]]] = {}
    tier = 0
    for table in re.findall(r"<table.*?</table>", page, re.S):
        rows: dict[str, tuple[float, float]] = {}
        for tr in re.findall(r"<tr>(.*?)</tr>", table, re.S):
            cells = [" ".join(_strip(c).split()) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            if len(cells) >= 4 and cells[1] == "GlobalStandard" and cells[0].startswith("gpt-"):
                rpm, tpm = _num(cells[2]), _num(cells[3])
                if rpm is not None and tpm is not None:
                    rows[cells[0]] = (rpm, tpm)
        if "gpt-6-astra" in rows:
            tier += 1
            out[tier] = rows
    return out


def parse_gemini_pricing(md: str) -> dict[str, dict]:
    """{model id: {"input"|"output"|"cache": (base, long or None)}} from the Standard tables."""
    out: dict[str, dict] = {}
    for section in re.split(r"\n(?=## )", md):
        ids = re.findall(r"\[`(gemini-[\w.\-]+)`\]", section[:600])
        m = re.search(r"### Standard\s*\n(.*?)(?:\n### |\Z)", section, re.S)
        if not ids or not m:
            continue
        rows: dict[str, tuple] = {}
        for line in m.group(1).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            key = ("input" if cells[0].startswith("Input price") else
                   "output" if cells[0].startswith("Output price") else
                   "cache" if cells[0].startswith("Context caching") else None)
            if key is None:
                continue
            amounts = [float(x.replace(",", "")) for x in re.findall(r"\$(\d[\d,]*(?:\.\d+)?)", cells[2])]
            if not amounts:
                continue
            # A second amount is a long-context price only when the cell says
            # so ("> 200k"); otherwise it may be a future price or a modality.
            long = amounts[1] if len(amounts) > 1 and "200k" in cells[2] else None
            rows[key] = (amounts[0], long)
        for mid in ids:
            out.setdefault(mid, rows)
    return out


def parse_vertex_paygo(page: str) -> dict[str, dict[int, float]]:
    """{"pro"|"flash": {tier: baseline TPM}} from the Standard PayGo table."""
    out: dict[str, dict[int, float]] = {}
    row = re.compile(r"Tier (\d) (?:\$[\d,]+ ?[-–] ?\$[\d,]+|> ?\$[\d,]+) ([\d,]+)")
    for table in re.findall(r"<table.*?</table>", page, re.S):
        text = " ".join(_strip(table).split())
        if "Gemini Pro models" not in text:
            continue
        pro_at = text.find("Gemini Pro models")
        flash_at = text.find("Gemini Flash and Flash-Lite models")
        spans = {"pro": text[pro_at:flash_at if flash_at > pro_at else None],
                 "flash": text[flash_at:] if flash_at >= 0 else ""}
        for key, seg in spans.items():
            out[key] = {int(n): float(v.replace(",", "")) for n, v in row.findall(seg)}
    return out


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

_ANTHROPIC_RL_LABEL = {
    LLMModel.FABLE_5_1: "Claude Fable 5.x",
    LLMModel.FABLE_5: "Claude Fable 5.x",
    LLMModel.OPUS_5_5: "Claude Opus 5.5",
    LLMModel.OPUS_5: "Claude Opus 5",
    LLMModel.SONNET_5_5: "Claude Sonnet 5.5",
    LLMModel.SONNET_5: "Claude Sonnet 5",
    LLMModel.OPUS_4_8: "Claude Opus 4.x",
    LLMModel.SONNET_4_6: "Claude Sonnet 4.x",
    LLMModel.HAIKU_4_5: "Claude Haiku 4.5",
}

# Older or gated models the vendors list that the planner deliberately skips.
# Our own models are always matched first, so a prefix here never hides one.
_BEDROCK_KNOWN_OTHER = (
    "anthropic claude opus 4", "anthropic claude sonnet 4", "anthropic claude 3",
    "anthropic claude haiku 3", "anthropic claude mythos", "anthropic claude instant",
    "gpt-5.4", "gpt oss", "gpt-5.6 cyber", "openai gpt oss",
)
_GPT_KNOWN_ALIASES = {"gpt-6", "gpt-5.6"}
_GEMINI_KNOWN_OTHER = {"gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"}


def _plan(model: LLMModel, platform: LLMPlatform, plan_id: str):
    return next((p for p in list_plans(model, platform) if p.plan_id == plan_id), None)


def _v(limit) -> Optional[float]:
    return limit.value if limit is not None and limit.status is LimitStatus.ENFORCED else None


def _triple(plan) -> tuple[Optional[float], ...]:
    return (_v(plan.rpm), _v(plan.itpm), _v(plan.otpm))


def _cmp(report: DriftReport, source: str, subject: str, ours, theirs) -> None:
    report.checked[source] = report.checked.get(source, 0) + 1
    if tuple(ours) != tuple(theirs):
        report.findings.append(Finding(
            source, "mismatch", subject,
            " / ".join(_fmt(v) for v in ours), " / ".join(_fmt(v) for v in theirs)))


def _version(text: str) -> tuple[int, int]:
    """(major, minor) with a missing minor read as 0, so "gpt-6-terra" is (6, 0), not (6,)."""
    nums = [int(x) for x in re.findall(r"\d+", text)[:2]]
    return (nums + [0, 0])[0], (nums + [0, 0])[1]


def _compare_claude_docs(report: DriftReport, pages: dict[str, str]) -> None:
    claude = list_models(ModelLine.CLAUDE)

    rl = parse_anthropic_rate_limits(pages.get("anthropic_rate_limits", ""))
    if not rl:
        report.findings.append(Finding("anthropic", "parse_error", "rate limit 表格解析失敗"))
    else:
        for model, label in _ANTHROPIC_RL_LABEL.items():
            if label not in rl:
                report.findings.append(Finding("anthropic", "missing", f"{label} 不在官方 rate limit 表"))
                continue
            for tier in ("start", "build", "scale"):
                plan = _plan(model, LLMPlatform.ANTHROPIC, tier)
                if tier in rl[label] and plan is not None:
                    _cmp(report, "anthropic", f"{get_model(model).label} {tier}", _triple(plan), rl[label][tier])
        ours = set(_ANTHROPIC_RL_LABEL.values())
        for label in rl:
            if label not in ours and not label.lower().startswith(_ANTHROPIC_KNOWN_OTHER):
                report.findings.append(Finding("anthropic", "new_model",
                                               f"官方 rate limit 表新增 {label}，工具尚未收錄"))

    prices = parse_anthropic_pricing(pages.get("anthropic_pricing", ""))
    if not prices:
        report.findings.append(Finding("pricing", "parse_error", "定價表格解析失敗"))
    else:
        labels = {m.label for m in claude}
        for info in claude:
            if info.label not in prices:
                report.findings.append(Finding("pricing", "missing", f"{info.label} 不在官方定價表"))
                continue
            p = info.pricing
            _cmp(report, "pricing", info.label,
                 (p.input_per_mtok, p.cache_write_5m_per_mtok, p.cache_read_per_mtok, p.output_per_mtok),
                 prices[info.label])
        for label in prices:
            if label not in labels and not label.lower().startswith(_ANTHROPIC_KNOWN_OTHER):
                report.findings.append(Finding("pricing", "new_model", f"官方定價表新增 {label}，工具尚未收錄"))

    foundry = parse_foundry(pages.get("foundry", ""))
    if not foundry.get("enterprise"):
        report.findings.append(Finding("foundry", "parse_error", "Foundry 配額表格解析失敗"))
    else:
        known = {m.api_id for m in claude}
        for sub in ("payg", "enterprise"):
            rows = foundry.get(sub, {})
            for info in claude:
                plan = _plan(info.model, LLMPlatform.FOUNDRY, sub)
                if info.api_id not in rows:
                    report.findings.append(Finding("foundry", "missing", f"{info.api_id} ({sub}) 不在官方表"))
                elif plan is not None:
                    _cmp(report, "foundry", f"{info.label} {sub}", _triple(plan), rows[info.api_id])
            for mid in rows:
                if mid not in known and not mid.startswith(_FOUNDRY_KNOWN_OTHER):
                    report.findings.append(Finding("foundry", "new_model", f"Foundry 新增 {mid}，工具尚未收錄"))

    vertex = parse_vertex(pages.get("vertex", ""))
    if not vertex:
        report.findings.append(Finding("vertex", "parse_error", "Vertex 配額表格解析失敗"))
    else:
        for info in claude:
            rows = vertex.get(info.label)
            if rows is None:
                report.findings.append(Finding("vertex", "missing", f"{info.label} 不在官方表"))
                continue
            for key in ("global", "multi_region"):
                theirs, plan = rows.get(key), _plan(info.model, LLMPlatform.VERTEX, key)
                if theirs is None:
                    continue  # published blank (Fable 5.1 shares the Fable lineage bucket)
                if plan is None:
                    report.findings.append(Finding("vertex", "now_published",
                                                   f"{info.label} 已有 {key} 端點配額，工具尚未收錄"))
                    continue
                _cmp(report, "vertex", f"{info.label} {key}", _triple(plan), theirs)
        known = {m.label for m in claude}
        for label in vertex:
            if label not in known and not label.lower().startswith(_VERTEX_KNOWN_OTHER):
                report.findings.append(Finding("vertex", "new_model", f"Vertex 新增 {label}，工具尚未收錄"))


def _compare_bedrock(report: DriftReport, pages: dict[str, str]) -> None:
    gr = parse_bedrock_gr(pages.get("bedrock_gr", ""))
    if not gr:
        report.findings.append(Finding("bedrock", "parse_error", "AWS 配額總表解析失敗"))
        return
    modelled: set[str] = set()
    for info in list_models(ModelLine.CLAUDE) + list_models(ModelLine.GPT):
        prefix = "Anthropic " if info.line is ModelLine.CLAUDE else ""
        modelled.add((prefix + info.label).lower())

        m_in = gr.get(f"[bedrock-mantle endpoint] Input tokens per minute for {info.label}")
        m_out = gr.get(f"[bedrock-mantle endpoint] Output tokens per minute for {info.label}")
        mantle = _plan(info.model, LLMPlatform.BEDROCK, "mantle")
        if mantle is not None and mantle.itpm.status is LimitStatus.ENFORCED:
            _cmp(report, "bedrock", f"{info.label} mantle", (mantle.itpm.value, mantle.otpm.value), (m_in, m_out))
        elif m_in is not None:
            report.checked["bedrock"] = report.checked.get("bedrock", 0) + 1
            report.findings.append(Finding("bedrock", "now_published",
                                           f"AWS 已公布 {info.label} 的 Mantle 預設配額，工具仍標示未公布或未收錄",
                                           "—", f"{_fmt(m_in)} / {_fmt(m_out)}"))
        else:
            report.checked["bedrock"] = report.checked.get("bedrock", 0) + 1

        name = f"{prefix}{info.label}"
        r_tpm = gr.get(f"Global cross-region model inference tokens per minute for {name}")
        r_rpm = gr.get(f"Global cross-region model inference requests per minute for {name}")
        runtime = _plan(info.model, LLMPlatform.BEDROCK, "runtime")
        if runtime is not None and runtime.tpm.status is LimitStatus.ENFORCED:
            _cmp(report, "bedrock", f"{info.label} runtime", (_v(runtime.tpm), _v(runtime.rpm)), (r_tpm, r_rpm))
        elif r_tpm is None:
            report.checked["bedrock"] = report.checked.get("bedrock", 0) + 1
        else:
            report.findings.append(Finding("bedrock", "now_published",
                                           f"AWS 已公布 {info.label} 的 bedrock-runtime 配額，工具尚未收錄"))

    for key in gr:
        m = re.match(r"Global cross-region model inference tokens per minute for (.+)$", key)
        if not m:
            continue
        name = m.group(1).strip()
        low = name.lower()
        if not (low.startswith("anthropic claude") or low.startswith("gpt-")):
            continue
        if low not in modelled and not low.startswith(_BEDROCK_KNOWN_OTHER):
            report.findings.append(Finding("bedrock", "new_model", f"Bedrock 新增 {name}，工具尚未收錄"))


def _compare_openai(report: DriftReport, pages: dict[str, str]) -> None:
    gpt = list_models(ModelLine.GPT)
    table = parse_openai_pricing(pages.get("openai_pricing", ""))
    if not table:
        report.findings.append(Finding("openai", "parse_error", "OpenAI 定價表（Standard pricing data）解析失敗"))
    for info in gpt:
        p = info.pricing
        if table:
            row = table.get(info.api_id)
            if row is None:
                report.findings.append(Finding("openai", "missing", f"{info.api_id} 不在定價表"))
            else:
                ours = (p.input_per_mtok, p.cache_read_per_mtok, p.cache_write_5m_per_mtok, p.output_per_mtok,
                        p.long_input_per_mtok, p.long_cache_read_per_mtok, p.long_output_per_mtok)
                theirs = (row[0], row[1], row[2], row[3], row[4], row[5], row[7])
                _cmp(report, "openai", f"{info.label} 定價（含長上下文）", ours, theirs)
        page = parse_openai_model_page(pages.get(f"openai_model:{info.api_id}", ""))
        if not page["tiers"]:
            report.findings.append(Finding("openai", "parse_error", f"{info.api_id} 模型頁的配額表解析失敗"))
            continue
        for tier in ("t1", "t3", "t5"):
            plan = _plan(info.model, LLMPlatform.OPENAI, tier)
            got = page["tiers"].get("tier" + tier[1:])
            if plan is None or got is None:
                report.findings.append(Finding("openai", "missing", f"{info.api_id} {tier} 不在模型頁"))
                continue
            _cmp(report, "openai", f"{info.label} {tier}", (_v(plan.rpm), _v(plan.tpm)), got)

    ids = parse_openai_pricing_ids(pages.get("openai_pricing", ""))
    if not ids:
        report.findings.append(Finding("openai", "parse_error", "OpenAI 定價頁解析失敗"))
    known = {m.api_id for m in gpt}
    for mid in sorted(ids):
        if mid in known or mid in _GPT_KNOWN_ALIASES or _version(mid) < (6, 0):
            continue
        report.findings.append(Finding("openai", "new_model", f"OpenAI 新增 {mid}，工具尚未收錄"))

    azure = parse_azure_openai(pages.get("azure_openai", ""))
    if len(azure) < 6:
        report.findings.append(Finding("azure_openai", "parse_error", "Azure OpenAI 層級表解析失敗"))
        return
    for info in gpt:
        for plan_id, tier in (("az_t1", 1), ("az_t3", 3), ("az_t6", 6)):
            plan, got = _plan(info.model, LLMPlatform.FOUNDRY, plan_id), azure[tier].get(info.api_id)
            if plan is None or got is None:
                report.findings.append(Finding("azure_openai", "missing", f"{info.api_id} Tier {tier} 不在官方表"))
                continue
            _cmp(report, "azure_openai", f"{info.label} Tier {tier}", (_v(plan.rpm), _v(plan.tpm)), got)
    for mid in azure[1]:
        if mid not in known and mid not in _GPT_KNOWN_ALIASES and _version(mid) >= (6, 0):
            report.findings.append(Finding("azure_openai", "new_model", f"Azure OpenAI 新增 {mid}，工具尚未收錄"))


def _compare_gemini(report: DriftReport, pages: dict[str, str]) -> None:
    gem = list_models(ModelLine.GEMINI)
    prices = parse_gemini_pricing(pages.get("gemini_pricing", ""))
    if not prices:
        report.findings.append(Finding("gemini", "parse_error", "Gemini 定價頁解析失敗"))
    else:
        for info in gem:
            rows = prices.get(info.api_id)
            if not rows or not all(k in rows for k in ("input", "output", "cache")):
                report.findings.append(Finding("gemini", "missing", f"{info.api_id} 不在定價頁"))
                continue
            p = info.pricing
            _cmp(report, "gemini", f"{info.label} 定價",
                 (p.input_per_mtok, p.output_per_mtok, p.cache_read_per_mtok,
                  p.long_input_per_mtok, p.long_output_per_mtok, p.long_cache_read_per_mtok),
                 (rows["input"][0], rows["output"][0], rows["cache"][0],
                  rows["input"][1], rows["output"][1], rows["cache"][1]))
        known = {m.api_id for m in gem}
        for mid in sorted(prices):
            m = re.match(r"^gemini-(\d+)\.(\d+)-(pro|flash|flash-lite)(-preview)?$", mid)
            if not m or mid in known or mid in _GEMINI_KNOWN_OTHER:
                continue
            if (int(m.group(1)), int(m.group(2))) >= (3, 1):
                report.findings.append(Finding("gemini", "new_model", f"Gemini 新增 {mid}，工具尚未收錄"))

    paygo = parse_vertex_paygo(pages.get("vertex_paygo", ""))
    if not paygo.get("pro") or not paygo.get("flash"):
        report.findings.append(Finding("vertex_paygo", "parse_error", "Vertex Standard PayGo 表格解析失敗"))
        return
    for info in gem:
        family = "pro" if "pro" in info.api_id else "flash"
        for n in (1, 2, 3, 4):
            plan = _plan(info.model, LLMPlatform.VERTEX, f"vx_t{n}")
            if plan is None:
                continue
            _cmp(report, "vertex_paygo", f"{info.label} Tier {n}", (_v(plan.tpm),), (paygo[family].get(n),))


def compare(pages: dict[str, str]) -> DriftReport:
    """Diff the catalogue against already-fetched page bodies."""
    report = DriftReport()
    _compare_claude_docs(report, pages)
    _compare_bedrock(report, pages)
    _compare_openai(report, pages)
    _compare_gemini(report, pages)
    return report


def page_urls() -> dict[str, str]:
    """Every page the check reads, keyed the way `compare` looks them up."""
    urls = dict(URLS)
    for info in list_models(ModelLine.GPT):
        urls[f"openai_model:{info.api_id}"] = f"{SRC_OPENAI_MODELS}/{info.api_id}.md"
    return urls


def fetch_pages(get: Optional[Callable[[str], str]] = None) -> dict[str, str]:
    if get is None:
        import httpx

        def get(url: str) -> str:
            resp = httpx.get(url, timeout=60, follow_redirects=True,
                             headers={"User-Agent": "cloudcost-drift-check"})
            resp.raise_for_status()
            return resp.text

    pages: dict[str, str] = {}
    for key, url in page_urls().items():
        try:
            pages[key] = get(url)
        except Exception as exc:  # a dead page is itself a finding, not a crash
            pages[key] = ""
            print(f"warning: could not fetch {url}: {exc}", file=sys.stderr)
    return pages


def render_markdown(report: DriftReport) -> str:
    lines = ["LLM 試算工具的內建資料與官方文件不一致，請人工確認後更新 `cloudcost/llm/catalog.py`",
             "並執行 `python -m cloudcost.llm.export` 重新產生前端資料。", ""]
    kinds = {"new_model": "官方新增、工具尚未收錄", "mismatch": "數值不一致", "missing": "官方找不到",
             "now_published": "平台開始公布數值", "parse_error": "頁面結構改變、無法解析"}
    for kind, title in kinds.items():
        items = [f for f in report.findings if f.kind == kind]
        if not items:
            continue
        lines.append(f"### {title}")
        for f in items:
            lines.append(f"- **{f.source}** {f.subject}" +
                         (f"：工具 `{f.expected}`，官方 `{f.actual}`" if f.expected or f.actual else ""))
        lines.append("")
    lines.append("來源：" + " · ".join(URLS.values()) + " · OpenAI 各模型頁（" + SRC_OPENAI_MODELS + "/<id>.md）")
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--markdown", action="store_true", help="print an issue body")
    args = ap.parse_args(argv)
    report = compare(fetch_pages())
    if args.markdown:
        print(render_markdown(report) if report.findings else "no drift")
    else:
        checked = ", ".join(f"{k} {v}" for k, v in sorted(report.checked.items()))
        print(f"checked: {checked}")
        for f in report.findings:
            print(f.line())
        print("clean" if report.clean else f"{len(report.findings)} finding(s)")
    return 0 if report.clean else 1


if __name__ == "__main__":
    sys.exit(main())
