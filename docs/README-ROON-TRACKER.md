# 🎵 Roon & Last.fm Music Tracker

Système de surveillance et d'enregistrement automatique des lectures Roon et Last.fm avec enrichissement des métadonnées via Spotify et Last.fm.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation rapide](#installation-rapide)
- [Installation manuelle](#installation-manuelle)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Fichiers générés](#fichiers-générés)
- [Dépannage](#dépannage)
- [Architecture](#architecture)

## ✨ Fonctionnalités

- 🔌 **Connexion automatique** à Roon Core via découverte réseau
- 🎧 **Surveillance en temps réel** de toutes les zones de lecture Roon
- 📻 **Surveillance Last.fm** - Vérification périodique des lectures Last.fm du mois en cours
- 🏷️ **Marquage de source** - Distinction entre lectures Roon et Last.fm
- 🔒 **Protection contre instances multiples** - Un seul processus actif à la fois
- 🚫 **Détection des doublons** - Évite l'enregistrement multiple d'une même lecture
- 🖼️ **Enrichissement automatique** avec URLs d'images publiques
  - Pochettes d'albums via Spotify et Last.fm
  - Vignettes d'artistes via Spotify
  - **Avantage**: Permet traitement ultérieur par IA et autres codes sans accès direct à Roon
- 🧹 **Nettoyage intelligent** des métadonnées
  - Gestion des artistes multiples (ex: "Artist1 / Artist2")
  - Suppression des annotations (ex: "(Remastered)", "(Live)", "[Italian]")
  - Préservation des informations importantes dans les crochets
- 🎯 **Validation stricte de l'artiste** lors des recherches Spotify
- 📊 **Système de scoring** pour sélectionner le meilleur match d'album
- ⏰ **Plage horaire configurable** pour l'enregistrement
- 💾 **Cache intelligent** pour minimiser les requêtes API
- 🔄 **Système de fallback avec validation** pour améliorer la fiabilité
- 📊 **Historique JSON** structuré et facilement exploitable

## 🔧 Prérequis

### Système
- macOS, Linux ou Windows
- Python 3.8 ou supérieur
- Connexion réseau locale (pour Roon Core)
- Connexion Internet (pour les API Spotify et Last.fm)

### Comptes requis

1. **Spotify Developer Account**
   - Créer une application sur https://developer.spotify.com/dashboard
   - Récupérer: `Client ID` et `Client Secret`

2. **Last.fm API Account**
   - Créer une application sur https://www.last.fm/api/account/create
   - Récupérer: `API Key` et `API Secret`
   - Noter votre username Last.fm

3. **Roon Core**
   - Roon Core doit être installé et en cours d'exécution
   - Sur le même réseau que le script

## 🚀 Installation rapide

### Script d'installation automatique

```bash
# Rendre le script exécutable
chmod +x setup-roon-tracker.sh

# Lancer l'installation
./setup-roon-tracker.sh
```

Le script va automatiquement:
1. ✅ Vérifier les prérequis (Python, pip, réseau)
2. 📦 Créer l'environnement virtuel Python
3. ⬇️ Installer les dépendances (roonapi, python-dotenv, certifi)
4. 🔑 Configurer les clés API (Spotify, Last.fm)
5. ⚙️ Configurer les heures d'écoute
6. 🧪 Tester la configuration
7. 🎬 Créer le script de lancement

## 📚 Installation manuelle

### 1. Créer l'environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
# ou
.venv\Scripts\activate     # Sur Windows
```

### 2. Installer les dépendances

```bash
pip install roonapi python-dotenv certifi
```

### 3. Créer le fichier `.env`

```bash
cat > .env << 'EOF'
# Configuration Spotify
SPOTIFY_CLIENT_ID=votre_client_id
SPOTIFY_CLIENT_SECRET=votre_client_secret

# Configuration Last.fm
API_KEY=votre_api_key_lastfm
API_SECRET=votre_api_secret_lastfm
LASTFM_USERNAME=votre_username_lastfm
EOF
```

### 4. Créer `roon-config.json`

```json
{
  "listen_start_hour": 6,
  "listen_end_hour": 23
}
```

## ⚙️ Configuration

### Fichier `.env`

Variables d'environnement pour les clés API:

```env
SPOTIFY_CLIENT_ID=abc123...
SPOTIFY_CLIENT_SECRET=xyz789...
API_KEY=lastfm_key...
API_SECRET=lastfm_secret...
LASTFM_USERNAME=votre_username
```

### Fichier `roon-config.json`

Configuration Roon et plages horaires:

```json
{
  "token": "auto-généré-lors-connexion",
  "host": "auto-découvert",
  "port": "auto-découvert",
  "listen_start_hour": 6,    # Heure de début (0-23)
  "listen_end_hour": 23       # Heure de fin (0-23)
}
```

**Paramètres modifiables:**
- `listen_start_hour`: Début d'enregistrement (défaut: 6h)
- `listen_end_hour`: Fin d'enregistrement (défaut: 23h)

Les autres champs (`token`, `host`, `port`) sont générés automatiquement.

## 🎮 Utilisation

### Lancement avec le script

```bash
./start-roon-tracker.sh
```

### Lancement manuel

```bash
source .venv/bin/activate
python3 chk-roon.py
```

### Premier lancement

1. Le script recherche automatiquement Roon Core sur le réseau
2. Une demande d'autorisation apparaît dans Roon
3. **Aller dans Roon:** Paramètres > Extensions
4. **Autoriser** "Python Roon Tracker"
5. Le script commence la surveillance

### Arrêt

Appuyez sur `Ctrl+C` pour arrêter proprement la surveillance.

### Protection contre instances multiples

Le système empêche automatiquement le lancement de plusieurs instances simultanées :

```bash
# Si vous tentez de lancer une deuxième instance
❌ Une instance du Roon Tracker est déjà en cours d'exécution.
   Arrêtez l'instance en cours avant d'en lancer une nouvelle.
   (Fichier de verrouillage: chk-roon.lock)
```

**Mécanisme :**
- Un fichier de verrouillage `chk-roon.lock` est créé au démarrage
- Le verrou est automatiquement libéré à l'arrêt du programme
- Si le processus crash, le verrou est libéré automatiquement par l'OS

## 📁 Fichiers générés

### `chk-roon.json`

Historique des lectures au format JSON:

```json
{
    "tracks": [
        {
            "timestamp": 1768648694,
            "date": "2026-01-17 11:18",
            "artist": "Nina Simone",
            "title": "Ain't No Use",
            "album": "Pastel Blues",
            "loved": false,
            "artist_spotify_image": "https://i.scdn.co/image/...",
            "album_spotify_image": "https://i.scdn.co/image/...",
            "album_lastfm_image": "https://lastfm.freetls.fastly.net/...",
            "source": "roon"
        }
    ]
}
```

### `roon-config.json`

Configuration et état de connexion Roon (mis à jour automatiquement).

### `chk-roon.lock`

Fichier de verrouillage temporaire (créé pendant l'exécution, supprimé à l'arrêt).
Contient le PID du processus actif pour empêcher les instances multiples.

## 🔍 Dépannage

### Aucun Roon Core trouvé

```
❌ Aucun Roon Core trouvé
```

**Solutions:**
1. Vérifier que Roon Core est lancé
2. Vérifier que le script et Roon Core sont sur le même réseau
3. Vérifier les pare-feu (autoriser la découverte mDNS)

### Token non reçu

```
❌ Token non reçu
```

**Solutions:**
1. Aller dans Roon > Paramètres > Extensions
2. Chercher "Python Roon Tracker"
3. Cliquer sur "Autoriser"

### Images toujours `null`

**Solutions:**
1. Vérifier les clés API dans `.env`
2. Tester manuellement:
   ```bash
   source .venv/bin/activate
   python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('SPOTIFY_CLIENT_ID'))"
   ```
3. Vérifier les messages de debug dans la console
4. La fonction `repair_null_spotify_images()` s'exécute automatiquement au démarrage et tente de récupérer les images manquantes

### Erreurs SSL/Certificats

```
❌ SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
```bash
# Mettre à jour certifi
pip install --upgrade certifi

# Ou installer les certificats Python (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Fichier de verrouillage bloqué

```
❌ Une instance du Roon Tracker est déjà en cours d'exécution.
```

**Si aucun processus n'est actif mais le message persiste:**

1. Vérifier qu'aucun processus n'est actif:
   ```bash
   ps aux | grep chk-roon.py
   ```

2. Si aucun processus, supprimer manuellement le verrou:
   ```bash
   rm chk-roon.lock
   ```

3. Relancer le tracker:
   ```bash
   ./start-roon-tracker.sh
   ```

## 🏗️ Architecture

### Flux d'exécution

```
┌──────────────────┐
│  Démarrage       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Chargement .env  │
│ et configuration │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Découverte Roon  │
│ Core (réseau)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Connexion +      │
│ Autorisation     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Boucle de        │◄────┐
│ surveillance     │     │
│ (45 secondes)    │     │
└────────┬─────────┘     │
         │               │
         ▼               │
┌──────────────────┐     │
│ Nouvelle piste ? │─Non─┤
└────────┬─────────┘     │
         │ Oui           │
         ▼               │
┌──────────────────┐     │
│ Dans plage       │     │
│ horaire ?        │─Non─┤
└────────┬─────────┘     │
         │ Oui           │
         ▼               │
┌──────────────────┐     │
│ Nettoyage        │     │
│ métadonnées      │     │
└────────┬─────────┘     │
         │               │
         ▼               │
┌──────────────────┐     │
│ Recherche images │     │
│ (Spotify/Last.fm)│     │
└────────┬─────────┘     │
         │               │
         ▼               │
┌──────────────────┐     │
│ Enregistrement   │     │
│ dans JSON        │     │
└────────┬─────────┘     │
         │               │
         └───────────────┘
```

### Modules principaux

| Module | Fonction |
|--------|----------|
| `clean_artist_name()` | Nettoyage des noms d'artistes |
| `clean_album_name()` | Nettoyage des noms d'albums (parenthèses + crochets) |
| `normalize_string_for_comparison()` | Normalisation pour comparaison insensible à la casse |
| `artist_matches()` | Validation de correspondance d'artiste avec tolérance |
| `get_spotify_token()` | Authentification OAuth Spotify |
| `search_spotify_artist_image()` | Recherche image artiste (avec retry automatique) |
| `search_spotify_album_image()` | Recherche couverture album (avec validation artiste, scoring, fallback et retry) |
| `search_lastfm_album_image()` | Recherche couverture Last.fm |
| `search_spotify_track_album()` | Recherche album d'une piste (pour radio) |
| `get_lastfm_recent_tracks()` | Récupération des lectures Last.fm récentes |
| `is_track_already_saved()` | Vérification des doublons |
| `repair_null_spotify_images()` | Réparation automatique des images manquantes |
| `test_roon_connection()` | Découverte et connexion Roon |
| `explore_roon_info()` | Boucle principale de surveillance |

### Système de cache

Les recherches d'images sont mises en cache pour optimiser les performances:

- **Cache artistes Spotify:** `{nom_artiste: url_image}`
- **Cache albums Spotify:** `{(artiste, album): url_image}`
- **Cache albums Last.fm:** `{(artiste, album): url_image}`
- **Cache token Spotify:** `{access_token, expires_at}`

## 📊 Format de sortie

### Structure JSON

```json
{
    "tracks": [
        {
            "timestamp": 1768648694,           // Unix timestamp
            "date": "2026-01-17 11:18",        // Date formatée
            "artist": "Nina Simone",            // Artiste (nettoyé)
            "title": "Ain't No Use",            // Titre
            "album": "Pastel Blues",            // Album (nettoyé)
            "loved": false,                     // False pour Roon, peut être true pour Last.fm
            "artist_spotify_image": "url",      // Image artiste Spotify
            "album_spotify_image": "url",       // Couverture Spotify
            "album_lastfm_image": "url",        // Couverture Last.fm
            "source": "roon"                    // Source: "roon" ou "lastfm"
        }
    ]
}
```

### Exemple de nettoyage

| Original | Nettoyé |
|----------|---------|
| `"Dalida / Raymond Lefèvre / Orchestra"` | `"Dalida"` |
| `"Nina Simone (Live)"` | `"Nina Simone"` |
| `"Circlesongs (Voice)"` | `"Circlesongs"` || `"9 [Italian]"` | `"9"` || `"Greatest Hits (Remastered 2024)"` | `"Greatest Hits"` |

### 📻 Traitement des stations de radio

Le tracker détecte automatiquement les écoutes de stations de radio et extrait intelligemment les informations musicales.

**Stations de radio détectées:**
- RTS La Première
- RTS Couleur 3
- RTS Espace 2
- RTS Option Musique
- Radio Meuh
- Radio Nova

**Fonctionnement:**

Lorsqu'une station de radio est détectée (le titre correspond à l'une des stations configurées), le script:

1. **Parse le champ artiste** qui contient en réalité les informations de la piste en cours
   - Format attendu: `"Artiste - Titre de la piste"`
   - Exemple: `"George Ezra - Budapest"` est parsé en artiste: `"George Ezra"` et titre: `"Budapest"`

2. **Filtre les faux positifs** (émissions de radio, journaux)
   - Vérifie la présence du séparateur `" - "` (espace-tiret-espace)
   - Vérifie que le nom de l'artiste est de longueur raisonnable (< 50 caractères)
   - Ignore les lignes sans format musical

3. **Recherche l'album sur Spotify** via la fonction `search_spotify_track_album()`
   - Recherche par artiste + titre pour trouver l'album d'origine
   - Fallback : recherche uniquement par titre si la première tentative échoue
   - Si aucun album trouvé, utilise "Inconnu"

4. **Enrichit normalement** avec les images d'artiste et d'album

**Exemple de traitement:**

```python
# Données brutes de Roon pour une radio
title = "RTS Couleur 3"
artist = "George Ezra - Budapest"
album = "Inconnu"

# Après traitement
title = "Budapest"           # Titre extrait
artist = "George Ezra"       # Artiste extrait
album = "Wanted on Voyage"   # Album trouvé via Spotify
```

**Messages de debug:**

```
[DEBUG] 📻 Station de radio détectée: RTS Couleur 3
[DEBUG] 📻 Extraction radio - Artiste: 'George Ezra', Titre: 'Budapest'
[DEBUG] 📻 Album trouvé: 'Wanted on Voyage'
```

Cette fonctionnalité permet de tracer précisément les musiques découvertes à la radio, même si Roon ne fournit pas directement les métadonnées musicales pour les flux radio.

## 🤝 Contribution

Pour contribuer ou signaler un bug:
1. Créer une issue avec description détaillée
2. Inclure les logs de debug
3. Préciser la version de Python et des dépendances

## 📝 Licence

Projet personnel - Patrick Ostertag © 2026

## 🔗 Liens utiles

- [Roon API Documentation](https://github.com/pavoni/python-roon-api)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Last.fm API](https://www.last.fm/api)
- [Python dotenv](https://github.com/theskumar/python-dotenv)

---

**Version:** 2.2.0  
**Dernière mise à jour:** 21 janvier 2026  
**Auteur:** Patrick Ostertag
