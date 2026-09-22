"""Document, image, and visual report processor for multi-format humanization and PDF export."""

from __future__ import annotations

import html
import io
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import docx
except ImportError:
    docx = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import fpdf
except ImportError:
    fpdf = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

from core.score_stylometry import EditorialReport, compute_word_diff_html


def is_playwright_available() -> bool:
    """Check if playwright library is importable."""
    return sync_playwright is not None


def extract_text_from_file(uploaded_file) -> tuple[bool, str, str]:
    """Extract text from uploaded document. Returns (success, text_content, file_type)."""
    filename = uploaded_file.name
    ext = Path(filename).suffix.lower()

    if ext in [".txt", ".md"]:
        try:
            content = uploaded_file.getvalue().decode("utf-8", errors="replace")
            return True, content, ext[1:]
        except (AttributeError, UnicodeError, OSError) as e:
            return False, f"Erreur de lecture du fichier texte : {e}", ext[1:]

    elif ext == ".docx":
        if docx is None:
            return False, "La bibliothèque python-docx n'est pas installée.", "docx"
        try:
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return True, "\n\n".join(full_text), "docx"
        except Exception as e:  # noqa: BLE001 - Catch all library-specific parsing errors
            return (
                False,
                f"Erreur lors de la lecture du fichier Word (.docx) : {e}",
                "docx",
            )

    elif ext == ".pdf":
        if pypdf is None:
            return False, "La bibliothèque pypdf n'est pas installée.", "pdf"
        try:
            reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text_pages = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
            return True, "\n\n".join(text_pages), "pdf"
        except Exception as e:  # noqa: BLE001 - Catch all library-specific parsing errors
            return False, f"Erreur lors de l'extraction du PDF : {e}", "pdf"

    return False, f"Format de document non supporté ({ext}).", ext


def create_clean_docx(text: str) -> io.BytesIO:
    """Create a clean .docx file from humanized text."""
    if docx is None:
        raise RuntimeError("python-docx n'est pas installé.")
    doc = docx.Document()
    paragraphs = text.split("\n\n")
    for p in paragraphs:
        if p.strip():
            doc.add_paragraph(p.strip())
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def create_clean_pdf(text: str) -> io.BytesIO:
    """Create a clean .pdf file from humanized text with proper paragraph layout."""
    if fpdf is None:
        raise RuntimeError("fpdf2 n'est pas installé.")
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)

    for para in text.split("\n\n"):
        p = para.strip()
        if p:
            pdf.multi_cell(0, 6, p)
            pdf.ln(3)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


def strip_image_metadata(uploaded_file) -> tuple[bool, io.BytesIO, dict[str, Any]]:
    """Strip EXIF, C2PA, XMP, and software tags from an image using PIL."""
    if Image is None:
        return False, io.BytesIO(), {"error": "Pillow (PIL) n'est pas installé."}

    try:
        image = Image.open(io.BytesIO(uploaded_file.getvalue()))
        clean_img = Image.new(image.mode, image.size)
        if hasattr(image, "get_flattened_data"):
            clean_img.putdata(list(image.get_flattened_data()))
        else:
            clean_img.putdata(list(image.getdata()))

        fmt = image.format or "PNG"
        output_buffer = io.BytesIO()

        if fmt.upper() in ["JPEG", "JPG"]:
            clean_img.save(output_buffer, format="JPEG", quality=95)
        else:
            clean_img.save(output_buffer, format="PNG", optimize=True)

        output_buffer.seek(0)
        stats = {
            "original_size": len(uploaded_file.getvalue()),
            "cleaned_size": len(output_buffer.getvalue()),
            "format": fmt,
            "dimensions": f"{image.size[0]}x{image.size[1]}",
            "metadata_stripped": True,
        }
        return True, output_buffer, stats
    except Exception as e:  # noqa: BLE001 - Catch PIL processing errors
        return False, io.BytesIO(), {"error": str(e)}


def generate_diff_report_html(
    report: EditorialReport,
    input_text: str,
    output_text: str,
    profile_name: str = "Avocat",
) -> str:
    """Génère un document HTML complet et autonome optimisé pour le rendu PDF A4."""
    now_str = datetime.now().astimezone().strftime("%d/%m/%Y à %H:%M")
    rep_in = report.rep_in
    rep_out = report.rep_out
    stats = report.diff_stats

    retention_rate = stats.get("retention_rate", 100.0)
    words_before = stats.get("words_before", 0)
    words_after = stats.get("words_after", 0)
    words_deleted = stats.get("words_deleted", 0)
    words_added = stats.get("words_added", 0)
    words_preserved = stats.get("words_preserved", 0)

    raw_diff_content, _ = compute_word_diff_html(
        input_text, output_text, container=False
    )

    # Tics items HTML
    tics_html_blocks = []
    if report.tics_by_category:
        for cat, tics in report.tics_by_category.items():
            tics_items_html = "".join(
                f"<li><code>{html.escape(t['text'])}</code> : <em>{html.escape(t['label'])}</em> (poids : {t['weight']})</li>"
                for t in tics
            )
            tics_html_blocks.append(
                f"""<div class="category-block no-break">
                    <div class="category-header">{html.escape(cat)} ({len(tics)} occurrence{"s" if len(tics) > 1 else ""})</div>
                    <ul class="choice-list">{tics_items_html}</ul>
                </div>"""
            )
    else:
        tics_html_blocks.append(
            '<div class="category-block"><p style="margin:0; color:#166534; font-size:12px;">✅ Aucun tic de phrasé d\'IA détecté dans le texte source.</p></div>'
        )

    # Choices items HTML
    choices_html_blocks = []
    for choice in report.choices_made:
        items_html = "".join(
            f"<li>{html.escape(item)}</li>" for item in choice.get("items", [])
        )
        choices_html_blocks.append(
            f"""<div class="choice-card no-break">
                <div class="choice-title">{html.escape(choice.get("category", ""))}</div>
                <div class="choice-desc">{html.escape(choice.get("description", ""))}</div>
                <ul class="choice-list">{items_html}</ul>
            </div>"""
        )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tracking des modifs</title>
    <style>
        @page {{
            size: A4;
            margin: 12mm 14mm 12mm 14mm;
        }}
        @media print {{
            body {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
            .no-break {{
                page-break-inside: avoid !important;
            }}
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1E293B;
            background: #FFFFFF;
            margin: 0;
            padding: 0;
            font-size: 12px;
            line-height: 1.55;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #2563EB;
            padding-bottom: 10px;
            margin-bottom: 12px;
        }}
        .header-title {{
            font-size: 18px;
            font-weight: 800;
            color: #0F172A;
            margin: 0;
            letter-spacing: -0.3px;
        }}
        .header-sub {{
            font-size: 11px;
            color: #64748B;
            margin-top: 2px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 12px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 8px 12px;
        }}
        .meta-label {{
            color: #64748B;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
            font-weight: 600;
        }}
        .meta-value {{
            font-weight: 700;
            color: #0F172A;
            font-size: 12px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 14px;
        }}
        .kpi-card {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 8px 10px;
        }}
        .kpi-label {{
            font-size: 10.5px;
            font-weight: 600;
            color: #475569;
            margin-bottom: 2px;
        }}
        .kpi-value {{
            font-size: 16px;
            font-weight: 800;
            color: #0F172A;
        }}
        .kpi-sub {{
            font-size: 10px;
            color: #64748B;
            margin-top: 2px;
        }}
        .section-title {{
            font-size: 13px;
            font-weight: 700;
            color: #0F172A;
            margin: 14px 0 6px 0;
            padding-bottom: 3px;
            border-bottom: 1px solid #E2E8F0;
        }}
        .diff-legend {{
            display: flex;
            gap: 12px;
            align-items: center;
            font-size: 11px;
            margin-bottom: 6px;
        }}
        .legend-del {{
            background-color: #FEE2E2;
            color: #991B1B;
            text-decoration: line-through;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .legend-ins {{
            background-color: #DCFCE7;
            color: #166534;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
        }}
        .legend-keep {{
            color: #64748B;
        }}
        .diff-box {{
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 12px 14px;
            font-size: 12px;
            line-height: 1.65;
            color: #1E293B;
            margin-bottom: 12px;
            white-space: normal;
            word-break: break-word;
        }}
        .diff-del {{
            background-color: #FEE2E2 !important;
            color: #991B1B !important;
            text-decoration: line-through !important;
            padding: 1px 4px;
            border-radius: 3px;
            margin: 0 1px;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        .diff-ins {{
            background-color: #DCFCE7 !important;
            color: #166534 !important;
            font-weight: 700 !important;
            padding: 1px 4px;
            border-radius: 3px;
            margin: 0 1px;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        .category-block {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 5px;
            padding: 8px 12px;
            margin-bottom: 6px;
        }}
        .category-header {{
            font-weight: 700;
            font-size: 11.5px;
            color: #1E293B;
            margin-bottom: 4px;
        }}
        .choice-card {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-left: 3px solid #2563EB;
            border-radius: 5px;
            padding: 8px 12px;
            margin-bottom: 6px;
        }}
        .choice-title {{
            font-weight: 700;
            font-size: 11.5px;
            color: #0F172A;
            margin-bottom: 2px;
        }}
        .choice-desc {{
            font-size: 10.5px;
            color: #64748B;
            margin-bottom: 4px;
            font-style: italic;
        }}
        .choice-list {{
            margin: 0;
            padding-left: 16px;
            font-size: 11px;
            color: #334155;
        }}
        .choice-list li {{
            margin-bottom: 2px;
        }}
        .choice-list code {{
            background: #F1F5F9;
            padding: 1px 4px;
            border-radius: 3px;
            font-size: 10.5px;
            color: #0F172A;
        }}
        .footer {{
            margin-top: 16px;
            border-top: 1px solid #E2E8F0;
            padding-top: 6px;
            text-align: center;
            font-size: 9.5px;
            color: #94A3B8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="header-title">Tracking des modifs</div>
            <div class="header-sub">Bilan comparatif mot-à-mot, métriques stylométriques et traçabilité des modifications</div>
        </div>
        <div>
            <span class="badge">Validé</span>
        </div>
    </div>

    <div class="meta-grid no-break">
        <div class="meta-item">
            <div class="meta-label">Date de l'audit</div>
            <div class="meta-value">{html.escape(now_str)}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Profil stylistique appliqué</div>
            <div class="meta-value">{html.escape(profile_name)}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Conservation factuelle</div>
            <div class="meta-value" style="color: #166534;">{retention_rate} %</div>
        </div>
    </div>

    <div class="kpi-grid no-break">
        <div class="kpi-card">
            <div class="kpi-label">Indice de densité d'IA</div>
            <div class="kpi-value">{rep_out.composite_score:.2f} <span style="font-size:12px; color:#166534;">({rep_out.composite_score - rep_in.composite_score:+.2f})</span></div>
            <div class="kpi-sub">Source : {rep_in.composite_score:.2f} ({rep_in.density_tier})</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Tics d'IA neutralisés</div>
            <div class="kpi-value">{rep_out.ai_phrase_count} <span style="font-size:12px; color:#166534;">({rep_out.ai_phrase_count - rep_in.ai_phrase_count:+d})</span></div>
            <div class="kpi-sub">Source : {rep_in.ai_phrase_count} détecté(s)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Relief du rythme (Burstiness)</div>
            <div class="kpi-value">{rep_out.burstiness:.2f} <span style="font-size:12px; color:#2563EB;">({rep_out.burstiness - rep_in.burstiness:+.2f})</span></div>
            <div class="kpi-sub">Source : {rep_in.burstiness:.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Diversité lexicale (MATTR)</div>
            <div class="kpi-value">{rep_out.mattr:.2f} <span style="font-size:12px; color:#2563EB;">({rep_out.mattr - rep_in.mattr:+.2f})</span></div>
            <div class="kpi-sub">Source : {rep_in.mattr:.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Rétention des mots</div>
            <div class="kpi-value">{words_preserved} / {words_before}</div>
            <div class="kpi-sub">Taux de fidélité : {retention_rate} %</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Volume de mots</div>
            <div class="kpi-value">{words_after} mots</div>
            <div class="kpi-sub">Purgés : {words_deleted} | Insérés : {words_added}</div>
        </div>
    </div>

    <div class="section-title">1. Diff visuel mot-à-mot</div>
    <div class="diff-legend no-break">
        <span>Légende :</span>
        <span class="legend-del">Mots et tics d'IA supprimés</span>
        <span class="legend-ins">Formulations réécrites</span>
        <span class="legend-keep">(Texte non surligné : éléments conservés à l'identique)</span>
    </div>
    <div class="diff-box">
        {raw_diff_content}
    </div>

    <div class="section-title no-break">2. Traçabilité des tics et artefacts purgés</div>
    {"".join(tics_html_blocks)}

    <div class="category-block no-break" style="margin-top:6px;">
        <div class="category-header">Typographie et nettoyage déterministe (Layer A)</div>
        <ul class="choice-list">
            <li>Tirets cadratins (<code>—</code> / <code>–</code>) : <strong>{report.em_dashes_before}</strong> dans la source, <strong>{report.em_dashes_after}</strong> dans le résultat final.</li>
            <li>Caractères Unicode invisibles et espaces de traçage purgés : <strong>{report.invisible_chars_count}</strong>.</li>
        </ul>
    </div>

    <div class="section-title no-break" style="margin-top:14px;">3. Choix éditoriaux et calibration stylistique</div>
    {"".join(choices_html_blocks)}

    <div class="footer">
        Traitement sécurisé, souverain et sans traçage
    </div>
</body>
</html>"""


def generate_diff_pdf(
    report: EditorialReport,
    input_text: str,
    output_text: str,
    profile_name: str = "Avocat",
) -> tuple[bool, bytes, str]:
    """Génère un rapport PDF A4 de haute précision via Playwright (Chromium headless).

    Retourne (succès, octets_pdf, message_erreur).
    """
    if sync_playwright is None:
        return (
            False,
            b"",
            "La bibliothèque 'playwright' n'est pas installée. Installez-la avec 'pip install playwright' puis 'playwright install chromium'.",
        )

    html_content = generate_diff_report_html(
        report=report,
        input_text=input_text,
        output_text=output_text,
        profile_name=profile_name,
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content, wait_until="networkidle")
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={
                    "top": "12mm",
                    "bottom": "12mm",
                    "left": "12mm",
                    "right": "12mm",
                },
            )
            browser.close()
        return True, pdf_bytes, ""
    except Exception as e:  # noqa: BLE001 - Catch Playwright browser/render errors
        return (
            False,
            b"",
            f"Erreur lors de la conversion PDF via Playwright : {e}",
        )
