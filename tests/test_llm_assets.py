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
import shutil
import subprocess

import pytest

from cloudcost.llm import AppWorkload, LLMModel, LLMWorkload, QuotaOverride, evaluate_workload
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
    @pytest.mark.parametrize("workload", SCENARIOS, ids=lambda w: f"{w.model.value}-{len(w.apps)}app")
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
