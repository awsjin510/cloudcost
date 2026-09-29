"""The browser copy of the planner must not drift from the Python one.

Two guards:

* ``data.js`` is generated from ``cloudcost.llm.catalog``; the committed file
  has to match what the generator produces right now.
* ``engine.js`` is a hand-written port, so it is executed under Node and its
  output diffed against the Python implementation for a spread of scenarios.

Between them, a change to a quota number or a sizing rule that only lands on
one side becomes a test failure rather than a wrong answer in the browser.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from cloudcost.llm import (
    AppWorkload,
    LLMModel,
    LLMWorkload,
    ModelLine,
    QuotaOverride,
    evaluate_workload,
    size_from_scenario,
)
from cloudcost.llm.export import (
    ASSET_DIR,
    MIRRORED,
    MIRROR_DIR,
    render_data_js,
    sync_assets,
)

NODE = shutil.which("node")
requires_node = pytest.mark.skipif(NODE is None, reason="node is not installed")

SCENARIOS: list[LLMWorkload] = [
    # The canonical pre-sales question.
    LLMWorkload(apps=[AppWorkload(concurrent_users=100)]),
    # Caching changes both capacity and cost.
    LLMWorkload(apps=[AppWorkload(concurrent_users=100, cache_hit_rate=0.8)], max_tokens=4_000),
    # Output-bound rather than input-bound.
    LLMWorkload(
        apps=[
            AppWorkload(
                concurrent_users=20,
                requests_per_user_per_minute=3,
                input_tokens_per_request=60_000,
                output_tokens_per_request=8_000,
                cache_hit_rate=0.8,
            )
        ],
        monthly_requests=5_000_000,
    ),
    # Several applications sharing one organisation's quota.
    LLMWorkload(
        apps=[
            AppWorkload(name="客服", concurrent_users=200, input_tokens_per_request=4_000,
                        output_tokens_per_request=500, cache_hit_rate=0.6),
            AppWorkload(name="RAG", concurrent_users=60, cache_hit_rate=0.3),
            AppWorkload(name="代理", concurrent_users=15, requests_per_user_per_minute=3,
                        input_tokens_per_request=60_000, output_tokens_per_request=8_000,
                        cache_hit_rate=0.8),
        ],
        max_tokens=16_000,
        monthly_requests=20_000_000,
    ),
    # Account-specific quota replacing an unpublished default.
    LLMWorkload(
        apps=[AppWorkload(concurrent_users=100)],
        max_tokens=4_000,
        account_quotas=[QuotaOverride(plan_id="mantle", itpm=20_000_000, otpm=4_000_000)],
    ),
    # Every other model.
    *[LLMWorkload(model=m, apps=[AppWorkload(concurrent_users=120, cache_hit_rate=0.5)])
      for m in LLMModel if m is not LLMModel.FABLE_5_1],
    # Thinking tokens, truncation warning and batch eligibility.
    LLMWorkload(
        apps=[AppWorkload(concurrent_users=150, thinking_tokens_per_request=3_000, cache_hit_rate=0.4)],
        max_tokens=4_000,
        monthly_requests=800_000,
        batch_eligible=True,
    ),
    # Every scenario as the form builds it, at a load that forces advice.
    *[size_from_scenario(sid, users=2_000, peak_profile="spiky")
      for sid in ("support", "rag", "summarize", "coding", "writing")],
    # Every scenario on every vendor line.
    *[size_from_scenario(sid, users=800, line=line)
      for line in (ModelLine.GPT, ModelLine.GEMINI, ModelLine.GROK)
      for sid in ("support", "rag", "summarize", "coding", "writing")],
    # Every model at one load, without a monthly volume (daily quotas unknown).
    *[LLMWorkload(model=m, apps=[AppWorkload(concurrent_users=300, cache_hit_rate=0.3,
                                             thinking_tokens_per_request=500)])
      for m in LLMModel],
    # Long prompts cross the GPT (272K) and Gemini (200K) long-context thresholds.
    LLMWorkload(model=LLMModel.GPT_6_SOL, apps=[AppWorkload(concurrent_users=20, input_tokens_per_request=300_000)],
                max_tokens=8_000, monthly_requests=200_000),
    LLMWorkload(model=LLMModel.GEMINI_3_1_PRO, apps=[AppWorkload(concurrent_users=20, input_tokens_per_request=250_000)],
                max_tokens=8_000, monthly_requests=200_000),
    # Grok's long-context rate starts at exactly 200K; Batch is 20% off or absent.
    LLMWorkload(model=LLMModel.GROK_4_7, apps=[AppWorkload(concurrent_users=20, input_tokens_per_request=200_000)],
                max_tokens=8_000, monthly_requests=200_000, batch_eligible=True),
    LLMWorkload(model=LLMModel.GROK_4_3, apps=[AppWorkload(concurrent_users=3_000, input_tokens_per_request=199_999)],
                max_tokens=8_000, monthly_requests=200_000, batch_eligible=True),
    LLMWorkload(model=LLMModel.SONNET_5_5, apps=[AppWorkload(concurrent_users=50)], max_tokens=2_000),
    # Account overrides on combined-TPM and spend-cap dimensions.
    LLMWorkload(model=LLMModel.GPT_6_ASTRA, apps=[AppWorkload(concurrent_users=200)], max_tokens=6_000,
                account_quotas=[QuotaOverride(plan_id="runtime", tpm=50_000_000, rpm=20_000),
                                QuotaOverride(plan_id="az_t1", tpm=9_000_000)]),
    LLMWorkload(model=LLMModel.GEMINI_3_8_FLASH, apps=[AppWorkload(concurrent_users=2_000)], monthly_requests=5_000_000,
                account_quotas=[QuotaOverride(plan_id="g_t1", rpm=2_000, rpd=100_000, usd10m=40)]),
]

_DRIVER = """
const path = process.argv[1];
const data = require(path + '/data.js');
Object.assign(globalThis, data);
const engine = require(path + '/engine.js');
const input = JSON.parse(process.argv[2]);
process.stdout.write(JSON.stringify(engine.evaluateWorkload(input.workload, input.platform)));
"""


def _run_js(workload: LLMWorkload, platform=None) -> dict:
    payload = json.dumps(
        {"workload": json.loads(workload.model_dump_json()), "platform": platform},
        ensure_ascii=False,
    )
    proc = subprocess.run(
        [NODE, "-e", _DRIVER, str(ASSET_DIR), payload],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _diff(py, js, path=""):
    """Yield human-readable differences, tolerating float representation."""
    if isinstance(py, dict) and isinstance(js, dict):
        for key in set(py) | set(js):
            if key not in py:
                yield f"{path}.{key}: missing in python"
            elif key not in js:
                yield f"{path}.{key}: missing in js"
            else:
                yield from _diff(py[key], js[key], f"{path}.{key}")
    elif isinstance(py, list) and isinstance(js, list):
        if len(py) != len(js):
            yield f"{path}: length {len(py)} vs {len(js)}"
            return
        for i, (a, b) in enumerate(zip(py, js)):
            yield from _diff(a, b, f"{path}[{i}]")
    elif isinstance(py, (int, float)) and isinstance(js, (int, float)) and not isinstance(py, bool):
        if py != pytest.approx(js, rel=1e-6, abs=1e-9):
            yield f"{path}: {py!r} vs {js!r}"
    elif py != js:
        yield f"{path}: {py!r} vs {js!r}"


class TestGeneratedData:
    def test_committed_data_js_is_current(self):
        """Regenerate with: python -m cloudcost.llm.export"""
        expected = render_data_js()
        for directory in (ASSET_DIR, MIRROR_DIR):
            target = directory / "data.js"
            assert target.exists(), f"{target} is missing"
            assert target.read_text(encoding="utf-8") == expected, (
                f"{target} is stale — run: python -m cloudcost.llm.export"
            )

    def test_docs_mirror_matches_the_package_copy(self):
        for name in MIRRORED:
            assert (ASSET_DIR / name).read_text(encoding="utf-8") == (
                MIRROR_DIR / name
            ).read_text(encoding="utf-8"), f"docs/llm/{name} is stale — run the exporter"

    def test_sync_is_idempotent(self):
        assert all(sync_assets(write=False).values())

    def test_data_js_is_marked_generated(self):
        assert "GENERATED FILE" in render_data_js()


@requires_node
class TestEngineParity:
    @pytest.mark.parametrize("workload", SCENARIOS, ids=[f"{i:02d}-{w.model.value}" for i, w in enumerate(SCENARIOS)])
    def test_js_matches_python(self, workload):
        py = json.loads(evaluate_workload(workload).model_dump_json())
        js = _run_js(workload)
        # The echoed `workload` differs only in how defaults are filled in by
        # Pydantic vs the JS object spread, which is not a behavioural rule.
        py.pop("workload", None)
        js.pop("workload", None)
        diffs = list(_diff(py, js))
        assert not diffs, "python/js divergence:\n  " + "\n  ".join(diffs[:20])

    def test_platform_filter_matches(self):
        w = SCENARIOS[0]
        py = json.loads(evaluate_workload(w, platform="vertex").model_dump_json())
        js = _run_js(w, platform="vertex")
        py.pop("workload", None)
        js.pop("workload", None)
        assert not list(_diff(py, js))
        assert len(js["results"]) == 2


_CLASS_DRIVER = """
const path = process.argv[1];
Object.assign(globalThis, require(path + '/data.js'));
const engine = require(path + '/engine.js');
const render = require(path + '/render.js');
const out = {};
for (const line of LLM_LINES) {
  for (const cls of LLM_CONST.MODEL_CLASSES) {
    out[line.line + '/' + cls] = [engine.modelFor(line.line, cls), render.llmModelFor(line.line, cls)];
  }
}
process.stdout.write(JSON.stringify(out));
"""


@requires_node
def test_line_switch_keeps_the_same_capability_class_as_python():
    """Switching AI 模型 in the form must land on the version the planner would pick."""
    from cloudcost.llm.catalog import MODEL_CLASSES, model_for

    proc = subprocess.run([NODE, "-e", _CLASS_DRIVER, str(ASSET_DIR)], capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    got = json.loads(proc.stdout)
    for line in ModelLine:
        for cls in MODEL_CLASSES:
            want = model_for(line, cls).value
            assert got[f"{line.value}/{cls}"] == [want, want], (line, cls)


def test_asset_urls_carry_the_release_version():
    """data.js and the modules must change together, so a cached old module cannot meet new data."""
    import tomllib

    root = Path(__file__).resolve().parents[1]
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    for page in (root / "docs" / "index.html", root / "cloudcost" / "web" / "templates" / "index.html"):
        html = page.read_text(encoding="utf-8")
        refs = re.findall(r'llm/[\w.]+\.(?:js|css)(\?v=[\w.]+)?"', html)
        assert refs, page
        assert set(refs) == {f"?v={version}"}, page
        assert f"CloudCost v{version}" in html, page


def test_llm_number_inputs_do_not_step_validate():
    """A stepped input rejects derived values such as 17,600 or 20,000 and blocks 試算配額與費用."""
    root = Path(__file__).resolve().parents[1]
    for page in (root / "docs" / "index.html", root / "cloudcost" / "web" / "templates" / "index.html"):
        for tag in re.findall(r'<input type="number" id="llm_[^>]*>', page.read_text(encoding="utf-8")):
            assert re.findall(r'step="(?!any")', tag) == [], (page.name, tag)
    form = (ASSET_DIR / "form.js").read_text(encoding="utf-8")
    assert re.findall(r'step="(?!any")', form) == []
