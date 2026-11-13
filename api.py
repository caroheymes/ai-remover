"""Internal & Cloud Run Hybrid REST API for AI-Remover."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.ai_bridge import get_available_agy_models, humanize_text, is_agy_available
from core.evaluator import evaluate_transformation
from core.profiles import PROFILES
from core.score_stylometry import analyze_stylometry
from core.telemetry import summarize_telemetry
from core.text_unicode import clean_unicode, inspect_unicode

app = FastAPI(
    title="AI-Remover Hybrid API",
    description=(
        "API interne (Antigravity CLI local) et externe (Google Cloud Run via en-tete "
        "X-Gemini-API-Key ou variable GEMINI_API_KEY)."
    ),
    version="1.1.0",
)


class TextOnlyRequest(BaseModel):
    text: str = Field(..., min_length=1)


class HumanizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    profile_id: str = "architecte"
    engine: str = "auto"
    model: str = "gemini-3.8-flash-low"
    custom_sample: str | None = None


class EvaluateRequest(BaseModel):
    source_text: str
    output_text: str
    required_facts: list[str] = Field(default_factory=list)
    forbidden_cliches: list[str] = Field(default_factory=list)


@app.get("/health")
def health_check() -> dict[str, Any]:
    agy_ok = is_agy_available()
    has_env_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    return {
        "status": "ok",
        "version": "1.1.0",
        "agy_available": agy_ok,
        "cloud_env_key_configured": has_env_key,
        "default_engine": "agy" if agy_ok else "BYOK",
    }


@app.get("/api/v1/profiles")
def list_profiles() -> dict[str, Any]:
    return {
        "profiles": [
            {
                "id": p.id,
                "name": p.name,
                "short_desc": p.short_desc,
            }
            for p in PROFILES.values()
        ]
    }


@app.get("/api/v1/models")
def list_models() -> dict[str, Any]:
    models = get_available_agy_models()
    return {
        "models": [{"id": mid, "label": label} for mid, label in models],
        "default_model": models[0][0] if models else "gemini-3.8-flash-low",
    }


@app.post("/api/v1/clean-unicode")
def clean_unicode_endpoint(req: TextOnlyRequest) -> dict[str, Any]:
    cleaned, stats = clean_unicode(req.text, normalize_spaces=True)
    return {
        "cleaned_text": cleaned,
        "stats": stats,
    }


@app.post("/api/v1/analyze")
def analyze_endpoint(req: TextOnlyRequest) -> dict[str, Any]:
    stylo = analyze_stylometry(req.text)
    uni = inspect_unicode(req.text)
    return {
        "word_count": stylo.word_count,
        "sentence_count": stylo.sentence_count,
        "burstiness": round(stylo.burstiness, 3),
        "mattr": round(stylo.mattr, 3),
        "ai_phrase_count": stylo.ai_phrase_count,
        "composite_score": stylo.composite_score,
        "density_tier": stylo.density_tier,
        "flagged_spans": stylo.flagged_spans,
        "invisible_count": uni.invisible_count,
        "space_homoglyph_count": uni.space_homoglyph_count,
        "tag_count": uni.tag_count,
    }


@app.post("/api/v1/humanize")
def humanize_endpoint(
    req: HumanizeRequest,
    x_gemini_api_key: Annotated[str | None, Header(alias="X-Gemini-API-Key")] = None,
) -> dict[str, Any]:
    header_key = (x_gemini_api_key or "").strip()
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    effective_key = header_key or env_key

    agy_ok = is_agy_available()
    requested = req.engine.strip().lower()

    if header_key or requested in ("byok", "gemini"):
        resolved_engine = "BYOK"
    elif requested == "agy":
        if not agy_ok:
            raise HTTPException(
                status_code=503,
                detail="Antigravity CLI local indisponible sur cet hote.",
            )
        resolved_engine = "agy"
    else:
        resolved_engine = "agy" if agy_ok else "BYOK"

    if resolved_engine == "BYOK" and not effective_key:
        raise HTTPException(
            status_code=401,
            detail=(
                "Cle API Gemini absente. Transmettez l'en-tete X-Gemini-API-Key "
                "ou configurez GEMINI_API_KEY sur le serveur."
            ),
        )

    gemini_model = (
        req.model
        if resolved_engine == "BYOK"
        and not req.model.endswith(("-low", "-medium", "-high"))
        else "gemini-3-flash-preview"
    )
    agy_model = req.model if resolved_engine == "agy" else "gemini-3.8-flash-low"

    _, unicode_stats = clean_unicode(req.text, normalize_spaces=True)
    rep_before = analyze_stylometry(req.text)

    t0 = time.perf_counter()
    ok, result = humanize_text(
        input_text=req.text,
        profile_id=req.profile_id,
        custom_sample=req.custom_sample,
        engine=resolved_engine,
        api_key=effective_key,
        gemini_model=gemini_model,
        agy_model=agy_model,
        source="api",
    )
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    if not ok:
        raise HTTPException(status_code=502, detail=result)

    rep_after = analyze_stylometry(result)
    return {
        "success": True,
        "humanized_text": result,
        "engine_used": resolved_engine,
        "model_used": gemini_model if resolved_engine == "BYOK" else agy_model,
        "profile_id": req.profile_id,
        "score_before": rep_before.composite_score,
        "score_after": rep_after.composite_score,
        "density_tier_before": rep_before.density_tier,
        "density_tier_after": rep_after.density_tier,
        "unicode_stats": unicode_stats,
        "latency_ms": latency_ms,
    }


@app.post("/api/v1/evaluate")
def evaluate_endpoint(req: EvaluateRequest) -> dict[str, Any]:
    res = evaluate_transformation(
        source_text=req.source_text,
        output_text=req.output_text,
        required_facts=req.required_facts,
        forbidden_cliches=req.forbidden_cliches,
    )
    return res.to_dict()


@app.get("/api/v1/telemetry/summary")
def telemetry_summary_endpoint() -> dict[str, Any]:
    return summarize_telemetry()
