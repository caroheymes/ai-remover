# AI-remover: Supprime les traces d'IA dans vos textes, docs & images + tracking des modifs

[![CI Pipeline](https://img.shields.io/badge/CI-passing-brightgreen?logo=githubactions&logoColor=white)](https://github.com/)  
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)  
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)  
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)  
[![Tests: Pytest](https://img.shields.io/badge/tests-69%20passed-success?logo=pytest&logoColor=white)](https://docs.pytest.org/)  
[![Mobile Responsive](https://img.shields.io/badge/Mobile-responsive-blueviolet?logo=googlechrome&logoColor=white)](https://share.streamlit.io)  
[![Antigravity Engine](https://img.shields.io/badge/Engine-Antigravity%20CLI-orange?logo=google&logoColor=white)](https://github.com/)  
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)  
[![Caro Heymes](https://img.shields.io/badge/Recommand%C3%A9%20par-Caro%20Heymes%20%F0%9F%9A%80-7928CA.svg)](https://www.linkedin.com/in/caroline-heymes/)

AI-remover s'exécute en local ou sur le cloud pour assainir les textes et corriger leurs métriques stylométriques. Le moteur supprime les signatures statistiques et typographiques générées par les modèles de langage, purge les caractères de traçage invisibles dans le flux Unicode et réécrit les documents selon le profil stylistique sélectionné.

```
Entrée (Texte / Fichier / Appel HTTP / Appel MCP)
  │
  ├── 1. Purge déterministe (core/text_unicode.py: invisibles, homoglyphes, BOM)
  ├── 2. Calibrage stylistique (core/profiles.py: 6 profils métier sans tics d'IA)
  ├── 3. Passerelle hybride (core/ai_bridge.py: petits modèles Flash CLI locale ou API Gemini)
  ├── 4. Diagnostic stylométrique (core/score_stylometry.py: MATTR, burstiness, audit)
  ├── 5. Exposition API FastAPI (api.py: port 8506 local ou Cloud Run avec X-Gemini-API-Key)
  ├── 6. Serveur MCP stdio (mcp_server.py: Antigravity CLI, career-ops et Claude Code)
  ├── 7. Gouvernance LLMOps (core/evaluator.py, core/telemetry.py, Golden Dataset et Ragas)
  └── 8. Validation continue (tests/: 69 tests automatisés et rapport PDF Playwright)
```

---

## Pourquoi ce projet existe

Les modèles de langage actuels injectent des régularités statistiques identifiables dans leurs flux textuels :

*   **Monotonie rythmique** : Le rythme s'avère uniforme, marqué par une variance de longueur de phrase très faible (burstiness minimale) et des découpages systématiques en trois propositions.
*   **Formules préfabriquées** : Le texte accumule des structures prévisibles, notamment de faux contrastes (_non seulement... mais aussi..._), des accroches scénarisées (_plongeons dans_, _il est essentiel de souligner_), des superlatifs imprécis et des métaphores génériques.
*   **Marqueurs invisibles et traçage** : Le flux brut embarque des marqueurs invisibles et des traces techniques, en particulier des points de code Unicode de largeur nulle (`U+200B`, `U+FEFF`), des espaces insécables détournés (`U+00A0`, `U+202F`) et des métadonnées de traçabilité (C2PA, EXIF, XMP).
*   **Structure artificielle** : Le formatage impose des modèles artificiels, alternant listes à puces prévisibles, tirets cadratins redondants et moralisations conclusives isolées sur une ligne.

AI-remover neutralise ces artefacts au travers d'un pipeline d'exécution documenté, sans dégrader ni altérer les données factuelles d'origine.

---

## Fonctionnement du système

Le pipeline de traitement s'exécute en trois étapes successives :

### 1\. Assainissement déterministe (Layer A)

Le module `core/text_unicode.py` inspecte et nettoie le flux textuel sans solliciter de modèle de langage :

*   Suppression des 50 points de code invisibles et artefacts de formatage stéganographique (BOM, séparateurs de variation mongols, caractères de contrôle LTR/RTL).
*   Normalisation des 15 variantes d'espaces exotiques vers l'espace standard ASCII `0x20`.
*   Remplacement systématique des tirets cadratins et demi-cadratins par des points, des virgules ou des parenthèses.

### 2\. Réécriture contextuelle par profil (Layer B)

Le module `core/profiles.py` génère le prompt de calibrage stylistique et applique 25 règles strictes issues des standards éditoriaux :

| Profil | Destination | Ligne directrice |
| --- | --- | --- |
| **Avocat** | Mémos, contrats, consultations | Rigueur doctrinale, exclusion des affirmations non étayées, modalisateurs calibrés. |
| **Analyste** | Notes de synthèse, analyses | Relations de cause à effet directes, priorisation des métriques chiffrées et arbitrage explicite des compromis (_trade-offs_). |
| **Architecte** | Spécifications techniques | Voix active, prise en compte des contraintes réelles d'ingénierie, suppression du jargon abstrait. |
| **Chercheur** | Articles, rapports d'étude | Rigueur méthodologique, séparation stricte entre données vérifiées et hypothèses. |
| **Communicant** | Publications réseaux sociaux | Accroche directe sans titrage formel, mise en page aérée pour mobile, 2 à 3 hashtags ciblés. |
| **Ma propre voix** | Signature personnalisée | Reproduction fidèle de l'échantillon fourni (vocabulaire, syntaxe et rythme). |

Le runtime prend en charge deux modes d'exécution : en local via le binaire Antigravity CLI (`agy -p`) avec segmentation automatique du payload anti-saturation, ou à distance via l'API REST Google Gemini pilotée par `core/ai_bridge.py`.

### 3\. Traçabilité, diff mot-à-mot et rapport PDF (Layer C)

Le module `core/score_stylometry.py` calcule un score de densité synthétique gradué de 0,0 à 1,0, produit un diff interactif et génère un rapport exécutif :

*   Diff visuel mot-à-mot identifiant les suppressions en rouge barré et les reformulations en vert.
*   Rapport exécutif au format PDF A4 généré via Playwright (Chromium headless), regroupant les métriques clés, le registre des tics purgés et le diff complet.
*   Taux de conservation factuelle mesurant la proportion exacte des termes d'origine préservés.
*   Diversité lexicale mesurée par l'indice MATTR (Type-Token Ratio calculé sur des fenêtres glissantes de 50 mots).
*   Burstiness quantifiée par le coefficient de variation de la longueur des phrases.

---

## Formats pris en charge

*   **Texte brut et Markdown** (`.txt`, `.md`) : lecture directe, assainissement et export immédiat.
*   **Documents Microsoft Word** (`.docx`) : extraction de la structure de paragraphes et reconstruction de fichiers Word propres.
*   **Documents PDF** (`.pdf`) : extraction textuelle et génération de PDF mis en page avec pagination automatique.
*   **Rapports d'audit PDF** : export A4 couleur haute fidélité du diff visuel mot-à-mot.
*   **Fichiers images** (`.png`, `.jpg`, `.jpeg`) : décompression mémoire et purge des métadonnées EXIF, C2PA et XMP.

---

## Installation et prérequis

### Prérequis

*   Python 3.10 ou supérieur (testé sur 3.10, 3.11 et 3.12).
*   Le gestionnaire de paquets [uv](https://github.com/astral-sh/uv) (recommandé pour la rapidité) ou `pip`.
*   [Cloudflare Tunnel (`cloudflared`)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) pour le partage distant illimité (optionnel, installé automatiquement par `partager.bat` sous Windows).

### Installation des dépendances

```
uv pip install -r requirements.txt
uv run playwright install chromium
```

Pour installer également les outils de test et de linter :

```
uv pip install -r requirements-dev.txt
```

---

## Guide d'utilisation

### 1\. Démarrage de l'interface graphique

L'application tourne sur Streamlit sur le port dédié `8505` :

```
# Sous Windows (en 1 clic)
launch.bat

# En ligne de commande via uv
uv run streamlit run app.py --server.port 8505
```

Accédez ensuite à l'interface depuis votre navigateur à l'adresse `http://localhost:8505`.

### 2\. Configuration du moteur d'IA

Dans la barre latérale de l'application, choisissez le moteur de traitement :

1.  **Antigravity CLI (Local & sans clé)** : utilise l'exécutable local `agy` déjà authentifié sur votre machine. Aucun envoi de clé API requis.
2.  **Bring Your Own Key / BYOK (API Google Gemini)** : injectez une clé d'API issue de Google AI Studio pour traiter les flux directement sans dépendance binaire locale (modèle `gemini-3-flash-preview` par défaut). Le runtime lit également la clé depuis la variable d'environnement `GEMINI_API_KEY` si elle est définie.

### 3\. Partage d'accès à distance illimité (Cloudflare Tunnel)

Pour exposer l'instance à un collaborateur de manière sécurisée sans configurer de redirection de port sur le routeur :

```
# Sous Windows (en 1 clic avec auto-installation si besoin)
partager.bat

# En ligne de commande (après installation de cloudflared)
# Windows : winget install Cloudflare.cloudflared
# macOS   : brew install cloudflared
cloudflared tunnel --url http://localhost:8505
```

Le terminal génère une URL publique sécurisée `https://xxxx.trycloudflare.com` qui reste active tant que le terminal est ouvert.

### 4\. API hybride interne et Google Cloud Run

Le service FastAPI (`api.py`) expose le moteur sur le port dédié `8506` en local (via `launch_api.bat`, documentation interactive sur `http://127.0.0.1:8506/docs`) et s'exécute sans modification sur Google Cloud Run grâce au `Dockerfile` fourni.

Sur `POST /api/v1/humanize`, un en-tête `X-Gemini-API-Key` permet d'injecter une clé d'API à la volée par requête sans stockage serveur. En l'absence d'en-tête, l'API utilise automatiquement votre CLI Antigravity locale (`gemini-3.8-flash-low`) ou la variable `GEMINI_API_KEY` montée depuis Secret Manager sur Cloud Run.

### 5\. Serveur MCP pour Antigravity CLI (`career-ops`) et Claude Code

Le serveur `mcp_server.py` expose les outils `humanize_text`, `analyze_ai_density` et `clean_invisible_unicode` en mode `stdio` pour Antigravity CLI et Claude Code (`.mcp.json` et configuration globale). Il interroge en priorité l'API interne (`http://127.0.0.1:8506`) et bascule automatiquement sur l'appel direct en mémoire si le démon HTTP est arrêté.

### 6\. Gouvernance LLMOps, Golden Dataset, Ragas et télémétrie

Chaque transformation alimente le journal structuré `logs/telemetry.jsonl` (`core/telemetry.py`), agrégé en direct sur `GET /api/v1/telemetry/summary` (taux de succès, p50, p95, comptage des timeouts). Le banc `evals/run_ragas_eval.py` vérifie sur `evals/golden_dataset.json` la rétention factuelle à 100 %, l'éradication des clichés interdits, l'hygiène Unicode et la similarité Ragas.

La documentation complète de l'architecture hybride, du déploiement Cloud Run, de la configuration MCP et du protocole LLMOps figure dans [docs/GUIDE_API_MCP_LLMOPS.md](docs/GUIDE_API_MCP_LLMOPS.md).

---

## Tests et qualité de code

Le projet intègre 69 tests unitaires et d'intégration validant l'assainissement Unicode, les profils, les métriques stylométriques, l'API hybride FastAPI, le serveur MCP, la télémétrie du Harness, l'évaluateur Golden Dataset/Ragas et le rendu PDF Playwright.

```
# Exécution de la suite complète de tests
uv run --with fastapi --with httpx --with fastmcp pytest -v

# Exécution du banc d'évaluation Golden Dataset et Ragas
uv run python evals/run_ragas_eval.py

# Vérification du linter et du formatage avec Ruff
uvx ruff check .
uvx ruff format --check .
```

Le pipeline d'intégration continue GitHub Actions (`.github/workflows/ci.yml`) valide automatiquement les builds sous Ubuntu et Windows pour les versions Python 3.10, 3.11 et 3.12.

---

## Structure des modules du projet

```
AI-remover/
├── app.py                     # Interface graphique Streamlit (port 8505)
├── api.py                     # API FastAPI hybride locale (port 8506) et Cloud Run
├── mcp_server.py              # Serveur MCP stdio pour Antigravity CLI et Claude Code
├── Dockerfile                 # Image conteneur légère pour Google Cloud Run
├── launch.bat                 # Lanceur Windows Streamlit avec libération du port 8505
├── launch_api.bat             # Lanceur Windows FastAPI avec libération du port 8506
├── partager.bat               # Tunnel de partage distant sécurisé Cloudflare
├── .mcp.json                  # Configuration MCP projet pour Claude Code
├── requirements.txt           # Dépendances de production
├── requirements-dev.txt       # Dépendances de développement et tests
│
├── core/                      # Moteurs de traitement métier et LLMOps
│   ├── text_unicode.py        # Détection et purge des caractères de traçage
│   ├── profiles.py            # Définitions des profils et règles de rédaction
│   ├── score_stylometry.py    # Algorithme stylométrique et journal des choix
│   ├── ai_bridge.py           # Passerelles petits modèles Flash CLI agy et API Gemini
│   ├── evaluator.py           # Portes qualité LLMOps et métriques Ragas
│   ├── telemetry.py           # Télémétrie JSONL structurée et agrégation p50/p95
│   └── file_processor.py      # Traitement documentaire (docx, pdf), Playwright et images
│
├── evals/                     # Banc d'évaluation et non-régression
│   ├── golden_dataset.json    # Corpus de référence métier (faits requis, clichés bannis)
│   └── run_ragas_eval.py      # Exécuteur CLI hors ligne et temps réel (--live)
│
├── docs/
│   └── GUIDE_API_MCP_LLMOPS.md # Documentation technique API, MCP, Cloud Run et LLMOps
│
└── tests/                     # Suite de 69 tests automatisés sous Pytest
    ├── conftest.py            # Isolation automatique des journaux de télémétrie en test
    ├── test_text_unicode.py
    ├── test_profiles.py
    ├── test_score_stylometry.py
    ├── test_file_processor.py
    ├── test_ai_bridge.py
    ├── test_api.py
    ├── test_mcp_server.py
    ├── test_evaluator.py
    └── test_telemetry.py
```

---

## Licence

Ce projet est distribué sous licence MIT.