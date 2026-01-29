# 📦 Dépendances du Projet Musique

## Vue d'ensemble

Ce document liste toutes les dépendances Python nécessaires pour le projet Musique (Collection & Tracking), organisées par fonction et scripts concernés.

**Version du projet:** 3.5.0  
**Date:** 29 janvier 2026

## Installation rapide

### Option 1: Script automatique (recommandé)
```bash
chmod +x scripts/install-dependencies.sh
./scripts/install-dependencies.sh
```

### Option 2: Installation manuelle
```bash
# Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Option 3: Installation minimale (tracker Roon uniquement)
```bash
# Pour uniquement exécuter chk-roon.py
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-roon.txt
```

## Dépendances externes (pip install)

### Core Dependencies
Utilisées par plusieurs scripts du projet.

| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `python-dotenv` | 1.0.0 | Gestion variables d'environnement (.env) | Tous les scripts |
| `requests` | 2.31.0 | Requêtes HTTP vers APIs | collection/, enrichment/, analysis/, gui/, trackers/ |
| `certifi` | 2023.0.0 | Gestion certificats SSL | trackers/ |

### Tracking & APIs musicales
| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `roonapi` | 0.1.0 | API Roon Core | `src/trackers/chk-roon.py` |
| `pylast` | 5.0.0 | API Last.fm | `src/trackers/chk-roon.py`<br>`src/trackers/chk-last-fm.py` |

### Métadonnées audio
| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `mutagen` | 1.47.0 | Lecture métadonnées FLAC/MP3 | `src/utils/List_all_music_on_drive.py` |

### Interface Web
| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `streamlit` | 1.53.0 | Framework Web UI | `src/gui/musique-gui.py` |
| `pillow` | 12.1.0 | Traitement images | `src/gui/musique-gui.py` |
| `markdown` | 3.4.0 | Conversion Markdown vers HTML | `src/gui/musique-gui.py` |

### Interface CLI
| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `rich` | 13.0.0 | Affichage terminal enrichi (tables, couleurs, panels) | `src/cli/` |
| `click` | 8.0.0 | Framework CLI avec commandes imbriquées | `src/cli/main.py` |
| `prompt-toolkit` | 3.0.0 | Outils interactifs CLI (prévu Phase 2) | À venir |

### Base de données
| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `sqlalchemy` | 2.0.0 | ORM pour gestion base SQLite | `src/models/schema.py`<br>`src/maintenance/migrate_to_sqlite.py` |

### Tests
| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `pytest` | 7.0.0 | Framework de tests unitaires | `src/tests/test_*.py` |
| `pytest-cov` | 4.0.0 | Couverture de code | Configuration dans `pytest.ini` |

**Note sur pytest-mock**: Non inclus car les tests utilisent `unittest.mock` de la bibliothèque standard Python.

## Modules Python Standard Library

Ces modules sont inclus avec Python et ne nécessitent pas d'installation.

### Manipulation de données
- `json` - Lecture/écriture fichiers JSON
- `csv` - Lecture/écriture fichiers CSV
- `base64` - Encodage Base64 (authentification APIs)
- `re` - Expressions régulières
- `unicodedata` - Normalisation Unicode

### Système et fichiers
- `os` - Opérations système et chemins
- `sys` - Paramètres système
- `fcntl` - Verrouillage de fichiers (Unix/macOS)

### Date et temps
- `datetime` - Manipulation dates et heures
- `time` - Fonctions temporelles

### Networking
- `urllib.request` - Requêtes HTTP basiques
- `urllib.parse` - Parsing URLs

### Utilitaires
- `collections` - Structures de données (Counter, defaultdict)
- `typing` - Annotations de type
- `secrets` - Nombres aléatoires sécurisés
- `random` - Nombres aléatoires
- `io` - I/O (BytesIO pour images)

## Détail par module du projet

### `src/trackers/` - Surveillance temps réel
**Scripts:** `chk-roon.py`, `chk-last-fm.py`

**Dépendances:**
- `roonapi` - Connexion Roon Core
- `pylast` - API Last.fm
- `certifi` - Certificats SSL
- `python-dotenv` - Variables d'environnement
- `requests` - Requêtes HTTP (Spotify, EurIA)

**Fichier requirements minimal:** `requirements-roon.txt`

### `src/collection/` - Gestion collection
**Scripts:** `Read-discogs-ia.py`, `generate-soundtrack.py`

**Dépendances:**
- `requests` - API Discogs, Spotify, EurIA
- `python-dotenv` - Variables d'environnement

### `src/enrichment/` - Enrichissement métadonnées
**Scripts:** `complete-resumes.py`, `complete-images-roon.py`, `normalize-supports.py`

**Dépendances:**
- `requests` - API Spotify, EurIA
- `python-dotenv` - Variables d'environnement

### `src/analysis/` - Analyse et génération
**Scripts:** `generate-haiku.py`, `analyze-listening-patterns.py`, `generate-playlist.py`

**Dépendances:**
- `requests` - API EurIA
- `python-dotenv` - Variables d'environnement

### `src/gui/` - Interface Web
**Scripts:** `musique-gui.py`

**Dépendances:**
- `streamlit` - Framework Web
- `pillow` - Traitement images
- `markdown` - Conversion Markdown vers HTML
- `requests` - Chargement images depuis URLs
- `python-dotenv` - Variables d'environnement

**Script de lancement:** `scripts/start-streamlit.sh`

### `src/cli/` - Interface CLI (v3.5.0)
**Scripts:** `main.py`, `ui/colors.py`, `utils/terminal.py`, `commands/*.py`

**Dépendances:**
- `rich` - Affichage terminal enrichi
- `click` - Framework CLI
- `prompt-toolkit` - Outils interactifs (prévu Phase 2)
- `python-dotenv` - Variables d'environnement

**Script de lancement:** `start-cli.sh` (gère auto-installation)

### `src/models/` - Schéma base de données (v3.4.0)
**Scripts:** `schema.py`

**Dépendances:**
- `sqlalchemy` - ORM pour SQLite

### `src/utils/` - Utilitaires
**Scripts:** `List_all_music_on_drive.py`, `test-spotify-search-v2.2.py`, `scheduler.py`

**Dépendances:**
- `mutagen` - Métadonnées audio (FLAC, MP3, ID3)
- `python-dotenv` - Variables d'environnement

### `src/maintenance/` - Maintenance
**Scripts:** `remove-consecutive-duplicates.py`, `fix-radio-tracks.py`, `clean-radio-tracks.py`, `migrate_to_sqlite.py`

**Dépendances:**
- `python-dotenv` - Variables d'environnement (certains scripts)
- `sqlalchemy` - Migration vers SQLite (migrate_to_sqlite.py)
- Principalement modules standard library

### `src/tests/` - Tests unitaires (v3.1.0+)
**Scripts:** `test_*.py`, `conftest.py`

**Dépendances:**
- `pytest` - Framework de tests
- `pytest-cov` - Couverture de code
- `unittest.mock` (stdlib) - Mocking

**Exécution:** `python3 -m pytest src/tests/ -v`

**Configuration:** `pytest.ini` à la racine du projet

## Vérification des dépendances installées

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lister les packages installés
pip list

# Vérifier une dépendance spécifique
pip show roonapi
pip show streamlit
```

## Mise à jour des dépendances

```bash
# Mettre à jour tous les packages
pip install --upgrade -r requirements.txt

# Mettre à jour un package spécifique
pip install --upgrade streamlit
```

## Installation par composant

Si vous n'avez besoin que d'un sous-ensemble de fonctionnalités, vous pouvez installer uniquement les dépendances nécessaires.

### Tracker Roon uniquement
```bash
# Installation minimale pour chk-roon.py
pip install -r requirements-roon.txt
# Ou installation manuelle
pip install roonapi pylast certifi python-dotenv requests
```

### Interface Web (GUI) uniquement
```bash
pip install streamlit pillow markdown requests python-dotenv
```

### Interface CLI uniquement
```bash
pip install rich click prompt-toolkit python-dotenv
# Ou utiliser le script automatique
./start-cli.sh  # Installe automatiquement les dépendances manquantes
```

### Utilitaires audio
```bash
pip install mutagen python-dotenv
```

### Développement et tests
```bash
pip install pytest pytest-cov
# pytest-mock n'est pas nécessaire (unittest.mock est utilisé)
```

### Migration base de données
```bash
pip install sqlalchemy python-dotenv
```

## Compatibilité

- **Python:** 3.8 ou supérieur (testé avec Python 3.11, 3.12, 3.13)
- **OS:** macOS, Linux, Windows (verrouillage fcntl fonctionne uniquement sur Unix/macOS)
- **Architecture:** x86_64, ARM64 (Apple Silicon compatible)

## Fichiers requirements

Le projet dispose de deux fichiers requirements :

- **`requirements.txt`** : Toutes les dépendances pour l'installation complète du projet
- **`requirements-roon.txt`** : Dépendances minimales pour le tracker Roon uniquement

**Utilisation recommandée** :
- Utilisez `requirements.txt` pour une installation complète
- Utilisez `requirements-roon.txt` pour un déploiement minimal (tracker uniquement)
- Les scripts d'installation (`install-dependencies.sh`, `setup-roon-tracker.sh`) gèrent cela automatiquement

## Troubleshooting

### Erreur: ModuleNotFoundError
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur: SSL Certificate
```bash
# Mettre à jour certifi
pip install --upgrade certifi

# Sur macOS, installer les certificats Python
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Erreur: ImportError pour mutagen
```bash
# Installer mutagen explicitement
pip install mutagen
```

### Problème avec Streamlit
```bash
# Réinstaller Streamlit
pip uninstall streamlit
pip install streamlit
```

## Génération du requirements.txt

Pour regénérer le fichier `requirements.txt` depuis l'environnement actuel :

```bash
# Depuis l'environnement virtuel activé
pip freeze > requirements-frozen.txt

# Ou générer une version épurée
pip list --format=freeze | grep -E "(roonapi|pylast|mutagen|streamlit|pillow|requests|python-dotenv|certifi)" > requirements-clean.txt
```

## Ressources

- **Documentation Python:** https://docs.python.org/3/
- **PyPI (Python Package Index):** https://pypi.org/
- **pip Documentation:** https://pip.pypa.io/
- **Environnements virtuels:** https://docs.python.org/3/library/venv.html

## Historique des versions

### v3.0.0 (24 janvier 2026)
- Documentation complète des dépendances
- Script d'installation automatique
- `mutagen` ajouté pour `List_all_music_on_drive.py`
- Réorganisation avec structure modulaire

### v2.x
- `requirements-roon.txt` partiel (seulement tracker)

---

**Maintenu par:** Patrick Ostertag  
**Contact:** Voir `.github/copilot-instructions.md`
