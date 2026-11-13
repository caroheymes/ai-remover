#!/usr/bin/env python3
"""MCP Server exposing humanize_text for Antigravity CLI and Claude Code."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import requests
from fastmcp import FastMCP

if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("ai_remover_mcp")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.ai_bridge import humanize_text, is_agy_available  # noqa: E402
from core.score_stylometry import analyze_stylometry  # noqa: E402
from core.text_unicode import clean_unicode, inspect_unicode  # noqa: E402

mcp = FastMCP("ai-remover")


def humanize_text_tool(
    text: str,
    profile_id: str = "architecte",
    model: str = "gemini-3.8-flash-low",
    custom_sample: str | None = None,
) -> dict[str, Any]:
    """Execute l'humanisation via l'API interne/Cloud Run si configuree, sinon via le pont local direct."""
    if not text or not text.strip():
        return {"success": True, "humanized_text": "", "transport": "noop"}

    api_url = os.environ.get("AI_REMOVER_API_URL", "").strip().rstrip("/")
    api_token = os.environ.get("AI_REMOVER_API_TOKEN", "").strip()
    api_key = (
        os.environ.get("AI_REMOVER_API_KEY", "").strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
    )

    if api_url:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"
        if api_key:
            headers["X-Gemini-API-Key"] = api_key
        try:
            resp = requests.post(
                f"{api_url}/api/v1/humanize",
                headers=headers,
                json={
                    "text": text,
                    "profile_id": profile_id,
                    "engine": "auto",
                    "model": model,
                    "custom_sample": custom_sample,
                },
                timeout=185,
            )
            if resp.status_code == 200:
                payload = resp.json()
                payload["transport"] = "http_api"
                return payload
            logger.warning(
                "Echec appel HTTP %s (code %s), bascule sur le pont local.",
                api_url,
                resp.status_code,
            )
        except requests.RequestException as exc:
            logger.warning(
                "API HTTP %s injoignable (%s), bascule directe sur core.ai_bridge.",
                api_url,
                exc,
            )

    rep_before = analyze_stylometry(text)
    engine = "agy" if is_agy_available() else "BYOK"
    ok, result = humanize_text(
        input_text=text,
        profile_id=profile_id,
        custom_sample=custom_sample,
        engine=engine,
        api_key=api_key,
        gemini_model=model if engine == "BYOK" else "gemini-3-flash-preview",
        agy_model=model,
        source="mcp",
    )
    if not ok:
        return {
            "success": False,
            "error": result,
            "transport": "direct_core",
        }

    rep_after = analyze_stylometry(result)
    return {
        "success": True,
        "humanized_text": result,
        "profile_id": profile_id,
        "engine_used": engine,
        "model_used": model,
        "score_before": rep_before.composite_score,
        "score_after": rep_after.composite_score,
        "transport": "direct_core",
    }


@mcp.tool(name="humanize_text")
def mcp_humanize_text(
    text: str,
    profile_id: str = "architecte",
    model: str = "gemini-3.8-flash-low",
    custom_sample: str | None = None,
) -> dict[str, Any]:
    """Reecrit et humanise un texte en supprimant les cliches d'IA, les tirets cadratins et les caracteres invisibles tout en preservant 100 % des faits techniques et chiffres. Profils : architecte, avocat, analyste, journaliste, academique, custom."""
    return humanize_text_tool(
        text=text,
        profile_id=profile_id,
        model=model,
        custom_sample=custom_sample,
    )


@mcp.tool(name="analyze_ai_density")
def analyze_ai_density(text: str) -> dict[str, Any]:
    """Mesure sans appel LLM la densite de marqueurs d'IA (score composite 0.0 a 1.0, cliches detectes, burstiness) et le nombre de caracteres Unicode invisibles."""
    stylo = analyze_stylometry(text)
    uni = inspect_unicode(text)
    return {
        "composite_score": stylo.composite_score,
        "density_tier": stylo.density_tier,
        "ai_phrase_count": stylo.ai_phrase_count,
        "burstiness": round(stylo.burstiness, 3),
        "flagged_spans": stylo.flagged_spans,
        "invisible_unicode_count": uni.invisible_count,
        "space_homoglyph_count": uni.space_homoglyph_count,
    }


@mcp.tool(name="clean_invisible_unicode")
def clean_invisible_unicode(text: str) -> dict[str, Any]:
    """Purge de maniere deterministe les caracteres Unicode invisibles, zero-width spaces et espaces insecables."""
    cleaned, stats = clean_unicode(text, normalize_spaces=True)
    return {
        "cleaned_text": cleaned,
        "removed_count": stats["removed_count"],
        "replaced_count": stats["replaced_count"],
    }


if __name__ == "__main__":
    mcp.run()
