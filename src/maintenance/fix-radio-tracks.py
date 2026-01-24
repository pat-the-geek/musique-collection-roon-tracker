#!/usr/bin/env python3
"""
Script pour corriger les enregistrements de radio dans chk-roon.json
Identifie les morceaux de musique joués sur les radios et extrait correctement
l'artiste, le titre et l'album.

Auteur: Patrick Ostertag
Date: 21 janvier 2026
"""

import json
import os
import time
import urllib.request
import urllib.parse
import base64
from datetime import datetime
from dotenv import load_dotenv

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Charger les variables d'environnement
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Configuration Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Stations de radio à détecter
RADIO_STATIONS = [
    "RTS La Première",
    "RTS Couleur 3",
    "RTS Espace 2",
    "RTS Option Musique",
    "Radio Nova"
]

# Cache pour le token Spotify
spotify_token_cache = {"access_token": None, "expires_at": 0}


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


def search_spotify_track_album(token: str, artist_name: str, track_title: str) -> str | None:
    """
    Recherche l'album d'une piste sur Spotify.
    
    Args:
        token: Token d'accès Spotify
        artist_name: Nom de l'artiste
        track_title: Titre de la piste
        
    Returns:
        Nom de l'album ou None si non trouvé
    """
    if not token:
        return None

    try:
        # Recherche de la piste
        query = urllib.parse.quote(f"track:{track_title} artist:{artist_name}")
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        tracks = data.get("tracks", {}).get("items", [])
        if tracks and tracks[0].get("album"):
            album_name = tracks[0]["album"]["name"]
            return album_name
        
        # Fallback : recherche sans artiste
        query = urllib.parse.quote(f"track:{track_title}")
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        tracks = data.get("tracks", {}).get("items", [])
        if tracks and tracks[0].get("album"):
            album_name = tracks[0]["album"]["name"]
            return album_name
            
        return None
    except Exception as e:
        print(f"⚠️ Erreur recherche Spotify pour {artist_name} - {track_title}: {e}")
        return None


def is_radio_track(track: dict) -> bool:
    """
    Détermine si un enregistrement provient d'une radio.
    
    Args:
        track: Dictionnaire contenant les données de la piste
        
    Returns:
        True si c'est une écoute de radio, False sinon
    """
    title = track.get("title", "")
    return any(station in title for station in RADIO_STATIONS)


def parse_radio_artist_field(artist_field: str) -> tuple[str, str] | None:
    """
    Parse le champ artist pour extraire l'artiste et le titre.
    Format attendu: "Artiste - Titre"
    
    Args:
        artist_field: Valeur du champ artist
        
    Returns:
        Tuple (artiste, titre) ou None si le format ne correspond pas
    """
    # Vérifier s'il y a un tiret avec des espaces autour
    if " - " in artist_field:
        parts = artist_field.split(" - ", 1)
        if len(parts) == 2:
            artist = parts[0].strip()
            title = parts[1].strip()
            # Vérifier que ce n'est pas une émission (éviter les faux positifs)
            # Les émissions ont souvent des titres très longs ou des caractères spéciaux
            if len(artist) > 0 and len(title) > 0 and len(artist) < 50:
                return (artist, title)
    
    return None


def fix_radio_tracks(json_file: str = None) -> None:
    """
    Corrige les enregistrements de radio dans le fichier JSON.
    
    Args:
        json_file: Chemin vers le fichier JSON à corriger
    """    
    if json_file is None:
        json_file = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")
        print("📂 Chargement de chk-roon.json...")
    
    # Charger le fichier
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
    
    # Identifier les pistes de radio à corriger
    radio_tracks = []
    for track in tracks:
        if is_radio_track(track):
            parsed = parse_radio_artist_field(track.get('artist', ''))
            if parsed:
                radio_tracks.append((track, parsed))
    
    if not radio_tracks:
        print("✅ Aucune piste de radio à corriger trouvée.")
        return
    
    print(f"\n🔍 {len(radio_tracks)} piste(s) de radio détectée(s) à corriger:\n")
    
    # Afficher les pistes détectées
    for track, (artist, title) in radio_tracks[:10]:
        original_artist = track.get('artist', '')
        station = track.get('title', '')
        print(f"  📻 {station}")
        print(f"     Original : '{original_artist}'")
        print(f"     → Artiste: {artist}")
        print(f"     → Titre  : {title}")
        print()
    
    if len(radio_tracks) > 10:
        print(f"  ... et {len(radio_tracks) - 10} autre(s)\n")
    
    # Demander confirmation
    reponse = input(f"⚠️  Corriger ces {len(radio_tracks)} piste(s) ? (o/n) : ").strip().lower()
    
    if reponse != 'o':
        print("❌ Opération annulée.")
        return
    
    # Récupérer le token Spotify
    print("\n🔑 Récupération du token Spotify...")
    spotify_token = get_spotify_token()
    if not spotify_token:
        print("⚠️ Impossible de récupérer le token Spotify")
        print("   Les albums ne seront pas recherchés.")
    
    print(f"\n🔄 Correction des pistes en cours...\n")
    
    # Appliquer les corrections
    corrected_count = 0
    albums_found = 0
    
    for track, (artist, title) in radio_tracks:
        original_artist = track['artist']
        station = track['title']
        
        # Mettre à jour l'artiste et le titre
        track['artist'] = artist
        track['title'] = title
        
        # Rechercher l'album sur Spotify
        album = None
        if spotify_token:
            print(f"🔍 Recherche album pour: {artist} - {title}...", end=" ")
            album = search_spotify_track_album(spotify_token, artist, title)
            if album:
                track['album'] = album
                albums_found += 1
                print(f"✅ {album}")
            else:
                print("⚠️ Album non trouvé")
            time.sleep(0.3)  # Éviter le rate limiting
        
        corrected_count += 1
    
    # Sauvegarder les modifications
    print(f"\n💾 Sauvegarde des modifications...")
    
    # Créer une sauvegarde avant de modifier
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_file = f"Anciennes versions/chk-roon-{timestamp}.json"
    
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"📦 Backup créé : {backup_file}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création du backup : {e}")
    
    # Sauvegarder le fichier corrigé
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Correction terminée !")
        print(f"\n📊 Résultats:")
        print(f"  - Pistes corrigées  : {corrected_count}")
        print(f"  - Albums trouvés    : {albums_found}")
        if spotify_token:
            success_rate = (albums_found / corrected_count * 100) if corrected_count > 0 else 0
            print(f"  - Taux de succès    : {success_rate:.1f}%")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")


def main():
    """Fonction principale."""
    print("=" * 80)
    print("🔧 CORRECTION DES ENREGISTREMENTS DE RADIO")
    print("=" * 80)
    print()
    print("Ce script identifie les morceaux de musique joués sur les radios")
    print("et extrait correctement l'artiste, le titre et recherche l'album.")
    print()
    print(f"Stations détectées : {', '.join(RADIO_STATIONS)}")
    print("=" * 80)
    print()
    
    fix_radio_tracks()


if __name__ == "__main__":
    main()
