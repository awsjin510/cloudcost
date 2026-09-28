"""Detect drift between the planner's catalogue and the vendors' own pages.

No vendor publishes default Claude quotas or list prices through an API
(checked 2026-09-28: the AWS Price List only reaches Claude 3, and the Azure
Retail Prices API has no Claude rows). The documentation pages themselves are
the authoritative source, and they are machine-readable enough to parse, so
this module fetches them, parses the tables, and reports every place the
catalogue disagrees — including models the vendors list that the catalogue
does not know about yet.

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
    SRC_BEDROCK,
    SRC_FOUNDRY,
    SRC_PRICING,
    SRC_VERTEX,
    LLMModel,
    LLMPlatform,
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
    "bedrock": SRC_BEDROCK,
}

# Labels the vendors list that the planner deliberately does not model
# (older generations, gated research models). Anything outside this set and
# outside the catalogue is reported as a new model.
_ANTHROPIC_KNOWN_OTHER = (
    "claude mythos", "claude opus 4", "claude sonnet 4", "claude haiku",
)
_FOUNDRY_KNOWN_OTHER = (
    "claude-mythos", "claude-opus-4", "claude-sonnet-4", "claude-haiku",
)
_VERTEX_KNOWN_OTHER = (
    "claude mythos", "claude opus 4", "claude sonnet 4", "claude haiku",
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


def parse_bedrock_mantle_models(page: str) -> list[str]:
    """Model names listed in the published Mantle default-quota table."""
    m = re.search(r"Default bedrock-mantle quotas by model(.*?)</table>", page, re.S)
    if not m:
        return []
    names = []
    for tr in re.findall(r"<tr>(.*?)</tr>", m.group(1), re.S):
        cells = [_strip(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if cells:
            names.append(cells[0])
    return names


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

_ANTHROPIC_RL_LABEL = {
    LLMModel.FABLE_5_1: "Claude Fable 5.x",
    LLMModel.FABLE_5: "Claude Fable 5.x",
    LLMModel.OPUS_5_5: "Claude Opus 5.5",
    LLMModel.OPUS_5: "Claude Opus 5",
    LLMModel.SONNET_5: "Claude Sonnet 5",
}


def _plan(model: LLMModel, platform: LLMPlatform, plan_id: str):
    return next(p for p in list_plans(model, platform) if p.plan_id == plan_id)


def _triple(plan) -> tuple[Optional[float], ...]:
    return (plan.rpm.value, plan.itpm.value, plan.otpm.value)


def _cmp(report: DriftReport, source: str, subject: str, ours, theirs) -> None:
    report.checked[source] = report.checked.get(source, 0) + 1
    if tuple(ours) != tuple(theirs):
        report.findings.append(Finding(
            source, "mismatch", subject,
            " / ".join(_fmt(v) for v in ours), " / ".join(_fmt(v) for v in theirs)))


def compare(pages: dict[str, str]) -> DriftReport:
    """Diff the catalogue against already-fetched page bodies."""
    report = DriftReport()

    # -- Anthropic rate limits
    rl = parse_anthropic_rate_limits(pages.get("anthropic_rate_limits", ""))
    if not rl:
        report.findings.append(Finding("anthropic", "parse_error", "rate limit 表格解析失敗"))
    else:
        for model, label in _ANTHROPIC_RL_LABEL.items():
            if label not in rl:
                report.findings.append(Finding("anthropic", "missing", f"{label} 不在官方 rate limit 表"))
                continue
            for tier in ("start", "build", "scale"):
                if tier in rl[label]:
                    _cmp(report, "anthropic", f"{get_model(model).label} {tier}",
                         _triple(_plan(model, LLMPlatform.ANTHROPIC, tier)), rl[label][tier])
        ours = set(_ANTHROPIC_RL_LABEL.values())
        for label in rl:
            if label not in ours and not label.lower().startswith(_ANTHROPIC_KNOWN_OTHER):
                report.findings.append(Finding("anthropic", "new_model",
                                               f"官方 rate limit 表新增 {label}，工具尚未收錄"))

    # -- Anthropic pricing
    prices = parse_anthropic_pricing(pages.get("anthropic_pricing", ""))
    if not prices:
        report.findings.append(Finding("pricing", "parse_error", "定價表格解析失敗"))
    else:
        labels = {m.label for m in list_models()}
        for info in list_models():
            if info.label not in prices:
                report.findings.append(Finding("pricing", "missing", f"{info.label} 不在官方定價表"))
                continue
            p = info.pricing
            _cmp(report, "pricing", info.label,
                 (p.input_per_mtok, p.cache_write_5m_per_mtok, p.cache_read_per_mtok, p.output_per_mtok),
                 prices[info.label])
        for label in prices:
            if label not in labels and not label.lower().startswith(_ANTHROPIC_KNOWN_OTHER):
                report.findings.append(Finding("pricing", "new_model",
                                               f"官方定價表新增 {label}，工具尚未收錄"))

    # -- Foundry
    foundry = parse_foundry(pages.get("foundry", ""))
    if not foundry.get("enterprise"):
        report.findings.append(Finding("foundry", "parse_error", "Foundry 配額表格解析失敗"))
    else:
        for sub in ("payg", "enterprise"):
            rows = foundry.get(sub, {})
            for info in list_models():
                if info.api_id not in rows:
                    report.findings.append(Finding("foundry", "missing", f"{info.api_id} ({sub}) 不在官方表"))
                    continue
                _cmp(report, "foundry", f"{info.label} {sub}",
                     _triple(_plan(info.model, LLMPlatform.FOUNDRY, sub)), rows[info.api_id])
            known = {m.api_id for m in list_models()}
            for mid in rows:
                if mid not in known and not mid.startswith(_FOUNDRY_KNOWN_OTHER):
                    report.findings.append(Finding("foundry", "new_model", f"Foundry 新增 {mid}，工具尚未收錄"))

    # -- Vertex
    vertex = parse_vertex(pages.get("vertex", ""))
    if not vertex:
        report.findings.append(Finding("vertex", "parse_error", "Vertex 配額表格解析失敗"))
    else:
        for info in list_models():
            rows = vertex.get(info.label)
            if rows is None:
                report.findings.append(Finding("vertex", "missing", f"{info.label} 不在官方表"))
                continue
            for key in ("global", "multi_region"):
                theirs = rows.get(key)
                if theirs is None:
                    # Fable 5.1's cells are published blank: it draws on the
                    # shared Fable lineage bucket, which is how it is modelled.
                    continue
                _cmp(report, "vertex", f"{info.label} {key}",
                     _triple(_plan(info.model, LLMPlatform.VERTEX, key)), theirs)
        known = {m.label for m in list_models()}
        for label in vertex:
            if label not in known and not label.lower().startswith(_VERTEX_KNOWN_OTHER):
                report.findings.append(Finding("vertex", "new_model", f"Vertex 新增 {label}，工具尚未收錄"))

    # -- Bedrock: the catalogue says "unpublished"; flag if that stops being true
    page = pages.get("bedrock", "")
    if "Default bedrock-mantle quotas by model" not in page:
        report.findings.append(Finding("bedrock", "parse_error", "Mantle 預設配額表格找不到"))
    else:
        report.checked["bedrock"] = 1
        listed = " | ".join(parse_bedrock_mantle_models(page)).lower()
        for info in list_models():
            short = info.label.replace("Claude ", "").lower()
            if re.search(rf"claude {re.escape(short)}(?![\d.])", listed):
                report.findings.append(Finding("bedrock", "now_published",
                                               f"Bedrock 已公布 {info.label} 的 Mantle 預設配額，工具仍標示未公布"))
    return report


def fetch_pages(get: Optional[Callable[[str], str]] = None) -> dict[str, str]:
    if get is None:
        import httpx

        def get(url: str) -> str:
            resp = httpx.get(url, timeout=60, follow_redirects=True,
                             headers={"User-Agent": "cloudcost-drift-check"})
            resp.raise_for_status()
            return resp.text

    pages: dict[str, str] = {}
    for key, url in URLS.items():
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
    lines.append("來源：" + " · ".join(URLS.values()))
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
