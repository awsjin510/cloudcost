"""Tests for the vendor-documentation drift checker.

Fixtures under tests/fixtures/llm_sources are trimmed copies of the official
pages as fetched on 2026-09-28/29, so these tests run offline and pin down
both "today the catalogue matches" and "a change would be caught".
"""

from pathlib import Path

import pytest

from cloudcost.llm import LLMModel, ModelLine, list_models
from cloudcost.llm.drift import (
    compare,
    fetch_pages,
    page_urls,
    parse_anthropic_pricing,
    parse_anthropic_rate_limits,
    parse_azure_openai,
    parse_bedrock_gr,
    parse_foundry,
    parse_gemini_pricing,
    parse_openai_model_page,
    parse_openai_pricing,
    parse_vertex,
    parse_vertex_paygo,
    render_markdown,
)

FIXTURES = Path(__file__).parent / "fixtures" / "llm_sources"
FILES = {
    "anthropic_rate_limits": "anthropic_rate_limits.md",
    "anthropic_pricing": "anthropic_pricing.md",
    "foundry": "foundry.html",
    "vertex": "vertex.html",
    "bedrock_gr": "bedrock_gr.html",
    "openai_pricing": "openai_pricing.md",
    "azure_openai": "azure_openai.html",
    "gemini_pricing": "gemini_pricing.md",
    "vertex_paygo": "vertex_paygo.html",
}


@pytest.fixture
def pages():
    out = {k: (FIXTURES / v).read_text(encoding="utf-8") for k, v in FILES.items()}
    for info in list_models(ModelLine.GPT):
        out[f"openai_model:{info.api_id}"] = (FIXTURES / f"openai_{info.api_id}.md").read_text(encoding="utf-8")
    return out


def _kinds(report, source=None):
    return {(f.source, f.kind) for f in report.findings if source is None or f.source == source}


def _inject_row(html, row, before="</table>"):
    return html.replace(before, row + before, 1)


class TestParsers:
    def test_anthropic_tiers(self, pages):
        rl = parse_anthropic_rate_limits(pages["anthropic_rate_limits"])
        assert rl["Claude Fable 5.x"]["start"] == (1_000, 500_000, 100_000)
        assert rl["Claude Opus 5.5"]["scale"] == (10_000, 10_000_000, 2_000_000)
        assert rl["Claude Haiku 4.5"]["build"] == (5_000, 5_000_000, 1_000_000)

    def test_anthropic_pricing(self, pages):
        prices = parse_anthropic_pricing(pages["anthropic_pricing"])
        assert prices["Claude Fable 5.1"] == (10, 12.5, 0.25, 50)
        assert prices["Claude Haiku 4.5"] == (1, 1.25, 0.1, 5)

    def test_foundry_subscriptions(self, pages):
        f = parse_foundry(pages["foundry"])
        assert f["payg"]["claude-fable-5-1"] == (0, 0, 0)
        assert f["payg"]["claude-sonnet-4-6"] == (80, 80_000, 16_000)

    def test_vertex_claude_endpoints(self, pages):
        v = parse_vertex(pages["vertex"])
        assert v["Claude Sonnet 5"]["global"] == (2_500, 25_000_000, 2_500_000)
        assert v["Claude Fable 5.1"].get("global") is None  # published blank

    def test_bedrock_general_reference(self, pages):
        gr = parse_bedrock_gr(pages["bedrock_gr"])
        # The slide's original AWS figures: Fable 5 on the Mantle endpoint.
        assert gr["[bedrock-mantle endpoint] Input tokens per minute for Claude Fable 5"] == 2_000_000
        assert gr["[bedrock-mantle endpoint] Output tokens per minute for Claude Fable 5"] == 200_000
        assert gr["Global cross-region model inference tokens per minute for GPT-6 Sol"] == 2_000_000

    def test_openai_model_page_tiers_under_either_heading(self, pages):
        """Most pages title the table "Standard"; the Luna pages say "default"."""
        for mid in ("gpt-6-sol", "gpt-6-luna"):
            tiers = parse_openai_model_page(pages[f"openai_model:{mid}"])["tiers"]
            assert set(tiers) == {"tier1", "tier2", "tier3", "tier4", "tier5"}
        assert parse_openai_model_page(pages["openai_model:gpt-6-luna"])["tiers"]["tier5"] == (30_000, 180_000_000)

    def test_openai_pricing_table_includes_long_context(self, pages):
        t = parse_openai_pricing(pages["openai_pricing"])
        assert t["gpt-5.6-sol"] == (4, 0.4, 5, 20, 8, 0.8, 10, 30)
        assert t["gpt-5.5"][2] is None  # no cache-write charge

    def test_azure_six_tiers(self, pages):
        az = parse_azure_openai(pages["azure_openai"])
        assert sorted(az) == [1, 2, 3, 4, 5, 6]
        assert az[1]["gpt-6-astra"] == (1_000, 1_000_000)
        assert az[6]["gpt-5.5"] == (15_000, 15_000_000)

    def test_gemini_second_price_is_not_always_long_context(self, pages):
        """3.8 Flash lists its 2027 price second; only "> 200k" marks long context."""
        g = parse_gemini_pricing(pages["gemini_pricing"])
        assert g["gemini-3.8-flash"]["input"] == (0.75, None)
        assert g["gemini-3.1-pro-preview"]["input"] == (2.0, 4.0)

    def test_vertex_paygo_baselines(self, pages):
        v = parse_vertex_paygo(pages["vertex_paygo"])
        assert v["pro"] == {1: 500_000, 2: 1_000_000, 3: 2_000_000, 4: 10_000_000}
        assert v["flash"][4] == 50_000_000


class TestCurrentCatalogue:
    def test_matches_every_published_number(self, pages):
        report = compare(pages)
        assert report.clean, "\n".join(f.line() for f in report.findings)

    def test_every_source_was_actually_checked(self, pages):
        report = compare(pages)
        for source in ("anthropic", "pricing", "foundry", "vertex", "bedrock", "openai",
                       "azure_openai", "gemini", "vertex_paygo"):
            assert report.checked.get(source, 0) > 0, source
        assert sum(report.checked.values()) >= 160

    def test_every_claude_model_is_mapped_to_its_rate_limit_row(self):
        """A model missing from this map would never be checked against the tier table."""
        from cloudcost.llm.drift import _ANTHROPIC_RL_LABEL

        assert set(_ANTHROPIC_RL_LABEL) == {m.model for m in list_models(ModelLine.CLAUDE)}

    def test_page_list_covers_every_gpt_model(self):
        urls = page_urls()
        for info in list_models(ModelLine.GPT):
            assert urls[f"openai_model:{info.api_id}"].endswith(f"/{info.api_id}.md")


class TestDetection:
    def test_a_changed_claude_quota(self, pages):
        pages["anthropic_rate_limits"] = pages["anthropic_rate_limits"].replace("| 500,000 ", "| 600,000 ", 1)
        assert any(f.kind == "mismatch" and "start" in f.subject for f in compare(pages).findings)

    def test_a_new_claude_model(self, pages):
        """The failure this checker exists for: the vendor ships a model we lack."""
        i = pages["anthropic_rate_limits"].index('<Tab title="Start tier">')
        j = pages["anthropic_rate_limits"].index("| Claude Fable", i)
        pages["anthropic_rate_limits"] = (pages["anthropic_rate_limits"][:j]
                                          + "| Claude Opus 6 | 1,000 | 2,000,000 | 400,000 |\n    "
                                          + pages["anthropic_rate_limits"][j:])
        assert any(f.kind == "new_model" and "Opus 6" in f.subject for f in compare(pages).findings)

    def test_a_bedrock_default_that_changed(self, pages):
        gr = pages["bedrock_gr"]
        i = gr.index("Input tokens per minute for Claude Fable 5<")
        j = gr.index("2,000,000", i)
        pages["bedrock_gr"] = gr[:j] + "3,000,000" + gr[j + len("2,000,000"):]
        assert any(f.source == "bedrock" and f.kind == "mismatch" and "Fable 5 mantle" in f.subject
                   for f in compare(pages).findings)

    def test_bedrock_publishing_a_default_we_mark_unpublished(self, pages):
        row = ("<tr><td>[bedrock-mantle endpoint] Input tokens per minute for Claude Opus 5.5</td>"
               "<td>Each supported Region: 20,000,000</td><td>Yes</td></tr>"
               "<tr><td>[bedrock-mantle endpoint] Output tokens per minute for Claude Opus 5.5</td>"
               "<td>Each supported Region: 2,000,000</td><td>Yes</td></tr>")
        pages["bedrock_gr"] = _inject_row(pages["bedrock_gr"], row)
        assert ("bedrock", "now_published") in _kinds(compare(pages))

    def test_bedrock_publishing_a_runtime_quota_we_mark_unpublished(self, pages):
        """Sonnet 5.5 shipped before AWS listed its bedrock-runtime default."""
        row = ("<tr><td>Global cross-region model inference tokens per minute for Anthropic Claude Sonnet 5.5</td>"
               "<td>Each supported Region: 6,000,000</td><td>Yes</td></tr>")
        pages["bedrock_gr"] = _inject_row(pages["bedrock_gr"], row)
        assert any(f.kind == "now_published" and "Sonnet 5.5" in f.subject for f in compare(pages).findings)

    def test_a_new_model_on_bedrock(self, pages):
        row = ("<tr><td>Global cross-region model inference tokens per minute for GPT-6 Terra</td>"
               "<td>Each supported Region: 8,000,000</td><td>Yes</td></tr>")
        pages["bedrock_gr"] = _inject_row(pages["bedrock_gr"], row)
        assert any(f.kind == "new_model" and "GPT-6 Terra" in f.subject for f in compare(pages).findings)

    def test_an_openai_tier_change(self, pages):
        key = "openai_model:gpt-6-sol"
        pages[key] = pages[key].replace("| Tier 1 | 500 | 500,000 |", "| Tier 1 | 500 | 800,000 |", 1)
        assert any(f.source == "openai" and "t1" in f.subject for f in compare(pages).findings)

    def test_a_new_gpt_6_variant_is_not_ignored(self, pages):
        """Regression: "gpt-6-terra" parsed as version (6,), which sorted below (6, 0)."""
        pages["openai_pricing"] += "\n| gpt-6-terra | $1.00 | $0.10 | $1.25 | $5.00 | | | | |\n"
        assert any("gpt-6-terra" in f.subject for f in compare(pages).findings)

    def test_a_new_openai_model(self, pages):
        pages["openai_pricing"] = pages["openai_pricing"].replace(
            "| gpt-6-astra |", "| gpt-6-terra | $1.00 | $0.10 | $1.25 | $5.00 | $2.00 | $0.20 | $2.50 | $7.50 |\n| gpt-6-astra |", 1)
        assert any(f.kind == "new_model" and "gpt-6-terra" in f.subject for f in compare(pages).findings)

    def test_an_openai_price_change(self, pages):
        pages["openai_pricing"] = pages["openai_pricing"].replace("| gpt-5.6-sol | $4.00 |", "| gpt-5.6-sol | $5.00 |", 1)
        assert any(f.source == "openai" and f.kind == "mismatch" and "GPT-5.6 Sol" in f.subject
                   for f in compare(pages).findings)

    def test_an_azure_tier_change(self, pages):
        az = pages["azure_openai"]
        i = az.index("gpt-6-astra")
        j = az.index("1,000,000", i)
        pages["azure_openai"] = az[:j] + "2,000,000" + az[j + len("1,000,000"):]
        assert ("azure_openai", "mismatch") in _kinds(compare(pages))

    def test_a_gemini_price_change(self, pages):
        before = pages["gemini_pricing"]
        pages["gemini_pricing"] = before.replace("| $2.00, prompts \\<= 200k", "| $2.50, prompts \\<= 200k", 1)
        assert pages["gemini_pricing"] != before
        assert ("gemini", "mismatch") in _kinds(compare(pages))

    def test_a_new_gemini_model(self, pages):
        """Copy the 3.8 Flash section under a new id, as Google does for each release."""
        md = pages["gemini_pricing"]
        section = md[:md.index("\n## ", 1)]
        new = section.replace("Gemini 3.8 Flash", "Gemini 3.9 Flash").replace("gemini-3.8-flash", "gemini-3.9-flash")
        pages["gemini_pricing"] = new + "\n" + md
        assert any(f.kind == "new_model" and "gemini-3.9-flash" in f.subject for f in compare(pages).findings)

    def test_known_older_gemini_flash_versions_are_not_new_models(self, pages):
        assert ("gemini", "new_model") not in _kinds(compare(pages))

    def test_a_vertex_paygo_change(self, pages):
        pages["vertex_paygo"] = pages["vertex_paygo"].replace("500,000", "750,000", 1)
        assert ("vertex_paygo", "mismatch") in _kinds(compare(pages))

    def test_a_restructured_page_is_a_finding_not_a_crash(self):
        report = compare({})
        assert not report.clean
        assert {f.kind for f in report.findings} <= {"parse_error", "missing"}


class TestPlumbing:
    def test_unreachable_pages_degrade_to_findings(self):
        def boom(url):
            raise OSError("offline")

        pages = fetch_pages(get=boom)
        assert set(pages) == set(page_urls())
        assert not compare(pages).clean

    def test_markdown_groups_findings_for_an_issue(self, pages):
        pages["anthropic_rate_limits"] = pages["anthropic_rate_limits"].replace("| 500,000 ", "| 600,000 ", 1)
        body = render_markdown(compare(pages))
        assert "數值不一致" in body
        assert "python -m cloudcost.llm.export" in body
