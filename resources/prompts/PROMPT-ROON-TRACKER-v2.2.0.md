# Prompt pour générer le Roon & Last.fm Music Tracker v2.2.0

## Contexte et objectif

Je souhaite créer un script Python professionnel qui surveille en temps réel les lectures musicales dans Roon (système de gestion de bibliothèque musicale) ET les lectures Last.fm du mois en cours, et enregistre automatiquement chaque piste jouée dans un fichier JSON unique avec des métadonnées enrichies provenant de Spotify et Last.fm.

**Version cible:** 2.2.0  
**Date:** 21 janvier 2026  
**Auteur:** Patrick Ostertag

## Spécifications fonctionnelles

### 1. Protection contre instances multiples (Système de verrouillage)

- Implémenter un système de verrouillage avec fichier `chk-roon.lock`
- Utiliser `fcntl.flock()` pour un verrou exclusif non-bloquant (LOCK_EX | LOCK_NB)
- Au démarrage du programme:
  - Tenter d'acquérir le verrou via `acquire_lock()`
  - Si échec (autre instance active): afficher message et terminer avec `sys.exit(1)`
  - Si succès: écrire le PID dans le fichier et continuer
- À l'arrêt du programme (bloc `finally`):
  - Toujours libérer le verrou via `release_lock()`
  - Supprimer le fichier de verrouillage
- Le verrou doit être automatiquement libéré si le processus crash (gestion OS)

**Fonctions à créer:**

```python
def acquire_lock() -> bool:
    """Acquiert un verrou exclusif pour empêcher instances multiples.
    
    Crée un fichier de verrouillage et tente d'obtenir un verrou exclusif
    (non-bloquant). Si une autre instance est déjà en cours, retourne False.
    
    Returns:
        True si le verrou a été acquis, False si une autre instance est active.
    """
    # Ouvrir/créer chk-roon.lock en mode écriture
    # Utiliser fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # Écrire le PID dans le fichier
    # Retourner True si succès, False si IOError
```

```python
def release_lock() -> None:
    """Libère le verrou et supprime le fichier de verrouillage.
    
    Appelée automatiquement à la fin du programme pour nettoyer
    les ressources et permettre le lancement d'une nouvelle instance.
    """
    # Libérer avec fcntl.flock(handle, fcntl.LOCK_UN)
    # Fermer le fichier
    # Supprimer chk-roon.lock
```

**Messages:**
```
❌ Une instance du Roon Tracker est déjà en cours d'exécution.
   Arrêtez l'instance en cours avant d'en lancer une nouvelle.
   (Fichier de verrouillage: chk-roon.lock)
```

```
🔓 Verrou libéré - une nouvelle instance peut être lancée
```

### 2. Connexion à Roon Core

- Découvrir automatiquement le serveur Roon Core sur le réseau local via `RoonDiscovery`
- Établir une connexion via l'API Roon en utilisant la bibliothèque `roonapi`
- Gérer l'authentification avec un système de token persistant
- Sauvegarder le token, host et port dans `roon-config.json`
- Afficher des messages informatifs pendant le processus de connexion
- Timeout de connexion: 30 secondes maximum

**Fonction `test_roon_connection()`:**
1. Charger la configuration existante
2. Découvrir Roon Core avec `RoonDiscovery(None).all()`
3. Si aucun serveur trouvé, afficher aide et retourner None
4. Extraire host et port du tuple retourné
5. Se connecter avec `RoonApi(appinfo, token, host, port, blocking_init=False)`
6. Attendre le token jusqu'à 30 secondes
7. Si token reçu, retourner l'instance RoonApi

### 3. Surveillance des lectures Roon

- Surveiller en continu toutes les zones de lecture Roon actives
- Détecter les nouvelles pistes en cours de lecture (state='playing')
- Éviter les doublons avec `last_track_key` (combinaison zone_id + track_key)
- Extraire les informations depuis `now_playing.three_line`:
  - line1 = Titre de la piste
  - line2 = Nom de l'artiste
  - line3 = Nom de l'album
- Vérifier l'état toutes les 45 secondes
- Marquer la source comme `"roon"`

**Détection et traitement des stations de radio:**
- Liste des stations: RTS La Première, RTS Couleur 3, RTS Espace 2, RTS Option Musique, Radio Nova
- Fonction `is_radio_station(title)`: Vérifie si le titre correspond à une station
- Fonction `parse_radio_artist_field(artist_field)`: Parse le format "Artiste - Titre"
  - Vérifier présence de " - " (espace-tiret-espace)
  - Vérifier longueur raisonnable de l'artiste (< 50 caractères)
  - Retourner tuple (artiste, titre) ou None si pas musical
- Si radio détectée:
  - Parser le champ artist pour extraire artiste et titre réels
  - Appeler `search_spotify_track_album()` pour trouver l'album
  - Si album trouvé, continuer l'enrichissement normal
  - Si non trouvé ou format non musical, ignorer l'écoute

### 4. Surveillance des lectures Last.fm

**Fonction `get_lastfm_recent_tracks()`:**
- Récupérer les 5 dernières lectures de l'utilisateur Last.fm
- Période: depuis le début du mois en cours jusqu'à maintenant (UTC)
- Utiliser `pylast` et la variable `LASTFM_USERNAME`
- Calculer time_from et time_to en timestamps Unix
- Utiliser `user.get_recent_tracks(limit=5, time_from=time_from, time_to=time_to)`
- Retourner liste de track_items
- Gérer gracieusement l'absence de connexion Last.fm

**Fonction `is_track_already_saved(artist, title, album, timestamp)`:**
- Charger l'historique depuis `chk-roon.json`
- Vérifier si une lecture identique existe déjà
- Tolérance de ±60 secondes sur le timestamp
- Retourner True si trouvée, False sinon

**Intégration dans la boucle principale:**
- À chaque itération (toutes les 45 secondes):
  - Vérifier les lectures Last.fm
  - Parcourir en ordre inverse (du plus ancien au plus récent)
  - Pour chaque lecture récente:
    - Ignorer si timestamp <= last_lastfm_timestamp (déjà traitée)
    - Vérifier avec `is_track_already_saved()` pour éviter doublons avec Roon
    - Vérifier la plage horaire d'écoute (track_datetime.hour)
    - Extraire: artist, title, album, loved, timestamp
    - Enrichir avec images (Spotify artiste, Spotify album, Last.fm album)
    - Sauvegarder avec `source: "lastfm"`
    - Afficher "🎧 [Last.fm]" au lieu de "🎵"
    - Mettre à jour `last_lastfm_timestamp` après chaque lecture
  - Afficher le nombre de nouvelles lectures Last.fm trouvées

### 5. Gestion des plages horaires

**Fonction `is_within_listening_hours(start_hour, end_hour)`:**
- Comparer l'heure système actuelle avec la plage configurée
- Retourner True si dans la plage, False sinon
- La comparaison inclut l'heure de fin (ex: end_hour=23 inclut 23:00-23:59)

**Paramètres dans `roon-config.json`:**
- `listen_start_hour` (défaut: 6) - Heure de début (0-23)
- `listen_end_hour` (défaut: 23) - Heure de fin (0-23)

**Comportement:**
- Ignorer les lectures en dehors de cette plage avec un message informatif
- Afficher l'heure actuelle et la plage configurée lors de l'ignorance
- Mettre à jour `last_track_key` même si ignoré pour éviter spam de messages

### 6. Nettoyage intelligent des métadonnées

**Fonction `clean_artist_name(artist_name: str) -> str`:**
```python
"""Nettoie et normalise le nom d'un artiste pour améliorer les recherches.
    
Cette fonction traite les cas courants de métadonnées Roon incluant plusieurs
artistes séparés par des slashes ou des informations additionnelles entre parenthèses.

Args:
    artist_name: Nom brut de l'artiste tel que fourni par Roon.
    
Returns:
    Nom d'artiste nettoyé et normalisé.
    
Examples:
    >>> clean_artist_name("Dalida / Raymond Lefèvre")
    'Dalida'
    >>> clean_artist_name("Nina Simone (Live Version)")
    'Nina Simone'
"""
```

Traitement:
- Vérifier si 'Inconnu' → retourner tel quel
- Si contient '/', prendre uniquement le premier artiste avant '/'
- Supprimer les métadonnées entre parenthèses en fin de chaîne avec regex `r'\s*\([^)]*\)\s*$'`
- Normaliser les espaces avec `.strip()`

**Fonction `clean_album_name(album_name: str) -> str`:**
```python
"""Nettoie et normalise le nom d'un album pour améliorer les recherches.

Supprime les métadonnées additionnelles souvent présentes dans les noms d'albums
Roon, comme les mentions de format, version, ou année entre parenthèses ou crochets.

Args:
    album_name: Nom brut de l'album tel que fourni par Roon.
    
Returns:
    Nom d'album nettoyé et normalisé.
    
Examples:
    >>> clean_album_name("Circlesongs (Voice)")
    'Circlesongs'
    >>> clean_album_name("9 [Italian]")
    '9'
"""
```

Traitement:
- Vérifier si 'Inconnu' → retourner tel quel
- Supprimer les métadonnées entre parenthèses () OU crochets [] en fin de chaîne
- Regex: `r'\s*[\(\[][^\)\]]*[\)\]]\s*$'`
- Normaliser les espaces avec `.strip()`

### 7. Enrichissement avec Spotify (Version 2.2.0 - Améliorée)

**Authentification OAuth 2.0:**
- Fonction `get_spotify_token()` avec mise en cache
- Utiliser Client Credentials Flow
- Récupérer les identifiants depuis `.env`:
  - `SPOTIFY_CLIENT_ID`
  - `SPOTIFY_CLIENT_SECRET`
- Mettre en cache le token avec son expiration dans `spotify_token_cache`
- Rafraîchir automatiquement 60 secondes avant expiration
- Encoder les credentials en Base64 pour l'authentification

**Système de retry automatique (v2.2.0):**
- Paramètre `max_retries` (défaut: 3) pour toutes les fonctions de recherche
- Gestion automatique des erreurs HTTP:
  - **HTTP 401 (Unauthorized)**: Token expiré
    - Appeler `get_spotify_token()` pour obtenir nouveau token
    - Réessayer la requête avec le nouveau token
    - Message: `[DEBUG] ⚠️ Token expiré (401), tentative X/Y`
  - **HTTP 429 (Rate Limit)**: Trop de requêtes
    - Attendre 2 secondes
    - Réessayer automatiquement
    - Message: `[DEBUG] ⚠️ Rate limit (429), attente de 2 secondes...`
  - **Autres erreurs**: Attendre 1 seconde et réessayer
- Abandonner après max_retries tentatives

**Fonction `normalize_string_for_comparison(s: str) -> str`:**
```python
"""Normalise une chaîne pour comparaison (minuscules, sans espaces multiples).

Args:
    s: Chaîne à normaliser
    
Returns:
    Chaîne normalisée en minuscules avec espaces uniques
    
Examples:
    >>> normalize_string_for_comparison("Nina  SIMONE")
    'nina simone'
"""
```
- Convertir en minuscules avec `.lower()`
- Supprimer espaces superflus avec `.strip()` et `.split()`
- Rejoindre avec espace unique: `' '.join(s.lower().strip().split())`

**Fonction `artist_matches(search_artist: str, found_artist: str) -> bool`:**
```python
"""Vérifie si deux noms d'artistes correspondent (avec tolérance).

Args:
    search_artist: Nom de l'artiste recherché
    found_artist: Nom de l'artiste trouvé dans les résultats
    
Returns:
    True si les artistes correspondent, False sinon
    
Examples:
    >>> artist_matches("Nina Simone", "Nina Simone")
    True
    >>> artist_matches("Nina Simone", "nina simone")
    True
    >>> artist_matches("Various", "Various Artists")
    True
    >>> artist_matches("Eros Ramazzotti", "Madonna")
    False
"""
```

Règles de validation:
1. Normaliser les deux chaînes avec `normalize_string_for_comparison()`
2. Si identiques → True
3. Si l'un commence par "various" et l'autre aussi → True (gère Various Artists)
4. Si l'un contient l'autre (dans n'importe quel sens) → True (gère "The Beatles" vs "Beatles")
5. Sinon → False

**Recherche d'images d'artistes avec retry:**
```python
def search_spotify_artist_image(token: str | None, artist_name: str, max_retries: int = 3) -> str | None:
```

Traitement:
1. Vérifier le cache: `cache_artist_images_spotify`
2. Si pas de token, retourner None
3. Nettoyer le nom avec `clean_artist_name()`
4. Boucle de retry (max_retries):
   - Si attempt > 0: Récupérer nouveau token avec `get_spotify_token()`
   - Rechercher sur Spotify: `type=artist`, `limit=1`
   - Query: `artist:{cleaned_artist}`
   - Gestion des erreurs HTTP:
     - 401: continuer la boucle (nouveau token)
     - 429: attendre 2s et continuer
     - Autres: attendre 1s et continuer
   - Si succès: récupérer première image de `items[0]["images"][0]["url"]`
5. Mettre en cache (avec nom original comme clé)
6. Retourner l'URL ou None

Messages de debug:
```
[DEBUG] Recherche Spotify artist - Original: 'X' -> Nettoyé: 'Y'
[DEBUG] Tentative X/Y - Récupération d'un nouveau token Spotify
[DEBUG] ✅ Spotify artist 'Y': https://...
[DEBUG] ⚠️ Aucune image trouvée pour l'artiste 'Y'
[DEBUG] ❌ Impossible de récupérer un token Spotify
```

**Recherche d'images d'albums avec validation stricte et scoring (v2.2.0):**
```python
def search_spotify_album_image(token: str | None, artist_name: str, album_name: str, max_retries: int = 3) -> str | None:
```

Traitement en deux essais avec validation:

**Essai 1 - Recherche avec artiste + album:**
1. Nettoyer les noms avec `clean_artist_name()` et `clean_album_name()`
2. Query: `album:{cleaned_album} artist:{cleaned_artist}`
3. **Récupérer 5 résultats** (`limit=5`) au lieu d'un seul
4. Pour chaque résultat:
   - Vérifier présence d'images
   - Extraire le nom de l'artiste principal: `item['artists'][0]['name']`
   - **Valider l'artiste** avec `artist_matches(cleaned_artist, album_artist)`
   - Si validation échoue: afficher message et passer au suivant
   - Si validation réussit: calculer un score de pertinence

**Système de scoring (v2.2.0):**
- Normaliser les noms d'albums avec `normalize_string_for_comparison()`
- Calcul du score:
  - **100 points**: Correspondance exacte (norm_searched == norm_found)
  - **80 points**: L'un contient l'autre (in)
  - **50 points**: Score basé sur mots communs (ratio = mots_communs / mots_recherchés)
- Garder le meilleur match avec le score le plus élevé
- **Seuil de validation Essai 1**: score > 50

**Essai 2 - Fallback sans artiste (si Essai 1 échoue):**
1. Query: uniquement `album:{cleaned_album}`
2. Même logique de validation d'artiste et scoring
3. **Seuil de validation Essai 2**: score > 30 (plus tolérant)
4. Note: Validation d'artiste encore plus importante en fallback

**Gestion du retry:**
- À chaque tentative, possibilité de récupérer nouveau token
- Gestion des erreurs 401, 429 identique aux autres fonctions
- Les deux essais sont dans la même boucle de retry

Mise en cache:
- Clé composite: `(artist_name, album_name)` (noms originaux)
- Cache: `cache_album_images_spotify`

Messages de debug détaillés:
```
[DEBUG] Recherche Spotify album - Album: 'X' -> 'Y', Artist: 'A' -> 'B'
[DEBUG] ⚠️ Artiste non correspondant: recherché 'X', trouvé 'Y'
[DEBUG] 🎯 Match trouvé: 'Album Name' par 'Artist' (score: 85.0)
[DEBUG] ✅ Spotify album 'Album' (score: 85.0): https://...
[DEBUG] ⚠️ Aucun match avec artiste validé (meilleur score: 40.0)
[DEBUG] Fallback: recherche sans artiste (avec validation)...
[DEBUG] ⚠️ Fallback - Artiste non correspondant: 'X' != 'Y'
[DEBUG] 🎯 Fallback match: 'Album' par 'Artist' (score: 95.0)
[DEBUG] ✅ Spotify album (fallback validé) 'Album' (score: 95.0): https://...
```

**Recherche d'album pour une piste radio:**
```python
def search_spotify_track_album(token: str | None, artist_name: str, track_title: str, max_retries: int = 3) -> str | None:
```

Utilisée uniquement pour les stations de radio pour retrouver l'album d'origine.

Traitement:
1. Nettoyer artiste et titre
2. **Essai 1**: Recherche `track:{title} artist:{artist}`, type=track
3. **Essai 2**: Fallback uniquement par titre
4. Extraire le nom d'album de `tracks[0]['album']['name']`
5. Même système de retry que les autres fonctions
6. Retourner le nom de l'album ou None

### 8. Enrichissement avec Last.fm

**Initialisation de la connexion:**
```python
lastfm_network = None
if API_KEY and API_SECRET:
    try:
        lastfm_network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
        print("✅ Connexion Last.fm initialisée")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de Last.fm: {e}")
```

**Fonction `search_lastfm_album_image(artist_name: str, album_name: str) -> str | None`:**
- Vérifier le cache: `cache_album_images_lastfm`
- Nettoyer les noms avec `clean_artist_name()` et `clean_album_name()`
- Encoder les paramètres avec `urllib.parse.quote()`
- Appeler l'API: `method=album.getinfo`
- URL: `https://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={API_KEY}&artist={artist}&album={album}&format=json`
- Récupérer la plus grande image (dernière dans la liste): `images[-1]["#text"]`
- Vérifier que l'URL n'est pas vide
- Mettre en cache avec clé composite `(artist_name, album_name)`
- Retourner l'URL ou None

### 9. Réparation automatique des images manquantes (v2.1.0+)

**Fonction `repair_null_spotify_images() -> int`:**
Exécutée automatiquement au démarrage du programme pour réparer les images manquantes.

```python
"""Parcourt le fichier JSON et répare les images Spotify manquantes (null).

Charge chk-roon.json, identifie les entrées avec des images Spotify null,
et tente de les récupérer à nouveau. Sauvegarde le fichier uniquement s'il y a
eu des modifications.

Returns:
    Nombre d'images réparées avec succès.
"""
```

Traitement:
1. Afficher message: `🔧 Détection d'anomalies - Vérification des images Spotify manquantes...`
2. Charger l'historique avec `load_tracks_history()`
3. Récupérer un token Spotify frais
4. Compter les images null (artistes et albums, ignorer 'Inconnu')
5. Si aucune null: afficher `✅ Aucune image Spotify manquante - Le fichier est OK`
6. Sinon: afficher décompte et `🔄 Réparation en cours...`
7. Pour chaque piste:
   - Si `artist_spotify_image` null et artist != 'Inconnu':
     - Appeler `search_spotify_artist_image()`
     - Si récupérée: modifier la piste, incrémenter compteur
     - Attendre 0.5s (rate limiting)
   - Même logique pour `album_spotify_image`
8. Si modifications effectuées:
   - Sauvegarder le fichier
   - Afficher: `✅ Réparation terminée: X images récupérées et sauvegardées`
9. Retourner le nombre d'images réparées

Messages:
```
🔧 Détection d'anomalies - Vérification des images Spotify manquantes...
📊 Trouvé X images d'artistes manquantes et Y images d'albums manquantes
🔄 Réparation en cours...

[1/150] Réparation artiste: Nina Simone
  ✅ Image artiste récupérée
[2/150] Réparation album: Nina Simone - Pastel Blues
  ✅ Image album récupérée

✅ Réparation terminée: 25 images récupérées et sauvegardées
```

### 10. Système de cache

Implémenter cinq dictionnaires de cache globaux:

```python
cache_artist_images_spotify = {}      # {artist_name: url}
cache_album_images_spotify = {}       # {(artist, album): url}
cache_album_images_lastfm = {}        # {(artist, album): url}
spotify_token_cache = {
    "access_token": None,
    "expires_at": 0
}
```

Principes:
- Toujours vérifier le cache AVANT toute requête API
- Utiliser le nom original (non nettoyé) comme clé pour le cache
- Pour les albums: clé composite `(artist_name, album_name)`
- Sauvegarder même les résultats négatifs (None) pour éviter re-recherches

### 11. Enregistrement des données

**Structure du fichier `chk-roon.json`:**
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

**Fonction `load_tracks_history() -> dict`:**
- Charger le fichier `chk-roon.json` s'il existe
- Gérer les erreurs de lecture/parsing JSON
- Retourner `{"tracks": []}` par défaut
- Messages: `⚠️ Erreur lors du chargement de {ROON_TRACKS_FILE}: {e}`

**Fonction `save_track(track_info: dict) -> bool`:**
- Charger l'historique actuel
- Insérer la nouvelle piste EN DÉBUT de liste: `tracks.insert(0, track_info)`
- Sauvegarder avec `json.dump(history, f, ensure_ascii=False, indent=4)`
- Retourner True si succès, False si erreur
- Messages: `⚠️ Erreur lors de la sauvegarde dans {ROON_TRACKS_FILE}: {e}`

**Champs requis dans track_info:**
- `timestamp` (int): Unix timestamp en UTC
- `date` (str): Date formatée '%Y-%m-%d %H:%M'
- `artist` (str): Nom de l'artiste
- `title` (str): Titre de la piste
- `album` (str): Nom de l'album
- `loved` (bool): False pour Roon, peut être True pour Last.fm
- `artist_spotify_image` (str|None): URL image artiste
- `album_spotify_image` (str|None): URL image album Spotify
- `album_lastfm_image` (str|None): URL image album Last.fm
- `source` (str): "roon" ou "lastfm"

### 12. Configuration et fichiers

**Fichier `.env` (variables d'environnement):**
```env
# Configuration Spotify
SPOTIFY_CLIENT_ID=abc123...
SPOTIFY_CLIENT_SECRET=xyz789...

# Configuration Last.fm
API_KEY=lastfm_key...
API_SECRET=lastfm_secret...
LASTFM_USERNAME=votre_username
```

Charger avec:
```python
from dotenv import load_dotenv
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# etc.
```

**Fichier `roon-config.json`:**
```json
{
  "token": "auto-généré-lors-connexion",
  "host": "auto-découvert",
  "port": "auto-découvert",
  "listen_start_hour": 6,
  "listen_end_hour": 23
}
```

**Fonction `load_roon_config() -> dict`:**
- Charger le fichier s'il existe
- Ajouter valeurs par défaut si manquantes:
  - `listen_start_hour`: 6
  - `listen_end_hour`: 23
- Retourner dict avec au moins ces deux clés
- Messages: `📂 Configuration chargée depuis {ROON_CONFIG_FILE}`

**Fonction `save_roon_config(config: dict) -> bool`:**
- Sauvegarder avec `json.dump(config, f, indent=2)`
- Retourner True si succès, False si erreur
- Messages: `💾 Configuration sauvegardée dans {ROON_CONFIG_FILE}`

### 13. Messages de debug détaillés et informatifs

**Format des messages console:**

Émojis standard:
- 🎵 : Lectures Roon
- 🎧 : Lectures Last.fm
- 🔊 : Zones audio
- 📻 : Stations de radio
- 🎯 : Match trouvé (scoring)
- ✅ : Succès
- ⚠️ : Avertissements
- ❌ : Erreurs
- 📂 : Fichiers
- 💾 : Sauvegardes
- 🔧 : Réparation
- 📊 : Statistiques
- 🔄 : Processus en cours
- 🔑 : Token/Authentification
- 🔓 : Libération de verrou
- ⏱️ : Timeout
- [DEBUG] : Messages de débogage techniques

**Messages pour chaque étape:**

1. Démarrage:
```
🎵 Initialisation de la connexion à Roon...
⏳ Recherche de Roon Core sur le réseau...
✅ Roon Core trouvé: ('192.168.1.253', '9330')
✅ Connexion établie avec Roon Core!
📍 Token: abc123...
```

2. Informations système:
```
📊 Informations Roon:
--------------------------------------------------

🔊 Zones disponibles: 1
  • Zone principale (ID: 12345)

🎧 Sorties audio disponibles: 2
  • Haut-parleurs (ID: 67890)
    État: playing

==================================================
🎵 Surveillance des lectures en cours...
   Plage horaire active: 06:00 - 23:59
   (Appuyez sur Ctrl+C pour arrêter)
==================================================
```

3. Token Spotify:
```
✅ Token Spotify récupéré: BQDxK8j3m...
[DEBUG] Tentative 2/3 - Récupération d'un nouveau token Spotify
[DEBUG] ❌ Impossible de récupérer un token Spotify
```

4. Réparation d'images (au démarrage):
```
🔧 Détection d'anomalies - Vérification des images Spotify manquantes...
[DEBUG] Aucune piste à réparer
✅ Aucune image Spotify manquante - Le fichier est OK

📊 Trouvé 15 images d'artistes manquantes et 8 images d'albums manquantes
🔄 Réparation en cours...

[1/150] Réparation artiste: Nina Simone
  ✅ Image artiste récupérée
[2/150] Réparation album: Nina Simone - Pastel Blues
  ✅ Image album récupérée

✅ Réparation terminée: 23 images récupérées et sauvegardées
⚠️ Aucune image n'a pu être récupérée
```

5. Lectures Last.fm:
```
[DEBUG] Vérification des lectures Last.fm...
[DEBUG] Last.fm: 5 lectures récupérées pour username (5 dernières)
[DEBUG] Last.fm: Piste déjà enregistrée: Artist - Title (timestamp)
[DEBUG] Last.fm: Hors plage horaire: Artist - Title (03:00)
[DEBUG] 3 nouvelle(s) lecture(s) Last.fm enregistrée(s)
[DEBUG] Aucune nouvelle lecture Last.fm

🎧 [Last.fm] 2026-01-17 14:23 - George Ezra - Budapest (Wanted on Voyage) ❤️
   Artist Spotify img: https://...
   Album Spotify img: https://...
   Album Last.fm img: https://...
```

6. Lectures Roon:
```
[DEBUG] Roon three_line - line1: Ain't No Use, line2: Nina Simone, line3: Pastel Blues
```

7. Stations de radio:
```
[DEBUG] 📻 Station de radio détectée: RTS Couleur 3
[DEBUG] 📻 Extraction radio - Artiste: 'George Ezra', Titre: 'Budapest'
[DEBUG] 📻 Album trouvé: 'Wanted on Voyage'
[DEBUG] 📻 Album non trouvé - Écoute radio ignorée
[DEBUG] 📻 Format non musical détecté (émission/journal) - Écoute ignorée
```

8. Nettoyage métadonnées:
```
[DEBUG] Recherche Spotify pour artiste: 'Nina Simone', album: 'Pastel Blues'
[DEBUG] Recherche Spotify artist - Original: 'Dalida / Raymond' -> Nettoyé: 'Dalida'
[DEBUG] Recherche Spotify album - Album: '9 [Italian]' -> '9', Artist: 'Eros (2)' -> 'Eros'
[DEBUG] Recherche Last.fm - Album: 'Pastel Blues' -> 'Pastel Blues', Artist: 'Nina Simone' -> 'Nina Simone'
```

9. Validation d'artiste et scoring:
```
[DEBUG] ⚠️ Artiste non correspondant: recherché 'Nina Simone', trouvé 'Madonna'
[DEBUG] 🎯 Match trouvé: 'Pastel Blues' par 'Nina Simone' (score: 100.0)
[DEBUG] 🎯 Fallback match: '9' par 'Eros Ramazzotti' (score: 80.0)
[DEBUG] ⚠️ Aucun match avec artiste validé (meilleur score: 40.0)
[DEBUG] Fallback: recherche sans artiste (avec validation)...
[DEBUG] ⚠️ Fallback - Artiste non correspondant: 'Various' != 'Nina Simone'
```

10. Résultats recherche:
```
[DEBUG] ✅ Spotify artist 'Nina Simone': https://i.scdn.co/image/...
[DEBUG] ⚠️ Aucune image trouvée pour l'artiste 'Unknown Artist'
[DEBUG] ✅ Spotify album 'Pastel Blues' (score: 95.0): https://...
[DEBUG] ✅ Spotify album (fallback validé) '9' (score: 85.0): https://...
[DEBUG] ✅ Last.fm album 'Pastel Blues': https://lastfm.freetls.fastly.net/...
[DEBUG] ⚠️ Last.fm: aucune image pour 'Album Unknown'
[DEBUG] ❌ Erreur HTTP 429 Spotify artist 'X': ...
```

11. Enregistrement:
```
🎵 2026-01-17 11:18 - Nina Simone - Ain't No Use (Pastel Blues)
   Artist Spotify img: https://i.scdn.co/image/...
   Album Spotify img: https://i.scdn.co/image/...
   Album Last.fm img: https://lastfm.freetls.fastly.net/...

[DEBUG] Résultats - Artist Spotify: https://..., Album Spotify: https://..., Album Last.fm: https://...
```

12. Plage horaire:
```
⏸️  03:42 - Hors plage horaire d'écoute (06:00-23:59)
   Piste ignorée: Nina Simone - Feeling Good
```

13. Arrêt:
```
⚠️ Arrêt de la surveillance
⚠️ Interruption par l'utilisateur
🔓 Verrou libéré - une nouvelle instance peut être lancée
```

### 14. Flux d'exécution principal

**Fonction `main()` - Point d'entrée:**

```python
def main() -> None:
    """Point d'entrée principal du programme.
    
    Orchestre le flux d'exécution complet:
    1. Vérification qu'aucune autre instance n'est en cours
    2. Chargement de la configuration Roon
    3. Réparation automatique des images manquantes
    4. Connexion au serveur Roon Core
    5. Sauvegarde du token d'authentification si nouveau
    6. Lancement de la surveillance des lectures
    
    Le programme s'exécute en boucle infinie jusqu'à interruption manuelle
    (Ctrl+C) ou erreur fatale.
    """
```

Structure complète:
```python
def main() -> None:
    # 1. VERROUILLAGE
    if not acquire_lock():
        print("❌ Une instance du Roon Tracker est déjà en cours d'exécution.")
        print("   Arrêtez l'instance en cours avant d'en lancer une nouvelle.")
        print(f"   (Fichier de verrouillage: {ROON_LOCK_FILE})")
        sys.exit(1)
    
    try:
        # 2. CHARGEMENT CONFIGURATION
        config = load_roon_config()
        
        # 3. RÉPARATION AUTOMATIQUE DES IMAGES
        repair_null_spotify_images()
        
        # 4. TEST CONNEXION ROON
        roonapi = test_roon_connection()
        
        if roonapi:
            # 5. SAUVEGARDE TOKEN SI NOUVEAU/CHANGÉ
            if roonapi.token and (not config.get('token') or config.get('token') != roonapi.token):
                discover = RoonDiscovery(None)
                servers = discover.all()
                if servers:
                    host, port = servers[0]
                    config['token'] = roonapi.token
                    config['host'] = host
                    config['port'] = port
                    # Conserver les heures d'écoute existantes
                    if 'listen_start_hour' not in config:
                        config['listen_start_hour'] = 6
                    if 'listen_end_hour' not in config:
                        config['listen_end_hour'] = 23
                    save_roon_config(config)
                    print(f"\n✅ Configuration sauvegardée")
            
            # 6. LANCEMENT SURVEILLANCE
            explore_roon_info(roonapi, config)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 7. LIBÉRATION VERROU (TOUJOURS)
        release_lock()
        print("\n🔓 Verrou libéré - une nouvelle instance peut être lancée")


if __name__ == "__main__":
    main()
```

**Fonction `explore_roon_info(roonapi: RoonApi, config: dict) -> None`:**

Boucle principale de surveillance:

```python
def explore_roon_info(roonapi: RoonApi, config: dict) -> None:
    """Surveille et enregistre en continu les lectures musicales Roon.
    
    Boucle principale qui:
    1. Affiche les informations système (zones, sorties audio)
    2. Surveille en continu les pistes jouées dans toutes les zones
    3. Vérifie les lectures Last.fm périodiquement
    4. Vérifie la plage horaire d'écoute configurée
    5. Enrichit les métadonnées avec images Spotify et Last.fm
    6. Enregistre les nouvelles lectures dans le fichier JSON
    
    Args:
        roonapi: Instance RoonApi connectée et authentifiée
        config: Dictionnaire de configuration contenant listen_start_hour et listen_end_hour
    """
```

Structure complète:
```python
def explore_roon_info(roonapi: RoonApi, config: dict) -> None:
    if not roonapi:
        return
    
    # 1. EXTRACTION CONFIGURATION
    listen_start_hour = config.get('listen_start_hour', 6)
    listen_end_hour = config.get('listen_end_hour', 23)
    
    # 2. AFFICHAGE INFORMATIONS SYSTÈME
    print("\n📊 Informations Roon:")
    print("-" * 50)
    
    zones = roonapi.zones
    print(f"\n🔊 Zones disponibles: {len(zones)}")
    for zone_id, zone in zones.items():
        print(f"  • {zone['display_name']} (ID: {zone_id})")
    
    outputs = roonapi.outputs
    print(f"\n🎧 Sorties audio disponibles: {len(outputs)}")
    for output_id, output in outputs.items():
        print(f"  • {output['display_name']} (ID: {output_id})")
        print(f"    État: {output.get('state', 'inconnu')}")
    
    print("\n" + "=" * 50)
    print(f"🎵 Surveillance des lectures en cours...")
    print(f"   Plage horaire active: {listen_start_hour:02d}:00 - {listen_end_hour:02d}:59")
    print("   (Appuyez sur Ctrl+C pour arrêter)")
    print("=" * 50)
    
    # 3. RÉCUPÉRATION TOKEN SPOTIFY
    spotify_token = get_spotify_token()
    if spotify_token:
        print(f"✅ Token Spotify récupéré: {spotify_token[:20]}...")
    else:
        print("⚠️ Impossible de récupérer le token Spotify - les images Spotify ne seront pas disponibles")
    
    # 4. VARIABLES DE SUIVI
    last_track_key = None  # Pour Roon
    last_lastfm_timestamp = 0  # Pour Last.fm
    
    # 5. BOUCLE INFINIE
    try:
        while True:
            # A. VÉRIFICATION LAST.FM
            if lastfm_network and LASTFM_USERNAME:
                try:
                    print("\n[DEBUG] Vérification des lectures Last.fm...")
                    lastfm_tracks = get_lastfm_recent_tracks()
                    
                    new_tracks_count = 0
                    for track_item in reversed(lastfm_tracks):
                        timestamp = int(track_item.timestamp)
                        
                        # Ignorer si déjà traité
                        if timestamp <= last_lastfm_timestamp:
                            continue
                        
                        # Extraire informations
                        artist = track_item.track.artist.name
                        title = track_item.track.title
                        album = track_item.album or "Album inconnu"
                        loved = getattr(track_item, 'loved', False)
                        
                        # Vérifier doublons avec Roon
                        if is_track_already_saved(artist, title, album, timestamp):
                            print(f"[DEBUG] Last.fm: Piste déjà enregistrée: {artist} - {title} ({timestamp})")
                            continue
                        
                        # Vérifier plage horaire
                        track_datetime = datetime.fromtimestamp(timestamp, timezone.utc).astimezone()
                        track_hour = track_datetime.hour
                        if track_hour < listen_start_hour or track_hour > listen_end_hour:
                            print(f"[DEBUG] Last.fm: Hors plage horaire: {artist} - {title} ({track_hour:02d}:00)")
                            continue
                        
                        # Enrichir avec images
                        artist_spotify_image = search_spotify_artist_image(spotify_token, artist)
                        album_spotify_image = search_spotify_album_image(spotify_token, artist, album) if album != "Album inconnu" else None
                        album_lastfm_image = search_lastfm_album_image(artist, album) if album != "Album inconnu" else None
                        
                        # Créer l'entrée
                        date_str = track_datetime.strftime('%Y-%m-%d %H:%M')
                        track_info = {
                            "timestamp": timestamp,
                            "date": date_str,
                            "artist": artist,
                            "title": title,
                            "album": album,
                            "loved": loved,
                            "artist_spotify_image": artist_spotify_image,
                            "album_spotify_image": album_spotify_image,
                            "album_lastfm_image": album_lastfm_image,
                            "source": "lastfm"
                        }
                        
                        # Sauvegarder
                        if save_track(track_info):
                            new_tracks_count += 1
                            print(
                                f"\n🎧 [Last.fm] {date_str} - {artist} - {title} ({album}) {'❤️' if loved else ''}\n"
                                f"   Artist Spotify img: {artist_spotify_image}\n"
                                f"   Album Spotify img: {album_spotify_image}\n"
                                f"   Album Last.fm img: {album_lastfm_image}"
                            )
                        
                        # Mettre à jour timestamp
                        if timestamp > last_lastfm_timestamp:
                            last_lastfm_timestamp = timestamp
                    
                    if new_tracks_count > 0:
                        print(f"[DEBUG] {new_tracks_count} nouvelle(s) lecture(s) Last.fm enregistrée(s)")
                    else:
                        print("[DEBUG] Aucune nouvelle lecture Last.fm")
                        
                except Exception as e:
                    print(f"⚠️ Erreur lors du traitement des lectures Last.fm: {e}")
            
            # B. PARCOURS ZONES ROON
            for zone_id, zone in roonapi.zones.items():
                now_playing = zone.get('now_playing')
                if now_playing:
                    # Extraire métadonnées
                    three_line = now_playing.get('three_line', {})
                    line1 = three_line.get('line1', 'Inconnu')
                    line2 = three_line.get('line2', 'Inconnu')
                    line3 = three_line.get('line3', 'Inconnu')
                    
                    print(f"\n[DEBUG] Roon three_line - line1: {line1}, line2: {line2}, line3: {line3}")
                    
                    title = line1
                    artist = line2
                    album = line3
                    
                    state = zone.get('state', 'unknown')
                    
                    # Clé unique
                    track_key = f"{artist}|{title}|{album}"
                    
                    # Nouvelle piste en cours de lecture
                    if state == 'playing' and track_key != last_track_key:
                        # Vérifier plage horaire
                        if not is_within_listening_hours(listen_start_hour, listen_end_hour):
                            current_time = datetime.now().strftime('%H:%M')
                            print(f"\n⏸️  {current_time} - Hors plage horaire d'écoute ({listen_start_hour:02d}:00-{listen_end_hour:02d}:59)")
                            print(f"   Piste ignorée: {artist} - {title}")
                            last_track_key = track_key
                            continue
                        
                        last_track_key = track_key
                        
                        # Traitement radio
                        if is_radio_station(title):
                            print(f"[DEBUG] 📻 Station de radio détectée: {title}")
                            parsed = parse_radio_artist_field(artist)
                            if parsed:
                                artist, title = parsed
                                print(f"[DEBUG] 📻 Extraction radio - Artiste: '{artist}', Titre: '{title}'")
                                album = search_spotify_track_album(spotify_token, artist, title)
                                if album:
                                    print(f"[DEBUG] 📻 Album trouvé: '{album}'")
                                else:
                                    print(f"[DEBUG] 📻 Album non trouvé - Écoute radio ignorée")
                                    last_track_key = track_key
                                    continue
                            else:
                                print(f"[DEBUG] 📻 Format non musical détecté (émission/journal) - Écoute ignorée")
                                last_track_key = track_key
                                continue
                        
                        print(f"[DEBUG] Recherche Spotify pour artiste: '{artist}', album: '{album}'")
                        
                        # Récupérer images
                        artist_spotify_image = search_spotify_artist_image(spotify_token, artist)
                        album_spotify_image = search_spotify_album_image(spotify_token, artist, album) if album != 'Inconnu' else None
                        album_lastfm_image = search_lastfm_album_image(artist, album) if album != 'Inconnu' else None
                        
                        print(f"[DEBUG] Résultats - Artist Spotify: {artist_spotify_image}, Album Spotify: {album_spotify_image}, Album Last.fm: {album_lastfm_image}")
                        
                        # Créer l'entrée
                        timestamp = int(time.time())
                        date_str = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M')
                        
                        track_info = {
                            "timestamp": timestamp,
                            "date": date_str,
                            "artist": artist,
                            "title": title,
                            "album": album,
                            "loved": False,
                            "artist_spotify_image": artist_spotify_image,
                            "album_spotify_image": album_spotify_image,
                            "album_lastfm_image": album_lastfm_image,
                            "source": "roon"
                        }
                        
                        # Sauvegarder et afficher
                        if save_track(track_info):
                            print(
                                f"\n🎵 {date_str} - {artist} - {title} ({album})\n"
                                f"   Artist Spotify img: {artist_spotify_image}\n"
                                f"   Album Spotify img: {album_spotify_image}\n"
                                f"   Album Last.fm img: {album_lastfm_image}"
                            )
            
            # C. ATTENTE AVANT PROCHAINE ITÉRATION
            time.sleep(45)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Arrêt de la surveillance")
```

### 15. Informations de l'application et constantes

**Constantes globales en haut du fichier:**
```python
# Configuration Roon
ROON_APP_NAME = "Python Roon Tracker"
ROON_APP_VERSION = "1.0.0"
ROON_PUBLISHER = "Patrick"
ROON_EMAIL = "patrick.ostertag@gmail.com"
ROON_CONFIG_FILE = "roon-config.json"
ROON_TRACKS_FILE = "chk-roon.json"
ROON_LOCK_FILE = "chk-roon.lock"

# Configuration Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Configuration Last.fm
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")

# Stations de radio à détecter
RADIO_STATIONS = [
    "RTS La Première",
    "RTS Couleur 3",
    "RTS Espace 2",
    "RTS Option Musique",
    "Radio Nova"
]
```

**Variables globales pour le cache:**
```python
cache_artist_images_spotify = {}
cache_album_images_spotify = {}
cache_album_images_lastfm = {}
spotify_token_cache = {"access_token": None, "expires_at": 0}

# Initialisation Last.fm
lastfm_network = None
if API_KEY and API_SECRET:
    try:
        lastfm_network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
        print("✅ Connexion Last.fm initialisée")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de Last.fm: {e}")
else:
    print("⚠️ API_KEY ou API_SECRET Last.fm manquant - la vérification Last.fm sera désactivée")

# Fichier de verrouillage global
lock_file_handle = None
```

## Spécifications techniques

### Imports requis

```python
#!/usr/bin/env python3
"""Module de surveillance et d'enregistrement des lectures Roon et Last.fm.

Ce module se connecte à l'API Roon pour surveiller en temps réel les pistes musicales
jouées et vérifie également les lectures Last.fm. Il enregistre les métadonnées enrichies 
(artiste, titre, album) avec les URLs d'images provenant de Spotify et Last.fm dans un 
fichier JSON unique.

Fonctionnalités principales:
    - Connexion automatique à Roon Core via découverte réseau
    - Surveillance continue des lectures Roon en cours
    - Vérification périodique des lectures Last.fm du mois en cours
    - Détection automatique des doublons (évite l'enregistrement multiple)
    - Enrichissement avec images d'artistes et d'albums (Spotify, Last.fm)
    - Nettoyage intelligent des métadonnées (artistes multiples, versions, crochets)
    - Validation stricte de l'artiste lors des recherches Spotify
    - Système de scoring pour sélectionner le meilleur match d'album
    - Gestion de plages horaires d'écoute configurables
    - Mise en cache des recherches d'images pour optimisation
    - Système de fallback avec validation pour améliorer la fiabilité
    - Marquage de la source (Roon ou Last.fm) pour chaque lecture

Fichiers utilisés:
    - roon-config.json: Configuration Roon (token, host, port, heures d'écoute)
    - chk-roon.json: Historique des lectures avec métadonnées enrichies
    - .env: Variables d'environnement (clés API Spotify, Last.fm et username)

Dépendances:
    - roonapi: Interface avec l'API Roon
    - pylast: Interface avec l'API Last.fm
    - python-dotenv: Chargement des variables d'environnement
    - certifi: Gestion des certificats SSL

Exemple d'utilisation:
    $ python chk-roon.py
    
Configuration requise dans .env:
    SPOTIFY_CLIENT_ID=votre_client_id
    SPOTIFY_CLIENT_SECRET=votre_client_secret
    API_KEY=votre_lastfm_api_key
    API_SECRET=votre_lastfm_api_secret
    LASTFM_USERNAME=votre_username_lastfm

Auteur: Patrick Ostertag
Version: 2.2.0
Date: 21 janvier 2026
"""

import json
import os
import time
import certifi
import urllib.request
import urllib.parse
import base64
import fcntl
import sys
import pylast
from datetime import datetime, timezone, timedelta
from roonapi import RoonApi, RoonDiscovery
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration SSL
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
```

### Type hints (Python 3.10+)

Utiliser les annotations de type modernes:
- `str | None` au lieu de `Optional[str]`
- `dict`, `bool`, `int`, `list` pour les types de base
- `-> None` pour fonctions sans retour
- `-> bool`, `-> str`, `-> dict` pour fonctions avec retour

### Documentation (Docstrings format Google)

Chaque fonction doit avoir une docstring complète avec:

```python
def fonction_exemple(param1: str, param2: int) -> str | None:
    """Description courte d'une ligne.
    
    Description détaillée sur plusieurs lignes si nécessaire.
    Explication du contexte et du comportement.
    
    Args:
        param1: Description du premier paramètre.
        param2: Description du second paramètre.
        
    Returns:
        Description de ce qui est retourné.
        Cas spéciaux et valeurs possibles.
        
    Examples:
        >>> fonction_exemple("test", 42)
        'résultat'
        >>> fonction_exemple("", 0)
        None
        
    Note:
        Informations supplémentaires importantes.
        Comportements spéciaux à connaître.
        
    Raises:
        TypeErreur: Si les paramètres sont invalides (optionnel).
    """
```

**Docstring du module** (en haut du fichier après le shebang):
- Description complète du module
- Liste des fonctionnalités principales (avec puces)
- Fichiers utilisés
- Dépendances requises
- Exemple d'utilisation
- Configuration requise
- Auteur, version, date

## Exigences de robustesse

### Gestion des erreurs

- Try/except autour de chaque requête HTTP
- Messages d'erreur informatifs avec émojis appropriés
- Ne jamais crasher, retourner None en cas d'erreur
- Afficher les erreurs mais continuer l'exécution
- Capturer et afficher le traceback complet en cas d'erreur fatale
- Libérer le verrou TOUJOURS dans le bloc finally

### Performance et optimisation

- Cache systématique pour toutes les recherches (même résultats négatifs)
- Token Spotify réutilisé jusqu'à expiration (vérification toutes les 60s avant expiration)
- Un seul token Spotify par session
- Vérification Roon toutes les 45 secondes (pas trop fréquent)
- Rate limiting pour réparation d'images: 0.5s entre requêtes
- Utilisation de `blocking_init=False` pour RoonApi (non-bloquant)

### Maintenabilité et lisibilité

- Code modulaire avec fonctions bien séparées et documentées
- Constantes en MAJUSCULES en haut du fichier
- Commentaires en français pour expliquer la logique complexe
- Noms de variables descriptifs (éviter x, y, z)
- Messages utilisateur clairs et en français
- Respect de PEP 8 pour la mise en forme
- Une fonction = une responsabilité
- Éviter les imbrications trop profondes (max 3-4 niveaux)

## Comportements spécifiques et cas limites

### Premier lancement

1. Créer `roon-config.json` avec heures par défaut si absent
2. Demander autorisation dans Roon avec message explicatif
3. Créer `chk-roon.json` vide à la première sauvegarde
4. Afficher messages informatifs pour guider l'utilisateur

### Cas limites et valeurs spéciales

- `Artiste = "Inconnu"` → ne pas modifier, ne pas chercher d'images
- `Album = "Inconnu"` → ne pas chercher d'images
- Plusieurs artistes avec "/" → prendre uniquement le premier
- Token Spotify expiré → renouveler automatiquement dans les fonctions de recherche
- Aucune image trouvée → null dans le JSON (pas de chaîne vide)
- Roon Core déconnecté → afficher erreur et arrêter proprement
- Last.fm non configuré → désactiver uniquement la vérification Last.fm, continuer Roon
- Station de radio sans format musical → ignorer l'écoute
- Album radio non trouvé → ignorer l'écoute

### Gestion des timestamps

- **Toujours utiliser UTC** pour les timestamps: `datetime.now(timezone.utc)`
- Format de date: `'%Y-%m-%d %H:%M'`
- Conversion en timestamp Unix: `int(datetime.timestamp())`
- Conversion depuis timestamp: `datetime.fromtimestamp(timestamp, timezone.utc)`
- Pour vérification plage horaire: convertir en heure locale avec `.astimezone()`

### Encoding et formats

- **Encoding UTF-8** pour tous les fichiers: `encoding='utf-8'`
- JSON avec caractères non-ASCII préservés: `ensure_ascii=False`
- Indentation JSON lisible: `indent=4` pour historique, `indent=2` pour config
- Regex pour nettoyage parenthèses: `r'\s*\([^)]*\)\s*$'`
- Regex pour nettoyage crochets ET parenthèses: `r'\s*[\(\[][^\)\]]*[\)\]]\s*$'`

## Validation finale et checklist

Le script complet doit pouvoir:

- ✅ **Protection**: Empêcher les instances multiples avec verrouillage fcntl
- ✅ **Connexion**: Se connecter automatiquement à Roon Core via découverte réseau
- ✅ **Multi-zones**: Surveiller plusieurs zones Roon simultanément
- ✅ **Last.fm**: Surveiller les lectures Last.fm du mois en cours
- ✅ **Doublons**: Détecter et éviter les doublons entre Roon et Last.fm
- ✅ **Source**: Marquer la source de chaque lecture ("roon" ou "lastfm")
- ✅ **Radio**: Détecter et traiter les stations de radio avec parsing intelligent
- ✅ **Nettoyage**: Nettoyer les métadonnées (multiples artistes, parenthèses, crochets)
- ✅ **Validation**: Valider l'artiste avec tolérance lors des recherches Spotify
- ✅ **Scoring**: Calculer un score de pertinence pour sélectionner le meilleur match
- ✅ **Retry**: Gérer automatiquement les erreurs 401 et 429 avec retry automatique
- ✅ **Images**: Récupérer les images Spotify (artiste, album) et Last.fm (album)
- ✅ **Réparation**: Réparer automatiquement les images manquantes au démarrage
- ✅ **Plages horaires**: Respecter les plages horaires pour Roon ET Last.fm
- ✅ **Cache**: Utiliser le cache efficacement pour toutes les recherches
- ✅ **Erreurs**: Gérer les erreurs sans crasher (messages informatifs)
- ✅ **JSON**: Enregistrer au format JSON structuré et lisible
- ✅ **Messages**: Afficher des messages informatifs avec émojis appropriés
- ✅ **Arrêt propre**: S'arrêter proprement avec Ctrl+C et libérer le verrou
- ✅ **Debug**: Fournir des messages de debug détaillés pour le suivi

## Tests à effectuer après génération

1. **Test de verrouillage**: Lancer deux instances simultanément → la seconde doit être refusée
2. **Test de connexion Roon**: Première connexion → demande d'autorisation dans Roon
3. **Test de surveillance**: Jouer une piste → elle doit apparaître dans chk-roon.json
4. **Test de nettoyage**: Piste avec "/" ou "(Live)" → métadonnées nettoyées
5. **Test de validation**: Album avec mauvais artiste → doit être rejeté ou fallback
6. **Test de scoring**: Chercher album ambigu → doit choisir le meilleur match
7. **Test Last.fm**: Avoir des lectures Last.fm récentes → doivent être ajoutées
8. **Test doublons**: Même piste dans Roon et Last.fm → une seule entrée
9. **Test radio**: Écouter RTS Couleur 3 avec musique → extraction artiste/titre/album
10. **Test plages horaires**: Jouer hors plage → piste ignorée avec message
11. **Test réparation**: Fichier avec images null → réparées au démarrage
12. **Test retry**: Simuler erreur 401/429 → doit réessayer automatiquement
13. **Test arrêt propre**: Ctrl+C → message + libération du verrou
14. **Test cache**: Même artiste/album plusieurs fois → une seule requête API

---

**Génère maintenant le script Python complet `chk-roon.py` version 2.2.0 en suivant EXACTEMENT ces spécifications détaillées.**

**Points critiques à ne pas oublier:**
1. Validation stricte de l'artiste avec `artist_matches()` dans `search_spotify_album_image()`
2. Système de scoring avec seuils (>50 pour essai 1, >30 pour fallback)
3. Récupération de 5 résultats au lieu d'un seul pour le scoring
4. Paramètre `max_retries=3` dans toutes les fonctions de recherche Spotify
5. Gestion automatique des erreurs 401 (token expiré) et 429 (rate limit)
6. Fonction `repair_null_spotify_images()` appelée au démarrage dans `main()`
7. Détection et traitement intelligent des stations de radio
8. Protection contre instances multiples avec verrouillage fcntl
9. Marquage de source "roon" ou "lastfm" dans chaque track_info
10. Messages de debug détaillés avec émojis appropriés à chaque étape
