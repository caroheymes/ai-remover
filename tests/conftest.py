from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_telemetry_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "AI_REMOVER_TELEMETRY_FILE", str(tmp_path / "test_telemetry.jsonl")
    )
