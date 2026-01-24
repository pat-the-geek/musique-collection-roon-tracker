"""
Script pour récupérer et afficher les lectures Last.fm du mois en cours (version 1.0).

Fonctionnalités principales :
- Récupère les pistes Last.fm pour l'utilisateur sur le mois courant.
- Affiche les lectures (artiste, titre, album, statut aimé) dans la console.
- Enrichit chaque piste avec des URLs d'images Spotify (artiste, album) et Last.fm (album).
- Écrit le résultat structuré dans chk-last-fm.json.

Dépendances :
- pylast : interaction avec l'API Last.fm
- python-dotenv : chargement des variables d'environnement depuis .env
- certifi : bundle de certificats si nécessaire

Configuration (.env) :
- API_KEY=your_lastfm_api_key
- API_SECRET=your_lastfm_api_secret
- LASTFM_USERNAME=your_lastfm_username
- LASTFM_LIMIT=500              # optionnel, défaut 200
- SPOTIFY_CLIENT_ID=your_spotify_client_id
- SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

Usage :
- python chk-last-fm.py

Sortie :
- Affichage console synthétique des lectures avec URLs d'images
- Fichier chk-last-fm.json contenant : artist_spotify_image, album_spotify_image, album_lastfm_image

Auteur : Assistant IA
Date : 17 janvier 2026
Version : 1.0
"""

import pylast
import os
import certifi
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import json
import urllib.request
import urllib.parse
import base64
import time

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Charger les variables d'environnement depuis le fichier .env
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Si Python n'a pas de cafile configuré, pointer vers le bundle de certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

# Récupération des clés API et paramètres depuis les variables d'environnement
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
USERNAME = os.getenv("LASTFM_USERNAME")
LIMIT = int(os.getenv("LASTFM_LIMIT", 200))  # Limite par défaut à 200 si non spécifiée
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Initialisation de la connexion à Last.fm
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

# Cache pour les URLs Spotify et Last.fm (artiste et album)
cache_artist_images_spotify = {}
cache_album_images_spotify = {}
cache_album_images_lastfm = {}
spotify_token_cache = {"access_token": None, "expires_at": 0}


def get_spotify_token():
    """Récupère un token Spotify via le client credentials flow, avec mise en cache."""
    # Réutilise le token tant qu'il est valide pour limiter les requêtes réseau
    if spotify_token_cache["access_token"] and time.time() < spotify_token_cache["expires_at"] - 60:
        return spotify_token_cache["access_token"]

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("SPOTIFY_CLIENT_ID ou SPOTIFY_CLIENT_SECRET manquant dans l'environnement")
        return None

    token_url = "https://accounts.spotify.com/api/token"
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode("utf-8")
    auth_header = base64.b64encode(credentials).decode("utf-8")
    req = urllib.request.Request(token_url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {auth_header}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req) as response:
            payload = json.loads(response.read().decode("utf-8"))
        spotify_token_cache["access_token"] = payload.get("access_token")
        expires_in = payload.get("expires_in", 3600)
        spotify_token_cache["expires_at"] = time.time() + expires_in
        return spotify_token_cache["access_token"]
    except Exception as exc:
        print(f"Erreur lors de la récupération du token Spotify: {exc}")
        return None


def search_spotify_artist_image(token, artist_name):
    """Recherche l'image principale de l'artiste sur Spotify avec cache local."""
    # Premier passage: on sert le cache si disponible, sinon on déclenche une seule requête
    if artist_name in cache_artist_images_spotify:
        return cache_artist_images_spotify[artist_name]

    if not token:
        cache_artist_images_spotify[artist_name] = None
        return None

    query = urllib.parse.quote(f"artist:{artist_name}")
    url = f"https://api.spotify.com/v1/search?q={query}&type=artist&limit=1"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        items = data.get("artists", {}).get("items", [])
        image_url = items[0]["images"][0]["url"] if items and items[0].get("images") else None
        cache_artist_images_spotify[artist_name] = image_url
        return image_url
    except Exception:
        cache_artist_images_spotify[artist_name] = None
        return None


def search_spotify_album_image(token, artist_name, album_name):
    """Recherche l'image de l'album sur Spotify avec cache local."""
    # La clé combine artiste et album pour isoler les réutilisations
    cache_key = (artist_name, album_name)
    if cache_key in cache_album_images_spotify:
        return cache_album_images_spotify[cache_key]

    if not token:
        cache_album_images_spotify[cache_key] = None
        return None

    query = urllib.parse.quote(f"album:{album_name} artist:{artist_name}")
    url = f"https://api.spotify.com/v1/search?q={query}&type=album&limit=1"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        items = data.get("albums", {}).get("items", [])
        image_url = items[0]["images"][0]["url"] if items and items[0].get("images") else None
        cache_album_images_spotify[cache_key] = image_url
        return image_url
    except Exception:
        cache_album_images_spotify[cache_key] = None
        return None


def search_lastfm_album_image(artist_name, album_name):
    """Recherche l'image de l'album via l'API Last.fm avec cache local."""
    cache_key = (artist_name, album_name)
    if cache_key in cache_album_images_lastfm:
        return cache_album_images_lastfm[cache_key]

    if not API_KEY:
        cache_album_images_lastfm[cache_key] = None
        return None

    try:
        artist_encoded = urllib.parse.quote(artist_name)
        album_encoded = urllib.parse.quote(album_name)
        url = (
            f"https://ws.audioscrobbler.com/2.0/?method=album.getinfo"
            f"&api_key={API_KEY}&artist={artist_encoded}&album={album_encoded}&format=json"
        )
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
        images = data.get("album", {}).get("image", [])
        image_url = images[-1]["#text"] if images else None
        cache_album_images_lastfm[cache_key] = image_url
        return image_url
    except Exception:
        cache_album_images_lastfm[cache_key] = None
        return None

# Calcul du début et de la fin du mois actuel en UTC
now = datetime.now(timezone.utc)
start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
# Fin du mois : premier jour du mois suivant moins 1 seconde
end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

# Conversion en timestamps Unix pour l'API
time_from = int(start_of_month.timestamp())
time_to = int(end_of_month.timestamp())

# Récupération de l'utilisateur et de ses lectures récentes
user = network.get_user(USERNAME)
recent_tracks = user.get_recent_tracks(limit=LIMIT, time_from=time_from, time_to=time_to)

# Affichage des informations générales
print(f"Lectures de {USERNAME} ce mois ({start_of_month.strftime('%B %Y')}):")

# Liste pour stocker les données des pistes
tracks_data = []

# Si des pistes sont trouvées, afficher les propriétés disponibles (pour debug)
if recent_tracks:
    first_track = recent_tracks[0]
    print(f"Propriétés disponibles pour une lecture : {dir(first_track)}")
    print(f"Exemple - Timestamp: {first_track.timestamp}, Loved: {getattr(first_track, 'loved', 'N/A')}")
    print("--- Liste des lectures ---")

# Parcours des pistes et collecte des données
# On récupère un token unique pour la session afin de limiter les appels d'authentification
spotify_token = get_spotify_token()

# Parcours des pistes et collecte des données
for track_item in recent_tracks:
    # Extraction des informations de base
    artist = track_item.track.artist.name
    title = track_item.track.title
    album = track_item.album or "Album inconnu"
    loved = getattr(track_item, 'loved', False)
    
    # Récupération des images
    artist_spotify_image = search_spotify_artist_image(spotify_token, artist)
    
    album_spotify_image = None
    album_lastfm_image = None
    if album != "Album inconnu":
        album_spotify_image = search_spotify_album_image(spotify_token, artist, album)
        album_lastfm_image = search_lastfm_album_image(artist, album)
    
    # Conversion du timestamp en date lisible
    timestamp = int(track_item.timestamp)
    date_str = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M')
    
    # Affichage dans la console
    print(
        f"{date_str} - {artist} - {title} ({album}) {'❤️' if loved else ''} "
        f"| Artist Spotify img: {artist_spotify_image} "
        f"| Album Spotify img: {album_spotify_image} "
        f"| Album Last.fm img: {album_lastfm_image}"
    )
    
    # Ajout à la liste pour le JSON
    tracks_data.append({
        "timestamp": timestamp,
        "date": date_str,
        "artist": artist,
        "title": title,
        "album": album,
        "loved": loved,
        "artist_spotify_image": artist_spotify_image,
        "album_spotify_image": album_spotify_image,
        "album_lastfm_image": album_lastfm_image
    })

# Sauvegarde des données dans un fichier JSON
with open(os.path.join(PROJECT_ROOT, "data", "history", "chk-last-fm.json"), "w", encoding="utf-8") as f:
    json.dump({
        "username": USERNAME,
        "month": start_of_month.strftime('%B %Y'),
        "tracks": tracks_data
    }, f, ensure_ascii=False, indent=4)

# Message de confirmation
print(f"\nDonnées sauvegardées dans chk-last-fm.json")