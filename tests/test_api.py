from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


class TestInternalAndHybridApi:
    def test_health_endpoint(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "agy_available" in data

    def test_profiles_and_models_endpoints(self):
        p_resp = client.get("/api/v1/profiles")
        assert p_resp.status_code == 200
        profiles = p_resp.json()["profiles"]
        assert any(p["id"] == "architecte" for p in profiles)
        assert any(p["id"] == "avocat" for p in profiles)

        with patch("api.get_available_agy_models") as mock_models:
            mock_models.return_value = [
                ("gemini-3.8-flash-low", "Gemini 3.8 Flash (Low)")
            ]
            m_resp = client.get("/api/v1/models")
            assert m_resp.status_code == 200
            assert m_resp.json()["models"][0]["id"] == "gemini-3.8-flash-low"

    def test_analyze_and_clean_unicode_endpoints(self):
        dirty = "Bonjour\u200b\u00a0le monde ! Il convient de souligner que ce paysage numérique évolue."
        c_resp = client.post("/api/v1/clean-unicode", json={"text": dirty})
        assert c_resp.status_code == 200
        c_data = c_resp.json()
        assert "\u200b" not in c_data["cleaned_text"]
        assert "\u00a0" not in c_data["cleaned_text"]
        assert c_data["stats"]["removed_count"] >= 1

        a_resp = client.post("/api/v1/analyze", json={"text": dirty})
        assert a_resp.status_code == 200
        a_data = a_resp.json()
        assert "composite_score" in a_data
        assert a_data["invisible_count"] >= 1

    @patch("api.humanize_text")
    @patch("api.is_agy_available", return_value=True)
    def test_humanize_local_agy_mode(self, _mock_agy, mock_humanize):
        mock_humanize.return_value = (True, "Texte direct et factuel.")
        resp = client.post(
            "/api/v1/humanize",
            json={
                "text": "Il convient de souligner l'importance de ce projet.",
                "profile_id": "architecte",
                "engine": "auto",
                "model": "gemini-3.8-flash-low",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["engine_used"] == "agy"
        assert data["humanized_text"] == "Texte direct et factuel."

    @patch("api.humanize_text")
    def test_humanize_header_api_key_injection_for_cloud_run(self, mock_humanize):
        mock_humanize.return_value = (True, "Sortie Cloud Run via cle injectee.")
        resp = client.post(
            "/api/v1/humanize",
            headers={"X-Gemini-API-Key": "AIzaSyInjectedKey"},
            json={
                "text": "Texte source.",
                "profile_id": "avocat",
                "engine": "auto",
                "model": "gemini-3-flash-preview",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["engine_used"] == "BYOK"
        _, kwargs = mock_humanize.call_args
        assert kwargs["api_key"] == "AIzaSyInjectedKey"
        assert kwargs["engine"] == "BYOK"

    @patch("api.is_agy_available", return_value=False)
    def test_humanize_missing_key_when_no_cli_returns_401(self, _mock_agy, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        resp = client.post(
            "/api/v1/humanize",
            json={"text": "Texte sur Cloud Run sans cle.", "engine": "BYOK"},
        )
        assert resp.status_code == 401
