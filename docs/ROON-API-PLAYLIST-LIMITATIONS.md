# Roon API - Limitations pour la Création de Playlists

**Date**: 27 janvier 2026  
**Issue**: #19 - Création de playlists basées sur les patterns d'écoute

## 🚫 Limitation Critique

**L'API Roon ne supporte PAS la création automatique de playlists via des appels API programmatiques.**

## Recherche Effectuée

### Sources Consultées

1. **Communauté Roon Labs**
   - Thread: "Creating playlists" (https://community.roonlabs.com/t/creating-playlists/253188)
   - Thread: "How to recreate a Plex-based playlist import" (https://community.roonlabs.com/t/how-to-recreate-a-plex-based-playlist-import-python-script-in-roon/280914)
   
2. **Documentation Officielle**
   - PyPI: roonapi (https://pypi.org/project/roonapi/)
   - GitHub: pyroon (https://github.com/pavoni/pyroon)
   - GitHub: python-roon (https://github.com/relausen/python-roon)

### Capacités de l'API Roon

✅ **Ce que l'API PEUT faire:**
- Se connecter à Roon Core via découverte réseau
- Surveiller les zones de lecture actives
- Rechercher des pistes, albums, artistes dans la bibliothèque
- **Ajouter des pistes à la queue de lecture (playback queue)**
- Contrôler la lecture (play, pause, stop, skip)
- Récupérer les métadonnées des pistes en cours de lecture

❌ **Ce que l'API NE PEUT PAS faire:**
- **Créer une playlist programmatiquement**
- **Sauvegarder la queue en playlist**
- Modifier une playlist existante
- Supprimer une playlist
- Renommer une playlist

### Workflow Actuel (Manuel)

Pour créer une playlist avec l'API Roon, il faut:
1. Utiliser l'API pour rechercher et ajouter des pistes à la queue
2. **MANUELLEMENT** sauvegarder la queue comme playlist via l'interface Roon
3. L'étape 2 ne peut pas être automatisée

## 💡 Solution Alternative Proposée

Puisque la création directe dans Roon est impossible, nous proposons:

### 1. Génération de Playlists au Format JSON

**Fichier**: `output/playlists/playlist-YYYYMMDD-HHMMSS.json`

```json
{
  "name": "Top Sessions - Janvier 2026",
  "description": "Playlist générée automatiquement basée sur les sessions d'écoute fréquentes",
  "created_at": "2026-01-27T13:45:00Z",
  "algorithm": "top_sessions",
  "total_tracks": 25,
  "total_duration_minutes": 100,
  "tracks": [
    {
      "artist": "Nina Simone",
      "title": "Feeling Good",
      "album": "I Put A Spell On You",
      "timestamp": 1738000000,
      "source": "roon",
      "artist_spotify_image": "https://...",
      "album_spotify_image": "https://...",
      "album_lastfm_image": "https://..."
    }
  ]
}
```

### 2. Export au Format M3U (Standard Universel)

**Fichier**: `output/playlists/playlist-YYYYMMDD-HHMMSS.m3u`

```
#EXTM3U
#PLAYLIST:Top Sessions - Janvier 2026
#EXTIMG:https://...
#EXTINF:240,Nina Simone - Feeling Good
/path/to/music/Nina Simone/I Put A Spell On You/01 Feeling Good.flac
```

Compatible avec:
- VLC Media Player
- iTunes/Apple Music
- Winamp
- Foobar2000
- Et tout lecteur supportant M3U

### 3. Export au Format CSV (Import Excel/Sheets)

**Fichier**: `output/playlists/playlist-YYYYMMDD-HHMMSS.csv`

```csv
Artist,Title,Album,Duration,Source,Spotify URL,Discogs URL
Nina Simone,Feeling Good,I Put A Spell On You,240,roon,https://...,https://...
```

### 4. Export au Format Roon-Compatible (Pour Import Manuel)

**Fichier**: `output/playlists/playlist-YYYYMMDD-HHMMSS-roon.txt`

Format texte avec instructions d'import dans Roon:
```
=== PLAYLIST POUR ROON ===
Nom: Top Sessions - Janvier 2026
Description: Basée sur les sessions d'écoute fréquentes
Créée le: 2026-01-27

INSTRUCTIONS D'IMPORT DANS ROON:
1. Ouvrir Roon
2. Aller dans la section "Browse" > "Tracks"
3. Utiliser la fonction "Focus" pour rechercher chaque track ci-dessous
4. Ajouter chaque track à la queue de lecture
5. Une fois la queue complète, faire clic-droit > "Save as Playlist"
6. Nommer la playlist: "Top Sessions - Janvier 2026"

=== TRACKS (25) ===
1. Nina Simone - Feeling Good (I Put A Spell On You)
2. Miles Davis - So What (Kind of Blue)
...
```

## 📊 Algorithmes de Génération Proposés

### 1. Playlists Basées sur les Sessions (`top_sessions`)

- Analyse les sessions d'écoute continues (gap < 30 minutes)
- Sélectionne les pistes des sessions les plus longues
- Trie par fréquence d'apparition dans les sessions

### 2. Playlists Basées sur les Corrélations (`artist_correlations`)

- Identifie les artistes souvent écoutés ensemble
- Crée des playlists thématiques basées sur ces corrélations
- Exemple: "Jazz Sessions" avec Miles Davis + John Coltrane

### 3. Playlists Basées sur les Transitions (`artist_flow`)

- Analyse les transitions fréquentes entre artistes
- Crée un "flow" musical naturel basé sur vos habitudes
- Exemple: Nina Simone → Billie Holiday → Ella Fitzgerald

### 4. Playlists Temporelles (`time_based`)

- **Peak Hours**: Pistes les plus écoutées pendant les heures de pic
- **Weekend Vibes**: Pistes typiques du weekend
- **Evening Chill**: Pistes écoutées en soirée

### 5. Playlists Albums Complets (`complete_albums`)

- Sélectionne les albums écoutés en entier (≥5 pistes)
- Trie par fréquence d'écoute complète
- Idéal pour les albums concepts

### 6. Playlists Discovery (`rediscovery`)

- Pistes aimées mais non écoutées récemment (>30 jours)
- Encourage la redécouverte de votre bibliothèque
- Basé sur l'historique d'écoute

## 🔄 Intégration avec le Scheduler

La génération de playlists sera planifiable comme les haïkus:

**Configuration dans `roon-config.json`**:
```json
{
  "scheduled_tasks": {
    "generate_playlist": {
      "enabled": true,
      "frequency_unit": "day",
      "frequency_count": 7,
      "last_execution": null,
      "description": "Generate playlists based on listening patterns",
      "playlist_type": "top_sessions",
      "max_tracks": 25,
      "output_formats": ["json", "m3u", "csv", "roon-txt"]
    }
  }
}
```

## 🎯 Bénéfices de cette Approche

1. **Automatisation Complète**: Génération programmée via scheduler
2. **Multi-Format**: JSON, M3U, CSV, texte Roon
3. **Portabilité**: Utilisable hors de Roon (VLC, iTunes, etc.)
4. **Intelligence**: 6 algorithmes basés sur vos patterns réels
5. **Traçabilité**: Historique des playlists générées
6. **Flexibilité**: Configurable via GUI Streamlit

## ❓ Questions Ouvertes

### Pourquoi Roon ne supporte-t-il pas la création de playlists via API?

**Réponse de la communauté Roon**:
- Décision de design pour protéger l'intégrité de la bibliothèque
- Éviter les abus programmatiques (spam de playlists)
- Encourager l'interaction manuelle avec l'interface Roon
- L'API est principalement conçue pour la lecture, pas la gestion de contenu

### Est-ce que cela va changer?

**Peu probable à court terme**:
- Cette limitation existe depuis plusieurs années
- Pas de roadmap publique pour cette fonctionnalité
- La communauté a proposé des alternatives (comme la nôtre)

## 📚 Références

- [Roon API Documentation](https://github.com/RoonLabs/node-roon-api)
- [roonapi Python Library](https://pypi.org/project/roonapi/)
- [Community Discussion: Creating Playlists](https://community.roonlabs.com/t/creating-playlists/253188)
- [Community Discussion: Playlist Import Scripts](https://community.roonlabs.com/t/how-to-recreate-a-plex-based-playlist-import-python-script-in-roon/280914)

## 🔗 Voir Aussi

- [docs/README-SCHEDULER.md](./README-SCHEDULER.md) - Documentation du scheduler
- [src/analysis/analyze-listening-patterns.py](../src/analysis/analyze-listening-patterns.py) - Analyse existante
- [Issue #19](https://github.com/pat-the-geek/musique-collection-roon-tracker/issues/19) - Demande initiale
