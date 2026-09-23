"""Layer A: invisible Unicode / homoglyph space detection and cleaning.
Vendored from watermarks-remover / clean-user-facing-text.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

# Format / invisible controls commonly used for steganography or broken pastes.
STRIP_CODEPOINTS: frozenset[int] = frozenset(
    {
        0x00AD,  # soft hyphen
        0x034F,  # combining grapheme joiner
        0x061C,  # Arabic letter mark
        0x115F,  # Hangul choseong filler
        0x1160,  # Hangul jungseong filler
        0x17B4,  # Khmer vowel inherent AQ
        0x17B5,  # Khmer vowel inherent AA
        0x180B,  # Mongolian free variation selector-1
        0x180C,
        0x180D,
        0x180E,  # Mongolian vowel separator
        0x180F,  # Mongolian free variation selector-4
        0x200B,  # zero width space
        0x200C,  # zero width non-joiner
        0x200D,  # zero width joiner
        0x200E,  # LRM
        0x200F,  # RLM
        0x202A,  # LRE
        0x202B,  # RLE
        0x202C,  # PDF
        0x202D,  # LRO
        0x202E,  # RLO
        0x2060,  # word joiner
        0x2061,  # function application
        0x2062,  # invisible times
        0x2063,  # invisible separator
        0x2064,  # invisible plus
        0x2066,  # LRI
        0x2067,  # RLI
        0x2068,  # FSI
        0x2069,  # PDI
        0x206A,  # inhibit symmetric swapping
        0x206B,
        0x206C,
        0x206D,
        0x206E,
        0x206F,
        0xFEFF,  # BOM / ZWNBSP
        0xFE00,  # variation selectors
        0xFE01,
        0xFE02,
        0xFE03,
        0xFE04,
        0xFE05,
        0xFE06,
        0xFE07,
        0xFE08,
        0xFE09,
        0xFE0A,
        0xFE0B,
        0xFE0C,
        0xFE0D,
        0xFE0E,
        0xFE0F,
        0x3164,  # Hangul filler
        0xFFA0,  # halfwidth Hangul filler
        0xFFF9,  # interlinear annotation
        0xFFFA,
        0xFFFB,
    }
)

# Spaces that look like (or substitute for) U+0020.
SPACE_HOMOGLYPHS: dict[int, str] = {
    0x00A0: " ",  # no-break space
    0x1680: " ",  # Ogham space mark
    0x2000: " ",  # en quad
    0x2001: " ",  # em quad
    0x2002: " ",  # en space
    0x2003: " ",  # em space
    0x2004: " ",  # three-per-em space
    0x2005: " ",  # four-per-em space
    0x2006: " ",  # six-per-em space
    0x2007: " ",  # figure space
    0x2008: " ",  # punctuation space
    0x2009: " ",  # thin space
    0x200A: " ",  # hair space
    0x202F: " ",  # narrow no-break space
    0x205F: " ",  # medium mathematical space
    0x3000: " ",  # ideographic space
}

TAG_CODEPOINTS: frozenset[int] = frozenset(range(0xE0000, 0xE0080))


@dataclass
class InspectionReport:
    total_chars: int = 0
    invisible_count: int = 0
    space_homoglyph_count: int = 0
    tag_count: int = 0
    found_chars: dict[str, int] = field(default_factory=dict)
    flagged_positions: list[dict[str, any]] = field(default_factory=list)


def inspect_unicode(text: str) -> InspectionReport:
    """Detect invisible characters, exotic spaces, and tag characters."""
    report = InspectionReport(total_chars=len(text))
    counter = Counter()

    for idx, ch in enumerate(text):
        cp = ord(ch)
        char_name = unicodedata.name(ch, f"U+{cp:04X}")
        hex_code = f"U+{cp:04X}"

        if cp in STRIP_CODEPOINTS:
            report.invisible_count += 1
            counter[f"{hex_code} ({char_name})"] += 1
            report.flagged_positions.append(
                {
                    "index": idx,
                    "type": "invisible",
                    "char": ch,
                    "hex": hex_code,
                    "name": char_name,
                }
            )
        elif cp in SPACE_HOMOGLYPHS:
            report.space_homoglyph_count += 1
            counter[f"{hex_code} ({char_name})"] += 1
            report.flagged_positions.append(
                {
                    "index": idx,
                    "type": "space_homoglyph",
                    "char": ch,
                    "hex": hex_code,
                    "name": char_name,
                }
            )
        elif cp in TAG_CODEPOINTS:
            report.tag_count += 1
            counter[f"{hex_code} (TAG CHARACTER)"] += 1
            report.flagged_positions.append(
                {
                    "index": idx,
                    "type": "tag",
                    "char": ch,
                    "hex": hex_code,
                    "name": char_name,
                }
            )

    report.found_chars = dict(counter)
    return report


def clean_unicode(
    text: str,
    normalize_spaces: bool = True,
    nfkc: bool = False,
) -> tuple[str, dict[str, any]]:
    """Clean invisible characters and normalize space homoglyphs."""
    out = []
    removed_count = 0
    replaced_count = 0

    for ch in text:
        cp = ord(ch)
        if cp in STRIP_CODEPOINTS or cp in TAG_CODEPOINTS:
            removed_count += 1
            continue
        if normalize_spaces and cp in SPACE_HOMOGLYPHS:
            out.append(SPACE_HOMOGLYPHS[cp])
            replaced_count += 1
            continue
        out.append(ch)

    cleaned = "".join(out)
    if nfkc:
        cleaned = unicodedata.normalize("NFKC", cleaned)

    stats = {
        "input_length": len(text),
        "output_length": len(cleaned),
        "removed_count": removed_count,
        "replaced_count": replaced_count,
    }
    return cleaned, stats


def normalize_human_punctuation(text: str) -> str:
    """Normalise la ponctuation selon la frappe humaine au clavier standard :
    - Zéro espace avant les ponctuations (?, !, ;, :, ,, ., ))
    - Un seul espace standard après les ponctuations (?, !, ;, :, ,, .) si suivies de texte
    - Guillemets droits doubles \" (U+0022) exclusivement (purge de «, », “, ”)
    - Apostrophes droites ' (U+0027) exclusivement (purge de ’, ‘, `, ´)
    - Zéro espace insécable ou demi-espace (conversion en espace standard U+0020)
    - Zéro tiret cadratin ou demi-cadratin (conversion en tiret court standard -)
    """
    if not text:
        return text

    # 1. Conversion de tous les espaces homoglyphes / insécables en espace standard
    for cp in SPACE_HOMOGLYPHS:
        text = text.replace(chr(cp), " ")

    # 2. Remplacement des apostrophes courbes/typographiques par l'apostrophe droite standard '
    text = re.sub(r"[’‘ʼ`´]", "'", text)

    # 3. Remplacement des guillemets français et courbes (avec absorption des espaces internes)
    text = re.sub(r"[«“„]\s*", '"', text)
    text = re.sub(r"\s*[»”‟]", '"', text)

    # 4. Remplacement des tirets cadratins / demi-cadratins par le tiret court -
    text = text.replace("—", "-").replace("–", "-")

    # 5. Suppression de tout espace avant les signes de ponctuation simples et doubles : ? ! ; : , . ) ] }
    text = re.sub(r"[ \t]+([?!;:,.)\]}])", r"\1", text)

    # 6. Suppression de tout espace après les parenthèses / crochets ouvrants ( [ {
    text = re.sub(r"([(\[{])[ \t]+", r"\1", text)

    # 7. Espaces après ? ! ; , si suivi d'un caractère alphanumérique ou parenthèse/guillemet ouvrant
    text = re.sub(r"([?!;,])([a-zA-Z0-9À-ÖØ-öø-ÿ(\[\"])", r"\1 \2", text)

    # 8. Deux-points (:) : assurer un espace après, sauf pour URLs (https://) et heures/ratios (14:30)
    def _fix_colon_after(m: re.Match) -> str:
        prefix = m.group(1)
        next_char = m.group(2)
        if prefix.lower() in ("http", "https", "ftp", "file") and next_char == "/":
            return f"{prefix}:{next_char}"
        if prefix[-1].isdigit() and next_char.isdigit():
            return f"{prefix}:{next_char}"
        return f"{prefix}: {next_char}"

    text = re.sub(r"([^\s:]+):([^\s/0-9])", _fix_colon_after, text)

    # 9. Point (.) : assurer un espace après s'il est suivi d'une lettre majuscule, sans toucher aux chiffres (3.14) ni extensions (.py)
    text = re.sub(r"(?<=[a-zA-ZÀ-ÖØ-öø-ÿ\)])\.(?=[A-ZÀ-ÖØ-ß])", ". ", text)

    # 10. Réduction des espaces multiples
    text = re.sub(r"[ \t]+", " ", text)

    # 12. Nettoyage des débuts/fins de lignes
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)
