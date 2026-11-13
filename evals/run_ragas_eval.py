"""CLI Runner for Golden Dataset & Ragas LLMOps Harness Evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.ai_bridge import humanize_text
from core.evaluator import (
    compute_ragas_non_llm_metrics,
    evaluate_transformation,
    load_golden_dataset,
)


def run_benchmark(
    live_llm: bool = False,
    engine: str = "agy",
    model: str = "gemini-3.8-flash-low",
    api_key: str = "",
    limit: int | None = None,
) -> dict[str, Any]:
    cases = load_golden_dataset()
    if limit is not None and limit > 0:
        cases = cases[:limit]

    case_reports: list[dict[str, Any]] = []
    passed_count = 0

    for case in cases:
        cid = case["id"]
        profile_id = case["profile_id"]
        source_text = case["source_text"]
        reference_text = case["reference_human_text"]

        if live_llm:
            ok, candidate_text = humanize_text(
                input_text=source_text,
                profile_id=profile_id,
                engine=engine,
                api_key=api_key,
                gemini_model=model,
                agy_model=model,
                source="eval",
            )
            if not ok:
                case_reports.append(
                    {
                        "id": cid,
                        "profile_id": profile_id,
                        "passed": False,
                        "error": candidate_text,
                    }
                )
                continue
        else:
            candidate_text = reference_text

        eval_res = evaluate_transformation(
            source_text=source_text,
            output_text=candidate_text,
            required_facts=case["required_facts"],
            forbidden_cliches=case["forbidden_cliches"],
        )
        eval_res.ragas_scores = compute_ragas_non_llm_metrics(
            source_text=source_text,
            output_text=candidate_text,
            reference_text=reference_text,
        )

        if eval_res.passed:
            passed_count += 1

        entry = {"id": cid, "profile_id": profile_id, **eval_res.to_dict()}
        case_reports.append(entry)

    total = len(cases)
    pass_rate = round(passed_count / total, 4) if total else 0.0
    avg_fact = (
        round(
            sum(float(c.get("factual_retention", 0.0)) for c in case_reports) / total,
            4,
        )
        if total
        else 0.0
    )
    avg_cliche = (
        round(
            sum(float(c.get("cliche_eradication", 0.0)) for c in case_reports) / total,
            4,
        )
        if total
        else 0.0
    )
    avg_drop = (
        round(
            sum(float(c.get("stylometry_drop", 0.0)) for c in case_reports) / total,
            4,
        )
        if total
        else 0.0
    )

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "live_llm" if live_llm else "golden_reference_validation",
        "engine": engine if live_llm else "reference",
        "model": model if live_llm else "reference",
        "total_cases": total,
        "passed_cases": passed_count,
        "pass_rate": pass_rate,
        "avg_factual_retention": avg_fact,
        "avg_cliche_eradication": avg_cliche,
        "avg_stylometry_drop": avg_drop,
        "cases": case_reports,
    }

    out_dir = BASE_DIR / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "eval_report.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute la suite d'evaluation Golden Dataset et Ragas LLMOps."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Appelle reellement le moteur IA (agy ou BYOK) sur le Golden Dataset.",
    )
    parser.add_argument("--engine", default="agy", choices=["agy", "BYOK"])
    parser.add_argument("--model", default="gemini-3.8-flash-low")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    report = run_benchmark(
        live_llm=args.live,
        engine=args.engine,
        model=args.model,
        api_key=args.api_key,
        limit=args.limit,
    )
    print(
        f"Evaluation terminee ({report['mode']}): "
        f"{report['passed_cases']}/{report['total_cases']} valides "
        f"(retention factuelle moy.: {report['avg_factual_retention']}, "
        f"eradication cliches moy.: {report['avg_cliche_eradication']}, "
        f"baisse stylometrique moy.: {report['avg_stylometry_drop']})"
    )
    return 0 if report["pass_rate"] >= 0.8 else 1


if __name__ == "__main__":
    raise SystemExit(main())
