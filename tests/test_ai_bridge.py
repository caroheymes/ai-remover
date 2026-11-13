from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import requests

from core.ai_bridge import (
    call_antigravity_cli,
    call_gemini_api,
    get_agy_path,
    is_agy_available,
)


class TestAiBridge:
    def test_get_agy_path(self):
        path = get_agy_path()
        assert isinstance(path, str)
        assert len(path) > 0

    def test_is_agy_available(self):
        result = is_agy_available()
        assert isinstance(result, bool)

    @patch("subprocess.run")
    def test_call_antigravity_cli_success(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Texte réécrit et humanisé avec succès."
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc

        success, result = call_antigravity_cli("Prompt de test", model="test-model")
        assert success is True
        assert result == "Texte réécrit et humanisé avec succès."
        assert mock_run.called

    @patch("subprocess.run")
    def test_call_antigravity_cli_failure(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "Erreur de modèle introuvable."
        mock_run.return_value = mock_proc

        success, result = call_antigravity_cli("Prompt de test")
        assert success is False
        assert "Erreur Antigravity CLI" in result

    @patch("subprocess.run")
    def test_call_antigravity_cli_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="agy", timeout=10)
        success, result = call_antigravity_cli("Prompt", timeout_seconds=10)
        assert success is False
        assert "Délai d'attente dépassé" in result

    def test_call_gemini_api_missing_key(self):
        success, result = call_gemini_api("Prompt de test", api_key="")
        assert success is False
        assert "Clé d'API Google AI Studio manquante" in result

    @patch("requests.post")
    def test_call_gemini_api_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Texte humanisé par Gemini API."}]}}
            ]
        }
        mock_post.return_value = mock_resp

        success, result = call_gemini_api(
            "Prompt", api_key="AIzaSyDummyKey", model="gemini-3-flash-preview"
        )
        assert success is True
        assert result == "Texte humanisé par Gemini API."

    @patch("requests.post")
    def test_call_gemini_api_http_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "API key not valid"
        mock_post.return_value = mock_resp

        success, result = call_gemini_api("Prompt", api_key="InvalidKey")
        assert success is False
        assert "Erreur API Google Gemini (HTTP 403)" in result

    @patch("requests.post")
    def test_call_gemini_api_network_exception(self, mock_post):
        mock_post.side_effect = requests.RequestException("Connexion impossible")
        success, result = call_gemini_api("Prompt", api_key="SomeKey")
        assert success is False
        assert "Exception lors de l'appel à l'API Gemini" in result

    def test_split_text_into_chunks(self):
        from core.ai_bridge import split_text_into_chunks

        short_text = "Court paragraphe."
        assert split_text_into_chunks(short_text, max_chunk_size=100) == [short_text]

        long_text = "\n\n".join(
            [f"Paragraphe numéro {i} avec du contenu explicatif." for i in range(20)]
        )
        chunks = split_text_into_chunks(long_text, max_chunk_size=150)
        assert len(chunks) > 1
        assert all(len(c) <= 200 for c in chunks)

    @patch("subprocess.run")
    def test_call_antigravity_cli_long_prompt(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Partie traitée."
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc

        long_source = "Contenu substantiel. " * 500  # ~10,500 chars
        prompt = (
            "Consignes initiales\n\n"
            "--- TEXTE SOURCE À HUMANISER ---\n"
            f"{long_source}\n\n"
            "--- TEXTE FINAL HUMANISÉ ---"
        )

        success, result = call_antigravity_cli(prompt)
        assert success is True
        assert "Partie traitée." in result
        # Check that multiple chunks were executed
        assert mock_run.call_count >= 2

    @patch("core.ai_bridge.call_gemini_api")
    def test_humanize_text_gemini(self, mock_gemini):
        from core.ai_bridge import humanize_text

        mock_gemini.return_value = (True, "Texte humanisé avec brio.")
        ok, res = humanize_text(
            "Court texte source.",
            profile_id="avocat",
            engine="BYOK",
            api_key="DummyKey",
        )
        assert ok is True
        assert res == "Texte humanisé avec brio."
        assert mock_gemini.called

    @patch("core.ai_bridge.call_antigravity_cli")
    def test_humanize_text_chunking_preserves_all_parts(self, mock_cli):
        from core.ai_bridge import humanize_text

        mock_cli.side_effect = [
            (True, "Paragraphe 1 humanisé."),
            (True, "Paragraphe 2 humanisé."),
        ]
        multi_para_text = "Premier paragraphe complet.\n\nDeuxième paragraphe complet."
        ok, res = humanize_text(
            multi_para_text,
            profile_id="avocat",
            engine="agy",
            max_chunk_size=30,  # force 2 chunks
        )
        assert ok is True
        assert "Paragraphe 1 humanisé." in res
        assert "Paragraphe 2 humanisé." in res
        assert mock_cli.call_count == 2

    @patch("core.ai_bridge.call_antigravity_cli")
    def test_humanize_text_normalizes_punctuation(self, mock_cli):
        from core.ai_bridge import humanize_text

        mock_cli.return_value = (
            True,
            "Voici les faits : « l’outil » est prêt ! Qu’en pensez-vous ?",
        )
        ok, res = humanize_text(
            "Texte source",
            profile_id="architecte",
            engine="agy",
        )
        assert ok is True
        assert res == "Voici les faits: \"l'outil\" est prêt! Qu'en pensez-vous?"

    @patch("subprocess.run")
    def test_get_available_agy_models_filtering(self, mock_run):
        from core.ai_bridge import get_available_agy_models

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = (
            "gemini-4-carbon-high\tGemini 4 Carbon (High)\n"
            "claude-opus-5-5-high\tClaude Opus 5.5 (High)\n"
            "gemini-3.8-flash-medium\tGemini 3.8 Flash (Medium)\n"
            "gemini-3.8-flash-low\tGemini 3.8 Flash (Low)\n"
            "claude-sonnet-5-5-low\tClaude Sonnet 5.5 (Low)\n"
        )
        mock_run.return_value = mock_proc

        models = get_available_agy_models()
        model_ids = [m[0] for m in models]

        assert "gemini-3.8-flash-low" in model_ids
        assert "gemini-3.8-flash-medium" in model_ids
        # Exclusion stricte des modèles lourds
        assert "gemini-4-carbon-high" not in model_ids
        assert "claude-opus-5-5-high" not in model_ids
        assert "claude-sonnet-5-5-low" not in model_ids
        # Flash low doit être en première position (recommandé par défaut)
        assert models[0][0] == "gemini-3.8-flash-low"

    @patch("subprocess.run")
    def test_get_available_agy_models_fallback(self, mock_run):
        from core.ai_bridge import get_available_agy_models

        mock_run.side_effect = RuntimeError("Binaire indisponible")
        models = get_available_agy_models()
        assert len(models) >= 1
        assert models[0][0] == "gemini-3.8-flash-low"

    @patch("subprocess.run")
    def test_call_antigravity_cli_fallback_on_unknown_model(self, mock_run):
        # Premier appel avec un modèle inconnu qui échoue, second appel de repli sans --model qui réussit
        fail_proc = MagicMock()
        fail_proc.returncode = 1
        fail_proc.stdout = ""
        fail_proc.stderr = "Error: unknown model deprecated-model"

        ok_proc = MagicMock()
        ok_proc.returncode = 0
        ok_proc.stdout = "Humanisation réussie via repli."
        ok_proc.stderr = ""

        mock_run.side_effect = [fail_proc, ok_proc]
        success, result = call_antigravity_cli("Prompt", model="deprecated-model")
        assert success is True
        assert result == "Humanisation réussie via repli."
