"""Core modules for AI-Remover."""

from __future__ import annotations

from core.ai_bridge import call_antigravity_cli, call_gemini_api, is_agy_available
from core.file_processor import (
    create_clean_docx,
    create_clean_pdf,
    extract_text_from_file,
    generate_diff_pdf,
    generate_diff_report_html,
    is_playwright_available,
    strip_image_metadata,
)
from core.profiles import PROFILES, build_humanize_prompt
from core.score_stylometry import (
    analyze_stylometry,
    compute_word_diff_html,
    generate_audit_log_markdown,
    generate_editorial_report,
)
from core.text_unicode import clean_unicode, inspect_unicode

__all__ = [
    "PROFILES",
    "analyze_stylometry",
    "build_humanize_prompt",
    "call_antigravity_cli",
    "call_gemini_api",
    "clean_unicode",
    "compute_word_diff_html",
    "create_clean_docx",
    "create_clean_pdf",
    "extract_text_from_file",
    "generate_audit_log_markdown",
    "generate_diff_pdf",
    "generate_diff_report_html",
    "generate_editorial_report",
    "inspect_unicode",
    "is_agy_available",
    "is_playwright_available",
    "strip_image_metadata",
]
