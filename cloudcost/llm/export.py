"""Generate the browser-side copy of the quota catalogue.

The GitHub Pages build has no backend, so the static page has to carry its
own copy of the engine. Hand-maintaining a second copy of 32 quota rows is
how numbers drift apart, so the data half is *generated* from
``cloudcost.llm.catalog`` and the generated file is committed. A test
asserts the committed file still matches, which turns drift into a test
failure instead of a wrong answer on a customer call.

The logic half (``engine.js``) is a hand-written port; a parity test runs
it under Node against the Python implementation to keep the two honest.

Regenerate with::

    python -m cloudcost.llm.export
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from cloudcost.llm.catalog import (
    ACTIVE_HOURS_PER_DAY,
    MAX_OUTPUT_TOKENS,
    PEAK_FACTORS,
    VERIFIED,
    WORKING_DAYS_PER_MONTH,
    list_models,
    list_plans,
    list_scenarios,
)
from cloudcost.llm.planner import AMPLE_THRESHOLD, MAX_SUGGESTED_CACHE_RATE

#: Served by the FastAPI app and installed with the package.
ASSET_DIR = Path(__file__).resolve().parent.parent / "web" / "static" / "llm"

#: Standalone copy deployed to GitHub Pages.
MIRROR_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "llm"

#: Hand-written files mirrored verbatim from ASSET_DIR to MIRROR_DIR.
MIRRORED = ("engine.js", "render.js", "form.js", "style.css")

DATA_FILENAME = "data.js"

_HEADER = """// GENERATED FILE — do not edit by hand.
// Regenerate with:  python -m cloudcost.llm.export
// Source of truth:  cloudcost/llm/catalog.py
//
// Quota values are platform DEFAULTS, not model limits; every one of them
// can be raised on request. Each row carries the document it came from.
"""


def _js(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def _limit(limit) -> dict:
    out: dict = {"status": limit.status.value}
    if limit.value is not None:
        out["value"] = limit.value
    if limit.note:
        out["note"] = limit.note
    return out


def render_data_js() -> str:
    """Render the generated data module as JavaScript source."""
    consts = {
        "MAX_OUTPUT_TOKENS": MAX_OUTPUT_TOKENS,
        "VERIFIED": VERIFIED,
        "AMPLE_THRESHOLD": AMPLE_THRESHOLD,
        "MAX_SUGGESTED_CACHE_RATE": MAX_SUGGESTED_CACHE_RATE,
        "PEAK_FACTORS": PEAK_FACTORS,
        "ACTIVE_HOURS_PER_DAY": ACTIVE_HOURS_PER_DAY,
        "WORKING_DAYS_PER_MONTH": WORKING_DAYS_PER_MONTH,
    }

    scenarios = [
        {
            "scenario_id": s.scenario_id,
            "label": s.label,
            "blurb": s.blurb,
            "icon": s.icon,
            "input_tokens_per_request": s.input_tokens_per_request,
            "output_tokens_per_request": s.output_tokens_per_request,
            "cache_hit_rate": s.cache_hit_rate,
            "max_tokens": s.max_tokens,
            "suggested_model": s.suggested_model.value,
            "messages_per_user_per_day": s.messages_per_user_per_day,
        }
        for s in list_scenarios()
    ]

    models = [
        {
            "model": m.model.value,
            "label": m.label,
            "pricing": {
                "input_per_mtok": m.pricing.input_per_mtok,
                "output_per_mtok": m.pricing.output_per_mtok,
                "cache_read_per_mtok": m.pricing.cache_read_per_mtok,
                "cache_write_5m_per_mtok": m.pricing.cache_write_5m_per_mtok,
            },
            "notes": m.notes,
        }
        for m in list_models()
    ]

    plans = [
        {
            "model": p.model.value,
            "model_label": p.model_label,
            "platform": p.platform.value,
            "plan_id": p.plan_id,
            "platform_label": p.platform_label,
            "plan_label": p.plan_label,
            "rpm": _limit(p.rpm),
            "itpm": _limit(p.itpm),
            "otpm": _limit(p.otpm),
            "reserves_max_tokens": p.reserves_max_tokens,
            "notes": p.notes,
            "source": p.source,
            "verified": p.verified,
        }
        for p in list_plans()
    ]

    lines = [
        _HEADER,
        f"const LLM_CONST = {_js(consts)};",
        "",
        f"const LLM_MODELS = {json.dumps(models, ensure_ascii=False, indent=2)};",
        "",
        f"const LLM_SCENARIOS = {json.dumps(scenarios, ensure_ascii=False, indent=2)};",
        "",
        "const LLM_PLANS = [",
    ]
    for plan in plans:
        lines.append("  " + _js(plan) + ",")
    lines.append("];")
    lines.append("")
    lines.append(
        "if (typeof module !== 'undefined') "
        "{ module.exports = { LLM_CONST, LLM_MODELS, LLM_SCENARIOS, LLM_PLANS }; }"
    )
    lines.append("")
    return "\n".join(lines)


def sync_assets(write: bool = True) -> dict[str, bool]:
    """Write data.js and mirror the hand-written files into docs/.

    Returns a map of relative path -> whether the on-disk content already
    matched. With ``write=False`` nothing is touched, which is what the
    freshness test uses.
    """
    results: dict[str, bool] = {}

    data_js = render_data_js()
    for directory in (ASSET_DIR, MIRROR_DIR):
        target = directory / DATA_FILENAME
        current = target.read_text(encoding="utf-8") if target.exists() else None
        results[str(target)] = current == data_js
        if write and current != data_js:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(data_js, encoding="utf-8")

    for name in MIRRORED:
        source = ASSET_DIR / name
        target = MIRROR_DIR / name
        if not source.exists():
            raise FileNotFoundError(
                f"{source} is missing; it is hand-written and must exist before mirroring"
            )
        expected = source.read_text(encoding="utf-8")
        current = target.read_text(encoding="utf-8") if target.exists() else None
        results[str(target)] = current == expected
        if write and current != expected:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    return results


def main() -> None:
    for path, was_current in sync_assets(write=True).items():
        print(("unchanged  " if was_current else "updated    ") + path)


if __name__ == "__main__":
    main()
