# AI-remover: assainissement anti-IA de textes, documents et images avec gouvernance LLMOps

[![CI Pipeline](https://img.shields.io/badge/CI-passing-brightgreen?logo=githubactions&logoColor=white)](https://github.com/caroheymes/ai-remover/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Tests: Pytest](https://img.shields.io/badge/tests-71%20passed-success?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Antigravity Engine](https://img.shields.io/badge/Engine-Antigravity%20CLI%20%26%20Cloud%20Run-orange?logo=google&logoColor=white)](https://github.com/caroheymes/ai-remover)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

AI-remover s'exécute en local ou sur Google Cloud Run pour assainir les textes en français comme en anglais et corriger leurs métriques stylométriques. Le moteur supprime les signatures statistiques et typographiques produites par les modèles de langage, purge les caractères de traçage invisibles dans le flux Unicode et réécrit les documents selon le profil métier sélectionné tout en conservant 100 % des faits, chiffres et références.

```text
Entrée (Interface Streamlit / Fichier / Appel HTTP REST / Appel MCP stdio)
  |
  +-- 1. Purge déterministe (core/text_unicode.py: invisibles, homoglyphes, BOM)
  +-- 2. Calibrage bilingue FR/EN (core/profiles.py: 6 profils métier sans tics d'IA)
  +-- 3. Passerelle hybride (core/ai_bridge.py: petits modèles Flash CLI agy ou API Gemini)
  +-- 4. Diagnostic stylométrique (core/score_stylometry.py: MATTR, burstiness, diff mot-à-mot)
  +-- 5. API FastAPI sécurisée (api.py: port 8506 local ou Cloud Run avec Bearer + X-Gemini-API-Key)
  +-- 6. Serveur MCP stdio (mcp_server.py: Antigravity CLI, career-ops et Claude Code)
  +-- 7. Gouvernance LLMOps (core/evaluator.py, core/telemetry.py, Golden Dataset 14 cas FR/EN, Ragas)
  +-- 8. Validation continue (tests/: 71 tests automatisés, porte CI GitHub Actions et rapport PDF)
```

---

## Pourquoi ce projet existe

Les modèles de langage injectent quatre familles d'artefacts mesurables dans leurs sorties textuelles.

### Monotonie rythmique

La longueur des phrases demeure trop uniforme, ce qui effondre le coefficient de variation (burstiness minimale) et multiplie les cadences ternaires mécaniques.

### Formules préfabriquées francophones et anglophones

Le texte accumule les faux contrastes (`non seulement... mais aussi...`, `not only... but also...`), les chevilles d'annonce (`il convient de souligner`, `delve into`, `in today's fast-paced landscape`), les clichés de lettres de motivation (`à la croisée de`, `correspond parfaitement à mon parcours`, `thrilled to apply`, `at the intersection of`, `seamlessly`) et les superlatifs creux.

### Marqueurs invisibles et métadonnées de provenance

Le flux brut transporte des points de code Unicode de largeur nulle (`U+200B`, `U+FEFF`), des espaces insécables détournés (`U+00A0`, `U+202F`) et, dans les fichiers images, des métadonnées EXIF, XMP ou C2PA.

### Formatage artificiel

La mise en forme abuse des listes verticales à titres gras suivis de deux-points, des tirets cadratins et des sentences morales isolées en clôture.

AI-remover neutralise ces quatre couches sans jamais tronquer ni inventer les faits techniques, juridiques ou financiers du document d'origine.

---

## Architecture du pipeline en trois couches

### 1. Assainissement déterministe hors-LLM (`core/text_unicode.py`)

Cette première passe inspecte et nettoie le texte sans aucun appel réseau. Elle élimine 50 points de code invisibles et stéganographiques (BOM, séparateurs de variation, contrôles directionnels), rabat les 15 variantes d'espaces exotiques vers l'espace ASCII standard `0x20` et normalise les tirets cadratins ou demi-cadratins ainsi que les guillemets et apostrophes courbes.

### 2. Réécriture contextuelle bilingue par profil (`core/profiles.py`)

Le générateur d'instructions verrouille la langue du texte source (aucune traduction accidentelle d'une lettre anglaise vers le français) et applique 25 règles éditoriales strictes adaptées à six profils métier:

| Profil | Destination | Ligne directrice |
| :--- | :--- | :--- |
| **Avocat** | Consultations, conclusions, contrats | Standard LawyerScrib: voix active, qualification juridique nette, préservation intégrale des arrêts et articles de loi, zéro cheville rhétorique. |
| **Analyste** | Notes de stratégie, audits FinOps | Causalités directes, mise en avant des métriques chiffrées et explicitation des compromis opérationnels (`trade-offs`). |
| **Architecte** | Spécifications, lettres Lead Dev / Staff | Delivery technique concret, cadrage métier, stacks réelles de production et bannissement intégral des clichés de candidature FR/EN. |
| **Chercheur** | Articles scientifiques, revues | Prudence méthodologique, séparation explicite entre résultats mesurés et hypothèses, conservation des intervalles d'incertitude. |
| **Communicant** | Publications LinkedIn, X, infolettres | Accroche factuelle immédiate sans titre rigide, paragraphes courts adaptés au mobile, zéro vocabulaire publicitaire agressif. |
| **Ma propre voix** | Empreinte personnelle | Reproduction du rythme, de la syntaxe et du lexique d'un échantillon rédigé par l'utilisateur (`custom_sample`). |

En exécution locale (`agy`), `core/ai_bridge.py` interroge dynamiquement `agy models` pour ne proposer que les petits modèles rapides de la famille Flash (`gemini-3.8-flash-low` par défaut) et intègre un mécanisme de repli automatique si un identifiant de modèle est déprécié par le fournisseur.

### 3. Diagnostic stylométrique, diff visuel et observabilité (`core/score_stylometry.py`, `core/telemetry.py`)

Après réécriture, le moteur calcule le score composite de densité IA (de `0.0` à `1.0`), la diversité lexicale MATTR sur fenêtre glissante de 50 mots, la burstiness et le diff mot-à-mot exportable en PDF A4 via Playwright (avec repli HTML autonome). Chaque appel alimente en parallèle le journal structuré `logs/telemetry.jsonl`.

---

## Formats pris en charge

L'onglet documentaire de l'application traite les fichiers texte brut et Markdown (`.txt`, `.md`), les documents Microsoft Word (`.docx`) reconstruits proprement, les fichiers PDF (`.pdf`), les rapports d'audit comparatifs PDF A4 ainsi que les images (`.png`, `.jpg`, `.jpeg`) pour la suppression en mémoire des blocs EXIF, XMP et C2PA.

---

## Installation

Prérequis: Python 3.10, 3.11 ou 3.12 et le gestionnaire [uv](https://github.com/astral-sh/uv) (ou `pip`).

```powershell
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
uv run playwright install chromium
```

---

## Modes d'utilisation

### 1. Interface graphique Streamlit et tableau de bord LLMOps (port 8505)

```powershell
# Sous Windows (libère automatiquement le port 8505 si occupé)
launch.bat

# Ou en ligne de commande
uv run streamlit run app.py --server.port 8505
```

L'interface est accessible sur `http://localhost:8505`. Elle regroupe cinq onglets: traitement de texte instantané, documents et médias, studio de voix personnalisée, guide des règles de style et tableau de bord **Observabilité LLMOps** (taux de succès, centiles de latence `p50` et `p95` par modèle, volume par canal et exécution en un clic du Golden Dataset bilingue).

### 2. API REST hybride locale (port 8506) et Google Cloud Run

En local, le service FastAPI (`api.py`) démarre sur `http://127.0.0.1:8506` (documentation OpenAPI sur `/docs`) et exploite votre CLI Antigravity locale sans clé API:

```powershell
launch_api.bat
```

Pour un usage externe sur Google Cloud Run, le script `deploy_cloud_run.ps1` déploie une image légère (`Dockerfile` + `.dockerignore`), applique une politique FinOps de purge Artifact Registry ne conservant que les 2 dernières images, configure l'échelle à zéro (`min-instances=0`, `max-instances=2`, `512Mi`), verrouille toutes les routes `/api/v1/*` par un jeton `Authorization: Bearer <AI_REMOVER_API_TOKEN>` comparé en temps constant et exige l'injection à la volée de la clé Gemini via l'en-tête `X-Gemini-API-Key` (aucune clé Gemini stockée sur le serveur):

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy_cloud_run.ps1 -ProjectId VOTRE_PROJET_GCP
```

### 3. Serveur MCP pour Antigravity CLI (`career-ops`) et Claude Code

Le serveur `mcp_server.py` expose trois outils sur le protocole MCP (`stdio`): `humanize_text`, `analyze_ai_density` et `clean_invisible_unicode`. Il interroge en priorité l'API sur `AI_REMOVER_API_URL` (avec support de `AI_REMOVER_API_TOKEN` et `AI_REMOVER_API_KEY`) et bascule automatiquement sur l'exécution directe Python en mémoire si le démon HTTP local est éteint. Il est utilisable directement pour purifier les lettres de motivation francophones et anglophones dans `career-ops` avant compilation PDF.

### 4. Partage ponctuel par tunnel Cloudflare

Pour partager temporairement l'interface locale avec un tiers sans ouvrir de port routeur:

```powershell
partager.bat
```

Le guide complet d'exploitation de l'API, du serveur MCP, de `career-ops` et des métriques LLMOps est disponible dans [docs/GUIDE_API_MCP_LLMOPS.md](docs/GUIDE_API_MCP_LLMOPS.md).

---

## Gouvernance LLMOps, Golden Dataset bilingue et tests

Le corpus d'étalonnage `evals/golden_dataset.json` (v1.1.0) contient 14 cas métiers complets (9 en français et 5 en anglais) couvrant l'ingénierie MLOps/RAG/data, le droit des affaires/RGPD et l'analyse FinOps GPU. Pour chaque cas, `core/evaluator.py` vérifie quatre portes cumulatives: conservation de 100 % des faits requis, éradication de 100 % des clichés interdits, hygiène Unicode irréprochable (`1.0`) et score stylométrique final inférieur ou égal à `0.45`, complétées par les métriques de similarité Ragas (`NonLLMStringSimilarity`, `RougeScore` ou repli lexical F1 hors-ligne).

```powershell
# Suite complète des 71 tests unitaires et d'intégration
uv run --with fastapi --with httpx --with fastmcp pytest -v

# Porte de non-régression Golden Dataset hors-ligne (14 cas FR/EN)
uv run python evals/run_ragas_eval.py

# Évaluation réelle sur le modèle Flash local
uv run python evals/run_ragas_eval.py --live --limit 3 --model gemini-3.8-flash-low

# Linter et formatage Ruff
uv run --with ruff ruff check .
uv run --with ruff ruff format --check .
```

Le workflow GitHub Actions (`.github/workflows/ci.yml`) exécute automatiquement Ruff, les 71 tests Pytest et la porte Golden Dataset sur Ubuntu et Windows (Python 3.10, 3.11 et 3.12) à chaque push.

---

## Structure du dépôt

```text
AI-remover/
├── app.py                        # Interface Streamlit + onglet Observabilité LLMOps (port 8505)
├── api.py                        # API FastAPI hybride v1.2.0 (Bearer auth + X-Gemini-API-Key)
├── mcp_server.py                 # Serveur MCP stdio pour Antigravity CLI et Claude Code
├── Dockerfile                    # Image conteneur Python 3.12 légère pour Cloud Run
├── .dockerignore                 # Exclusion des environnements virtuels, journaux et tests
├── deploy_cloud_run.ps1          # Déploiement Cloud Run sécurisé avec purge Artifact Registry
├── launch.bat                    # Lanceur Windows Streamlit (port 8505)
├── launch_api.bat                # Lanceur Windows FastAPI (port 8506)
├── partager.bat                  # Tunnel distant Cloudflare
├── .mcp.json                     # Configuration MCP locale pour Claude Code
├── reprise.md                    # Document d'état opérationnel et de reprise rapide
├── requirements.txt              # Dépendances de production
├── requirements-dev.txt          # Dépendances de développement et de test
├── core/
│   ├── text_unicode.py           # Détection et purge déterministe des caractères invisibles
│   ├── profiles.py               # 6 profils métier bilingues FR/EN et règles anti-IA
│   ├── score_stylometry.py       # Détection stylométrique FR/EN, MATTR, burstiness et diff
│   ├── ai_bridge.py              # Pont petits modèles Flash Antigravity CLI et API Gemini
│   ├── evaluator.py              # Portes qualité LLMOps et métriques Ragas
│   ├── telemetry.py              # Télémétrie JSONL structurée et agrégation p50/p95 par modèle
│   └── file_processor.py         # Extraction et export docx/pdf, Playwright et purge EXIF/C2PA
├── evals/
│   ├── golden_dataset.json       # Corpus bilingue v1.1.0 (14 cas FR/EN, faits et clichés)
│   └── run_ragas_eval.py         # Harnais CLI d'évaluation hors-ligne et temps réel (--live)
├── docs/
│   └── GUIDE_API_MCP_LLMOPS.md   # Guide technique complet API, Cloud Run, MCP et LLMOps
└── tests/                        # 71 tests automatisés sous Pytest
```

---

## Licence

Ce projet est distribué sous licence MIT.
