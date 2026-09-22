"""Dual AI Provider Bridge: Local Antigravity CLI and Google Gemini Direct API."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import requests

# Windows CreateProcessW has a hard 32767-character command line limit.
# We limit individual CLI sub-prompts to 7000 characters to ensure safe execution.
MAX_SAFE_CLI_PROMPT_LEN = 7000


def get_agy_path() -> str:
    """Find the path to the agy executable."""
    found = shutil.which("agy")
    if found:
        return found

    # Common default paths on Windows
    candidate = Path(os.environ.get("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe"
    if candidate.is_file():
        return str(candidate)

    return "agy"


def is_agy_available() -> bool:
    """Check if Antigravity CLI binary exists and is accessible on the system."""
    path = get_agy_path()
    if path != "agy":
        return Path(path).is_file()
    return shutil.which("agy") is not None


def split_text_into_chunks(text: str, max_chunk_size: int = 2500) -> list[str]:
    """Découpe un texte long en blocs cohérents respectant strictement les paragraphes."""
    if len(text) <= max_chunk_size:
        return [text]

    # 1. Découpage par paragraphes (\n\n)
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return [text]

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0

    for p in paragraphs:
        p_len = len(p) + 2
        if current_len + p_len > max_chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_len = len(p)
        else:
            current_chunk.append(p)
            current_len += p_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    # 2. Découpage secondaire si un paragraphe unique dépasse max_chunk_size
    final_chunks: list[str] = []
    for c in chunks:
        if len(c) <= max_chunk_size:
            final_chunks.append(c)
        else:
            lines = [l for l in c.split("\n") if l.strip()]
            if len(lines) > 1:
                sub_c: list[str] = []
                sub_len = 0
                for line in lines:
                    if sub_len + len(line) + 1 > max_chunk_size and sub_c:
                        final_chunks.append("\n".join(sub_c))
                        sub_c = [line]
                        sub_len = len(line)
                    else:
                        sub_c.append(line)
                        sub_len += len(line) + 1
                if sub_c:
                    final_chunks.append("\n".join(sub_c))
            else:
                sentences = [s.strip() for s in c.split(". ") if s.strip()]
                sub_c = []
                sub_len = 0
                for s in sentences:
                    s_text = s if s.endswith(".") else s + "."
                    if sub_len + len(s_text) + 1 > max_chunk_size and sub_c:
                        final_chunks.append(" ".join(sub_c))
                        sub_c = [s_text]
                        sub_len = len(s_text)
                    else:
                        sub_c.append(s_text)
                        sub_len += len(s_text) + 1
                if sub_c:
                    final_chunks.append(" ".join(sub_c))

    return final_chunks if final_chunks else [text]


def _call_single_agy_turn(
    prompt: str, model: str | None = None, timeout_seconds: int = 120
) -> tuple[bool, str]:
    """Execute a single call to agy.exe with shell=False and UTF-8 encoding to avoid Windows buffer limits."""
    agy_bin = get_agy_path()
    cmd = [
        agy_bin,
        "-p",
        prompt,
        "--dangerously-skip-permissions",
        "--disable-slash-commands",
    ]
    if model:
        cmd.extend(["--model", model])

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    try:
        # shell=False avoids cmd.exe 8192-character buffer overflow
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            shell=False,
            env=env,
            check=False,
        )

        if result.returncode == 0 and result.stdout.strip():
            return True, result.stdout.strip()
        else:
            err = result.stderr.strip() or "La commande agy a retourné une sortie vide."
            return False, f"Erreur Antigravity CLI (code {result.returncode}): {err}"
    except subprocess.TimeoutExpired:
        return (
            False,
            f"Délai d'attente dépassé ({timeout_seconds}s) lors de l'appel à Antigravity CLI.",
        )
    except OSError as e:
        if getattr(e, "winerror", None) == 206 or "206" in str(e):
            return (
                False,
                "Erreur de longueur Windows (WinError 206) : le texte dépasse la capacité maximale de la ligne de commande système.",
            )
        return False, f"Exception lors de l'exécution d'Antigravity CLI : {e!s}"
    except (subprocess.SubprocessError, ValueError) as e:
        return False, f"Exception lors de l'exécution d'Antigravity CLI : {e!s}"


def call_antigravity_cli(
    prompt: str, model: str | None = None, timeout_seconds: int = 180
) -> tuple[bool, str]:
    """Call local Antigravity CLI (agy -p) safely handling long prompts without WinError 206."""
    if len(prompt) <= MAX_SAFE_CLI_PROMPT_LEN:
        return _call_single_agy_turn(
            prompt, model=model, timeout_seconds=timeout_seconds
        )

    # Long prompt handling: detect structured template sections and chunk the input body
    source_marker = "--- TEXTE SOURCE À HUMANISER"
    final_marker = "--- TEXTE FINAL HUMANISÉ"

    if source_marker in prompt and final_marker in prompt:
        prefix, rest = prompt.split(source_marker, 1)
        source_header_end = rest.find("\n")
        if source_header_end != -1:
            actual_source_header = source_marker + rest[:source_header_end]
            body_and_final = rest[source_header_end + 1 :]
            body, suffix_header = body_and_final.split(final_marker, 1)
            suffix = final_marker + suffix_header

            text_chunks = split_text_into_chunks(body.strip(), max_chunk_size=3000)
            results: list[str] = []

            for chunk in text_chunks:
                sub_prompt = f"{prefix}{actual_source_header}\n{chunk}\n\n{suffix}"
                ok, res = _call_single_agy_turn(
                    sub_prompt, model=model, timeout_seconds=timeout_seconds
                )
                if not ok:
                    return False, res
                results.append(res)

            return True, "\n\n".join(results)

    # Generic long prompt fallback
    chunks = split_text_into_chunks(prompt, max_chunk_size=MAX_SAFE_CLI_PROMPT_LEN)
    results: list[str] = []
    for chunk in chunks:
        ok, res = _call_single_agy_turn(
            chunk, model=model, timeout_seconds=timeout_seconds
        )
        if not ok:
            return False, res
        results.append(res)

    return True, "\n\n".join(results)


def call_gemini_api(
    prompt: str,
    api_key: str,
    model: str = "gemini-3-flash-preview",
    temperature: float = 0.4,
    timeout_seconds: int = 90,
) -> tuple[bool, str]:
    """Call Google Gemini API directly via HTTP REST without external SDK dependencies."""
    if not api_key or not api_key.strip():
        return (
            False,
            "Clé d'API Google AI Studio manquante. Veuillez saisir votre clé dans la barre latérale ou choisir le moteur Antigravity CLI.",
        )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 8192,
        },
    }

    try:
        resp = requests.post(
            url, headers=headers, json=payload, timeout=timeout_seconds
        )
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if (
                candidates
                and "content" in candidates[0]
                and "parts" in candidates[0]["content"]
            ):
                text_parts = [
                    p.get("text", "") for p in candidates[0]["content"]["parts"]
                ]
                return True, "".join(text_parts).strip()
            return False, "Réponse API vide ou bloquée par les filtres de sécurité."
        else:
            return (
                False,
                f"Erreur API Google Gemini (HTTP {resp.status_code}) : {resp.text}",
            )
    except (requests.RequestException, ValueError, KeyError) as e:
        return False, f"Exception lors de l'appel à l'API Gemini : {e!s}"


def humanize_text(
    input_text: str,
    profile_id: str = "avocat",
    custom_sample: str | None = None,
    engine: str = "agy",
    api_key: str = "",
    gemini_model: str = "gemini-3-flash-preview",
    max_chunk_size: int = 2500,
) -> tuple[bool, str]:
    """Orchestre l'humanisation complète d'un texte ou document avec découpage par blocs pour garantir 100 % d'exhaustivité et zéro omission."""
    from core.profiles import build_humanize_prompt
    from core.text_unicode import clean_unicode

    clean_in, _ = clean_unicode(input_text, normalize_spaces=True)
    if not clean_in.strip():
        return True, ""

    chunks = split_text_into_chunks(clean_in, max_chunk_size=max_chunk_size)
    results: list[str] = []

    for chunk in chunks:
        prompt = build_humanize_prompt(
            input_text=chunk,
            profile_id=profile_id,
            custom_sample=custom_sample,
        )

        if "BYOK" in engine or "gemini" in engine.lower():
            ok, out = call_gemini_api(
                prompt=prompt, api_key=api_key, model=gemini_model
            )
        else:
            ok, out = call_antigravity_cli(prompt=prompt)

        if not ok:
            return False, out

        clean_out, _ = clean_unicode(out, normalize_spaces=True)
        clean_out = clean_out.replace("—", ",").replace("–", "-")
        results.append(clean_out.strip())

    return True, "\n\n".join(results)
