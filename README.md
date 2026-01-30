# 🎵 Musique - Projet de Tracking Musical

> ⚠️ **PROOF OF CONCEPT** - Ce projet est une démonstration de faisabilité technique explorant l'intégration d'APIs musicales (Last.fm, Spotify, Discogs) avec enrichissement IA (EurIA/Qwen3) pour le tracking, l'analyse et la présentation de données musicales personnelles.

## 🗺️ Roadmap et Plan d'Évolution

**📌 Nouveau**: Consultez le **[ROADMAP.md](ROADMAP.md)** pour la vision stratégique complète du projet avec:
- 📊 Analyse des modifications récentes
- 🎯 Problèmes identifiés et issues en cours
- 📅 Plans d'action court, moyen et long terme
- 🚀 Recommandations prioritaires
- 📈 Métriques de succès et KPIs

## 🎯 État du Projet

**Version actuelle : 4.0.0** (Simplification - Last.fm uniquement - 30 janvier 2026)

**Statut :** ✅ Fonctionnel • 🧪 Expérimental • 📊 En évolution

### Fonctionnalités Validées
- ✅ Surveillance Last.fm avec enrichissement images publiques (Spotify)
- ✅ Import automatique collection Discogs avec résumés IA
- ✅ Interface Web Streamlit pour gestion collection
- ✅ Génération de présentations musicales (haïkus) via IA
- ✅ Vue Timeline pour visualisation horaire des écoutes
- ✅ Navigation temporelle horizontale avec alternance couleurs
- ✅ Modes compact/détaillé pour affichage Timeline
- ✅ Génération de playlists intelligentes basée sur patterns d'écoute
- ✅ 7 algorithmes de génération (sessions, correlations, flow, temps, albums, redécouverte, IA)
- ✅ Export playlists multi-formats (JSON, M3U, CSV, TXT)
- ✅ Déduplication automatique des doublons dans playlists
- ✅ Analyse patterns d'écoute (sessions, corrélations, statistiques)
- ✅ Cross-référence films/soundtracks via projet Cinéma
- ✅ Système de cache et retry pour robustesse API
- ✅ Services partagés (`spotify_service`, `metadata_cleaner`, `ai_service`)
- ✅ Infrastructure de tests complète
- ✅ Constantes centralisées dans `constants.py`
- ✅ Service IA centralisé pour enrichissement albums
- ✅ Génération automatique d'informations pour chaque album détecté
- ✅ Fallback intelligent Discogs → IA (80%+ optimisation)
- ✅ Journal technique IA quotidien avec rétention 24h
- ✅ Vue "🤖 Journal IA" dans l'interface GUI

### 📦 Nouveautés v4.0.0 (30 janvier 2026)

**🎯 Simplification Majeure**:
- ❌ **Suppression Roon API**: Interface Roon retirée (pas assez robuste)
- ❌ **Suppression CLI**: Module CLI retiré (trop complexe)
- ✅ **Focus Last.fm**: Conservation uniquement de la détection Last.fm
- ✅ **Renommage Interface**: "Journal d'écoute Last.fm" et "Timeline Last.fm"
- ✅ **Code simplifié**: -6000+ lignes de code retirées
- ✅ **Dépendances réduites**: Suppression de `roonapi`, `rich`, `click`, `prompt-toolkit`

**Objectif**: Retour à un logiciel plus simple et maintenable.
```

👉 **Voir les détails**: 
- [issues/ISSUE-59-IMPLEMENTATION-PROPOSAL.md](issues/ISSUE-59-IMPLEMENTATION-PROPOSAL.md) - Proposition complète
- [issues/ISSUE-59-PHASE1-REPORT.md](issues/ISSUE-59-PHASE1-REPORT.md) - Rapport Phase 1
- [src/cli/README.md](src/cli/README.md) - Documentation CLI

### 📦 Nouveautés v3.3.1 (27 janvier 2026)

**🎵 Génération de Playlists Intelligentes** (Issue #19):
- `generate-playlist.py`: Générateur de playlists basé sur patterns d'écoute (800+ lignes)
  - **7 algorithmes de génération**:
    - `top_sessions`: Pistes des sessions d'écoute les plus longues
    - `artist_correlations`: Artistes souvent écoutés ensemble
    - `artist_flow`: Transitions naturelles entre artistes
    - `time_based`: Pistes selon périodes temporelles (peak hours, weekend)
    - `complete_albums`: Albums écoutés en entier
    - `rediscovery`: Pistes aimées mais non écoutées récemment
    - `ai_generated`: 🆕 Génération par IA basée sur un prompt utilisateur
  - **Export multi-formats**: JSON, M3U, CSV, TXT (instructions Roon)
  - **Intégration scheduler**: Génération automatique planifiée
  - **Configuration**: Via `roon-config.json` (type, fréquence, formats, prompt IA)

**🔧 Déduplication Automatique** (Issue #38, v1.2.0):
- Détection et suppression automatique des doublons dans playlists
- Normalisation par (artiste + titre + album)
- Ignore variations casse et espaces
- Affichage nombre doublons supprimés

**🕐 Correction Timezone** (Issue #32):
- Fix décalage horaire UTC → heure locale
- 4 corrections (chk-roon.py, chk-last-fm.py)
- Impact: Journal Roon, Journal IA, logs quotidiens
- Ajout tests timezone (test_timestamp_fix.py, 5 tests)
- Script vérification verify_timezone_fix.py

**🧪 Tests et Documentation**:
- +5 tests timezone (228 tests au total, +2.2%)
- Documentation: TIMEZONE-FIX-SUMMARY.md, docs/FIX-TIMEZONE-ISSUE-32.md
- Intégration dans generate-playlist.py documentée

👉 **Voir les détails**: README-GENERATE-PLAYLIST.md (à créer)

### 📦 Nouveautés v3.3.0 (27 janvier 2026)

**🤖 Intégration IA pour Enrichissement Automatique**:
- `ai_service.py`: Service centralisé EurIA API (280 lignes)
  - Génération descriptions d'albums (500 caractères max)
  - Fallback intelligent Discogs → IA
  - Retry automatique avec gestion d'erreurs
  - Configuration via `.env` (URL, bearer, max_attempts)

**📊 Enrichissement Automatique des Tracks**:
- Nouveau champ `ai_info` dans `chk-roon.json`
- Génération pour tous les albums détectés (Roon + Last.fm)
- Priorité Discogs (80%+ hits) pour réduire appels API
- Support stations radio si album identifié

**📝 Journal Technique IA**:
- Logs quotidiens: `output/ai-logs/ai-log-YYYY-MM-DD.txt`
- Format structuré (timestamp, artiste, album, info)
- Nettoyage automatique > 24h
- ~10-50 KB par jour pour 50 albums

**🎨 Interface GUI Enrichie**:
- Expandeurs "🤖 Info IA" dans Journal Roon
- Nouvelle vue "🤖 Journal IA" avec sélection de fichiers
- Affichage formaté des entrées quotidiennes
- Compteur d'albums traités par jour

**🧪 Tests et Documentation**:
- `test_ai_service.py`: Script de tests manuels (à convertir en tests pytest)
- `issues/ISSUE-21-IMPLEMENTATION.md`: Rapport d'implémentation complet
- `docs/AI-INTEGRATION.md`: Guide technique

👉 **Voir les détails**: [issues/ISSUE-21-IMPLEMENTATION.md](issues/ISSUE-21-IMPLEMENTATION.md)

### 📦 Nouveautés v3.1.0 (24 janvier 2026)

**🔧 Refactoring Majeur**: Création du module `src/services/`
- `spotify_service.py`: Service Spotify centralisé (560 lignes) avec cache, retry, timeouts
- `metadata_cleaner.py`: Fonctions de nettoyage métadonnées (240 lignes)
- `constants.py`: 100+ constantes centralisées (URLs, timeouts, seuils)

**🧪 Infrastructure de Tests Complète**:
- **162 tests unitaires** avec pytest (~2034 lignes de code)
- **91% de couverture** pour modules testés
- **test_spotify_service.py**: 49 tests, 88% couverture
- **test_constants.py**: 57 tests, 100% couverture
- **test_metadata_cleaner.py**: 27 tests, ~95% couverture
- **test_scheduler.py**: 29 tests, ~90% couverture (ajouté v3.2.0)
- Fixtures réutilisables dans `conftest.py`
- Documentation complète dans `src/tests/README.md`

**🐛 Corrections**:
- Suppression imports dupliqués (`generate-haiku.py`, `chk-last-fm.py`)
- Amélioration gestion d'erreurs avec logging structuré
- Ajout timeouts sur tous les appels HTTP

**📚 Documentation**:
- `docs/IMPROVEMENTS-v3.1.0.md`: Guide détaillé des améliorations
- `ANALYSE-COMPLETE-v3.1.0.md`: Analyse complète + recommandations futures

👉 **Voir le guide complet**: [ANALYSE-COMPLETE-v3.1.0.md](ANALYSE-COMPLETE-v3.1.0.md)

### 🚀 Pistes d'Amélioration Prioritaires

> 📌 **Voir**: [ROADMAP.md](ROADMAP.md) pour le plan d'évolution détaillé à court (0-3 mois), moyen (3-12 mois) et long terme (12+ mois)

#### 📊 **1. Base de données relationnelle**
Remplacer les fichiers JSON par SQLite ou PostgreSQL pour :
- Requêtes plus rapides et complexes
- Gestion de transactions ACID
- Support de requêtes SQL avancées (agrégations, jointures)
- Indexation pour performance sur grandes collections (>10 000 pistes)
- Gestion concurrence multi-utilisateurs

#### 🎯 **2. Déduplication intelligente**
Implémenter un système de matching avancé :
- Algorithme de similarité de chaînes (Levenshtein, fuzzy matching)
- Détection albums identiques avec orthographes variables
- Normalisation unicode (accents, diacritiques)
- Gestion des rééditions/remasters (même album, dates différentes)
- Dashboard de gestion des doublons potentiels

#### 📈 **3. Analytics avancées**
Enrichir l'analyse des patterns d'écoute :
- Visualisations interactives (Plotly, matplotlib)
- Prédiction des goûts musicaux (ML clustering)
- Détection de nouvelles tendances d'écoute
- Recommandations basées sur historique (système de recommandation)
- Export vers Tableau/PowerBI pour dashboards avancés

#### 🌐 **4. API REST publique**
Créer une API RESTful avec FastAPI :
- Endpoints pour consultation collection (`/albums`, `/artists`)
- Webhooks pour notifications temps réel
- Rate limiting et authentification OAuth2
- Documentation OpenAPI/Swagger automatique
- Support GraphQL pour requêtes flexibles

#### 🎨 **5. Interface Web améliorée**
Moderniser l'interface Streamlit ou migrer vers :
- React/Vue.js pour SPA responsive
- Lecteur audio intégré (preview Spotify)
- Édition batch (multi-sélection)
- Glisser-déposer pour upload covers custom
- Mode sombre et thèmes personnalisables
- PWA (Progressive Web App) pour usage mobile

#### 🔐 **6. Sécurité et multi-utilisateurs**
Implémenter une authentification robuste :
- Login/Register avec JWT tokens
- Gestion de rôles (admin, viewer, editor)
- Isolation des collections par utilisateur
- Chiffrement des credentials API
- Logs d'audit des modifications

#### ☁️ **7. Déploiement cloud**
Containeriser et déployer sur infrastructure cloud :
- Docker + docker-compose pour portabilité
- Déploiement sur AWS/GCP/Azure (Container Apps)
- CI/CD avec GitHub Actions
- Monitoring avec Prometheus/Grafana
- Backups automatiques S3/Azure Blob
- CDN pour images (CloudFront, Cloudflare)

#### 🎵 **8. Intégration musicale étendue**
Connecter plus de sources musicales :
- Apple Music API (collection iCloud)
- YouTube Music API
- Bandcamp (achats, wishlist)
- SoundCloud (likes, playlists)
- Tidal, Qobuz (haute résolution)
- Synchronisation bidirectionnelle entre services

#### 🤖 **9. Intelligence artificielle avancée**
Exploiter davantage l'IA pour :
- Génération automatique de playlists thématiques
- Classification automatique par mood/genre (ML)
- Détection de morceaux similaires (audio fingerprinting)
- Reconnaissance vocale pour commandes
- Chatbot musical conversationnel (RAG sur collection)
- Analyse sentimentale des paroles

#### 📱 **10. Applications mobiles natives**
Développer des apps iOS/Android :
- Flutter ou React Native pour cross-platform
- Notifications push pour nouvelles lectures
- Widget home screen avec statistiques
- Reconnaissance audio Shazam-like
- Mode offline avec sync différée
- Intégration CarPlay/Android Auto

#### 🔄 **11. Export et interopérabilité**
Ajouter des formats d'export standardisés :
- Export JSPF (playlists JSON)
- Export MusicBrainz ID mappings
- Export vers formats DJ (Rekordbox, Serato)
- Import depuis iTunes/Winamp XML
- Compatibilité avec tags ID3v2
- Export PDF de catalogue enrichi

#### ⚡ **12. Performance et scalabilité**
Optimiser pour grandes collections :
- Lazy loading et pagination côté serveur
- Compression images avec WebP
- Cache Redis pour requêtes fréquentes
- Queue asynchrone (Celery) pour tâches lourdes
- Indexation full-text (Elasticsearch)
- Sharding de la base de données

### 🛠️ Technologies Suggérées

**Backend :**
- FastAPI (API REST)
- SQLAlchemy (ORM)
- Celery + Redis (tâches async)
- Pydantic (validation)

**Frontend :**
- React + TypeScript
- Material-UI ou Tailwind CSS
- React Query (cache)
- Chart.js/D3.js (visualisations)

**Infrastructure :**
- Docker + Kubernetes
- PostgreSQL (primary DB)
- Redis (cache/queue)
- MinIO ou S3 (stockage images)
- Nginx (reverse proxy)

**IA/ML :**
- Sentence Transformers (embeddings)
- Scikit-learn (clustering)
- LangChain (RAG)
- Whisper (transcription)

---

## 📁 Organisation du Projet (Nouvelle Structure)

```
Musique/
├── 📂 src/                          # Code source Python
│   ├── trackers/                    # Surveillance temps réel
│   │   ├── chk-roon.py             # Tracker Roon + Last.fm combiné
│   │   └── chk-last-fm.py          # Tracker Last.fm standalone
│   │
│   ├── collection/                  # Gestion collection
│   │   ├── Read-discogs-ia.py      # Import Discogs avec IA
│   │   └── generate-soundtrack.py  # Détection BOF
│   │
│   ├── enrichment/                  # Enrichissement données
│   │   ├── complete-resumes.py     # Génération résumés IA
│   │   ├── complete-images-roon.py # Complétion images
│   │   └── normalize-supports.py   # Normalisation formats
│   │
│   ├── analysis/                    # Analyse & rapports
│   │   ├── analyze-listening-patterns.py  # Analyse patterns
│   │   ├── generate-haiku.py       # Génération haïkus IA
│   │   └── generate-playlist.py    # 🆕 Génération playlists
│   │
│   ├── maintenance/                 # Nettoyage & maintenance
│   │   ├── remove-consecutive-duplicates.py
│   │   ├── fix-radio-tracks.py
│   │   └── clean-radio-tracks.py
│   │
│   ├── utils/                       # Utilitaires
│   │   ├── List_all_music_on_drive.py
│   │   └── test-spotify-search-v2.2.py
│   │
│   └── gui/                         # Interface web
│       └── musique-gui.py          # Streamlit GUI
│
├── 📂 data/                         # Données JSON actives
│   ├── config/                      # Configuration
│   │   ├── .env                    # Variables d'environnement
│   │   ├── roon-config.json        # Config Roon
│   │   └── Liste_sites_musique-favoris.json
│   │
│   ├── collection/                  # Collection musicale
│   │   ├── discogs-collection.json # Collection Discogs
│   │   └── soundtrack.json         # Bandes originales
│   │
│   ├── history/                     # Historique lectures
│   │   ├── chk-roon.json          # Historique Roon/Last.fm
│   │   ├── chk-roon.lock          # Verrou processus
│   │   └── chk-last-fm.json       # Cache Last.fm
│   │
│   └── exports/                     # Exports formatés
│       ├── discogs-collection.md
│       ├── discogs-collection.pdf
│       ├── Collection-discogs.csv
│       └── list_all_music.csv
│
├── 📂 output/                       # Fichiers générés
│   ├── haikus/                      # Présentations haïkus
│   │   └── generate-haiku-*.txt
│   └── reports/                     # Rapports d'analyse
│       └── listening-patterns-*.txt
│
├── 📂 backups/                      # Sauvegardes organisées
│   ├── json/                        # Backups JSON
│   │   ├── chk-roon/
│   │   ├── discogs-collection/
│   │   └── soundtrack/
│   ├── python/                      # Backups scripts
│   └── legacy/                      # Ancienne structure
│
├── 📂 docs/                         # Documentation
│   ├── README-ROON-TRACKER.md
│   ├── README-MUSIQUE-GUI.md
│   ├── README-ROON-CONFIG.md
│   ├── README-GENERATE-HAIKU.md
│   ├── ARCHITECTURE-OVERVIEW.md
│   └── CHANGELOG-*.md
│
├── 📂 resources/                    # Ressources
│   ├── prompts/                     # Prompts IA
│   └── images/                      # Diagrammes
│
├── 📂 scripts/                      # Scripts shell
│   ├── setup-roon-tracker.sh       # Installation
│   ├── start-streamlit.sh          # Lancement GUI
│   ├── start-all.sh                # 🚀 Lancement simultané (tracker + GUI)
│   └── update_python_certificates.sh
│
├── 📂 archive/                      # Archives
│   └── Autres codes python/
│
├── .github/
│   └── copilot-instructions.md     # Instructions IA
│
├── start-roon-tracker.sh           # 🚀 Lancer tracker (racine)
├── start-all.sh                    # 🚀 Lancer tout (tracker + GUI) - RECOMMANDÉ
├── requirements-roon.txt           # Dépendances Python
└── .gitignore
```

## 🚀 Démarrage Rapide

### Première Installation

```bash
# 1. Créer environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Configurer .env
cp data/config/.env.example data/config/.env
# Éditer data/config/.env avec vos clés API Last.fm, Spotify, Discogs, EurIA
```

### Utilisation Quotidienne

```bash
# 🚀 Lancer l'interface Web
./start-all.sh

# 🚀 Lancer sans ouvrir le navigateur automatiquement
./start-all.sh --no-browser

# Ou lancer les composants séparément:

# Tracker Last.fm (temps réel)
python3 src/trackers/chk-last-fm.py

# Import collection Discogs
cd src/collection && python3 Read-discogs-ia.py

# Génération haïkus
cd src/analysis && python3 generate-haiku.py

# 🆕 Génération playlists intelligentes
cd src/analysis && python3 generate-playlist.py --algorithm top_sessions --max-tracks 25

# Génération playlist avec IA
cd src/analysis && python3 generate-playlist.py --algorithm ai_generated --ai-prompt "jazz cool pour le soir"

# Analyse patterns d'écoute
cd src/analysis && python3 analyze-listening-patterns.py
```

## 📝 Scripts Principaux

### Trackers (temps réel)

- **`src/trackers/chk-last-fm.py`**: Tracker Last.fm standalone

### Collection

- **`src/collection/Read-discogs-ia.py`**: Import Discogs avec enrichissement IA
- **`src/collection/generate-soundtrack.py`**: Détection bandes originales (cross-check avec catalogue films)

### Enrichissement

- **`src/enrichment/complete-resumes.py`**: Génération résumés manquants (EurIA)
- **`src/enrichment/complete-images-roon.py`**: Complétion images Spotify/Last.fm
- **`src/enrichment/normalize-supports.py`**: Normalisation formats (Vinyle/CD)

### Analyse

- **`src/analysis/analyze-listening-patterns.py`**: Analyse sessions, corrélations, patterns temporels
- **`src/analysis/generate-haiku.py`**: Génération présentations IA (iA Presenter)
- **`src/analysis/generate-playlist.py`**: 🆕 Génération playlists intelligentes (7 algorithmes + IA)

### Maintenance

- **`src/maintenance/remove-consecutive-duplicates.py`**: Suppression doublons consécutifs
- **`src/maintenance/fix-radio-tracks.py`**: Correction métadonnées radio
- **`src/maintenance/clean-radio-tracks.py`**: Nettoyage lectures radio invalides

### Interface

- **`src/gui/musique-gui.py`**: Interface web Streamlit complète

## 🔧 Configuration

### Variables d'Environnement

Fichier: `data/config/.env`

```env
# Spotify API
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...

# Last.fm API
API_KEY=...
API_SECRET=...
LASTFM_USERNAME=...

# Discogs API
DISCOGS_API_KEY=...
DISCOGS_USERNAME=...

# EurIA API
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=...
```

### Configuration Roon

Fichier: `data/config/roon-config.json`

```json
{
  "token": "auto-généré",
  "host": "auto-découvert",
  "port": "9330",
  "listen_start_hour": 6,
  "listen_end_hour": 23,
  "radio_stations": [...]
}
```

## 📊 Fichiers de Données

### Sources de Vérité

- **`data/collection/discogs-collection.json`**: Collection musicale complète (Discogs)
- **`data/history/chk-roon.json`**: Historique complet des lectures (Roon + Last.fm)

### Fichiers Générés

- **`output/haikus/generate-haiku-*.txt`**: Présentations albums IA
- **`output/reports/listening-patterns-*.txt`**: Rapports d'analyse

### Exports

- **`data/exports/discogs-collection.md`**: Export Markdown collection
- **`data/exports/discogs-collection.pdf`**: Export PDF collection
- **`data/exports/*.csv`**: Exports CSV

## 🔄 Flux de Données

```
[Roon Core] ──────► chk-roon.py ──────► data/history/chk-roon.json
    │                    │
    │                    ├──► [Spotify API] (images)
    │                    └──► [Last.fm API] (loved status)
    │
[Last.fm] ────────► chk-last-fm.py ───► data/history/chk-last-fm.json

[Discogs API] ───► Read-discogs-ia.py ─► data/collection/discogs-collection.json
                         │
                         └──► [EurIA API] (résumés)

[Catalogue Films] ─► generate-soundtrack.py ─► data/collection/soundtrack.json
```

## 📚 Documentation Détaillée

### Guides d'utilisation
- **[docs/README-START-ALL.md](docs/README-START-ALL.md)**: Lancement simultané (tracker + GUI)
- **[docs/README-ROON-TRACKER.md](docs/README-ROON-TRACKER.md)**: Configuration tracker Roon
- **[docs/README-MUSIQUE-GUI.md](docs/README-MUSIQUE-GUI.md)**: Utilisation interface Streamlit
- **[docs/README-SCHEDULER.md](docs/README-SCHEDULER.md)**: Planification automatique des tâches
- **[docs/README-ROON-CONFIG.md](docs/README-ROON-CONFIG.md)**: Configuration roon-config.json

### Documentation technique
- **[docs/ARCHITECTURE-OVERVIEW.md](docs/ARCHITECTURE-OVERVIEW.md)**: Vue d'ensemble architecture
- **[docs/DEPENDENCIES.md](docs/DEPENDENCIES.md)**: 📦 **MIS À JOUR** - Guide complet des dépendances Python (v3.5.0)
  - Installation complète vs minimale (tracker uniquement)  
  - Dépendances par composant (GUI, CLI, tests, database)  
  - Différence entre requirements.txt et requirements-roon.txt  
  - Troubleshooting et compatibilité
- **[docs/MERGED-BRANCHES.md](docs/MERGED-BRANCHES.md)**: 🔀 Liste complète des branches mergées avec main (38 branches)
- **[requirements.txt](requirements.txt)**: Fichier de dépendances Python (installation complète)
- **[requirements-roon.txt](requirements-roon.txt)**: Dépendances minimales (tracker uniquement)
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)**: Guide développement IA

## ⚠️ Bonnes Pratiques

### Backups Automatiques

- Scripts créent automatiquement des backups avant modifications
- Emplacement: `backups/json/{chk-roon,discogs-collection,soundtrack}/`
- Rétention: 5 backups les plus récents

### Chemins Relatifs

- Tous les scripts utilisent des chemins relatifs depuis leur emplacement
- Format: `../../data/collection/discogs-collection.json`
- Configuration: `../../data/config/.env`

### Sécurité

- ⚠️ Ne jamais versionner `data/config/.env`
- ⚠️ Les tokens/tokens dans `roon-config.json` sont sensibles
- ✅ Fichier `.gitignore` protège automatiquement

## 🆕 Changelog

### Version 3.4.0 (28 janvier 2026)

**Nouvelle fonctionnalité Timeline:**
- ✅ Vue Timeline horaire pour Journal Roon (Issue #46)
- ✅ Navigation temporelle avec scroll horizontal
- ✅ Alternance de couleurs par heure (gris/blanc)
- ✅ Modes compact et détaillé
- ✅ Statistiques journalières (tracks, artistes, albums, peak hour)
- ✅ Configuration basée sur habitudes d'écoute (roon-config.json)

**Corrections:**
- ✅ Fix affichage Timeline cas limites (Issue #57)
- ✅ Amélioration robustesse parsing dates
- ✅ Optimisation performances

### Version 3.3.1 (27 janvier 2026)

**Génération Playlists:**
- ✅ Module generate-playlist.py avec 7 algorithmes (Issue #19)
- ✅ Export multi-formats (JSON, M3U, CSV, TXT)
- ✅ Génération playlists via IA avec prompt personnalisé
- ✅ Déduplication automatique (Issue #38)

**Corrections:**
- ✅ Fix timezone décalage horaire UTC (Issue #32)
- ✅ Tests timezone (5 nouveaux tests)

### Version 3.0.0 (23 janvier 2026)

**Réorganisation complète:**
- ✅ Structure modulaire par fonction
- ✅ Séparation code/données/docs
- ✅ Chemins relatifs robustes
- ✅ Backups organisés par type
- ✅ Scripts shell mis à jour
- ✅ Documentation centralisée

**Migration depuis ancienne structure:**
- Scripts déplacés vers `src/`
- Données déplacées vers `data/`
- Documentation déplacée vers `docs/`
- Ancien contenu archivé dans `backups/legacy/`

---

**Auteur**: Patrick Ostertag  
**Licence**: Personnel  
**Contact**: patrick.ostertag@gmail.com

---
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
