"""LLMOps Harness Evaluator and Ragas-compatible Factual & Stylometric Gates."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.score_stylometry import analyze_stylometry
from core.text_unicode import inspect_unicode

DEFAULT_GOLDEN_DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "evals" / "golden_dataset.json"
)


@dataclass
class TransformationEvalResult:
    factual_retention: float
    cliche_eradication: float
    unicode_hygiene: float
    score_before: float
    score_after: float
    stylometry_drop: float
    missing_facts: list[str] = field(default_factory=list)
    detected_cliches: list[str] = field(default_factory=list)
    ragas_scores: dict[str, float] = field(default_factory=dict)
    passed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_for_match(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip().lower()
    return collapsed.replace("\u00a0", " ").replace("\u202f", " ").replace("’", "'")


def compute_factual_retention(
    output_text: str, required_facts: list[str]
) -> tuple[float, list[str]]:
    """Measure exact/normalized preservation of substantive entities, metrics, and dates."""
    if not required_facts:
        return 1.0, []
    norm_out = _normalize_for_match(output_text)
    norm_out_compact = norm_out.replace(" %", "%")

    missing: list[str] = []
    for fact in required_facts:
        norm_fact = _normalize_for_match(fact)
        norm_fact_compact = norm_fact.replace(" %", "%")
        if norm_fact not in norm_out and norm_fact_compact not in norm_out_compact:
            missing.append(fact)

    retained = len(required_facts) - len(missing)
    return round(retained / len(required_facts), 4), missing


def compute_cliche_eradication(
    output_text: str, forbidden_cliches: list[str]
) -> tuple[float, list[str]]:
    """Verify eradication of explicit forbidden clichés in the rewritten output."""
    if not forbidden_cliches:
        return 1.0, []
    norm_out = _normalize_for_match(output_text)
    found: list[str] = []
    for cliche in forbidden_cliches:
        norm_c = _normalize_for_match(cliche)
        if norm_c and norm_c in norm_out:
            found.append(cliche)

    clean_count = len(forbidden_cliches) - len(found)
    return round(clean_count / len(forbidden_cliches), 4), found


def compute_unicode_hygiene(output_text: str) -> float:
    """Return 1.0 when zero invisible, tag, or space-homoglyph characters remain, and zero em/en dashes."""
    rep = inspect_unicode(output_text)
    anomalies = (
        rep.invisible_count
        + rep.space_homoglyph_count
        + rep.tag_count
        + output_text.count("—")
        + output_text.count("–")
    )
    if anomalies == 0:
        return 1.0
    return round(max(0.0, 1.0 - (anomalies * 0.1)), 4)


def evaluate_transformation(
    source_text: str,
    output_text: str,
    required_facts: list[str] | None = None,
    forbidden_cliches: list[str] | None = None,
    min_factual_retention: float = 1.0,
    min_cliche_eradication: float = 1.0,
    max_score_after: float = 0.45,
) -> TransformationEvalResult:
    """Evaluate a text-to-text humanization pass against factual, stylometric, and Unicode gates."""
    req = required_facts or []
    forb = forbidden_cliches or []

    factual_score, missing_facts = compute_factual_retention(output_text, req)
    cliche_score, detected_cliches = compute_cliche_eradication(output_text, forb)
    unicode_score = compute_unicode_hygiene(output_text)

    rep_in = analyze_stylometry(source_text)
    rep_out = analyze_stylometry(output_text)
    drop = round(rep_in.composite_score - rep_out.composite_score, 4)

    passed = (
        bool(output_text.strip())
        and factual_score >= min_factual_retention
        and cliche_score >= min_cliche_eradication
        and unicode_score == 1.0
        and rep_out.composite_score <= max_score_after
    )

    return TransformationEvalResult(
        factual_retention=factual_score,
        cliche_eradication=cliche_score,
        unicode_hygiene=unicode_score,
        score_before=rep_in.composite_score,
        score_after=rep_out.composite_score,
        stylometry_drop=drop,
        missing_facts=missing_facts,
        detected_cliches=detected_cliches,
        passed=passed,
    )


def load_golden_dataset(path: Path | None = None) -> list[dict[str, Any]]:
    target = path or DEFAULT_GOLDEN_DATASET_PATH
    data = json.loads(target.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "cases" in data:
        return list(data["cases"])
    if isinstance(data, list):
        return data
    raise ValueError("Format invalide pour golden_dataset.json")


def compute_ragas_non_llm_metrics(
    source_text: str, output_text: str, reference_text: str
) -> dict[str, float]:
    """Compute Ragas non-LLM reference similarity metrics when ragas is installed, or token F1 fallback."""
    try:
        import asyncio

        from ragas.dataset_schema import SingleTurnSample
        from ragas.metrics import NonLLMStringSimilarity, RougeScore

        sample = SingleTurnSample(
            user_input=source_text,
            response=output_text,
            reference=reference_text,
        )

        async def _score() -> dict[str, float]:
            sim_metric = NonLLMStringSimilarity()
            rouge_metric = RougeScore()
            sim_val = await sim_metric.single_turn_ascore(sample)
            rouge_val = await rouge_metric.single_turn_ascore(sample)
            return {
                "ragas_string_similarity": round(float(sim_val), 4),
                "ragas_rouge_l": round(float(rouge_val), 4),
            }

        return asyncio.run(_score())
    except (ImportError, RuntimeError, ValueError, TypeError):
        # Repli deterministe par recouvrement lexical normalise (F1 de jetons)
        out_tokens = set(re.findall(r"\w+", _normalize_for_match(output_text)))
        ref_tokens = set(re.findall(r"\w+", _normalize_for_match(reference_text)))
        if not out_tokens or not ref_tokens:
            return {"lexical_reference_f1": 0.0}
        inter = len(out_tokens & ref_tokens)
        prec = inter / len(out_tokens)
        rec = inter / len(ref_tokens)
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        return {"lexical_reference_f1": round(f1, 4)}
