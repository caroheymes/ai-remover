from __future__ import annotations

import io

import pytest
from PIL import Image

from core.file_processor import (
    create_clean_docx,
    create_clean_pdf,
    extract_text_from_file,
    strip_image_metadata,
)


class DummyUploadedFile:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


class TestFileProcessor:
    def test_extract_text_txt(self):
        content = "Bonjour, ceci est un document texte simple."
        file_obj = DummyUploadedFile("test.txt", content.encode("utf-8"))
        success, text, ext = extract_text_from_file(file_obj)
        assert success is True
        assert text == content
        assert ext == "txt"

    def test_extract_text_md(self):
        content = "# Titre Markdown\n\nParagraphe de test."
        file_obj = DummyUploadedFile("document.md", content.encode("utf-8"))
        success, text, ext = extract_text_from_file(file_obj)
        assert success is True
        assert text == content
        assert ext == "md"

    def test_extract_text_unsupported(self):
        file_obj = DummyUploadedFile("archive.zip", b"fake zip content")
        success, msg, ext = extract_text_from_file(file_obj)
        assert success is False
        assert "Format de document non supporté" in msg
        assert ext == ".zip"

    def test_create_and_extract_docx(self):
        sample_text = "Premier paragraphe du contrat.\n\nDeuxième paragraphe d'analyse."
        docx_buffer = create_clean_docx(sample_text)
        assert isinstance(docx_buffer, io.BytesIO)
        assert docx_buffer.getvalue() != b""

        # Test extracting from the generated docx
        file_obj = DummyUploadedFile("document.docx", docx_buffer.getvalue())
        success, text, ext = extract_text_from_file(file_obj)
        assert success is True
        assert ext == "docx"
        assert "Premier paragraphe" in text
        assert "Deuxième paragraphe" in text

    def test_create_and_extract_pdf(self):
        sample_text = "Paragraphe juridique dans le PDF.\n\nDeuxième section formelle."
        pdf_buffer = create_clean_pdf(sample_text)
        assert isinstance(pdf_buffer, io.BytesIO)
        assert pdf_buffer.getvalue() != b""

        # Test extracting from the generated pdf
        file_obj = DummyUploadedFile("rapport.pdf", pdf_buffer.getvalue())
        success, text, ext = extract_text_from_file(file_obj)
        assert success is True
        assert ext == "pdf"
        assert "Paragraphe juridique" in text

    def test_strip_image_metadata_png(self):
        # Create a small in-memory image
        img = Image.new("RGB", (100, 100), color="blue")
        raw_buffer = io.BytesIO()
        img.save(raw_buffer, format="PNG")
        raw_buffer.seek(0)

        file_obj = DummyUploadedFile("image.png", raw_buffer.getvalue())
        success, out_buffer, stats = strip_image_metadata(file_obj)

        assert success is True
        assert isinstance(out_buffer, io.BytesIO)
        assert stats["format"] == "PNG"
        assert stats["dimensions"] == "100x100"
        assert stats["metadata_stripped"] is True

    def test_strip_image_metadata_jpeg(self):
        img = Image.new("RGB", (50, 50), color="red")
        raw_buffer = io.BytesIO()
        img.save(raw_buffer, format="JPEG")
        raw_buffer.seek(0)

        file_obj = DummyUploadedFile("photo.jpg", raw_buffer.getvalue())
        success, out_buffer, stats = strip_image_metadata(file_obj)

        assert success is True
        assert isinstance(out_buffer, io.BytesIO)
        assert stats["format"] in ["JPEG", "JPG"]
        assert stats["dimensions"] == "50x50"

    def test_is_playwright_available(self):
        from core.file_processor import is_playwright_available

        assert isinstance(is_playwright_available(), bool)

    def test_generate_diff_report_html(self):
        from core.file_processor import generate_diff_report_html
        from core.score_stylometry import generate_editorial_report

        before = "Dans un monde en constante évolution, l'outil joue un rôle clé — une révolution sans précédent."
        after = "Le logiciel automatise les flux de travail de manière fiable."

        editorial = generate_editorial_report(
            input_text=before,
            output_text=after,
            profile_id="avocat",
            unicode_stats={"invisible_chars_removed": 1},
        )

        html_out = generate_diff_report_html(
            report=editorial,
            input_text=before,
            output_text=after,
            profile_name="Avocat d'affaires",
        )

        assert "<!DOCTYPE html>" in html_out
        assert "Tracking des modifs" in html_out
        assert "Validé" in html_out
        assert "Traitement sécurisé, souverain et sans traçage" in html_out
        assert "Studio d'Humanisation" not in html_out
        assert "Avocat d&#x27;affaires" in html_out or "Avocat d'affaires" in html_out
        assert "diff-del" in html_out
        assert "diff-ins" in html_out
        assert "Typographie et nettoyage déterministe" in html_out
        assert f"{editorial.diff_stats['retention_rate']} %" in html_out

    def test_generate_diff_pdf_success(self):
        from core.file_processor import generate_diff_pdf, is_playwright_available
        from core.score_stylometry import generate_editorial_report

        if not is_playwright_available():
            pytest.skip("Playwright n'est pas installé dans cet environnement.")

        before = "Il est crucial de noter que ce contrat joue un rôle charnière — une étape clé."
        after = "Le contrat formalise les obligations respectives des signataires."

        editorial = generate_editorial_report(
            input_text=before, output_text=after, profile_id="avocat"
        )

        ok, pdf_bytes, err = generate_diff_pdf(
            report=editorial,
            input_text=before,
            output_text=after,
            profile_name="Avocat",
        )

        assert ok is True
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF-")
        assert err == ""

    def test_generate_diff_pdf_missing_playwright(self, monkeypatch):
        import core.file_processor as fp
        from core.score_stylometry import generate_editorial_report

        monkeypatch.setattr(fp, "sync_playwright", None)

        editorial = generate_editorial_report(
            input_text="Texte", output_text="Texte", profile_id="avocat"
        )

        ok, pdf_bytes, err = fp.generate_diff_pdf(
            report=editorial, input_text="Texte", output_text="Texte"
        )

        assert ok is False
        assert pdf_bytes == b""
        assert "playwright" in err.lower()

    def test_generate_diff_pdf_runtime_error(self, monkeypatch):
        import core.file_processor as fp
        from core.score_stylometry import generate_editorial_report

        class MockPlaywrightContext:
            def __enter__(self):
                raise RuntimeError("Chromium launch crash simulation")

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

        monkeypatch.setattr(fp, "sync_playwright", lambda: MockPlaywrightContext())

        editorial = generate_editorial_report(
            input_text="Texte", output_text="Texte", profile_id="avocat"
        )

        ok, pdf_bytes, err = fp.generate_diff_pdf(
            report=editorial, input_text="Texte", output_text="Texte"
        )

        assert ok is False
        assert pdf_bytes == b""
        assert "Chromium launch crash simulation" in err
