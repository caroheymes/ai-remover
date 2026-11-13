"""Structured JSONL Harness Telemetry and Observability for LLMOps."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_TELEMETRY_PATH = (
    Path(__file__).resolve().parent.parent / "logs" / "telemetry.jsonl"
)


def get_telemetry_log_path(override: Path | None = None) -> Path:
    if override is not None:
        return override
    env_path = os.environ.get("AI_REMOVER_TELEMETRY_FILE", "").strip()
    if env_path:
        return Path(env_path)
    return DEFAULT_TELEMETRY_PATH


@dataclass
class TelemetryEvent:
    source: str
    engine: str
    model: str
    profile_id: str
    latency_ms: float
    success: bool
    chars_in: int
    chars_out: int
    score_before: float = 0.0
    score_after: float = 0.0
    unicode_cleaned_count: int = 0
    error: str | None = None
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def log_telemetry_event(
    event: TelemetryEvent, log_path: Path | None = None
) -> Path | None:
    """Append a structured JSONL telemetry record without raising on I/O issues."""
    if os.environ.get("AI_REMOVER_DISABLE_TELEMETRY", "").strip() == "1":
        return None
    target = get_telemetry_log_path(log_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        record = asdict(event)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return target
    except OSError:
        return None


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(
        len(sorted_vals) - 1, max(0, round((pct / 100.0) * (len(sorted_vals) - 1)))
    )
    return round(sorted_vals[idx], 2)


def load_recent_telemetry_events(
    limit: int = 20, log_path: Path | None = None
) -> list[dict[str, Any]]:
    """Return the most recent telemetry records (newest first) up to limit."""
    target = get_telemetry_log_path(log_path)
    if not target.is_file() or limit <= 0:
        return []
    records: list[dict[str, Any]] = []
    try:
        for line in target.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    except OSError:
        return []
    return list(reversed(records[-limit:]))


def summarize_telemetry(log_path: Path | None = None) -> dict[str, Any]:
    """Aggregate harness operational metrics from the JSONL telemetry stream."""
    target = get_telemetry_log_path(log_path)
    if not target.is_file():
        return {
            "total_calls": 0,
            "success_count": 0,
            "failure_count": 0,
            "timeout_count": 0,
            "success_rate": 1.0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "avg_score_drop": 0.0,
            "by_model": {},
            "by_source": {},
            "model_stats": [],
        }

    records: list[dict[str, Any]] = []
    try:
        for line in target.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass

    total = len(records)
    if total == 0:
        return {
            "total_calls": 0,
            "success_count": 0,
            "failure_count": 0,
            "timeout_count": 0,
            "success_rate": 1.0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "avg_score_drop": 0.0,
            "by_model": {},
            "by_source": {},
            "model_stats": [],
        }

    success_records = [r for r in records if r.get("success") is True]
    success_count = len(success_records)
    failure_count = total - success_count
    timeout_count = sum(
        1
        for r in records
        if not r.get("success")
        and (
            "délai d'attente" in str(r.get("error") or "").lower()
            or "timeout" in str(r.get("error") or "").lower()
        )
    )

    latencies = sorted(float(r.get("latency_ms", 0.0)) for r in records)
    score_drops = [
        float(r.get("score_before", 0.0)) - float(r.get("score_after", 0.0))
        for r in success_records
    ]

    by_model: dict[str, int] = {}
    by_source: dict[str, int] = {}
    per_model_buckets: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        m = str(rec.get("model") or "unknown")
        s = str(rec.get("source") or "unknown")
        by_model[m] = by_model.get(m, 0) + 1
        by_source[s] = by_source.get(s, 0) + 1
        per_model_buckets.setdefault(m, []).append(rec)

    model_stats: list[dict[str, Any]] = []
    for m_name, m_recs in sorted(
        per_model_buckets.items(), key=lambda item: len(item[1]), reverse=True
    ):
        m_total = len(m_recs)
        m_ok = [r for r in m_recs if r.get("success") is True]
        m_lats = sorted(float(r.get("latency_ms", 0.0)) for r in m_recs)
        m_drops = [
            float(r.get("score_before", 0.0)) - float(r.get("score_after", 0.0))
            for r in m_ok
        ]
        model_stats.append(
            {
                "model": m_name,
                "calls": m_total,
                "success_rate_pct": round((len(m_ok) / m_total) * 100.0, 1),
                "p50_ms": _percentile(m_lats, 50),
                "p95_ms": _percentile(m_lats, 95),
                "avg_score_drop": round(sum(m_drops) / len(m_drops), 2)
                if m_drops
                else 0.0,
            }
        )

    return {
        "total_calls": total,
        "success_count": success_count,
        "failure_count": failure_count,
        "timeout_count": timeout_count,
        "success_rate": round(success_count / total, 4),
        "avg_latency_ms": round(sum(latencies) / total, 2),
        "p50_latency_ms": _percentile(latencies, 50),
        "p95_latency_ms": _percentile(latencies, 95),
        "avg_score_drop": round(sum(score_drops) / len(score_drops), 2)
        if score_drops
        else 0.0,
        "by_model": by_model,
        "by_source": by_source,
        "model_stats": model_stats,
    }
