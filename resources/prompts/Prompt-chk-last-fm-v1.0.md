# Prompt: Générer le programme Python `chk-last-fm.py` (Version 1.0)

Tu es un assistant de développement Python. Crée un script nommé `chk-last-fm.py` qui récupère les écoutes Last.fm du mois en cours pour un utilisateur, enrichit chaque piste avec les URLs d'images Spotify (artiste, album) et Last.fm (album), puis écrit un fichier JSON.

## Objectif
- Récupérer les pistes écoutées par un utilisateur Last.fm pendant le mois courant (UTC).
- Pour chaque piste, obtenir:
  - URL de l'image de l'artiste via Spotify
  - URL de l'image de l'album via Spotify
  - URL de l'image de l'album via Last.fm
- Éviter les accès inutiles aux APIs via des caches en mémoire.
- Sauvegarder un fichier `chk-last-fm.json` structuré avec ces informations.

## Environnement et variables
Le script doit lire les variables d'environnement depuis un fichier `.env` via `python-dotenv`:
- `API_KEY`: clé API Last.fm
- `API_SECRET`: secret API Last.fm
- `LASTFM_USERNAME`: nom d'utilisateur Last.fm
- `LASTFM_LIMIT`: nombre max de pistes à récupérer (défaut: 200)
- `SPOTIFY_CLIENT_ID`: client id Spotify
- `SPOTIFY_CLIENT_SECRET`: client secret Spotify

Optionnel: définir `SSL_CERT_FILE` (si absent) vers le bundle de `certifi` pour éviter les erreurs SSL.

## Dépendances
- `pylast`: interaction Last.fm
- `python-dotenv`: chargement .env
- `certifi`: certificats
- Bibliothèque standard: `urllib.request`, `urllib.parse`, `json`, `time`, `datetime`, `base64`, `os`

## Spécifications fonctionnelles
1. Calculer le début et la fin du mois courant en UTC, puis convertir en timestamps Unix pour interroger l'API Last.fm.
2. Utiliser `pylast.LastFMNetwork` pour récupérer les pistes via `get_recent_tracks(limit, time_from, time_to)`.
3. Pour chaque piste:
   - Extraire `artist`, `title`, `album` (ou "Album inconnu" si absent) et l'état `loved` si disponible.
   - Obtenir un token Spotify via le Client Credentials Flow:
     - POST `https://accounts.spotify.com/api/token` avec `grant_type=client_credentials`.
     - Auth Basic: `base64(SPOTIFY_CLIENT_ID:SPOTIFY_CLIENT_SECRET)`.
     - Mettre en cache le token avec son expiration (`expires_in`) et le réutiliser tant qu'il est valide.
   - Chercher l'image artiste Spotify:
     - `GET https://api.spotify.com/v1/search?q=artist:<artist>&type=artist&limit=1`
     - Stocker l'URL de l'image si disponible.
     - Utiliser un cache dict: clé = `artist_name`.
   - Chercher l'image album Spotify:
     - `GET https://api.spotify.com/v1/search?q=album:<album> artist:<artist>&type=album&limit=1`
     - Stocker l'URL si disponible.
     - Cache dict: clé = `(artist_name, album_name)`.
   - Chercher l'image album Last.fm:
     - `GET https://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=<API_KEY>&artist=<artist>&album=<album>&format=json`
     - Prendre la plus grande image si le tableau `image` existe (souvent la dernière entrée).
     - Cache dict: clé = `(artist_name, album_name)`.
4. Afficher en console une ligne par piste incluant la date UTC formatée (`YYYY-MM-DD HH:MM`), `artist`, `title`, `album`, coeur si `loved`, et les trois URLs d'images.
5. Écrire `chk-last-fm.json` au format:
   ```json
   {
     "username": "<LASTFM_USERNAME>",
     "month": "<NomDuMois YYYY>",
     "tracks": [
       {
         "timestamp": 1737062400,
         "date": "2026-01-17 06:00",
         "artist": "Artist Name",
         "title": "Track Title",
         "album": "Album Name",
         "loved": false,
         "artist_spotify_image": "https://.../artist.jpg",
         "album_spotify_image": "https://.../album_spotify.jpg",
         "album_lastfm_image": "https://.../album_lastfm.jpg"
       }
     ]
   }
   ```
   - Utiliser `ensure_ascii=False` et `indent=4`.

## Caches requis
- `cache_artist_images_spotify: Dict[str, Optional[str]]`
- `cache_album_images_spotify: Dict[Tuple[str,str], Optional[str]]`
- `cache_album_images_lastfm: Dict[Tuple[str,str], Optional[str]]`
- `spotify_token_cache: {"access_token": Optional[str], "expires_at": float}` pour éviter de redemander un token si valide.

## Bonnes pratiques & robustesse
- Docstring module claire (version, fonctionnalités, dépendances, usage, sortie).
- Docstrings concises pour les fonctions utilitaires.
- Gestion d'erreurs simple (try/except) qui n’arrête pas le script, retourne `None` si indisponible.
- Pas d’appels réseau inutiles: vérifier caches avant requêtes.
- Formatage de la date en UTC, affichage lisible.
- Respect du style Python (PEP 8), noms explicites, pas de commentaires verbeux inline.

## Structure du code
- Chargement `.env`
- Init certifi et variables d’environnement
- Connexion Last.fm (`pylast.LastFMNetwork`)
- Définition des caches
- Fonctions:
  - `get_spotify_token()`
  - `search_spotify_artist_image(token, artist_name)`
  - `search_spotify_album_image(token, artist_name, album_name)`
  - `search_lastfm_album_image(artist_name, album_name)`
- Récupération des pistes du mois
- Boucle de traitement + affichage
- Écriture JSON

## Livrables
- Un fichier `chk-last-fm.py` prêt à exécuter.
- Le code doit être autonome (en supposant `.env` existant) et produire `chk-last-fm.json`.
- Inclure des commentaires succincts expliquant l’usage des caches et du token.

## Commande d’exécution (à titre indicatif)
```bash
python chk-last-fm.py
```
