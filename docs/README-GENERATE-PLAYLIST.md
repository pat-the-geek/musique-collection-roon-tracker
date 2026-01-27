# 🎵 Générateur de Playlists Intelligentes - Guide Complet

**Version:** 1.2.0  
**Date:** 27 janvier 2026  
**Module:** `src/analysis/generate-playlist.py`  
**Auteur:** Patrick Ostertag  
**Issue:** #19

---

## 📋 Vue d'Ensemble

Le générateur de playlists est un module avancé qui crée automatiquement des playlists musicales basées sur l'analyse de vos patterns d'écoute. Il offre 7 algorithmes différents, dont un générateur par IA, et exporte les résultats dans 4 formats compatibles avec divers lecteurs musicaux.

### ⚠️ Limitation Importante - API Roon

**L'API Roon ne permet PAS la création automatique de playlists.**

Ce script génère des exports dans plusieurs formats (JSON, M3U, CSV, TXT) qui peuvent être :
- Importés manuellement dans Roon (via fichier texte avec instructions)
- Utilisés avec d'autres lecteurs (VLC, iTunes, Foobar2000, etc.)
- Intégrés dans des services de streaming (via M3U)

---

## 🎯 Fonctionnalités Principales

### 7 Algorithmes de Génération

1. **top_sessions** - Sessions d'écoute les plus longues
   - Identifie les sessions d'écoute continues
   - Sélectionne les pistes des sessions les plus longues
   - Idéal pour recréer des moments d'écoute mémorables

2. **artist_correlations** - Artistes écoutés ensemble
   - Analyse les artistes fréquemment écoutés dans les mêmes sessions
   - Crée une playlist avec transitions naturelles
   - Parfait pour découvrir des artistes similaires

3. **artist_flow** - Transitions naturelles entre artistes
   - Détecte les transitions fréquentes entre artistes
   - Construit une playlist avec un flux cohérent
   - Excellent pour une écoute fluide et progressive

4. **time_based** - Pistes selon périodes temporelles
   - Sélectionne pistes selon heures de pointe, weekend, etc.
   - Options: `peak_hours`, `weekend`, `weekday`, `morning`, `evening`, `night`
   - Idéal pour créer des ambiances spécifiques

5. **complete_albums** - Albums écoutés en entier
   - Identifie les albums écoutés avec ≥5 pistes
   - Sélectionne pistes des albums les plus joués
   - Parfait pour les albums favoris

6. **rediscovery** - Pistes aimées mais oubliées
   - Trouve les pistes "loved" non écoutées récemment
   - Encourage la redécouverte de votre collection
   - Excellent pour varier les écoutes

7. **ai_generated** 🆕 - Génération par IA
   - Utilise l'API EurIA (Qwen3) pour générer une playlist
   - Basée sur un prompt utilisateur personnalisé
   - Exemples: "jazz cool pour le soir", "rock énergique pour sport"

### v1.2.0 - Déduplication Automatique

**Nouvelle fonctionnalité** (Issue #38):
- Détection automatique des doublons dans les playlists générées
- Normalisation par (artiste + titre + album)
- Ignore variations de casse et espaces
- Affiche le nombre de doublons supprimés
- Garantit des playlists propres et cohérentes

### 4 Formats d'Export

1. **JSON** - Métadonnées complètes
   - Toutes les informations disponibles
   - Images Spotify/Last.fm incluses
   - Format structuré pour traitement automatique

2. **M3U** - Format playlist standard
   - Compatible VLC, iTunes, Foobar2000, etc.
   - Inclut durée estimée et métadonnées
   - Prêt à l'emploi sur la plupart des lecteurs

3. **CSV** - Import tableur
   - Compatible Excel, Google Sheets, LibreOffice
   - Colonnes: Artiste, Titre, Album, Date, Durée estimée
   - Idéal pour analyse ou manipulation

4. **TXT (Roon)** - Instructions d'import manuel
   - Guide étape par étape pour créer playlist dans Roon
   - Liste formatée des pistes avec métadonnées
   - Instructions de recherche et d'ajout manuel

---

## 🚀 Utilisation

### Génération Manuelle

#### Commande de base
```bash
cd src/analysis
python3 generate-playlist.py --algorithm top_sessions --max-tracks 25
```

#### Options disponibles
```bash
# Algorithme et nombre de pistes
--algorithm {top_sessions|artist_correlations|artist_flow|time_based|complete_albums|rediscovery|ai_generated}
--max-tracks N                    # Nombre maximum de pistes (défaut: 25)

# Pour time_based
--time-period {peak_hours|weekend|weekday|morning|evening|night}

# Pour ai_generated
--ai-prompt "votre prompt"        # Exemple: "playlist calme pour méditer"

# Formats d'export
--output-formats json m3u csv roon-txt    # Formats à générer (défaut: tous)

# Affichage
--verbose                          # Mode verbeux avec détails
```

#### Exemples d'utilisation

**Sessions les plus longues:**
```bash
python3 generate-playlist.py --algorithm top_sessions --max-tracks 30
```

**Artistes corrélés:**
```bash
python3 generate-playlist.py --algorithm artist_correlations --max-tracks 20
```

**Heures de pointe uniquement:**
```bash
python3 generate-playlist.py --algorithm time_based --time-period peak_hours --max-tracks 25
```

**Redécouverte de pistes aimées:**
```bash
python3 generate-playlist.py --algorithm rediscovery --max-tracks 15
```

**Génération par IA:**
```bash
python3 generate-playlist.py --algorithm ai_generated --ai-prompt "jazz cool pour le soir" --max-tracks 20
```

**Export formats spécifiques:**
```bash
python3 generate-playlist.py --algorithm top_sessions --output-formats m3u csv --max-tracks 25
```

---

### Génération Automatique (Scheduler)

Le générateur peut être configuré pour s'exécuter automatiquement via le scheduler intégré.

#### Configuration dans roon-config.json

```json
{
  "scheduled_tasks": {
    "generate_playlist": {
      "enabled": true,
      "frequency_unit": "day",
      "frequency_count": 7,
      "playlist_type": "top_sessions",
      "max_tracks": 25,
      "output_formats": ["json", "m3u", "csv", "roon-txt"],
      "ai_prompt": "playlist calme pour méditer",
      "time_period": "peak_hours"
    }
  }
}
```

#### Paramètres de configuration

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|---------|
| `enabled` | boolean | Activer/désactiver la tâche | `false` |
| `frequency_unit` | string | Unité de fréquence (`hour`, `day`, `week`, `month`) | `"day"` |
| `frequency_count` | integer | Nombre d'unités entre exécutions | `7` |
| `playlist_type` | string | Algorithme à utiliser | `"top_sessions"` |
| `max_tracks` | integer | Nombre maximum de pistes | `25` |
| `output_formats` | array | Formats d'export | `["json", "m3u"]` |
| `ai_prompt` | string | Prompt pour algorithme `ai_generated` | `""` |
| `time_period` | string | Période pour algorithme `time_based` | `"peak_hours"` |

#### Gestion via Interface GUI

1. Ouvrir l'interface Streamlit (`./start-all.sh`)
2. Aller dans la section **"⚙️ Configuration Scheduler"**
3. Configurer les paramètres de génération de playlists
4. Sauvegarder et redémarrer le tracker

---

## 📂 Fichiers Générés

### Structure des fichiers de sortie

```
output/playlists/
├── playlist-top_sessions-20260127-143022.json
├── playlist-top_sessions-20260127-143022.m3u
├── playlist-top_sessions-20260127-143022.csv
└── playlist-roon-top_sessions-20260127-143022.txt
```

### Format JSON

```json
{
  "metadata": {
    "title": "Playlist: Top Sessions",
    "algorithm": "top_sessions",
    "generated_at": "2026-01-27 14:30:22",
    "total_tracks": 25,
    "duplicates_removed": 3,
    "source": "chk-roon.json"
  },
  "tracks": [
    {
      "artist": "Pink Floyd",
      "title": "Shine On You Crazy Diamond",
      "album": "Wish You Were Here",
      "date": "2026-01-20 19:45",
      "timestamp": 1737398700,
      "loved": true,
      "artist_spotify_image": "https://...",
      "album_spotify_image": "https://...",
      "album_lastfm_image": "https://...",
      "estimated_duration": "13:30"
    }
  ]
}
```

### Format M3U

```
#EXTM3U
#PLAYLIST: Playlist: Top Sessions
# Generated: 2026-01-27 14:30:22
# Algorithm: top_sessions
# Total tracks: 25
# Duplicates removed: 3

#EXTINF:810,Pink Floyd - Shine On You Crazy Diamond (Wish You Were Here)
Pink Floyd - Shine On You Crazy Diamond.mp3

#EXTINF:240,David Bowie - Heroes (Heroes)
David Bowie - Heroes.mp3
```

### Format CSV

```csv
Artiste,Titre,Album,Date,Durée Estimée
"Pink Floyd","Shine On You Crazy Diamond","Wish You Were Here","2026-01-20 19:45","13:30"
"David Bowie","Heroes","Heroes","2026-01-20 20:00","4:00"
```

### Format TXT (Instructions Roon)

```
PLAYLIST ROON: Playlist: Top Sessions
Générée le: 2026-01-27 14:30:22
Algorithme: top_sessions
Nombre de pistes: 25
Doublons supprimés: 3

INSTRUCTIONS D'IMPORT DANS ROON:
================================

1. Ouvrir Roon et aller dans "Playlists"
2. Cliquer sur "+ New Playlist"
3. Nommer la playlist: "Playlist: Top Sessions"
4. Pour chaque piste ci-dessous:
   - Utiliser la recherche Roon
   - Chercher: "Artiste + Titre"
   - Ajouter la piste trouvée à la playlist

PISTES À AJOUTER:
================

1. Pink Floyd - Shine On You Crazy Diamond
   Album: Wish You Were Here
   Date d'écoute: 2026-01-20 19:45

2. David Bowie - Heroes
   Album: Heroes
   Date d'écoute: 2026-01-20 20:00
```

---

## 🔍 Détails des Algorithmes

### top_sessions (Sessions Longues)

**Principe:**
- Détecte les sessions d'écoute continues (gap ≤30 minutes)
- Calcule la durée de chaque session (estimée à ~4 min/piste)
- Sélectionne les pistes des sessions les plus longues

**Paramètres:**
- `session_gap_minutes`: 30 (temps max entre pistes d'une session)
- `avg_track_duration_minutes`: 4 (durée moyenne estimée)

**Meilleur usage:** Recréer des moments d'écoute mémorables

---

### artist_correlations (Artistes Corrélés)

**Principe:**
- Analyse les artistes écoutés dans les mêmes sessions
- Calcule un score de corrélation pour chaque paire d'artistes
- Sélectionne pistes des artistes les plus corrélés

**Paramètres:**
- `min_correlation_score`: 3 (minimum d'occurrences ensemble)

**Meilleur usage:** Découvrir des artistes similaires, ambiance cohérente

---

### artist_flow (Flux d'Artistes)

**Principe:**
- Détecte les transitions fréquentes entre artistes consécutifs
- Construit une chaîne de transitions naturelles
- Crée un flux progressif d'artistes

**Paramètres:**
- `min_transition_count`: 2 (minimum de fois où transition observée)

**Meilleur usage:** Écoute fluide, découverte progressive

---

### time_based (Basé sur le Temps)

**Principe:**
- Filtre les pistes selon la période temporelle choisie
- Détecte les patterns d'écoute par heure/jour

**Périodes disponibles:**
- `peak_hours`: Heures les plus actives
- `weekend`: Samedi et dimanche
- `weekday`: Lundi à vendredi
- `morning`: 6h-12h
- `evening`: 18h-23h
- `night`: 23h-6h

**Meilleur usage:** Créer ambiances spécifiques (réveil, travail, détente)

---

### complete_albums (Albums Complets)

**Principe:**
- Identifie les albums écoutés avec ≥5 pistes
- Calcule le score de chaque album (nombre de fois écouté)
- Sélectionne pistes des albums les plus joués

**Paramètres:**
- `min_tracks_per_album`: 5 (seuil pour considérer album "complet")

**Meilleur usage:** Favoris, albums préférés

---

### rediscovery (Redécouverte)

**Principe:**
- Trouve les pistes marquées "loved" (❤️)
- Exclut celles écoutées récemment (≤30 jours)
- Encourage la redécouverte

**Paramètres:**
- `days_threshold`: 30 (jours depuis dernière écoute)

**Meilleur usage:** Redécouvrir des pistes oubliées, varier les écoutes

---

### ai_generated (Généré par IA) 🆕

**Principe:**
- Envoie un prompt à l'API EurIA (Qwen3)
- L'IA génère une liste de pistes basée sur le prompt
- Recherche les pistes correspondantes dans l'historique

**Paramètres:**
- `ai_prompt`: Prompt personnalisé (obligatoire)
- `max_tokens`: 2000
- `temperature`: 0.7

**Exemples de prompts:**
- "playlist calme pour méditer"
- "rock énergique pour faire du sport"
- "jazz cool pour une soirée romantique"
- "musique électronique pour travailler"
- "classique pour se concentrer"

**Meilleur usage:** Playlists thématiques personnalisées

---

## 🛠️ Configuration Avancée

### Variables d'Environnement

Pour utiliser l'algorithme `ai_generated`, configurez `.env`:

```env
# EurIA API (pour génération par IA)
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=your_bearer_token_here
max_attempts=5
default_error_message=Aucune information disponible
```

### Dépendances

```python
# Bibliothèques requises
json, os, sys, argparse
datetime, timedelta, pathlib
typing (List, Dict, Tuple, Optional)
collections (Counter, defaultdict)

# Modules internes
src.services.ai_service (generate_ai_playlist)
src.services.metadata_cleaner (normalize_string_for_comparison)
```

### Fichiers de Données

| Fichier | Chemin | Description | Requis |
|---------|--------|-------------|--------|
| Historique Roon | `data/history/chk-roon.json` | Lectures enregistrées | ✅ Oui |
| Collection Discogs | `data/collection/discogs-collection.json` | Collection musicale | ❌ Optionnel |

---

## 📊 Statistiques et Métriques

### Informations affichées

Après génération, le script affiche:
- ✅ Algorithme utilisé
- ✅ Nombre de pistes dans la playlist
- ✅ **Nombre de doublons supprimés** (v1.2.0)
- ✅ Formats d'export générés
- ✅ Chemins des fichiers créés
- ✅ Durée totale estimée

### Exemple de sortie

```
🎵 Génération de playlist...

Algorithme: top_sessions
Pistes dans la playlist: 25
Doublons supprimés: 3
Durée totale estimée: 1h 45min

✅ Exports générés:
   - JSON: output/playlists/playlist-top_sessions-20260127-143022.json
   - M3U:  output/playlists/playlist-top_sessions-20260127-143022.m3u
   - CSV:  output/playlists/playlist-top_sessions-20260127-143022.csv
   - TXT:  output/playlists/playlist-roon-top_sessions-20260127-143022.txt

✅ Playlist générée avec succès!
```

---

## 🐛 Dépannage

### Problème: Playlist vide

**Causes possibles:**
- Historique `chk-roon.json` vide ou inexistant
- Algorithme trop restrictif (ex: `rediscovery` sans pistes "loved")
- Période temporelle sans données (`time_based`)

**Solutions:**
- Vérifier que le tracker Roon a enregistré des lectures
- Essayer un autre algorithme
- Réduire les seuils (ex: `min_correlation_score`)

---

### Problème: IA ne génère pas de playlist

**Causes possibles:**
- Credentials EurIA manquants ou invalides
- Prompt trop vague ou complexe
- Timeout API

**Solutions:**
- Vérifier `.env` avec credentials corrects
- Simplifier le prompt (ex: "jazz calme" au lieu de "playlist jazz cool avec piano et saxophone pour soirée romantique")
- Augmenter `max_attempts` dans `.env`

---

### Problème: Beaucoup de doublons

**Note:** Ce problème est **résolu en v1.2.0** avec la déduplication automatique.

Si vous rencontrez des doublons:
- Vérifiez que vous utilisez la version 1.2.0+
- La déduplication est automatique et affiche le nombre supprimé
- Les doublons sont détectés par normalisation (artiste + titre + album)

---

## 📚 Documentation Complémentaire

- **Architecture:** [docs/ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md)
- **Service IA:** [docs/AI-INTEGRATION.md](AI-INTEGRATION.md)
- **Scheduler:** [docs/README-SCHEDULER.md](README-SCHEDULER.md)
- **Roon Tracker:** [docs/README-ROON-TRACKER.md](README-ROON-TRACKER.md)
- **Interface GUI:** [docs/README-MUSIQUE-GUI.md](README-MUSIQUE-GUI.md)

---

## 🔄 Changelog

### v1.2.0 (27 janvier 2026) - Issue #38
- ✅ Ajout déduplication automatique des doublons
- ✅ Normalisation par (artiste + titre + album)
- ✅ Affichage nombre doublons supprimés
- ✅ Ignore variations casse et espaces

### v1.1.0 (27 janvier 2026) - Issue #19
- ✅ Ajout algorithme `ai_generated` avec EurIA
- ✅ Export format TXT avec instructions Roon
- ✅ Support configuration via scheduler
- ✅ Intégration dans `roon-config.json`

### v1.0.0 (27 janvier 2026) - Issue #19
- ✅ 6 algorithmes de génération
- ✅ Export multi-formats (JSON, M3U, CSV)
- ✅ Intégration avec historique Roon
- ✅ Support collection Discogs

---

**Auteur:** Patrick Ostertag  
**Contact:** patrick.ostertag@gmail.com  
**Dernière mise à jour:** 27 janvier 2026
