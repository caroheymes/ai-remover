from __future__ import annotations

from unittest.mock import MagicMock, patch

from mcp_server import (
    analyze_ai_density,
    clean_invisible_unicode,
    humanize_text_tool,
)


class TestMcpServer:
    @patch("mcp_server.humanize_text")
    def test_humanize_text_direct_core_fallback(self, mock_humanize, monkeypatch):
        monkeypatch.delenv("AI_REMOVER_API_URL", raising=False)
        mock_humanize.return_value = (
            True,
            "Pipeline Python 3.12 en production sur BigQuery.",
        )

        res = humanize_text_tool(
            text="Fort de mon expérience, j'ai déployé un pipeline Python 3.12 sur BigQuery.",
            profile_id="architecte",
            model="gemini-3.8-flash-low",
        )
        assert res["success"] is True
        assert res["transport"] == "direct_core"
        assert "BigQuery" in res["humanized_text"]

    @patch("mcp_server.requests.post")
    def test_humanize_text_via_internal_api_when_configured(
        self, mock_post, monkeypatch
    ):
        monkeypatch.setenv("AI_REMOVER_API_URL", "http://127.0.0.1:8506")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "success": True,
            "humanized_text": "Texte traite par API interne.",
            "engine_used": "agy",
            "model_used": "gemini-3.8-flash-low",
            "score_before": 0.65,
            "score_after": 0.10,
        }
        mock_post.return_value = mock_resp

        res = humanize_text_tool(
            text="Texte source.",
            profile_id="architecte",
        )
        assert res["success"] is True
        assert res["transport"] == "http_api"
        assert res["humanized_text"] == "Texte traite par API interne."

    def test_analyze_and_clean_tools(self):
        sample = "Bonjour\u200b le monde. Il convient de souligner ce point."
        cleaned = clean_invisible_unicode(sample)
        assert "\u200b" not in cleaned["cleaned_text"]
        assert cleaned["removed_count"] == 1

        analysis = analyze_ai_density(sample)
        assert "composite_score" in analysis
        assert analysis["invisible_unicode_count"] == 1
