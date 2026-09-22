# AI-remover: Supprime les traces d'IA dans vos textes, docs & images + tracking des modifs

[![CI Pipeline](https://img.shields.io/badge/CI-passing-brightgreen?logo=githubactions&logoColor=white)](https://github.com/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Tests: Pytest](https://img.shields.io/badge/tests-46%20passed-success?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Mobile Responsive](https://img.shields.io/badge/Mobile-responsive-blueviolet?logo=googlechrome&logoColor=white)](https://share.streamlit.io)
[![Antigravity Engine](https://img.shields.io/badge/Engine-Antigravity%20CLI-orange?logo=google&logoColor=white)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Caro Heymes](https://img.shields.io/badge/Recommand%C3%A9%20par-Caro%20Heymes%20%F0%9F%9A%80-7928CA.svg)](https://www.linkedin.com/in/caroline-heymes/)

AI-remover s'exécute en local ou sur le cloud pour assainir les textes et corriger leurs métriques stylométriques. Le moteur supprime les signatures statistiques et typographiques générées par les modèles de langage, purge les caractères de traçage invisibles dans le flux Unicode et réécrit les documents selon le profil stylistique sélectionné.

```text
Entrée (Texte / Fichier / Média)
  │
  ├── 1. Purge déterministe (core/text_unicode.py : invisibles, homoglyphes, BOM)
  ├── 2. Calibrage stylistique (core/profiles.py : 6 profils métier sans tics d'IA)
  ├── 3. Passerelle de réécriture (core/ai_bridge.py : CLI Antigravity locale ou API Gemini)
  ├── 4. Diagnostic stylométrique (core/score_stylometry.py : MATTR, burstiness, audit)
  ├── 5. Diff mot-à-mot et export PDF A4 exécutif (Playwright Chromium headless)
  ├── 6. Suite de validation (tests/ : 46 tests unitaires automatisés)
  └── 7. Export natif (.docx, .pdf, .txt, .md, images nettoyées)
```

---

## Pourquoi ce projet existe

Les modèles de langage actuels injectent des régularités statistiques identifiables dans leurs flux textuels :

- **Monotonie rythmique** : Le rythme s'avère uniforme, marqué par une variance de longueur de phrase très faible (burstiness minimale) et des découpages systématiques en trois propositions.
- **Formules préfabriquées** : Le texte accumule des structures prévisibles, notamment de faux contrastes (*non seulement... mais aussi...*), des accroches scénarisées (*plongeons dans*, *il est essentiel de souligner*), des superlatifs imprécis et des métaphores génériques.
- **Marqueurs invisibles et traçage** : Le flux brut embarque des marqueurs invisibles et des traces techniques, en particulier des points de code Unicode de largeur nulle (`U+200B`, `U+FEFF`), des espaces insécables détournés (`U+00A0`, `U+202F`) et des métadonnées de traçabilité (C2PA, EXIF, XMP).
- **Structure artificielle** : Le formatage impose des modèles artificiels, alternant listes à puces prévisibles, tirets cadratins redondants et moralisations conclusives isolées sur une ligne.


AI-remover neutralise ces artefacts au travers d'un pipeline d'exécution documenté, sans dégrader ni altérer les données factuelles d'origine.

---

## Fonctionnement du système

Le pipeline de traitement s'exécute en trois étapes successives :

### 1. Assainissement déterministe (Layer A)
Le module `core/text_unicode.py` inspecte et nettoie le flux textuel sans solliciter de modèle de langage :
- Suppression des 50 points de code invisibles et artefacts de formatage stéganographique (BOM, séparateurs de variation mongols, caractères de contrôle LTR/RTL).
- Normalisation des 15 variantes d'espaces exotiques vers l'espace standard ASCII `0x20`.
- Remplacement systématique des tirets cadratins et demi-cadratins par des points, des virgules ou des parenthèses.

### 2. Réécriture contextuelle par profil (Layer B)
Le module `core/profiles.py` génère le prompt de calibrage stylistique et applique 25 règles strictes issues des standards éditoriaux :

| Profil | Destination | Ligne directrice |
| :--- | :--- | :--- |
| **Avocat** | Mémos, contrats, consultations | Rigueur doctrinale, exclusion des affirmations non étayées, modalisateurs calibrés. |
| **Analyste** | Notes de synthèse, analyses | Relations de cause à effet directes, priorisation des métriques chiffrées et arbitrage explicite des compromis (*trade-offs*). |
| **Architecte** | Spécifications techniques | Voix active, prise en compte des contraintes réelles d'ingénierie, suppression du jargon abstrait. |
| **Chercheur** | Articles, rapports d'étude | Rigueur méthodologique, séparation stricte entre données vérifiées et hypothèses. |
| **Communicant** | Publications réseaux sociaux | Accroche directe sans titrage formel, mise en page aérée pour mobile, 2 à 3 hashtags ciblés. |
| **Ma propre voix** | Signature personnalisée | Reproduction fidèle de l'échantillon fourni (vocabulaire, syntaxe et rythme). |

Le runtime prend en charge deux modes d'exécution : en local via le binaire Antigravity CLI (`agy -p`) avec segmentation automatique du payload anti-saturation, ou à distance via l'API REST Google Gemini pilotée par `core/ai_bridge.py`.

### 3. Traçabilité, diff mot-à-mot et rapport PDF (Layer C)
Le module `core/score_stylometry.py` calcule un score de densité synthétique gradué de 0,0 à 1,0, produit un diff interactif et génère un rapport exécutif :
- Diff visuel mot-à-mot identifiant les suppressions en rouge barré et les reformulations en vert.
- Rapport exécutif au format PDF A4 généré via Playwright (Chromium headless), regroupant les métriques clés, le registre des tics purgés et le diff complet.
- Taux de conservation factuelle mesurant la proportion exacte des termes d'origine préservés.
- Diversité lexicale mesurée par l'indice MATTR (Type-Token Ratio calculé sur des fenêtres glissantes de 50 mots).
- Burstiness quantifiée par le coefficient de variation de la longueur des phrases.

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

Accédez ensuite à l'interface depuis votre navigateur à l'adresse `http://localhost:8505`.

### 2. Configuration du moteur d'IA

Dans la barre latérale de l'application, choisissez le moteur de traitement :
1. **Antigravity CLI (Local & sans clé)** : utilise l'exécutable local `agy` déjà authentifié sur votre machine. Aucun envoi de clé API requis.
2. **Bring Your Own Key / BYOK (API Google Gemini)** : injectez une clé d'API issue de Google AI Studio pour traiter les flux directement sans dépendance binaire locale (modèle `gemini-3-flash-preview` par défaut). Le runtime lit également la clé depuis la variable d'environnement `GEMINI_API_KEY` si elle est définie.

### 3. Partage d'accès à distance illimité (Cloudflare Tunnel)

Pour exposer l'instance à un collaborateur de manière sécurisée sans configurer de redirection de port sur le routeur :

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

Le projet intègre 44 tests unitaires validant les modules d'assainissement, les profils, les métriques stylométriques, le moteur de rendu PDF Playwright et la gestion des fichiers.

```bash
# Exécution de la suite de tests
uv run pytest -v

# Vérification du typage et des règles de linter avec Ruff
uvx ruff check .

# Contrôle du formatage de code
uvx ruff format --check .
```


Le pipeline d'intégration continue GitHub Actions (`.github/workflows/ci.yml`) valide automatiquement les builds sous Ubuntu et Windows pour les versions Python 3.10, 3.11 et 3.12.

---

## Structure des modules du projet

```text
AI-remover/
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
└── tests/                     # Suite de 46 tests unitaires automatisés
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
