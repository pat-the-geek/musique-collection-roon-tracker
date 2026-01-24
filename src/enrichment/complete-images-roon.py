#!/usr/bin/env python3
"""
Script pour compléter les images manquantes dans chk-roon.json
Utilise les APIs Spotify et Last.fm pour récupérer les images.

Auteur: Patrick Ostertag
Date: 20 janvier 2026
"""

import json
import os
import time
import urllib.request
import urllib.parse
import base64
import re
from dotenv import load_dotenv

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Charger les variables d'environnement
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
API_KEY = os.getenv("API_KEY")

# Cache pour éviter les requêtes répétées
cache_artist_images_spotify = {}
cache_album_images_spotify = {}
cache_album_images_lastfm = {}
spotify_token_cache = {"access_token": None, "expires_at": 0}

def clean_artist_name(artist_name: str) -> str:
    """Nettoie le nom d'artiste pour améliorer les recherches."""
    if not artist_name or artist_name == 'Inconnu':
        return artist_name
    
    # Si plusieurs artistes séparés par /, prendre le premier
    if '/' in artist_name:
        artist_name = artist_name.split('/')[0].strip()
    
    # Enlever les métadonnées entre parenthèses à la fin
    artist_name = re.sub(r'\s*\([^)]*\)\s*$', '', artist_name)
    
    return artist_name.strip()

def clean_album_name(album_name: str) -> str:
    """Nettoie le nom d'album pour améliorer les recherches."""
    if not album_name or album_name == 'Inconnu':
        return album_name
    
    # Enlever les métadonnées entre parenthèses à la fin
    album_name = re.sub(r'\s*\([^)]*\)\s*$', '', album_name)
    
    return album_name.strip()

def get_spotify_token() -> str | None:
    """Récupère un token d'accès Spotify via OAuth 2.0."""
    if spotify_token_cache["access_token"] and time.time() < spotify_token_cache["expires_at"] - 60:
        return spotify_token_cache["access_token"]

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
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
        print(f"⚠️ Erreur token Spotify: {exc}")
        return None

def search_spotify_artist_image(token: str | None, artist_name: str) -> str | None:
    """Recherche l'image d'artiste sur Spotify."""
    if artist_name in cache_artist_images_spotify:
        return cache_artist_images_spotify[artist_name]

    if not token:
        cache_artist_images_spotify[artist_name] = None
        return None

    cleaned_artist = clean_artist_name(artist_name)
    
    try:
        query = urllib.parse.quote(f"artist:{cleaned_artist}")
        url = f"https://api.spotify.com/v1/search?q={query}&type=artist&limit=1"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        items = data.get("artists", {}).get("items", [])
        image_url = items[0]["images"][0]["url"] if items and items[0].get("images") else None
        
        cache_artist_images_spotify[artist_name] = image_url
        return image_url
    except Exception:
        cache_artist_images_spotify[artist_name] = None
        return None

def search_spotify_album_image(token: str | None, artist_name: str, album_name: str) -> str | None:
    """Recherche l'image d'album sur Spotify avec fallback."""
    cache_key = (artist_name, album_name)
    if cache_key in cache_album_images_spotify:
        return cache_album_images_spotify[cache_key]

    if not token:
        cache_album_images_spotify[cache_key] = None
        return None

    cleaned_artist = clean_artist_name(artist_name)
    cleaned_album = clean_album_name(album_name)
    
    # Essai 1: avec artiste et album
    try:
        query = urllib.parse.quote(f"album:{cleaned_album} artist:{cleaned_artist}")
        url = f"https://api.spotify.com/v1/search?q={query}&type=album&limit=1"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        items = data.get("albums", {}).get("items", [])
        image_url = items[0]["images"][0]["url"] if items and items[0].get("images") else None
        
        if image_url:
            cache_album_images_spotify[cache_key] = image_url
            return image_url
    except Exception:
        pass
    
    # Essai 2: fallback sans artiste
    try:
        query = urllib.parse.quote(cleaned_album)
        url = f"https://api.spotify.com/v1/search?q={query}&type=album&limit=1"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        items = data.get("albums", {}).get("items", [])
        image_url = items[0]["images"][0]["url"] if items and items[0].get("images") else None
        
        cache_album_images_spotify[cache_key] = image_url
        return image_url
    except Exception:
        cache_album_images_spotify[cache_key] = None
        return None

def search_lastfm_album_image(artist_name: str, album_name: str) -> str | None:
    """Recherche l'image d'album via l'API Last.fm."""
    cache_key = (artist_name, album_name)
    if cache_key in cache_album_images_lastfm:
        return cache_album_images_lastfm[cache_key]

    if not API_KEY:
        cache_album_images_lastfm[cache_key] = None
        return None

    cleaned_artist = clean_artist_name(artist_name)
    cleaned_album = clean_album_name(album_name)

    try:
        artist_encoded = urllib.parse.quote(cleaned_artist)
        album_encoded = urllib.parse.quote(cleaned_album)
        url = (
            f"https://ws.audioscrobbler.com/2.0/?method=album.getinfo"
            f"&api_key={API_KEY}&artist={artist_encoded}&album={album_encoded}&format=json"
        )
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
        images = data.get("album", {}).get("image", [])
        image_url = images[-1]["#text"] if images and images[-1].get("#text") else None
        
        cache_album_images_lastfm[cache_key] = image_url
        return image_url
    except Exception:
        cache_album_images_lastfm[cache_key] = None
        return None

def main():
    """Fonction principale pour compléter les images manquantes."""
    json_file = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")
    
    print("📂 Chargement de chk-roon.json...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {json_file} n'existe pas.")
        return
    except json.JSONDecodeError:
        print(f"❌ Erreur : Le fichier {json_file} n'est pas un JSON valide.")
        return
    
    tracks = data.get('tracks', [])
    
    # Identifier les pistes avec images manquantes
    missing_artist = [t for t in tracks if not t.get('artist_spotify_image')]
    missing_album_spotify = [t for t in tracks if not t.get('album_spotify_image')]
    missing_album_lastfm = [t for t in tracks if not t.get('album_lastfm_image')]
    
    print(f"\n🔍 Analyse des images manquantes:")
    print(f"  - Artistes Spotify : {len(missing_artist)}")
    print(f"  - Albums Spotify   : {len(missing_album_spotify)}")
    print(f"  - Albums Last.fm   : {len(missing_album_lastfm)}")
    
    if not missing_artist and not missing_album_spotify and not missing_album_lastfm:
        print("\n✅ Toutes les images sont déjà présentes !")
        return
    
    # Récupérer le token Spotify
    print("\n🔑 Récupération du token Spotify...")
    spotify_token = get_spotify_token()
    if not spotify_token:
        print("⚠️ Impossible de récupérer le token Spotify")
    
    print(f"\n🚀 Complétion des images en cours...\n")
    
    completed_artist = 0
    completed_album_spotify = 0
    completed_album_lastfm = 0
    
    # Compléter les images manquantes
    for i, track in enumerate(tracks, 1):
        modified = False
        artist = track.get('artist', '')
        album = track.get('album', '')
        
        # Image artiste manquante
        if not track.get('artist_spotify_image') and spotify_token:
            image = search_spotify_artist_image(spotify_token, artist)
            if image:
                track['artist_spotify_image'] = image
                completed_artist += 1
                modified = True
                print(f"[{i}/{len(tracks)}] ✅ Artiste: {artist[:50]}")
        
        # Image album Spotify manquante
        if not track.get('album_spotify_image') and spotify_token:
            image = search_spotify_album_image(spotify_token, artist, album)
            if image:
                track['album_spotify_image'] = image
                completed_album_spotify += 1
                modified = True
                print(f"[{i}/{len(tracks)}] ✅ Album Spotify: {album[:50]}")
        
        # Image album Last.fm manquante
        if not track.get('album_lastfm_image'):
            image = search_lastfm_album_image(artist, album)
            if image:
                track['album_lastfm_image'] = image
                completed_album_lastfm += 1
                modified = True
                print(f"[{i}/{len(tracks)}] ✅ Album Last.fm: {album[:50]}")
        
        # Pause pour éviter le rate limiting
        if modified and i < len(tracks):
            time.sleep(0.3)
    
    # Sauvegarder les modifications
    if completed_artist or completed_album_spotify or completed_album_lastfm:
        print(f"\n💾 Sauvegarde des modifications...")
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"\n✅ Complétion terminée !")
            print(f"\n📊 Résultats:")
            print(f"  - Artistes Spotify : {completed_artist} ajoutées")
            print(f"  - Albums Spotify   : {completed_album_spotify} ajoutées")
            print(f"  - Albums Last.fm   : {completed_album_lastfm} ajoutées")
            print(f"  - Total            : {completed_artist + completed_album_spotify + completed_album_lastfm} images")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
    else:
        print("\n⚠️ Aucune image n'a pu être récupérée.")

if __name__ == "__main__":
    main()
