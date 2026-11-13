# Document de reprise du projet AI-Remover (API hybride, MCP et LLMOps)

Ce document consigne l'état technique complet du dépôt `C:\Users\Admin\Documents\HENRI` et son raccordement au système de candidatures `C:\Users\Admin\Documents\career-ops\career-ops` au 12 novembre 2026. Il permet de reprendre le développement, l'exploitation locale ou le déploiement Cloud Run sans perte de contexte.

## Contexte et correctifs initiaux

### Résolution du dépassement de délai de 180 secondes sur Antigravity CLI

L'interface Streamlit tombait en erreur (`Délai d'attente dépassé (180s) lors de l'appel à Antigravity CLI`) lors de l'humanisation de textes longs. L'analyse des journaux a montré que `core/ai_bridge.py` invoquait `agy -p` sans option `--model`, ce qui routait la requête vers le modèle global lourd configuré par défaut (`Gemini 4 Carbon High`) sur un prompt supérieur à 10 000 caractères.

Le pont `core/ai_bridge.py` interroge désormais dynamiquement la commande `agy models` via `get_available_agy_models()` et ne retient que les petits modèles rapides contenant `flash` (exclusion stricte de `carbon`, `argon`, `sonnet` et `opus`). Le modèle par défaut est fixé sur `gemini-3.8-flash-low`, qui traite le même volume en environ 8 à 11 secondes de bout en bout. Si Google déprécie ou retire un identifiant de modèle de la CLI (`model not found` ou `unknown model` dans `stderr`), `humanize_text` relance automatiquement l'appel sans drapeau `--model` pour éviter toute interruption de service. L'interface `app.py` expose ce sélecteur de modèles rapides dans la barre latérale.

### Libération automatique des ports locaux 8505 et 8506

Un processus Python orphelin bloquait le lancement de Streamlit sur le port `8505` (`Port 8505 is not available`). Le script `launch.bat` inspecte maintenant la table réseau (`netstat -aon | findstr :8505 | findstr LISTENING`) et termine tout processus actif sur ce port avant de démarrer l'interface. La même hygiène réseau a été intégrée dans `launch_api.bat` pour le port `8506` dédié à l'API interne.

## Architecture hybride mise en place

L'application fonctionne désormais selon trois canaux complémentaires qui partagent le même moteur métier (`core/`).

### Interface locale et API interne sur le poste de travail

L'interface Streamlit tourne sur `http://localhost:8505` tandis que le serveur FastAPI (`api.py`) écoute sur `http://127.0.0.1:8506`. En l'absence de clé API externe, tous deux exploitent la session locale Antigravity CLI (`agy`) sans facturation par jeton additionnelle.

### Déploiement externe sans état sur Google Cloud Run

Sur Cloud Run, la CLI locale `agy` n'existe pas. L'endpoint `POST /api/v1/humanize` accepte une clé Gemini injectée à la volée par l'appelant dans l'en-tête HTTP `X-Gemini-API-Key` (ou dans le champ JSON `api_key`) sans jamais la persister sur disque ni dans les journaux. En repli serveur, l'API lit la variable d'environnement `GEMINI_API_KEY` montée depuis Google Cloud Secret Manager. Un `Dockerfile` basé sur `python:3.12-slim` est prêt à la racine du dépôt.

### Serveur MCP universel pour Antigravity et Claude Code

Le serveur `mcp_server.py` expose trois outils sur le protocole MCP (`stdio`): `humanize_text`, `analyze_ai_density` et `clean_invisible_unicode`. Lorsqu'il reçoit un appel d'agent, il interroge en priorité l'API interne sur `http://127.0.0.1:8506` (`transport: "http_api"`). Si le démon FastAPI local est éteint, `mcp_server.py` bascule automatiquement en exécution directe Python dans le processus courant (`transport: "direct_core"`), ce qui garantit une disponibilité permanente dans les sessions d'agents.

## Inventaire des fichiers créés et modifiés

### Dépôt principal AI-Remover (`C:\Users\Admin\Documents\HENRI`)

| Fichier | État | Rôle technique |
| :--- | :--- | :--- |
| `core/ai_bridge.py` | Modifié | Filtrage dynamique des modèles `flash`, repli anti-dépréciation, fermeture de `stdin` (`DEVNULL`) et instrumentation télémétrique. |
| `core/telemetry.py` | Créé | Journalisation structurée JSONL (`logs/telemetry.jsonl`) et calcul des centiles de latence (`p50`, `p95`), taux de succès et baisse de score IA. |
| `core/evaluator.py` | Créé | Évaluation déterministe (rétention factuelle, éradication des tics IA, hygiène Unicode) et métriques Ragas hors-LLM (`NonLLMStringSimilarity`, `RougeScore`, repli lexical F1). |
| `core/__init__.py` | Modifié | Export public des fonctions de modèles `agy`, de télémétrie et d'évaluation. |
| `app.py` | Modifié | Ajout du menu déroulant des petits modèles locaux `agy` et passage de `source="ui"` à la télémétrie. |
| `api.py` | Créé | Serveur REST FastAPI hybride v1.2.0 (local `agy`, Cloud Run via `X-Gemini-API-Key` et verrouillage `Authorization: Bearer` via `AI_REMOVER_API_TOKEN`) sur le port `8506`. |
| `mcp_server.py` | Créé | Serveur FastMCP (`stdio`) exposant `humanize_text`, `analyze_ai_density` et `clean_invisible_unicode` avec support Bearer et repli automatique API vers coeur Python. |
| `.mcp.json` | Créé | Configuration MCP locale du dépôt `HENRI`. |
| `launch.bat` | Modifié | Nettoyage automatique du port `8505` avant lancement de Streamlit. |
| `launch_api.bat` | Créé | Nettoyage automatique du port `8506` et lancement du serveur Uvicorn local. |
| `Dockerfile` / `.dockerignore` | Créés | Image conteneur `python:3.12-slim` légère sur le port `8080` avec exclusion stricte des environnements virtuels, journaux et tests. |
| `deploy_cloud_run.ps1` | Créé | Script PowerShell de déploiement Cloud Run (`min-instances=0`, `max-instances=2`, `512Mi`, purge Artifact Registry à 2 images, jeton Bearer aléatoire). |
| `evals/golden_dataset.json` | Créé | Jeu d'étalonnage bilingue v1.1.0 de 14 cas métiers réalistes (9 FR + 5 EN sur `architecte`, `avocat`, `analyste`) avec entités critiques et expressions interdites. |
| `evals/run_ragas_eval.py` | Créé | Harnais CLI d'exécution des évaluations hors-ligne et en conditions réelles (`--live`), générant `logs/eval_report.json`. |
| `docs/GUIDE_API_MCP_LLMOPS.md` | Créé | Documentation technique complète (architecture, API REST, Cloud Run, MCP, `career-ops` et LLMOps). |
| `README.md` | Modifié | Référencement de l'architecture hybride, des outils MCP, de la suite d'évaluation et du guide technique. |
| `requirements.txt` / `requirements-dev.txt` | Modifiés | Ajout de `fastapi`, `uvicorn`, `fastmcp` et `httpx`. |
| `tests/conftest.py` | Créé | Isolation automatique du fichier de télémétrie vers `tmp_path` pendant les tests unitaires. |
| `tests/test_*.py` | Créés / Modifiés | Couverture complète (`test_api.py`, `test_mcp_server.py`, `test_evaluator.py`, `test_telemetry.py`, `test_ai_bridge.py`, `test_profiles.py`), soit 71 tests passants. |

Note importante sur l'arbre Git local: les fichiers `core/profiles.py`, `core/score_stylometry.py` et `tests/test_profiles.py` contenaient déjà des modifications locales non commitées avant cette session. Ces modifications ont été intégralement préservées.

### Dépôt `career-ops` et configurations globales des agents

| Emplacement | Rôle dans l'intégration |
| :--- | :--- |
| `C:\Users\Admin\Documents\career-ops\career-ops\.agents\plugins\ai-remover\plugin.json` | Manifeste du plugin MCP `ai-remover` pour les sessions Antigravity ouvertes sur `career-ops`. |
| `C:\Users\Admin\Documents\career-ops\career-ops\.agents\plugins\ai-remover\mcp_config.json` | Commande de lancement `stdio` du serveur MCP via l'environnement Python dédié. |
| `C:\Users\Admin\.gemini\config\mcp_config.json` | Enregistrement global du serveur `ai-remover` dans Antigravity CLI (`agy mcp list`). |
| `C:\Users\Admin\Documents\career-ops\career-ops\.mcp.json` | Déclaration MCP de projet pour Claude Code dans le dossier `career-ops`. |
| `C:\Users\Admin\Documents\career-ops\career-ops\.claude\settings.json` | Pré-autorisation (`permissions.allow`) des 3 outils `mcp__ai-remover__*` sans invite de confirmation bloquante. |
| `C:\Users\Admin\.claude.json` | Enregistrement global utilisateur dans Claude Code (`claude mcp list` affiche `Connected`). |
| `C:\Users\Admin\Documents\career-ops\career-ops\modes\_custom.md` | Règle persistante imposant le passage par `humanize_text` et `analyze_ai_density` avant la génération PDF des lettres de motivation, dans le respect strict de `DATA_CONTRACT.md`. |

## Commandes opérationnelles de reprise

### Démarrer les services locaux

Pour lancer l'interface graphique Streamlit sur `http://localhost:8505`:

```powershell
C:\Users\Admin\Documents\HENRI\launch.bat
```

Pour lancer l'API interne FastAPI sur `http://127.0.0.1:8506` (documentation interactive sur `http://127.0.0.1:8506/docs`):

```powershell
C:\Users\Admin\Documents\HENRI\launch_api.bat
```

Pour vérifier l'état de l'API interne et la télémétrie en ligne de commande:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8506/health"
Invoke-RestMethod -Uri "http://127.0.0.1:8506/api/v1/telemetry/summary"
```

### Vérifier le câblage MCP dans Antigravity et Claude Code

Toute session ouverte avant l'enregistrement du serveur MCP doit être redémarrée pour charger les outils. Les deux commandes suivantes permettent de contrôler l'état du connecteur:

```powershell
agy mcp list
claude mcp list
```

### Utiliser le MCP pour les lettres de motivation dans `career-ops`

Ouvrir un nouveau terminal dans `C:\Users\Admin\Documents\career-ops\career-ops`, lancer `claude` ou `agy`, puis appeler le workflow habituel:

```text
/career-ops cover <slug-entreprise>
```

Grâce aux instructions ajoutées dans `modes/_custom.md`, l'agent rédige d'abord les quatre blocs de la lettre (`opening`, `profile_intro`, `problems_section`, `closing`), les purifie via `humanize_text` avec `profile_key="architecte"` et `model="gemini-3.8-flash-low"`, vérifie que `analyze_ai_density` renvoie un score inférieur ou égal à 25 avec zéro caractère invisible et zéro tiret cadratin, puis exécute `node generate-cover-letter.mjs` pour produire le PDF dans `output/cover-letters/`. Pour cloner le style d'une ancienne lettre personnelle, il suffit de passer son texte brut dans l'argument `custom_sample` de `humanize_text`.

### Exécuter les contrôles qualité, tests et évaluations Ragas

Depuis `C:\Users\Admin\Documents\HENRI`, exécuter le linter Ruff et la suite complète des 71 tests unitaires et d'intégration:

```powershell
uv run --with ruff ruff check .
uv run --with fastapi --with httpx --with fastmcp pytest -q
```

Pour lancer le harnais d'évaluation sur le Golden Dataset bilingue hors-ligne (14 cas FR/EN):

```powershell
uv run python evals/run_ragas_eval.py
```

Pour lancer un test de non-régression bout en bout en conditions réelles sur `gemini-3.8-flash-low` et mettre à jour `logs/eval_report.json`:

```powershell
uv run python evals/run_ragas_eval.py --live --limit 3 --model gemini-3.8-flash-low
```

### Déployer l'API externe sécurisée sur Google Cloud Run

Après authentification GCP (`gcloud auth login`), exécuter depuis `C:\Users\Admin\Documents\HENRI`:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy_cloud_run.ps1 -ProjectId <PROJECT_ID>
```

Ce script configure une purge automatique Artifact Registry conservant uniquement les 2 dernières images, génère un jeton `AI_REMOVER_API_TOKEN` aléatoire requis dans `Authorization: Bearer <token>`, plafonne le service à `min-instances=0` et `max-instances=2` (`512Mi`) et ne stocke aucune clé Gemini sur le serveur.
