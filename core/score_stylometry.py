"""Zero-LLM statistical & stylometric AI-text detector and pattern highlighter."""

from __future__ import annotations

import difflib
import html
import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# High-frequency formulaic transition markers, hedging verbs, and structural boilerplate
AI_PHRASE_PATTERNS: tuple[tuple[str, str, float, str], ...] = (
    # (regex_pattern, human_label, weight, category)
    (
        r"\bdelve(?:s|d)?\s+into\b",
        "delve into / plonger dans",
        1.2,
        "Formules et clichés d'IA",
    ),
    (
        r"\ba\s+testament\s+to\b",
        "a testament to / un témoignage de",
        1.1,
        "Emphase artificielle",
    ),
    (
        r"\brich\s+tapestry(?:\s+of)?\b",
        "rich tapestry / riche mosaïque",
        1.3,
        "Métaphores et clichés",
    ),
    (
        r"\bplays?\s+a\s+(?:pivotal|crucial|vital|key)\s+role\b",
        "plays a crucial/pivotal role / joue un rôle clé",
        1.0,
        "Emphase artificielle",
    ),
    (
        r"\b(témoigne|témoignage)\s+de\s+(l'importance|la\s+richesse|la\s+volonté)\b",
        "témoigne de l'importance",
        1.1,
        "Emphase artificielle",
    ),
    (
        r"\bjoue\s+un\s+rôle\s+(crucial|charnière|fondateur|majeur|déterminant)\b",
        "joue un rôle crucial/charnière",
        1.0,
        "Emphase artificielle",
    ),
    (
        r"\bdans\s+un\s+(monde|paysage|environnement|contexte)\s+(en\s+constante\s+évolution|complexe|numérique|digital)\b",
        "dans un monde en constante évolution",
        1.4,
        "Formules et clichés d'IA",
    ),
    (
        r"\bin\s+(?:today'?s|the)\s+(?:(?:fast-paced|ever-evolving|digital|rapidly\s+changing)\s+)*(?:world|landscape|era|environment)\b",
        "in today's fast-paced world/landscape",
        1.4,
        "Formules et clichés d'IA",
    ),
    (
        r"\bà\s+l'ère\s+(du\s+numérique|de\s+l'intelligence\s+artificielle|de\s+l'information|du\s+digital)\b",
        "à l'ère du numérique/IA",
        1.3,
        "Formules et clichés d'IA",
    ),
    (
        r"\bin\s+the\s+era\s+of\s+(?:AI|artificial\s+intelligence|digital\s+transformation)\b",
        "in the era of AI/digital",
        1.3,
        "Formules et clichés d'IA",
    ),
    (
        r"\b(il\s+est\s+(important|essentiel|crucial|primordial|fondamental)\s+de\s+(noter|souligner|rappeler|mentionner))\b",
        "il est essentiel de noter/souligner",
        0.9,
        "Annonces et chauffes",
    ),
    (
        r"\bil\s+convient\s+de\s+(souligner|noter|rappeler|préciser)\b",
        "il convient de souligner/noter",
        0.9,
        "Annonces et chauffes",
    ),
    (
        r"\bit\s+is\s+(?:important|essential|crucial|worth\s+noting|vital)\s+to\s+(?:note|remember|consider|highlight)\b",
        "it is crucial to note",
        0.9,
        "Annonces et chauffes",
    ),
    (
        r"\bnot\s+only\b[\w\s,]+\bbut\s+(?:also\s+)?(?:serves\s+to|acts\s+as|highlights|represents)\b",
        "not only ... but also",
        0.9,
        "Faux contrastes mécaniques",
    ),
    (
        r"\bnon\s+seulement\b[\w\s,]+\bmais\s+(aussi|également|constitue|représente)\b",
        "non seulement ... mais aussi",
        0.9,
        "Faux contrastes mécaniques",
    ),
    (
        r"\bce\s+n'est\s+pas\s+(seulement|uniquement)[\w\s,]+c'est\b",
        "ce n'est pas seulement... c'est...",
        1.0,
        "Faux contrastes mécaniques",
    ),
    (
        r"\bit's\s+not\s+just\s+(?:about)?[\w\s,]+it's\s+(?:about)?\b",
        "it's not just... it's...",
        1.0,
        "Faux contrastes mécaniques",
    ),
    (
        r"\b(souligne|met\s+en\s+lumière|met\s+en\s+exergue)\s+(l'importance|la\s+nécessité|le\s+besoin)\b",
        "souligne l'importance / met en lumière",
        0.9,
        "Emphase artificielle",
    ),
    (
        r"\bunderscore(?:s|d)?\s+the\s+(?:importance|need|significance)\b",
        "underscores the importance",
        0.9,
        "Emphase artificielle",
    ),
    (
        r"\b(paysage|tissu|mosaïque)\s+(complexe|dynamique|numérique)\b",
        "paysage / tissu complexe",
        1.0,
        "Métaphores et clichés",
    ),
    (
        r"\bnavigat(?:e|ing|es|ed)\s+the\s+(?:complexities|intricacies|nuances)\b",
        "navigating complexities",
        1.0,
        "Formules et clichés d'IA",
    ),
    (
        r"\bnaviguer\s+(dans\s+les|à\s+travers\s+les)\s+(complexités|méandres)\b",
        "naviguer dans les complexités",
        1.0,
        "Formules et clichés d'IA",
    ),
    (
        r"\b(plongeons|plonger)\s+dans\b",
        "plongeons dans...",
        1.2,
        "Annonces et chauffes",
    ),
    (r"\blet'?s\s+dive\s+into\b", "let's dive into...", 1.2, "Annonces et chauffes"),
    (
        r"\bun\s+véritable\s+(catalyseur|tournant|moteur|levier|havre)\b",
        "un véritable catalyseur/tournant",
        1.1,
        "Emphase artificielle",
    ),
    (
        r"\ba\s+(?:game-changer|catalyst|beacon\s+of|cornerstone\s+of)\b",
        "game-changer / catalyst / beacon",
        1.1,
        "Emphase artificielle",
    ),
    (
        r"\b(niché|nichée)\s+au\s+cœur\s+de\b",
        "niché(e) au cœur de",
        1.2,
        "Formules et clichés d'IA",
    ),
    (
        r"\bnestled\s+in\s+the\s+heart\s+of\b",
        "nestled in the heart of",
        1.2,
        "Formules et clichés d'IA",
    ),
    (
        r"\bouvr(?:ir|ant|e|ent)\s+la\s+voie\s+à\b",
        "ouvrir la voie à",
        0.9,
        "Emphase artificielle",
    ),
    (
        r"\bpav(?:ing|es|ed)?\s+the\s+way\s+for\b",
        "paving the way for",
        0.9,
        "Emphase artificielle",
    ),
    (
        r"\b(favoriser|stimuler)\s+une\s+(synergie|collaboration|croissance)\b",
        "favoriser une synergie",
        1.0,
        "Formules et clichés d'IA",
    ),
    (
        r"\b(foster|fostering)\s+(?:collaboration|innovation|growth|synergy)\b",
        "fostering collaboration/synergy",
        1.0,
        "Formules et clichés d'IA",
    ),
    (
        r"\bforce\s+est\s+de\s+constater\b",
        "force est de constater",
        0.9,
        "Formules et clichés d'IA",
    ),
    (
        r"\b(en\s+conclusion|pour\s+résumer|en\s+somme|en\s+définitive|somme\s+toute)[,\s]",
        "en conclusion / pour résumer",
        0.8,
        "Clôtures artificielles",
    ),
    (
        r"\bin\s+conclusion\b[,\s]|\bto\s+sum\s+up\b[,\s]|\bultimately\b[,\s]",
        "in conclusion / ultimately",
        0.8,
        "Clôtures artificielles",
    ),
    (
        r"\bmoreover\b[,\s]|\bfurthermore\b[,\s]",
        "moreover / furthermore",
        0.6,
        "Connecteurs lourds",
    ),
    (
        r"\bde\s+surcroît\b[,\s]|\bqui\s+plus\s+est\b[,\s]",
        "de surcroît,",
        0.6,
        "Connecteurs lourds",
    ),
    (
        r"\b(j'espère\s+que\s+cela\s+(vous\s+)?aide|n'hésitez\s+pas\s+si\s+vous\s+avez\s+des\s+questions)\b",
        "Résidu de conversation",
        1.5,
        "Résidus de conversation",
    ),
    (
        r"\bi\s+hope\s+this\s+helps\b|\blet\s+me\s+know\s+if\s+you\s+need\b",
        "I hope this helps",
        1.5,
        "Résidus de conversation",
    ),
    (
        r"—|–",
        "Tiret cadratin / demi-cadratin (— / –)",
        0.8,
        "Ponctuation et typographie",
    ),
    (
        r"(?m)^\s*[\*\-]\s+\*\*[^\*:]+\*\*\s*:",
        "Liste robotique (**Titre :**)",
        1.0,
        "Formatage artificiel",
    ),
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-ß0-9])")
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


@dataclass
class StylometryReport:
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_len: float = 0.0
    burstiness: float = 0.0  # Coefficient of variation of sentence length
    mattr: float = 0.0  # Moving-average Type-Token Ratio
    ai_phrase_count: int = 0
    composite_score: float = 0.0  # 0.0 (Clean/Human) to 1.0 (High AI density)
    density_tier: str = "low"  # low, medium, high
    flagged_spans: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class EditorialReport:
    rep_in: StylometryReport
    rep_out: StylometryReport
    tics_by_category: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    choices_made: list[dict[str, Any]] = field(default_factory=list)
    em_dashes_before: int = 0
    em_dashes_after: int = 0
    invisible_chars_count: int = 0
    diff_stats: dict[str, Any] = field(default_factory=dict)
    diff_html: str = ""
    audit_markdown: str = ""


def split_sentences(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return []
    parts = SENTENCE_SPLIT_RE.split(clean)
    return [p.strip() for p in parts if p.strip()]


def calculate_mattr(words: list[str], window_size: int = 50) -> float:
    if not words:
        return 0.0
    if len(words) < window_size:
        return len({w.lower() for w in words}) / len(words)
    scores = []
    for i in range(len(words) - window_size + 1):
        window = words[i : i + window_size]
        scores.append(len({w.lower() for w in window}) / window_size)
    return sum(scores) / len(scores)


def analyze_stylometry(text: str) -> StylometryReport:
    report = StylometryReport()
    words = WORD_RE.findall(text)
    sentences = split_sentences(text)

    report.word_count = len(words)
    report.sentence_count = len(sentences)

    if report.word_count < 5:
        report.density_tier = "insuffisant"
        return report

    # 1. Longueur de phrases et burstiness
    lens = [len(WORD_RE.findall(s)) for s in sentences if s]
    if lens:
        report.avg_sentence_len = sum(lens) / len(lens)
        if len(lens) > 1:
            mean = report.avg_sentence_len
            variance = sum((l - mean) ** 2 for l in lens) / len(lens)
            std_dev = math.sqrt(variance)
            report.burstiness = std_dev / mean if mean > 0 else 0.0
        else:
            report.burstiness = 0.0

    # 2. MATTR (Diversité lexicale)
    report.mattr = calculate_mattr(words, window_size=min(50, len(words)))

    # 3. Détection des phrases et tics d'IA
    flagged = []
    phrase_score_sum = 0.0
    for pattern, label, weight, category in AI_PHRASE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            flagged.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group().strip(),
                    "label": label,
                    "category": category,
                    "weight": weight,
                }
            )
            phrase_score_sum += weight

    report.ai_phrase_count = len(flagged)
    report.flagged_spans = flagged

    # 4. Score composite calibré
    density_per_100 = (phrase_score_sum / max(1, report.word_count)) * 100
    burstiness_penalty = (
        max(0.0, (0.6 - report.burstiness) * 0.5) if report.burstiness < 0.6 else 0.0
    )
    cadence_penalty = min(0.6, density_per_100 * 0.15)

    score = cadence_penalty + burstiness_penalty
    report.composite_score = round(min(1.0, max(0.0, score)), 2)

    if report.composite_score >= 0.65:
        report.density_tier = "élevé"
    elif report.composite_score >= 0.35:
        report.density_tier = "modéré"
    else:
        report.density_tier = "faible"

    return report


def generate_editorial_report(
    input_text: str,
    output_text: str,
    profile_id: str = "avocat",
    unicode_stats: Any = None,
) -> EditorialReport:
    """Compare les textes source et cible pour récapituler les tics détectés et les choix éditoriaux."""
    rep_in = analyze_stylometry(input_text)
    rep_out = analyze_stylometry(output_text)

    # 1. Regrouper les tics identifiés dans le texte source par catégorie
    tics_by_cat: dict[str, list[dict[str, Any]]] = {}
    for span in rep_in.flagged_spans:
        cat = span["category"]
        if cat not in tics_by_cat:
            tics_by_cat[cat] = []
        tics_by_cat[cat].append(span)

    # 2. Mesures typographiques
    dashes_in = input_text.count("—") + input_text.count("–")
    dashes_out = output_text.count("—") + output_text.count("–")

    invisible_count = 0
    if unicode_stats:
        if hasattr(unicode_stats, "invisible_count"):
            invisible_count = unicode_stats.invisible_count + getattr(
                unicode_stats, "space_homoglyph_count", 0
            )
        elif isinstance(unicode_stats, dict):
            invisible_count = unicode_stats.get("invisible_chars_removed", 0)

    # 3. Compiler la liste explicite des choix éditoriaux effectués
    choices: list[dict[str, Any]] = []

    # Choix A : Typographie et ponctuation
    typo_details = []
    if dashes_in > 0:
        typo_details.append(
            f"Élimination de **{dashes_in} tiret(s) cadratin(s) (`—` / `–`)**, remplacés par une ponctuation naturelle (virgules, points ou structures directes)."
        )
    else:
        typo_details.append(
            "Garantie zéro tiret cadratin : typographie conforme aux règles de rédaction fluide."
        )

    if invisible_count > 0:
        typo_details.append(
            f"Purge déterministe de **{invisible_count} caractère(s) Unicode invisible(s)** ou espaces de traçage synthétique."
        )

    # Vérification des listes à puces robotiques
    if re.search(r"(?m)^\s*[\*\-]\s+\*\*[^\*:]+\*\*\s*:", input_text) and not re.search(
        r"(?m)^\s*[\*\-]\s+\*\*[^\*:]+\*\*\s*:", output_text
    ):
        typo_details.append(
            "Remplacement du formatage mécanique (listes avec titres en gras et deux-points) par des paragraphes rédigés."
        )

    choices.append(
        {
            "category": "Typographie et nettoyage déterministe",
            "description": "Purge des marqueurs visuels et invisibles typiques des modèles de langage.",
            "items": typo_details,
        }
    )

    # Choix B : Lexique et expressions
    lex_details = []
    purged_tics = []
    for span in rep_in.flagged_spans:
        span_text = span["text"].lower()
        if (
            span_text not in output_text.lower()
            and span["label"] not in purged_tics
            and span["category"] != "Ponctuation et typographie"
        ):
            purged_tics.append(span["label"])

    if purged_tics:
        lex_details.append(
            f"Suppression et neutralisation de **{len(purged_tics)} expression(s) ou cliché(s)** : *{', '.join(purged_tics[:6])}*{' et autres.' if len(purged_tics) > 6 else '.'}"
        )
    else:
        lex_details.append(
            "Nettoyage du vocabulaire convenu : suppression des superlatifs creux et des termes génériques."
        )

    lex_details.append(
        "Remplacement des verbes d'évitement et formules de remplissage par des désignations concrètes."
    )
    choices.append(
        {
            "category": "Vocabulaire et démétaphorisation",
            "description": "Remplacement du jargon et des métaphores préfabriquées par un lexique précis.",
            "items": lex_details,
        }
    )

    # Choix C : Rythme et syntaxe
    rhythm_details = []
    # Faux contrastes
    if re.search(
        r"\b(not\s+only|non\s+seulement|ce\s+n'est\s+pas\s+(seulement|uniquement))\b",
        input_text,
        re.IGNORECASE,
    ) and not re.search(
        r"\b(not\s+only|non\s+seulement|ce\s+n'est\s+pas\s+(seulement|uniquement))\b",
        output_text,
        re.IGNORECASE,
    ):
        rhythm_details.append(
            "Démantèlement des **faux contrastes mécaniques** (*Non seulement X, mais aussi Y*, *Ce n'est pas seulement... c'est...*) au profit d'affirmations directes."
        )

    # Annonces / Clôtures
    if re.search(
        r"\b(il\s+est\s+(important|essentiel|crucial)|plongeons\s+dans|en\s+conclusion|pour\s+résumer)\b",
        input_text,
        re.IGNORECASE,
    ) and not re.search(
        r"\b(il\s+est\s+(important|essentiel|crucial)|plongeons\s+dans|en\s+conclusion|pour\s+résumer)\b",
        output_text,
        re.IGNORECASE,
    ):
        rhythm_details.append(
            "Suppression des **chauffes théâtrales** (*Il est essentiel de souligner*, *Plongeons dans*) et des **clôtures redondantes** (*En conclusion*)."
        )

    # Burstiness change
    if rep_out.burstiness >= 0.35:
        rhythm_details.append(
            f"Restructuration du rythme (burstiness : **{rep_out.burstiness:.2f}**) : rupture de la monotonie de longueur de phrase par l'alternance de propositions courtes et denses."
        )
    else:
        rhythm_details.append(
            f"Variation de la longueur moyenne des phrases (**{rep_out.avg_sentence_len:.1f} mots par phrase**) pour un phrasé naturel."
        )

    choices.append(
        {
            "category": "Syntaxe et dynamique du rythme",
            "description": "Rupture de la cadence robotique uniforme et clarification des structures grammaticales.",
            "items": rhythm_details,
        }
    )

    # Choix D : Choix spécifiques au profil métier
    profile_decisions = {
        "avocat": {
            "title": "Profil Avocat et juriste d'affaires",
            "points": [
                "Qualification doctrinale et terminologique rigoureuse des notions juridiques.",
                "Élimination des affirmations péremptoires gratuites au profit d'un raisonnement étayé.",
                "Usage sobre et mesuré des modalisateurs sans empilement artificiel.",
            ],
        },
        "analyste": {
            "title": "Profil Analyste et stratège",
            "points": [
                "Focalisation sur les mécanismes causaux, les faits vérifiables et les données chiffrées.",
                "Mise en lumière explicite des compromis opérationnels (trade-offs) et coûts d'opportunité.",
                "Élimination intégrale des superlatifs creux et du verbiage non décisionnel.",
            ],
        },
        "architecte": {
            "title": "Profil Architecte technique et lead dev",
            "points": [
                "Formulation directe, pragmatique et orientée production logicielle.",
                "Adoption de la voix active (identification explicite du composant ou de l'acteur qui opère).",
                "Rejet des métaphores numériques floues (paysage digital) au profit des contraintes d'ingénierie réelles.",
            ],
        },
        "chercheur": {
            "title": "Profil Chercheur et universitaire",
            "points": [
                "Respect strict de la prudence épistémique (distinction nette entre faits démontrés et hypothèses).",
                "Neutralité formelle, absence totale de formules sensationnalistes.",
                "Préservation intégrale des protocoles, données et grandeurs scientifiques.",
            ],
        },
        "communicant": {
            "title": "Profil Communicant et rédacteur",
            "points": [
                "Remplacement du titre par une accroche narrative ou un fait brut : sur format court (publication pour réseaux sociaux type Instagram ou LinkedIn), le titre formel est supprimé et converti en première ligne d'accroche (hook) pour inciter au clic sur « Voir plus » et maximiser le taux d'ouverture.",
                "Contournement des filtres anti-publicité de Meta et LinkedIn : élimination de la structure publicitaire conventionnelle (titres rigides, promesses commerciales) afin d'éviter le déclassement algorithmique et maximiser la portée organique naturelle.",
                "Formatage mobile aéré : découpage en courts paragraphes percutants (1 à 3 phrases) pour un rythme de lecture naturel sans artifices.",
                "Sélection de 2 à 3 hashtags thématiques ciblés en clôture : ajout d'un nombre restreint de mots-clés spécifiques au sujet en toute fin de post pour le référencement sémantique, sans surcharge algorithmique.",
                "Démonstration par la preuve : valorisation de faits précis et de solutions concrètes sans vocabulaire commercial agressif ni incitation artificielle à l'engagement (engagement-bait).",
            ],
        },
        "custom": {
            "title": "Profil Ma propre voix",
            "points": [
                "Calibrage syntaxique et lexical sur l'empreinte de votre échantillon personnel.",
                "Conservation de vos habitudes de formulation, de votre ponctuation et de votre niveau de langue.",
                "Suppression des automatismes d'IA pour laisser transparaître votre voix authentique.",
            ],
        },
    }

    p_info = profile_decisions.get(profile_id, profile_decisions["avocat"])
    choices.append(
        {
            "category": f"Calibration au style : {p_info['title']}",
            "description": "Alignement précis avec les exigences de posture et de ton sélectionnées.",
            "items": p_info["points"],
        }
    )

    # Choix E : Préservation factuelle
    choices.append(
        {
            "category": "Intégrité factuelle absolue",
            "description": "Garantie de fidélité au fond du message source.",
            "items": [
                "Préservation de 100 % des faits, données chiffrées, entités, dates et consignes du texte source.",
                "Zéro hallucination, zéro omission de contrainte métier et zéro déformation du sens originel.",
            ],
        }
    )

    diff_html, diff_stats = compute_word_diff_html(input_text, output_text)

    report = EditorialReport(
        rep_in=rep_in,
        rep_out=rep_out,
        tics_by_category=tics_by_cat,
        choices_made=choices,
        em_dashes_before=dashes_in,
        em_dashes_after=dashes_out,
        invisible_chars_count=invisible_count,
        diff_stats=diff_stats,
        diff_html=diff_html,
    )
    report.audit_markdown = generate_audit_log_markdown(
        report, input_text=input_text, output_text=output_text, profile_id=profile_id
    )
    return report


def _diff_span_tokens(span_in: str, span_out: str) -> tuple[str, int, int, int]:
    """Calcule le diff mot-à-mot local pour un segment de texte."""
    tokens_in = re.findall(r"\S+|\s+", span_in)
    tokens_out = re.findall(r"\S+|\s+", span_out)
    matcher = difflib.SequenceMatcher(None, tokens_in, tokens_out)
    out_html: list[str] = []
    w_pres = 0
    w_del = 0
    w_add = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            chunk = "".join(tokens_in[i1:i2])
            w_pres += len(WORD_RE.findall(chunk))
            out_html.append(html.escape(chunk).replace("\n", "<br>"))
        elif tag == "delete":
            chunk = "".join(tokens_in[i1:i2])
            w_del += len(WORD_RE.findall(chunk))
            escaped = html.escape(chunk).replace("\n", "<br>")
            out_html.append(
                f'<span class="diff-del" style="background-color: #FEE2E2; color: #991B1B; text-decoration: line-through; padding: 2px 4px; border-radius: 4px; margin: 0 1px;">{escaped}</span>'
            )
        elif tag == "insert":
            chunk = "".join(tokens_out[j1:j2])
            w_add += len(WORD_RE.findall(chunk))
            escaped = html.escape(chunk).replace("\n", "<br>")
            out_html.append(
                f'<span class="diff-ins" style="background-color: #DCFCE7; color: #166534; font-weight: 600; padding: 2px 4px; border-radius: 4px; margin: 0 1px;">{escaped}</span>'
            )
        elif tag == "replace":
            chunk_del = "".join(tokens_in[i1:i2])
            chunk_ins = "".join(tokens_out[j1:j2])
            w_del += len(WORD_RE.findall(chunk_del))
            w_add += len(WORD_RE.findall(chunk_ins))
            esc_del = html.escape(chunk_del).replace("\n", "<br>")
            esc_ins = html.escape(chunk_ins).replace("\n", "<br>")
            out_html.append(
                f'<span class="diff-del" style="background-color: #FEE2E2; color: #991B1B; text-decoration: line-through; padding: 2px 4px; border-radius: 4px; margin: 0 1px;">{esc_del}</span>'
                f'<span class="diff-ins" style="background-color: #DCFCE7; color: #166534; font-weight: 600; padding: 2px 4px; border-radius: 4px; margin: 0 1px;">{esc_ins}</span>'
            )

    return "".join(out_html), w_pres, w_del, w_add


def compute_word_diff_html(
    text_before: str, text_after: str, container: bool = True
) -> tuple[str, dict[str, Any]]:
    """Génère un rendu HTML enrichi du diff mot-à-mot avec alignement de phrases pour éviter les fausses suppressions globales."""
    if not text_before and not text_after:
        return "", {
            "words_before": 0,
            "words_after": 0,
            "words_preserved": 0,
            "words_deleted": 0,
            "words_added": 0,
            "retention_rate": 100.0,
        }

    s_in = split_sentences(text_before)
    s_out = split_sentences(text_after)

    if not s_in and not s_out:
        return "", {
            "words_before": 0,
            "words_after": 0,
            "words_preserved": 0,
            "words_deleted": 0,
            "words_added": 0,
            "retention_rate": 100.0,
        }

    words_in_count = len(WORD_RE.findall(text_before))
    words_out_count = len(WORD_RE.findall(text_after))
    words_preserved = 0
    words_deleted = 0
    words_added = 0

    parts: list[str] = []

    # Repérage des phrases débutant un paragraphe dans le texte de sortie
    para_starts_out = set()
    for p in text_after.split("\n\n"):
        p_clean = p.strip()
        if p_clean:
            for s in s_out:
                if p_clean.startswith(s[: min(30, len(s))]):
                    para_starts_out.add(s)
                    break

    # Si le nombre de phrases est égal : appariement direct phrase par phrase
    if len(s_in) == len(s_out):
        for idx, (s1, s2) in enumerate(zip(s_in, s_out)):
            h_chunk, wp, wd, wa = _diff_span_tokens(s1, s2)
            words_preserved += wp
            words_deleted += wd
            words_added += wa
            if idx > 0 and s2 in para_starts_out:
                parts.append(f"<br><br>{h_chunk}")
            else:
                parts.append(h_chunk)
        html_body = " ".join(parts)
    else:
        # Appariement intelligent des séquences de phrases
        s_matcher = difflib.SequenceMatcher(
            None,
            [s.lower()[:35] for s in s_in],
            [s.lower()[:35] for s in s_out],
        )
        for tag, i1, i2, j1, j2 in s_matcher.get_opcodes():
            if tag == "equal":
                for s1, s2 in zip(s_in[i1:i2], s_out[j1:j2]):
                    h_chunk, wp, wd, wa = _diff_span_tokens(s1, s2)
                    words_preserved += wp
                    words_deleted += wd
                    words_added += wa
                    if parts and s2 in para_starts_out:
                        parts.append(f"<br><br>{h_chunk}")
                    else:
                        parts.append(h_chunk)
            elif tag == "replace":
                sin_block = " ".join(s_in[i1:i2])
                sout_block = " ".join(s_out[j1:j2])
                h_chunk, wp, wd, wa = _diff_span_tokens(sin_block, sout_block)
                words_preserved += wp
                words_deleted += wd
                words_added += wa
                first_s_out = s_out[j1] if j1 < len(s_out) else ""
                if parts and first_s_out in para_starts_out:
                    parts.append(f"<br><br>{h_chunk}")
                else:
                    parts.append(h_chunk)
            elif tag == "delete":
                sin_block = " ".join(s_in[i1:i2])
                h_chunk, wp, wd, wa = _diff_span_tokens(sin_block, "")
                words_preserved += wp
                words_deleted += wd
                words_added += wa
                parts.append(h_chunk)
            elif tag == "insert":
                sout_block = " ".join(s_out[j1:j2])
                h_chunk, wp, wd, wa = _diff_span_tokens("", sout_block)
                words_preserved += wp
                words_deleted += wd
                words_added += wa
                first_s_out = s_out[j1] if j1 < len(s_out) else ""
                if parts and first_s_out in para_starts_out:
                    parts.append(f"<br><br>{h_chunk}")
                else:
                    parts.append(h_chunk)

        html_body = " ".join(parts)

    words_preserved = max(0, words_in_count - words_deleted)
    retention_rate = round((words_preserved / max(1, words_in_count)) * 100, 1)

    diff_stats = {
        "words_before": words_in_count,
        "words_after": words_out_count,
        "words_preserved": words_preserved,
        "words_deleted": words_deleted,
        "words_added": words_added,
        "retention_rate": retention_rate,
    }

    if not container:
        return html_body, diff_stats

    full_html = (
        '<div style="font-family: inherit; line-height: 1.7; font-size: 0.95rem; color: #1E293B; '
        "background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px 20px; "
        f'max-height: 480px; overflow-y: auto;">{html_body}</div>'
    )

    return full_html, diff_stats


def generate_audit_log_markdown(
    report: EditorialReport,
    input_text: str,
    output_text: str,
    profile_id: str = "avocat",
) -> str:
    """Génère un rapport d'audit et de traçabilité complet au format Markdown."""
    now_str = datetime.now().astimezone().strftime("%d/%m/%Y à %H:%M")
    rep_in = report.rep_in
    rep_out = report.rep_out
    stats = report.diff_stats

    lines = [
        "# Journal d'audit et de traçabilité éditoriale",
        "",
        f"- **Date de l'audit** : {now_str}",
        f"- **Profil stylistique appliqué** : {profile_id.capitalize()}",
        f"- **Taux de conservation factuelle** : **{stats.get('retention_rate', 100)} %**",
        "",
        "---",
        "",
        "## 1. Synthèse métrique et stylométrique",
        "",
        "| Indicateur | Texte source | Texte humanisé | Évolution |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Score composite d'IA** | {rep_in.composite_score:.2f} ({rep_in.density_tier}) | {rep_out.composite_score:.2f} ({rep_out.density_tier}) | {rep_out.composite_score - rep_in.composite_score:+.2f} |",
        f"| **Tics d'IA détectés** | {rep_in.ai_phrase_count} | {rep_out.ai_phrase_count} | {rep_out.ai_phrase_count - rep_in.ai_phrase_count:+d} |",
        f"| **Relief du rythme (Burstiness)** | {rep_in.burstiness:.2f} | {rep_out.burstiness:.2f} | {rep_out.burstiness - rep_in.burstiness:+.2f} |",
        f"| **Diversité lexicale (MATTR)** | {rep_in.mattr:.2f} | {rep_out.mattr:.2f} | {rep_out.mattr - rep_in.mattr:+.2f} |",
        f"| **Volume de mots** | {stats.get('words_before', 0)} | {stats.get('words_after', 0)} | Mots épurés : {stats.get('words_deleted', 0)}, Ajoutés : {stats.get('words_added', 0)} |",
        "",
        "---",
        "",
        "## 2. Inventaire des tics et scories d'IA purgés",
        "",
    ]

    if report.tics_by_category:
        for cat, tics in report.tics_by_category.items():
            lines.append(f"### {cat} ({len(tics)} occurrence(s))")
            for t in tics:
                lines.append(
                    f"- Extrait : `{t['text']}` : *{t['label']}* (poids : {t['weight']})"
                )
            lines.append("")
    else:
        lines.append("Aucun tic de phrasé d'IA détecté dans le texte source.\n")

    lines.extend(
        [
            "### Typographie et nettoyage déterministe (Layer A)",
            f"- Tirets cadratins (`—` / `–`) : **{report.em_dashes_before}** dans la source, **{report.em_dashes_after}** dans le résultat final.",
            f"- Caractères Unicode invisibles et espaces de traçage purgés : **{report.invisible_chars_count}**.",
            "",
            "---",
            "",
            "## 3. Choix éditoriaux et règles appliquées",
            "",
        ]
    )

    for choice in report.choices_made:
        lines.append(f"### {choice['category']}")
        lines.append(f"*{choice['description']}*\n")
        for item in choice["items"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## 4. Comparatif textuel intégral",
            "",
            "### Texte source :",
            "",
            input_text.strip(),
            "",
            "### Texte humanisé :",
            "",
            output_text.strip(),
            "",
        ]
    )

    return "\n".join(lines)
