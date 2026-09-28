"""Tests for the vendor-documentation drift checker.

Fixtures under tests/fixtures/llm_sources are trimmed copies of the five
official pages as fetched on 2026-09-28, so these tests run offline and pin
down both "today the catalogue matches" and "a change would be caught".
"""

from pathlib import Path

import pytest

from cloudcost.llm.drift import (
    compare,
    fetch_pages,
    parse_anthropic_pricing,
    parse_anthropic_rate_limits,
    parse_foundry,
    parse_vertex,
    render_markdown,
)

FIXTURES = Path(__file__).parent / "fixtures" / "llm_sources"
FILES = {
    "anthropic_rate_limits": "anthropic_rate_limits.md",
    "anthropic_pricing": "anthropic_pricing.md",
    "foundry": "foundry.html",
    "vertex": "vertex.html",
    "bedrock": "bedrock.html",
}


@pytest.fixture
def pages():
    return {k: (FIXTURES / v).read_text(encoding="utf-8") for k, v in FILES.items()}


def _kinds(report, source=None):
    return {(f.source, f.kind) for f in report.findings if source is None or f.source == source}


class TestParsers:
    def test_anthropic_tiers(self, pages):
        rl = parse_anthropic_rate_limits(pages["anthropic_rate_limits"])
        assert rl["Claude Fable 5.x"]["start"] == (1_000, 500_000, 100_000)
        assert rl["Claude Opus 5.5"]["scale"] == (10_000, 10_000_000, 2_000_000)

    def test_anthropic_pricing(self, pages):
        prices = parse_anthropic_pricing(pages["anthropic_pricing"])
        assert prices["Claude Fable 5.1"] == (10, 12.5, 0.25, 50)
        assert prices["Claude Opus 5.5"] == (4, 5, 0.2, 20)

    def test_foundry_subscriptions(self, pages):
        f = parse_foundry(pages["foundry"])
        assert f["payg"]["claude-fable-5-1"] == (0, 0, 0)
        assert f["enterprise"]["claude-opus-5-5"] == (10_000, 10_000_000, 2_000_000)

    def test_vertex_endpoints(self, pages):
        v = parse_vertex(pages["vertex"])
        assert v["Claude Sonnet 5"]["global"] == (2_500, 25_000_000, 2_500_000)
        assert v["Claude Opus 5.5"]["multi_region"] == (1_000, 10_000_000, 1_000_000)
        # Published blank: Fable 5.1 shares the Fable lineage bucket.
        assert v["Claude Fable 5.1"].get("global") is None


class TestCurrentCatalogue:
    def test_matches_every_published_number(self, pages):
        report = compare(pages)
        assert report.clean, "\n".join(f.line() for f in report.findings)

    def test_every_source_was_actually_checked(self, pages):
        report = compare(pages)
        for source in ("anthropic", "pricing", "foundry", "vertex", "bedrock"):
            assert report.checked.get(source, 0) > 0, source


class TestDetection:
    def test_a_changed_quota_is_reported(self, pages):
        pages["anthropic_rate_limits"] = pages["anthropic_rate_limits"].replace(
            "| 500,000 ", "| 600,000 ", 1)
        report = compare(pages)
        hit = [f for f in report.findings if f.kind == "mismatch" and "start" in f.subject]
        assert hit and "600,000" in hit[0].actual

    def test_a_new_model_is_reported(self, pages):
        """The failure this checker exists for: the vendor ships a model we lack."""
        tab = '<Tab title="Start tier">'
        i = pages["anthropic_rate_limits"].index(tab)
        j = pages["anthropic_rate_limits"].index("| Claude Fable", i)
        row = "| Claude Opus 6 | 1,000 | 2,000,000 | 400,000 |\n    "
        pages["anthropic_rate_limits"] = pages["anthropic_rate_limits"][:j] + row + pages["anthropic_rate_limits"][j:]
        report = compare(pages)
        assert any(f.kind == "new_model" and "Opus 6" in f.subject for f in report.findings)

    def test_a_price_change_is_reported(self, pages):
        pages["anthropic_pricing"] = pages["anthropic_pricing"].replace(
            "| Claude Opus 5.5 ", "| Claude Opus 5.5 ", 1).replace("$4 / MTok", "$4.5 / MTok", 1)
        assert ("pricing", "mismatch") in _kinds(compare(pages))

    def test_a_new_foundry_deployment_is_reported(self, pages):
        extra = ("<tr><td>claude-opus-6</td><td>Global Standard</td><td>Yes</td><td>Yes</td>"
                 "<td>40</td><td>40,000</td><td>8,000</td></tr>")
        assert "</tbody>" in pages["foundry"]
        pages["foundry"] = pages["foundry"].replace("</tbody>", extra + "</tbody>", 1)
        assert ("foundry", "new_model") in _kinds(compare(pages))

    def test_bedrock_publishing_a_default_is_reported(self, pages):
        # The AWS table has no <tbody>; rows sit directly before </table>.
        extra = "<tr><td>Anthropic Claude Opus 5.5</td><td>10,000,000</td><td>2,000,000</td></tr>"
        assert "</table>" in pages["bedrock"]
        pages["bedrock"] = pages["bedrock"].replace("</table>", extra + "</table>", 1)
        assert ("bedrock", "now_published") in _kinds(compare(pages))

    def test_opus_4_7_on_bedrock_is_not_mistaken_for_a_modelled_model(self, pages):
        assert ("bedrock", "now_published") not in _kinds(compare(pages))

    def test_a_restructured_page_is_a_finding_not_a_crash(self):
        report = compare({k: "" for k in FILES})
        assert not report.clean
        assert {f.kind for f in report.findings} == {"parse_error"}


class TestPlumbing:
    def test_unreachable_pages_degrade_to_findings(self):
        def boom(url):
            raise OSError("offline")

        pages = fetch_pages(get=boom)
        assert set(pages) == set(FILES)
        assert not compare(pages).clean

    def test_markdown_groups_findings_for_an_issue(self, pages):
        pages["anthropic_rate_limits"] = pages["anthropic_rate_limits"].replace("| 500,000 ", "| 600,000 ", 1)
        body = render_markdown(compare(pages))
        assert "數值不一致" in body
        assert "python -m cloudcost.llm.export" in body
