# Henri: Antigravity Humanizer Studio

[![CI Pipeline](https://github.com/votre-compte/henri/actions/workflows/ci.yml/badge.svg)](https://github.com/votre-compte/henri/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests: Pytest](https://img.shields.io/badge/tests-44%20passed-success)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Henri est une application locale d'assainissement textuel et stylométrique. Elle supprime les signatures statistiques et typographiques des modèles de langage, purge les caractères de traçage invisibles et réécrit les documents selon la posture stylistique de votre choix.

```text
Entrée (Texte / Fichier / Média)
  │
  ├── 1. Purge déterministe (core/text_unicode.py : invisibles, homoglyphes, BOM)
  ├── 2. Calibrage stylistique (core/profiles.py : 6 profils métier sans tics d'IA)
  ├── 3. Passerelle de réécriture (core/ai_bridge.py : CLI Antigravity locale ou API Gemini)
  ├── 4. Diagnostic stylométrique (core/score_stylometry.py : MATTR, burstiness, audit)
  ├── 5. Diff mot-à-mot et export PDF A4 exécutif (Playwright Chromium headless)
  ├── 6. Suite de validation (tests/ : 44 tests unitaires automatisés)
  └── 7. Export natif (.docx, .pdf, .txt, .md, images nettoyées)
```

---

## Pourquoi ce projet existe

Les modèles de langage contemporains produisent des écrits marqués par des récurrences mesurables :

- **Monotonie rythmique** : longueur de phrase quasi constante (faible burstiness) et constructions en trois temps systématiques.
- **Formules préfabriquées** : faux contrastes (*non seulement... mais aussi...*), transitions théâtrales (*plongeons dans*, *il est essentiel de souligner*), superlatifs vagues et métaphores génériques.
- **Marqueurs invisibles et traçage** : injection de points de code Unicode de largeur nulle (`U+200B`, `U+FEFF`), d'espaces insécables de substitution (`U+00A0`, `U+202F`) et de métadonnées de provenance (C2PA, EXIF, XMP).
- **Structure artificielle** : listes à puces avec titres en gras et deux-points, tirets cadratins fréquents et conclusions moralisatrices en une ligne.

Henri corrige ces artefacts à travers une chaîne de traitement documentée et sans perte d'information factuelle.

---

## Comment le système fonctionne

Le traitement repose sur trois étapes successives :

### 1. Assainissement déterministe (Layer A)
Le module `core/text_unicode.py` inspecte et nettoie le texte sans faire appel à un modèle de langage :
- Suppression des 50 points de code invisibles et de formatage stéganographique (BOM, séparateurs de variation mongols, caractères de contrôle LTR/RTL).
- Remplacement des 15 variantes d'espaces exotiques par l'espace standard ASCII `0x20`.
- Élimination intégrale des tirets cadratins (`—`) et demi-cadratins (`–`) au profit de points, virgules ou parenthèses.

### 2. Réécriture contextuelle par profil (Layer B)
Le module `core/profiles.py` génère un prompt d'alignement stylistique et applique 25 règles strictes issues des standards éditoriaux humains :

| Profil | Destination | Ligne directrice |
| :--- | :--- | :--- |
| **Avocat** | Mémos, contrats, consultations | Précision doctrinale, absence d'affirmation gratuite, modalisateurs pondérés. |
| **Analyste** | Notes de synthèse, analyses | Causalités directes, mise en avant des chiffres et des compromis (*trade-offs*). |
| **Architecte** | Spécifications techniques | Voix active, contraintes d'ingénierie réelles, élimination du jargon abstrait. |
| **Chercheur** | Articles, rapports d'étude | Prudence méthodologique, distinction nette entre faits démontrés et hypothèses. |
| **Communicant** | Publications réseaux sociaux | Accroche directe sans titre formel, format mobile aéré, 2 à 3 hashtags ciblés. |
| **Ma propre voix** | Signature humaine personnalisée | Imitation de votre propre échantillon de texte (vocabulaire, syntaxe et rythme). |

L'exécution est assurée soit localement par le binaire Antigravity CLI (`agy -p`) avec découpage automatique anti-saturation, soit à distance par l'API REST Google Gemini via `core/ai_bridge.py`.

### 3. Traçabilité, diff mot-à-mot et rapport PDF (Layer C)
Le module `core/score_stylometry.py` calcule un score de densité synthétique (de 0,0 à 1,0), dresse un diff interactif et génère un rapport exécutif :
- **Diff visuel mot-à-mot** : surlignage immédiat des suppressions (rouge barré) et des reformulations (vert).
- **Rapport exécutif PDF A4** : document imprimable certifié avec cartes KPI, traçabilité des tics purgés et diff complet (Playwright Chromium headless).
- **Taux de conservation factuelle** : calcul de la proportion des termes d'origine préservés.
- **Diversité lexicale (MATTR)** : Type-Token Ratio sur fenêtres glissantes de 50 mots.
- **Burstiness** : coefficient de variation de la longueur des phrases.

---

## Formats pris en charge

- **Texte brut et Markdown** (`.txt`, `.md`) : lecture directe, assainissement et export immédiat.
- **Documents Microsoft Word** (`.docx`) : extraction de la structure de paragraphes et reconstruction de fichiers Word propres.
- **Documents PDF** (`.pdf`) : extraction textuelle et génération de PDF mis en page avec pagination automatique.
- **Rapports d'audit PDF** : export A4 couleur haute fidélité du diff visuel mot-à-mot.
- **Fichiers images** (`.png`, `.jpg`, `.jpeg`) : décompression mémoire et purge des métadonnées EXIF, C2PA et XMP.

---

## Installation et prérequis

### Prérequis
- Python 3.10 ou supérieur (testé sur 3.10, 3.11 et 3.12).
- Le gestionnaire de paquets [uv](https://github.com/astral-sh/uv) (recommandé pour la rapidité) ou `pip`.
- [Cloudflare Tunnel (`cloudflared`)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) pour le partage distant illimité (optionnel, installé automatiquement par `partager.bat` sous Windows).

### Installation des dépendances

```bash
uv pip install -r requirements.txt
uv run playwright install chromium
```

Pour installer également les outils de test et de linter :

```bash
uv pip install -r requirements-dev.txt
```

---

## Guide d'utilisation

### 1. Démarrage de l'interface graphique

L'application tourne sur Streamlit sur le port dédié `8505` :

```bash
# Sous Windows (en 1 clic)
launch.bat

# En ligne de commande via uv
uv run streamlit run app.py --server.port 8505
```

Ouvrez ensuite votre navigateur sur `http://localhost:8505`.

### 2. Configuration du moteur d'IA

Dans la barre latérale de l'application, choisissez le moteur de traitement :
1. **Antigravity CLI (Local & sans clé)** : utilise l'exécutable local `agy` déjà authentifié sur votre machine. Aucun envoi de clé API requis.
2. **Bring Your Own Key / BYOK (API Google Gemini)** : saisissez votre propre clé d'API gratuite issue de Google AI Studio pour exécuter les réécritures directement sans dépendance locale (modèle `gemini-3-flash-preview` par défaut). L'application récupère également la clé depuis la variable d'environnement `GEMINI_API_KEY` si elle est définie.

### 3. Partage d'accès à distance illimité (Cloudflare Tunnel)

Pour donner un accès sécurisé et sans limite de temps à un collaborateur sans ouvrir de port sur votre routeur :

```bash
# Sous Windows (en 1 clic avec auto-installation si besoin)
partager.bat

# En ligne de commande (après installation de cloudflared)
# Windows : winget install Cloudflare.cloudflared
# macOS   : brew install cloudflared
cloudflared tunnel --url http://localhost:8505
```

Le terminal génère une URL publique sécurisée `https://xxxx.trycloudflare.com` qui reste active tant que le terminal est ouvert.

---

## Tests et qualité de code

Le projet intègre une suite de 44 tests unitaires couvrant les modules d'assainissement, les profils, les algorithmes stylométriques, l'export PDF Playwright et les gestionnaires de fichiers.

```bash
# Exécution de la suite de tests
uv run pytest -v

# Vérification du typage et des règles de linter avec Ruff
uvx ruff check .

# Contrôle du formatage de code
uvx ruff format --check .
```

Les flux d'intégration continue GitHub Actions sont définis dans `.github/workflows/ci.yml` et s'exécutent automatiquement sous Ubuntu et Windows pour Python 3.10, 3.11 et 3.12.

---

## Structure des modules du projet

```text
HENRI/
├── app.py                     # Interface graphique Streamlit et orchestration
├── launch.bat                 # Lanceur rapide Windows (port 8505)
├── partager.bat               # Tunnel de partage distant sécurisé
├── requirements.txt           # Dépendances de production
├── requirements-dev.txt       # Dépendances de développement et tests
├── .gitignore                 # Règles d'exclusion des caches et fichiers personnels
├── .github/workflows/ci.yml   # Définition du pipeline CI/CD GitHub Actions
│
├── core/                      # Moteurs de traitement métier
│   ├── text_unicode.py        # Détection et purge des caractères de traçage
│   ├── profiles.py            # Définitions des profils et 25 règles de rédaction
│   ├── score_stylometry.py    # Algorithme stylométrique et journal des choix
│   ├── ai_bridge.py           # Connecteurs CLI Antigravity et API Gemini
│   └── file_processor.py      # Traitement documentaire (docx, pdf), Playwright et images
│
└── tests/                     # Suite de 44 tests unitaires automatisés
    ├── __init__.py
    ├── test_text_unicode.py   # Validation du nettoyage Unicode et homoglyphes
    ├── test_profiles.py       # Validation des 6 profils et génération des prompts
    ├── test_score_stylometry.py # Validation des métriques MATTR et burstiness
    ├── test_file_processor.py # Validation des formats docx, pdf, Playwright diff, md, txt, images
    └── test_ai_bridge.py      # Validation des passerelles CLI agy et API Gemini
```

---

## Licence

Ce projet est distribué sous licence MIT.
