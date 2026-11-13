from __future__ import annotations

import json
from pathlib import Path

from core.telemetry import TelemetryEvent, log_telemetry_event, summarize_telemetry


class TestTelemetry:
    def test_log_and_summarize_telemetry(self, tmp_path: Path):
        log_file = tmp_path / "telemetry.jsonl"

        ev1 = TelemetryEvent(
            source="api",
            engine="agy",
            model="gemini-3.8-flash-low",
            profile_id="architecte",
            latency_ms=1120.5,
            success=True,
            chars_in=450,
            chars_out=320,
            score_before=0.72,
            score_after=0.12,
            unicode_cleaned_count=3,
        )
        ev2 = TelemetryEvent(
            source="mcp",
            engine="agy",
            model="gemini-3.8-flash-low",
            profile_id="avocat",
            latency_ms=180050.0,
            success=False,
            chars_in=800,
            chars_out=0,
            score_before=0.68,
            score_after=0.68,
            unicode_cleaned_count=0,
            error="Délai d'attente dépassé (180s) lors de l'appel à Antigravity CLI.",
        )

        log_telemetry_event(ev1, log_path=log_file)
        log_telemetry_event(ev2, log_path=log_file)

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        parsed = json.loads(lines[0])
        assert parsed["source"] == "api"
        assert parsed["model"] == "gemini-3.8-flash-low"
        assert "trace_id" in parsed
        assert "timestamp" in parsed

        summary = summarize_telemetry(log_path=log_file)
        assert summary["total_calls"] == 2
        assert summary["success_count"] == 1
        assert summary["failure_count"] == 1
        assert summary["timeout_count"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["avg_score_drop"] == 0.60

    def test_summarize_empty_or_missing_file(self, tmp_path: Path):
        missing = tmp_path / "absent.jsonl"
        summary = summarize_telemetry(log_path=missing)
        assert summary["total_calls"] == 0
        assert summary["success_rate"] == 1.0
        assert summary["timeout_count"] == 0
