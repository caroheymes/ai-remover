from __future__ import annotations

from core.text_unicode import (
    clean_unicode,
    inspect_unicode,
)


class TestTextUnicode:
    def test_inspect_clean_text(self):
        text = "Ceci est un texte parfaitement propre sans aucun caractère spécial."
        report = inspect_unicode(text)
        assert report.total_chars == len(text)
        assert report.invisible_count == 0
        assert report.space_homoglyph_count == 0
        assert report.tag_count == 0
        assert len(report.flagged_positions) == 0
        assert len(report.found_chars) == 0

    def test_inspect_invisible_characters(self):
        # Zero-width space \u200b, soft hyphen \u00ad, BOM \ufeff
        text = "Texte\u200bavec\u00admarquage\ufeffsecret"
        report = inspect_unicode(text)
        assert report.invisible_count == 3
        assert report.space_homoglyph_count == 0
        assert report.tag_count == 0
        assert len(report.flagged_positions) == 3

    def test_inspect_space_homoglyphs(self):
        # Non-breaking space \u00a0, thin space \u2009, ideographic space \u3000
        text = "Mot1\u00a0Mot2\u2009Mot3\u3000Mot4"
        report = inspect_unicode(text)
        assert report.space_homoglyph_count == 3
        assert report.invisible_count == 0
        assert report.tag_count == 0

    def test_inspect_tag_characters(self):
        tag_char = chr(0xE0001)
        text = f"Alpha{tag_char}Beta"
        report = inspect_unicode(text)
        assert report.tag_count == 1
        assert report.invisible_count == 0

    def test_clean_unicode_stripping_and_space_normalization(self):
        text = "Introduction\u200b avec\u00a0espace\u202finsecable\ufeff et fin."
        cleaned, stats = clean_unicode(text, normalize_spaces=True, nfkc=False)
        assert "\u200b" not in cleaned
        assert "\ufeff" not in cleaned
        assert "\u00a0" not in cleaned
        assert "\u202f" not in cleaned
        assert cleaned == "Introduction avec espace insecable et fin."
        assert stats["removed_count"] == 2  # \u200b and \ufeff
        assert stats["replaced_count"] == 2  # \u00a0 and \u202f
        assert stats["input_length"] == len(text)
        assert stats["output_length"] == len(cleaned)

    def test_clean_unicode_without_space_normalization(self):
        text = "Introduction\u200b avec\u00a0espace."
        cleaned, stats = clean_unicode(text, normalize_spaces=False, nfkc=False)
        assert "\u200b" not in cleaned
        assert "\u00a0" in cleaned
        assert stats["removed_count"] == 1
        assert stats["replaced_count"] == 0

    def test_clean_unicode_nfkc(self):
        # Fullwidth Latin letter A: \uff21 -> 'A' in NFKC
        text = "\uff21\u200bBC"
        cleaned, stats = clean_unicode(text, normalize_spaces=True, nfkc=True)
        assert cleaned == "ABC"
        assert stats["removed_count"] == 1

    def test_empty_string(self):
        report = inspect_unicode("")
        assert report.total_chars == 0
        assert report.invisible_count == 0

        cleaned, stats = clean_unicode("")
        assert cleaned == ""
        assert stats["removed_count"] == 0
        assert stats["replaced_count"] == 0
