# 📦 Dépendances du Projet Musique

## Vue d'ensemble

Ce document liste toutes les dépendances Python nécessaires pour le projet Musique (Collection & Tracking), organisées par fonction et scripts concernés.

**Version du projet:** 3.0.0  
**Date:** 24 janvier 2026

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

## Dépendances externes (pip install)

### Core Dependencies
Utilisées par plusieurs scripts du projet.

| Package | Version minimale | Usage | Scripts concernés |
|---------|-----------------|-------|-------------------|
| `python-dotenv` | 1.0.0 | Gestion variables d'environnement (.env) | Tous les scripts |
| `requests` | 2.31.0 | Requêtes HTTP vers APIs | collection/, enrichment/, analysis/, gui/ |
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
**Scripts:** `generate-haiku.py`, `analyze-listening-patterns.py`

**Dépendances:**
- `requests` - API EurIA
- `python-dotenv` - Variables d'environnement

### `src/gui/` - Interface Web
**Scripts:** `musique-gui.py`

**Dépendances:**
- `streamlit` - Framework Web
- `pillow` - Traitement images
- `requests` - Chargement images depuis URLs
- `python-dotenv` - Variables d'environnement

### `src/utils/` - Utilitaires
**Scripts:** `List_all_music_on_drive.py`, `test-spotify-search-v2.2.py`

**Dépendances:**
- `mutagen` - Métadonnées audio (FLAC, MP3, ID3)
- `python-dotenv` - Variables d'environnement

### `src/maintenance/` - Maintenance
**Scripts:** `remove-consecutive-duplicates.py`, `fix-radio-tracks.py`, `clean-radio-tracks.py`

**Dépendances:**
- `python-dotenv` - Variables d'environnement (certains scripts)
- Principalement modules standard library

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

## Dépendances par fonctionnalité

### Pour utiliser le tracker Roon/Last.fm
```bash
pip install roonapi pylast certifi python-dotenv
```

### Pour utiliser l'interface Web Streamlit
```bash
pip install streamlit pillow requests python-dotenv
```

### Pour scanner les fichiers musicaux
```bash
pip install mutagen python-dotenv
```

### Pour importer la collection Discogs
```bash
pip install requests python-dotenv
```

## Compatibilité

- **Python:** 3.8 ou supérieur (testé avec Python 3.11, 3.12, 3.13)
- **OS:** macOS, Linux, Windows (verrouillage fcntl fonctionne uniquement sur Unix/macOS)
- **Architecture:** x86_64, ARM64 (Apple Silicon compatible)

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
