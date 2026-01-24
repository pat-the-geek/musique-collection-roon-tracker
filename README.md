# 🎵 Musique - Projet de Tracking Musical

> ⚠️ **PROOF OF CONCEPT** - Ce projet est une démonstration de faisabilité technique explorant l'intégration de multiples APIs musicales (Roon, Last.fm, Spotify, Discogs) avec enrichissement IA (EurIA/Qwen3) pour le tracking, l'analyse et la présentation de données musicales personnelles.

## 🎯 État du Projet

**Version actuelle : 3.0.0** (Architecture modulaire - 23 janvier 2026)

**Statut :** ✅ Fonctionnel • 🧪 Expérimental • 📊 En évolution

### Fonctionnalités Validées
- ✅ Surveillance temps réel Roon + Last.fm avec enrichissement images publiques
- ✅ Import automatique collection Discogs avec résumés IA
- ✅ Interface Web Streamlit pour gestion collection
- ✅ Génération de présentations musicales (haïkus) via IA
- ✅ Analyse patterns d'écoute (sessions, corrélations, statistiques)
- ✅ Cross-référence films/soundtracks via projet Cinéma
- ✅ Détection et traitement intelligent des radios
- ✅ Système de cache et retry pour robustesse API

### 🚀 Pistes d'Amélioration Prioritaires

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
│   │   └── generate-haiku.py       # Génération haïkus IA
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
│   └── update_python_certificates.sh
│
├── 📂 archive/                      # Archives
│   └── Autres codes python/
│
├── .github/
│   └── copilot-instructions.md     # Instructions IA
│
├── start-roon-tracker.sh           # 🚀 Lancer tracker (racine)
├── requirements-roon.txt           # Dépendances Python
└── .gitignore
```

## 🚀 Démarrage Rapide

### Première Installation

```bash
# 1. Installation des dépendances Python
./scripts/install-dependencies.sh

# 2. Configuration complète du tracker Roon
./scripts/setup-roon-tracker.sh

# 3. Lancer le tracker Roon
./start-roon-tracker.sh
```

**Ou manuellement:**
```bash
# Créer environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
cp data/config/.env.example data/config/.env
# Éditer data/config/.env avec vos clés API
```

### Utilisation Quotidienne

```bash
# Tracker Roon (temps réel)
./start-roon-tracker.sh

# Interface Web Streamlit
./scripts/start-streamlit.sh

# Import collection Discogs
cd src/collection && python3 Read-discogs-ia.py

# Génération haïkus
cd src/analysis && python3 generate-haiku.py

# Analyse patterns d'écoute
cd src/analysis && python3 analyze-listening-patterns.py
```

## 📝 Scripts Principaux

### Trackers (temps réel)

- **`src/trackers/chk-roon.py`**: Surveillance Roon + Last.fm (monitoring continu)
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
- **[docs/README-ROON-TRACKER.md](docs/README-ROON-TRACKER.md)**: Configuration tracker Roon
- **[docs/README-MUSIQUE-GUI.md](docs/README-MUSIQUE-GUI.md)**: Utilisation interface Streamlit
- **[docs/README-ROON-CONFIG.md](docs/README-ROON-CONFIG.md)**: Configuration roon-config.json

### Documentation technique
- **[docs/ARCHITECTURE-OVERVIEW.md](docs/ARCHITECTURE-OVERVIEW.md)**: Vue d'ensemble architecture
- **[docs/DEPENDENCIES.md](docs/DEPENDENCIES.md)**: Liste complète des dépendances
- **[requirements.txt](requirements.txt)**: Fichier de dépendances Python
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
