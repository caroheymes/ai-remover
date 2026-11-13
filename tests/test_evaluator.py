from __future__ import annotations

from pathlib import Path

from core.evaluator import (
    compute_cliche_eradication,
    compute_factual_retention,
    evaluate_transformation,
    load_golden_dataset,
)


class TestEvaluatorAndGoldenDataset:
    def test_golden_dataset_structure_and_size(self):
        dataset_path = (
            Path(__file__).resolve().parent.parent / "evals" / "golden_dataset.json"
        )
        cases = load_golden_dataset(dataset_path)
        assert len(cases) >= 8
        for case in cases:
            assert "id" in case
            assert "profile_id" in case
            assert "source_text" in case
            assert "reference_human_text" in case
            assert len(case["required_facts"]) >= 2
            assert len(case["forbidden_cliches"]) >= 1
            # La reference humaine doit deja respecter 100 % des faits requis et 0 cliche interdit
            fact_score, missing = compute_factual_retention(
                case["reference_human_text"], case["required_facts"]
            )
            assert fact_score == 1.0, f"Faits manquants dans {case['id']}: {missing}"
            cliche_score, found = compute_cliche_eradication(
                case["reference_human_text"], case["forbidden_cliches"]
            )
            assert cliche_score == 1.0, f"Cliches trouves dans {case['id']}: {found}"

    def test_evaluate_transformation_detects_fact_loss_and_cliches(self):
        source = (
            "Fort de mon expérience à la croisée de la data et du MLOps, "
            "j'ai déployé chez Interflora un modèle Prophet avec un MAPE de 15 % "
            "et économisé 500 kEUR sur BigQuery."
        )
        good_out = (
            "Chez Interflora, j'ai mis en production un modèle Prophet (MAPE de 15 %) "
            "et généré 500 kEUR d'économies mesurées sous BigQuery."
        )
        bad_out = (
            "Fort de mon expérience, j'ai conçu des solutions innovantes chez Interflora "
            "sur le cloud."
        )

        req_facts = ["Interflora", "Prophet", "15 %", "500 kEUR", "BigQuery"]
        forb = ["fort de mon expérience", "à la croisée de", "solutions innovantes"]

        good_eval = evaluate_transformation(
            source_text=source,
            output_text=good_out,
            required_facts=req_facts,
            forbidden_cliches=forb,
        )
        assert good_eval.factual_retention == 1.0
        assert good_eval.cliche_eradication == 1.0
        assert good_eval.unicode_hygiene == 1.0
        assert good_eval.passed is True

        bad_eval = evaluate_transformation(
            source_text=source,
            output_text=bad_out,
            required_facts=req_facts,
            forbidden_cliches=forb,
        )
        assert bad_eval.factual_retention < 0.5
        assert bad_eval.cliche_eradication < 1.0
        assert bad_eval.passed is False
