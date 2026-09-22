from __future__ import annotations

import pytest

from core.score_stylometry import (
    EditorialReport,
    analyze_stylometry,
    calculate_mattr,
    generate_editorial_report,
    split_sentences,
)


class TestScoreStylometry:
    def test_split_sentences(self):
        text = "Première phrase ici. Deuxième phrase là ! Est-ce la troisième ? Oui."
        sentences = split_sentences(text)
        assert len(sentences) == 4
        assert sentences[0] == "Première phrase ici."
        assert sentences[1] == "Deuxième phrase là !"
        assert sentences[2] == "Est-ce la troisième ?"
        assert sentences[3] == "Oui."

    def test_split_sentences_empty(self):
        assert split_sentences("") == []
        assert split_sentences("   \n\t  ") == []

    def test_calculate_mattr_small_and_large(self):
        # Empty
        assert calculate_mattr([]) == 0.0

        # Small list (< 50 words)
        words = ["le", "chat", "mange", "le", "poisson"]
        # unique: le, chat, mange, poisson (4) / 5 = 0.8
        assert calculate_mattr(words, window_size=50) == pytest.approx(0.8)

        # Longer list
        words_long = ["mot"] * 100
        assert calculate_mattr(words_long, window_size=50) == pytest.approx(1 / 50)

    def test_analyze_stylometry_insufficient_text(self):
        text = "Bonjour tout"
        report = analyze_stylometry(text)
        assert report.word_count < 5
        assert report.density_tier == "insuffisant"
        assert report.composite_score == 0.0

    def test_analyze_stylometry_human_text(self):
        text = (
            "Le tribunal a rendu son jugement hier matin. Les parties ont été notifiées par le greffe. "
            "Aucun pourvoi n'a été déposé pour le moment."
        )
        report = analyze_stylometry(text)
        assert report.word_count > 10
        assert report.sentence_count >= 3
        assert report.ai_phrase_count == 0
        assert report.density_tier == "faible"
        assert report.composite_score < 0.35

    def test_analyze_stylometry_ai_heavy_text(self):
        text = (
            "Dans un monde en constante évolution, l'intelligence artificielle joue un rôle crucial. "
            "Il est essentiel de souligner que cette riche mosaïque constitue un tournant décisif. "
            "Plongeons dans cet univers fascinant — un témoignage de l'innovation."
        )
        report = analyze_stylometry(text)
        assert report.ai_phrase_count >= 3
        assert len(report.flagged_spans) >= 3
        assert report.composite_score > 0.35

    def test_generate_editorial_report(self):
        input_text = (
            "Dans un monde en constante évolution, l'outil joue un rôle clé — une révolution sans précédent. "
            "Non seulement il optimise le flux, mais il renforce la synergie."
        )
        output_text = "Le logiciel automatise les transferts de fichiers. Il réduit le temps de traitement de 40 %."
        editorial = generate_editorial_report(
            input_text=input_text,
            output_text=output_text,
            profile_id="analyste",
            unicode_stats={"invisible_chars_removed": 2},
        )
        assert isinstance(editorial, EditorialReport)
        assert editorial.em_dashes_before >= 1
        assert editorial.em_dashes_after == 0
        assert editorial.invisible_chars_count == 2
        assert len(editorial.choices_made) >= 3
        # Check that choices contain profile specific points
        categories = [c["category"] for c in editorial.choices_made]
        assert any("Analyste" in cat for cat in categories)
        assert any("Intégrité factuelle" in cat for cat in categories)
        # Check diff and audit log integration
        assert editorial.diff_html != ""
        assert editorial.diff_stats["words_before"] > 0
        assert editorial.audit_markdown != ""
        assert "# Journal d'audit" in editorial.audit_markdown

    def test_compute_word_diff_html(self):
        from core.score_stylometry import compute_word_diff_html

        before = "Le chat noir dort."
        after = "Le chat blanc dort paisiblement."

        diff_html, stats = compute_word_diff_html(before, after)
        assert "diff-del" in diff_html or "#FEE2E2" in diff_html
        assert "diff-ins" in diff_html or "#DCFCE7" in diff_html
        assert stats["words_before"] == 4
        assert stats["words_after"] == 5
        assert stats["words_deleted"] >= 1  # "noir"
        assert stats["words_added"] >= 2  # "blanc", "paisiblement"
        assert 0.0 <= stats["retention_rate"] <= 100.0
