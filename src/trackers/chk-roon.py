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
    - Recherche d'URLs d'images publiques pour traitement ultérieur:
      * Pochettes d'albums (Spotify, Last.fm)
      * Vignettes d'artistes (Spotify)
      * Permet l'usage par IA et autres codes sans accès direct à Roon
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

# Déterminer le répertoire du script pour les chemins relatifs
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Charger les variables d'environnement
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Configuration SSL
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Configuration Roon
ROON_APP_NAME = "Python Roon Tracker"
ROON_APP_VERSION = "1.0.0"
ROON_PUBLISHER = "Patrick"
ROON_EMAIL = "patrick.ostertag@gmail.com"
ROON_CONFIG_FILE = os.path.join(PROJECT_ROOT, "data", "config", "roon-config.json")
ROON_TRACKS_FILE = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")
ROON_LOCK_FILE = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.lock")

# Configuration Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
API_KEY = os.getenv("API_KEY")

# Configuration Last.fm
API_SECRET = os.getenv("API_SECRET")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")

# Initialisation de la connexion à Last.fm
lastfm_network = None
if API_KEY and API_SECRET:
    try:
        lastfm_network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
        print("✅ Connexion Last.fm initialisée")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de Last.fm: {e}")
else:
    print("⚠️ API_KEY ou API_SECRET Last.fm manquant - la vérification Last.fm sera désactivée")

# Cache pour les URLs et le token Spotify
cache_artist_images_spotify = {}
cache_album_images_spotify = {}
cache_album_images_lastfm = {}
spotify_token_cache = {"access_token": None, "expires_at": 0}

# Fichier de verrouillage global
lock_file_handle = None


def acquire_lock() -> bool:
    """Acquiert un verrou exclusif pour empêcher plusieurs instances simultanées.
    
    Crée un fichier de verrouillage et tente d'obtenir un verrou exclusif
    (non-bloquant). Si une autre instance est déjà en cours d'exécution,
    la fonction retourne False.
    
    Returns:
        True si le verrou a été acquis avec succès, False si une autre
        instance est déjà active.
        
    Note:
        Le verrou est automatiquement libéré quand le processus se termine.
        Le fichier handle est stocké dans la variable globale lock_file_handle.
    """
    global lock_file_handle
    
    try:
        # Ouvrir le fichier de verrouillage en mode écriture
        lock_file_handle = open(ROON_LOCK_FILE, 'w')
        
        # Tenter d'acquérir un verrou exclusif non-bloquant
        fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Écrire le PID dans le fichier pour information
        lock_file_handle.write(str(os.getpid()))
        lock_file_handle.flush()
        
        return True
        
    except IOError:
        # Le verrou ne peut pas être acquis - une autre instance est active
        if lock_file_handle:
            lock_file_handle.close()
            lock_file_handle = None
        return False
    except Exception as e:
        print(f"⚠️ Erreur lors de l'acquisition du verrou: {e}")
        if lock_file_handle:
            lock_file_handle.close()
            lock_file_handle = None
        return False


def release_lock() -> None:
    """Libère le verrou et supprime le fichier de verrouillage.
    
    Appelée automatiquement à la fin du programme pour nettoyer
    les ressources et permettre le lancement d'une nouvelle instance.
    
    Note:
        Cette fonction est idempotente - elle peut être appelée plusieurs
        fois sans effet négatif.
    """
    global lock_file_handle
    
    if lock_file_handle:
        try:
            fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_UN)
            lock_file_handle.close()
            lock_file_handle = None
        except Exception:
            pass
    
    # Supprimer le fichier de verrouillage s'il existe
    try:
        if os.path.exists(ROON_LOCK_FILE):
            os.remove(ROON_LOCK_FILE)
    except Exception:
        pass


def clean_artist_name(artist_name: str) -> str:
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
        >>> clean_artist_name("Inconnu")
        'Inconnu'
        
    Note:
        - Si plusieurs artistes sont séparés par '/', seul le premier est conservé
        - Les informations entre parenthèses en fin de chaîne sont supprimées
        - Les espaces superflus sont normalisés
    """
    if not artist_name or artist_name == 'Inconnu':
        return artist_name
    
    # Si plusieurs artistes séparés par /, prendre le premier
    if '/' in artist_name:
        artist_name = artist_name.split('/')[0].strip()
    
    # Enlever les métadonnées entre parenthèses à la fin
    import re
    artist_name = re.sub(r'\s*\([^)]*\)\s*$', '', artist_name)
    
    return artist_name.strip()


def clean_album_name(album_name: str) -> str:
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
        >>> clean_album_name("Greatest Hits (Remastered Edition)")
        'Greatest Hits'
        >>> clean_album_name("Inconnu")
        'Inconnu'
        
    Note:
        Les informations entre parenthèses () et crochets [] en fin de chaîne sont supprimées
        pour améliorer la correspondance lors des recherches d'images.
    """
    if not album_name or album_name == 'Inconnu':
        return album_name
    
    # Enlever les métadonnées entre parenthèses () ou crochets [] à la fin
    import re
    album_name = re.sub(r'\s*[\(\[][^\)\]]*[\)\]]\s*$', '', album_name)
    
    return album_name.strip()


def get_spotify_token() -> str | None:
    """Récupère un token d'accès Spotify via OAuth 2.0 Client Credentials Flow.
    
    Utilise un système de cache pour réutiliser les tokens valides et minimiser
    les appels d'authentification à l'API Spotify. Le token est rafraîchi
    automatiquement 60 secondes avant son expiration.
    
    Returns:
        Token d'accès Spotify valide, ou None si l'authentification échoue
        ou si les credentials sont manquants.
        
    Raises:
        None: Les exceptions sont capturées et retournent None.
        
    Note:
        Nécessite les variables d'environnement:
        - SPOTIFY_CLIENT_ID: ID client de l'application Spotify
        - SPOTIFY_CLIENT_SECRET: Secret client de l'application Spotify
        
    Examples:
        >>> token = get_spotify_token()
        >>> if token:
        ...     # Utiliser le token pour les requêtes API
        ...     pass
    """
    if spotify_token_cache["access_token"] and time.time() < spotify_token_cache["expires_at"] - 60:
        return spotify_token_cache["access_token"]

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("⚠️ SPOTIFY_CLIENT_ID ou SPOTIFY_CLIENT_SECRET manquant dans .env")
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
        print(f"⚠️ Erreur lors de la récupération du token Spotify: {exc}")
        return None


def search_spotify_artist_image(token: str | None, artist_name: str, max_retries: int = 3) -> str | None:
    """Recherche l'image principale d'un artiste sur Spotify avec système de cache.
    
    Effectue une recherche sur l'API Spotify pour récupérer l'image de profil
    d'un artiste. Utilise un cache local pour éviter les requêtes répétitives.
    Le nom de l'artiste est nettoyé avant la recherche pour améliorer les résultats.
    
    Args:
        token: Token d'accès Spotify valide, ou None si non disponible.
        artist_name: Nom de l'artiste à rechercher (peut contenir plusieurs artistes
            séparés par '/' ou des métadonnées entre parenthèses).
        max_retries: Nombre maximum de tentatives (défaut: 3)
            
    Returns:
        URL de l'image de profil de l'artiste (format JPEG/PNG),
        ou None si l'artiste n'est pas trouvé ou si le token est invalide.
        
    Examples:
        >>> token = get_spotify_token()
        >>> url = search_spotify_artist_image(token, "Nina Simone")
        >>> print(url)
        'https://i.scdn.co/image/ab6761610000e5eb136c51c848c26a6cce7f9e56'
        
        >>> url = search_spotify_artist_image(token, "Dalida / Raymond Lefèvre")
        >>> # Recherche uniquement 'Dalida' après nettoyage
        
    Note:
        - Les résultats sont mis en cache avec le nom original comme clé
        - Le nettoyage conserve uniquement le premier artiste si plusieurs
        - Les messages de debug sont affichés pendant la recherche
        - Réessaye automatiquement si le token est expiré (401)
    """
    # Vérifier le cache avec le nom original
    if artist_name in cache_artist_images_spotify:
        return cache_artist_images_spotify[artist_name]

    if not token:
        print(f"[DEBUG] Pas de token Spotify disponible pour chercher l'artiste '{artist_name}'")
        cache_artist_images_spotify[artist_name] = None
        return None

    # Nettoyer le nom d'artiste
    cleaned_artist = clean_artist_name(artist_name)
    print(f"[DEBUG] Recherche Spotify artist - Original: '{artist_name}' -> Nettoyé: '{cleaned_artist}'")
    
    for attempt in range(max_retries):
        try:
            # Vérifier si on a besoin d'un nouveau token
            current_token = token
            if attempt > 0:
                print(f"[DEBUG] Tentative {attempt + 1}/{max_retries} - Récupération d'un nouveau token Spotify")
                current_token = get_spotify_token()
                if not current_token:
                    print(f"[DEBUG] ❌ Impossible de récupérer un token Spotify")
                    cache_artist_images_spotify[artist_name] = None
                    return None
            
            # Essayer avec le nom nettoyé
            query = urllib.parse.quote(f"artist:{cleaned_artist}")
            url = f"https://api.spotify.com/v1/search?q={query}&type=artist&limit=1"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {current_token}")

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            items = data.get("artists", {}).get("items", [])
            image_url = items[0]["images"][0]["url"] if items and items[0].get("images") else None
            
            if image_url:
                cache_artist_images_spotify[artist_name] = image_url
                print(f"[DEBUG] ✅ Spotify artist '{cleaned_artist}': {image_url}")
                return image_url
            else:
                print(f"[DEBUG] ⚠️ Aucune image trouvée pour l'artiste '{cleaned_artist}'")
                cache_artist_images_spotify[artist_name] = None
                return None
                
        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt < max_retries - 1:
                # Token expiré, réessayer avec un nouveau token
                print(f"[DEBUG] ⚠️ Token expiré (401), tentative {attempt + 1}/{max_retries}")
                time.sleep(1)
                continue
            elif e.code == 429 and attempt < max_retries - 1:
                # Rate limit, attendre avant de réessayer
                print(f"[DEBUG] ⚠️ Rate limit (429), attente de 2 secondes...")
                time.sleep(2)
                continue
            else:
                print(f"[DEBUG] ❌ Erreur HTTP {e.code} Spotify artist '{cleaned_artist}': {e}")
                cache_artist_images_spotify[artist_name] = None
                return None
        except Exception as e:
            print(f"[DEBUG] ❌ Erreur Spotify artist '{cleaned_artist}': {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            cache_artist_images_spotify[artist_name] = None
            return None
    
    # Si toutes les tentatives échouent
    cache_artist_images_spotify[artist_name] = None
    return None


def search_spotify_track_album(token: str | None, artist_name: str, track_title: str, max_retries: int = 3) -> str | None:
    """Recherche l'album d'une piste spécifique sur Spotify.
    
    Effectue une recherche de piste sur l'API Spotify pour récupérer le nom de l'album.
    Utilisé principalement pour les enregistrements radio où seul l'artiste et le titre
    sont connus.
    
    Args:
        token: Token d'accès Spotify valide, ou None si non disponible.
        artist_name: Nom de l'artiste.
        track_title: Titre de la piste.
        max_retries: Nombre maximum de tentatives (défaut: 3)
        
    Returns:
        Nom de l'album contenant la piste, ou None si non trouvé.
        
    Examples:
        >>> token = get_spotify_token()
        >>> album = search_spotify_track_album(token, "George Ezra", "Budapest")
        >>> print(album)
        'Wanted on Voyage'
        
    Note:
        - Nettoie les noms avant recherche
        - Fallback : recherche sans artiste si échec
        - Met en cache les résultats
    """
    cache_key = (artist_name, track_title)
    
    if not token:
        return None

    cleaned_artist = clean_artist_name(artist_name)
    cleaned_title = clean_album_name(track_title)  # Réutilise la fonction de nettoyage
    
    for attempt in range(max_retries):
        try:
            # Vérifier si on a besoin d'un nouveau token
            current_token = token
            if attempt > 0:
                current_token = get_spotify_token()
                if not current_token:
                    return None
            
            # Essai 1: avec artiste et titre
            query = urllib.parse.quote(f"track:{cleaned_title} artist:{cleaned_artist}")
            url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {current_token}")

            try:
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode("utf-8"))
                tracks = data.get("tracks", {}).get("items", [])
                if tracks and tracks[0].get("album"):
                    album_name = tracks[0]["album"]["name"]
                    print(f"[DEBUG] ✅ Spotify track album '{cleaned_title}': {album_name}")
                    return album_name
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                elif e.code == 429 and attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            
            # Essai 2: recherche seulement par titre (fallback)
            query = urllib.parse.quote(cleaned_title)
            url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {current_token}")
            
            try:
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode("utf-8"))
                tracks = data.get("tracks", {}).get("items", [])
                if tracks and tracks[0].get("album"):
                    album_name = tracks[0]["album"]["name"]
                    print(f"[DEBUG] ✅ Spotify track album (fallback) '{cleaned_title}': {album_name}")
                    return album_name
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                elif e.code == 429 and attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                break
            
            break
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            break
    
    print(f"[DEBUG] ⚠️ Album non trouvé pour la piste '{cleaned_title}'")
    return None


def normalize_string_for_comparison(s: str) -> str:
    """Normalise une chaîne pour comparaison (minuscules, sans espaces multiples)."""
    return ' '.join(s.lower().strip().split())

def artist_matches(search_artist: str, found_artist: str) -> bool:
    """Vérifie si deux noms d'artistes correspondent (avec tolérance).
    
    Args:
        search_artist: Nom de l'artiste recherché.
        found_artist: Nom de l'artiste trouvé dans les résultats.
        
    Returns:
        True si les artistes correspondent, False sinon.
        
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
    norm_search = normalize_string_for_comparison(search_artist)
    norm_found = normalize_string_for_comparison(found_artist)
    
    # Correspondance exacte
    if norm_search == norm_found:
        return True
    
    # Cas spécial: "Various" = "Various Artists"
    if norm_search.startswith('various') and norm_found.startswith('various'):
        return True
    
    # L'un contient l'autre (pour gérer "The Beatles" vs "Beatles")
    if norm_search in norm_found or norm_found in norm_search:
        return True
    
    return False

def search_spotify_album_image(token: str | None, artist_name: str, album_name: str, max_retries: int = 3) -> str | None:
    """Recherche l'image de couverture d'un album sur Spotify avec validation de l'artiste.
    
    Effectue une recherche d'album sur l'API Spotify avec validation stricte:
    1. Recherche avec artiste + album, récupère jusqu'à 5 résultats
    2. Valide que l'artiste du résultat correspond à celui recherché
    3. Calcule un score de pertinence basé sur la correspondance du nom
    4. Fallback : recherche uniquement par album avec validation d'artiste
    
    Utilise un cache local pour éviter les requêtes répétitives.
    
    Args:
        token: Token d'accès Spotify valide, ou None si non disponible.
        artist_name: Nom de l'artiste (utilisé pour affiner la recherche).
        album_name: Nom de l'album à rechercher.
        max_retries: Nombre maximum de tentatives (défaut: 3)
        
    Returns:
        URL de l'image de couverture de l'album (format JPEG/PNG),
        ou None si l'album n'est pas trouvé.
        
    Examples:
        >>> token = get_spotify_token()
        >>> url = search_spotify_album_image(token, "Nina Simone", "Pastel Blues")
        >>> print(url)
        'https://i.scdn.co/image/ab67616d0000b273df49506f74db624312118ca2'
        
        >>> url = search_spotify_album_image(token, "Eros Ramazzotti", "9 [Italian]")
        >>> # Valide que l'artiste du résultat est bien Eros Ramazzotti
        
    Note:
        - Les noms sont nettoyés avant recherche (suppression parenthèses/crochets)
        - Validation stricte de l'artiste dans tous les résultats
        - Recherche de 5 résultats et sélection du meilleur match
        - Le cache utilise (artist_name, album_name) comme clé composée
        - Messages de debug détaillés pour le suivi des recherches
        - Réessaye automatiquement si le token est expiré (401)
    """
    cache_key = (artist_name, album_name)
    if cache_key in cache_album_images_spotify:
        return cache_album_images_spotify[cache_key]

    if not token:
        print(f"[DEBUG] Pas de token Spotify disponible pour chercher l'album '{album_name}'")
        cache_album_images_spotify[cache_key] = None
        return None

    # Nettoyer les noms
    cleaned_artist = clean_artist_name(artist_name)
    cleaned_album = clean_album_name(album_name)
    print(f"[DEBUG] Recherche Spotify album - Album: '{album_name}' -> '{cleaned_album}', Artist: '{artist_name}' -> '{cleaned_artist}'")
    
    for attempt in range(max_retries):
        try:
            # Vérifier si on a besoin d'un nouveau token
            current_token = token
            if attempt > 0:
                print(f"[DEBUG] Tentative {attempt + 1}/{max_retries} - Récupération d'un nouveau token Spotify")
                current_token = get_spotify_token()
                if not current_token:
                    print(f"[DEBUG] ❌ Impossible de récupérer un token Spotify")
                    cache_album_images_spotify[cache_key] = None
                    return None
            
            # Essai 1: avec artiste et album nettoyés (recherche 5 résultats)
            query = urllib.parse.quote(f"album:{cleaned_album} artist:{cleaned_artist}")
            url = f"https://api.spotify.com/v1/search?q={query}&type=album&limit=5"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {current_token}")

            try:
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode("utf-8"))
                items = data.get("albums", {}).get("items", [])
                
                # Chercher le meilleur match en validant l'artiste
                best_match = None
                best_score = 0
                
                for item in items:
                    if not item.get("images"):
                        continue
                    
                    # Récupérer l'artiste principal de l'album
                    album_artists = item.get("artists", [])
                    if not album_artists:
                        continue
                    
                    album_artist = album_artists[0].get("name", "")
                    
                    # Vérifier si l'artiste correspond
                    if not artist_matches(cleaned_artist, album_artist):
                        print(f"[DEBUG] ⚠️ Artiste non correspondant: recherché '{cleaned_artist}', trouvé '{album_artist}'")
                        continue
                    
                    # Calculer un score de pertinence (basé sur la similarité du nom d'album)
                    album_title = item.get("name", "")
                    norm_searched = normalize_string_for_comparison(cleaned_album)
                    norm_found = normalize_string_for_comparison(album_title)
                    
                    # Score: 100 si exactement identique, sinon calcul de similarité
                    if norm_searched == norm_found:
                        score = 100
                    elif norm_searched in norm_found or norm_found in norm_searched:
                        score = 80
                    else:
                        # Score basé sur les mots en commun
                        searched_words = set(norm_searched.split())
                        found_words = set(norm_found.split())
                        common_words = searched_words & found_words
                        if searched_words:
                            score = (len(common_words) / len(searched_words)) * 50
                        else:
                            score = 0
                    
                    print(f"[DEBUG] 🎯 Match trouvé: '{album_title}' par '{album_artist}' (score: {score:.1f})")
                    
                    if score > best_score:
                        best_score = score
                        best_match = item
                
                # Si on a trouvé un bon match (score > 50)
                if best_match and best_score > 50:
                    image_url = best_match["images"][0]["url"]
                    cache_album_images_spotify[cache_key] = image_url
                    album_title = best_match.get("name", "")
                    print(f"[DEBUG] ✅ Spotify album '{album_title}' (score: {best_score:.1f}): {image_url}")
                    return image_url
                else:
                    print(f"[DEBUG] ⚠️ Aucun match avec artiste validé (meilleur score: {best_score:.1f})")
                    
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt < max_retries - 1:
                    print(f"[DEBUG] ⚠️ Token expiré (401) sur essai 1, tentative {attempt + 1}/{max_retries}")
                    time.sleep(1)
                    continue
                elif e.code == 429 and attempt < max_retries - 1:
                    print(f"[DEBUG] ⚠️ Rate limit (429) sur essai 1, attente de 2 secondes...")
                    time.sleep(2)
                    continue
                else:
                    print(f"[DEBUG] Essai 1 échoué: HTTP {e.code}")
            except Exception as e:
                print(f"[DEBUG] Essai 1 échoué: {e}")
            
            # Essai 2: recherche seulement par nom d'album (fallback avec validation)
            print(f"[DEBUG] Fallback: recherche sans artiste (avec validation)...")
            try:
                query = urllib.parse.quote(cleaned_album)
                url = f"https://api.spotify.com/v1/search?q={query}&type=album&limit=5"
                req = urllib.request.Request(url)
                req.add_header("Authorization", f"Bearer {current_token}")
                
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode("utf-8"))
                items = data.get("albums", {}).get("items", [])
                
                # Même logique de scoring avec validation d'artiste
                best_match = None
                best_score = 0
                
                for item in items:
                    if not item.get("images"):
                        continue
                    
                    album_artists = item.get("artists", [])
                    if not album_artists:
                        continue
                    
                    album_artist = album_artists[0].get("name", "")
                    
                    # Validation d'artiste encore plus importante en fallback
                    if not artist_matches(cleaned_artist, album_artist):
                        print(f"[DEBUG] ⚠️ Fallback - Artiste non correspondant: '{cleaned_artist}' != '{album_artist}'")
                        continue
                    
                    album_title = item.get("name", "")
                    norm_searched = normalize_string_for_comparison(cleaned_album)
                    norm_found = normalize_string_for_comparison(album_title)
                    
                    if norm_searched == norm_found:
                        score = 100
                    elif norm_searched in norm_found or norm_found in norm_searched:
                        score = 80
                    else:
                        searched_words = set(norm_searched.split())
                        found_words = set(norm_found.split())
                        common_words = searched_words & found_words
                        if searched_words:
                            score = (len(common_words) / len(searched_words)) * 50
                        else:
                            score = 0
                    
                    print(f"[DEBUG] 🎯 Fallback match: '{album_title}' par '{album_artist}' (score: {score:.1f})")
                    
                    if score > best_score:
                        best_score = score
                        best_match = item
                
                if best_match and best_score > 30:  # Seuil plus bas pour fallback
                    image_url = best_match["images"][0]["url"]
                    cache_album_images_spotify[cache_key] = image_url
                    album_title = best_match.get("name", "")
                    print(f"[DEBUG] ✅ Spotify album (fallback validé) '{album_title}' (score: {best_score:.1f}): {image_url}")
                    return image_url
                else:
                    print(f"[DEBUG] ⚠️ Fallback: aucun match validé (meilleur score: {best_score:.1f})")
                    
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt < max_retries - 1:
                    print(f"[DEBUG] ⚠️ Token expiré (401) sur fallback, tentative {attempt + 1}/{max_retries}")
                    time.sleep(1)
                    continue
                elif e.code == 429 and attempt < max_retries - 1:
                    print(f"[DEBUG] ⚠️ Rate limit (429) sur fallback, attente de 2 secondes...")
                    time.sleep(2)
                    continue
                else:
                    print(f"[DEBUG] ❌ Fallback échoué: HTTP {e.code}")
                    break
            except Exception as e:
                print(f"[DEBUG] ❌ Fallback échoué: {e}")
                break
                
            # Si on arrive ici, aucune image trouvée
            break
            
        except Exception as e:
            print(f"[DEBUG] ❌ Erreur générale: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            break
    
    print(f"[DEBUG] ⚠️ Aucune image trouvée pour l'album '{cleaned_album}' de '{cleaned_artist}'")
    cache_album_images_spotify[cache_key] = None
    return None


def is_radio_station(title: str, radio_stations: list) -> bool:
    """Vérifie si le titre correspond à une station de radio.
    
    Args:
        title: Titre de la piste à vérifier.
        radio_stations: Liste des stations de radio à détecter.
        
    Returns:
        True si c'est une station de radio, False sinon.
        
    Examples:
        >>> is_radio_station("RTS La Première", ["RTS La Première"])
        True
        >>> is_radio_station("Pastel Blues", ["RTS La Première"])
        False
    """
    return any(station in title for station in radio_stations)


def parse_radio_artist_field(artist_field: str) -> tuple[str, str] | None:
    """Parse le champ artist pour extraire l'artiste et le titre d'une radio.
    
    Les stations de radio encodent souvent les informations musicales au format
    "Artiste - Titre" dans le champ artist. Cette fonction extrait ces informations.
    
    Args:
        artist_field: Valeur du champ artist (ex: "George Ezra - Budapest").
        
    Returns:
        Tuple (artiste, titre) si le format correspond, None sinon.
        
    Examples:
        >>> parse_radio_artist_field("George Ezra - Budapest")
        ('George Ezra', 'Budapest')
        >>> parse_radio_artist_field("électricité, arnaques et service civil")
        None
        
    Note:
        Filtre les faux positifs (émissions, journaux) en vérifiant:
        - Présence de " - " (espace-tiret-espace)
        - Longueur raisonnable de l'artiste (< 50 caractères)
        - Parties non vides après split
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


def search_lastfm_album_image(artist_name: str, album_name: str) -> str | None:
    """Recherche l'image de couverture d'un album via l'API Last.fm.
    
    Interroge l'API Last.fm pour récupérer la plus grande image de couverture
    disponible pour un album donné. Complète les recherches Spotify en offrant
    une source alternative d'images.
    
    Args:
        artist_name: Nom de l'artiste de l'album.
        album_name: Nom de l'album à rechercher.
        
    Returns:
        URL de l'image de couverture de l'album (taille maximale disponible),
        ou None si l'album n'est pas trouvé ou si l'image est vide.
        
    Examples:
        >>> url = search_lastfm_album_image("Nina Simone", "Pastel Blues")
        >>> print(url)
        'https://lastfm.freetls.fastly.net/i/u/300x300/cdef71c12efb0d695ecb4a4d37756fd3.jpg'
        
    Note:
        - Nécessite la variable d'environnement API_KEY (clé API Last.fm)
        - Les noms sont nettoyés avant la recherche
        - Récupère la dernière image de la liste (plus grande taille)
        - Vérifie que l'URL n'est pas vide avant de la retourner
        - Les résultats sont mis en cache avec (artist, album) comme clé
    """
    cache_key = (artist_name, album_name)
    if cache_key in cache_album_images_lastfm:
        return cache_album_images_lastfm[cache_key]

    if not API_KEY:
        print(f"[DEBUG] Pas de clé API Last.fm disponible")
        cache_album_images_lastfm[cache_key] = None
        return None

    # Nettoyer les noms
    cleaned_artist = clean_artist_name(artist_name)
    cleaned_album = clean_album_name(album_name)
    print(f"[DEBUG] Recherche Last.fm - Album: '{album_name}' -> '{cleaned_album}', Artist: '{artist_name}' -> '{cleaned_artist}'")

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
        # Prendre la plus grande image (dernière dans la liste) et vérifier qu'elle n'est pas vide
        image_url = images[-1]["#text"] if images and images[-1].get("#text") else None
        
        if image_url:
            cache_album_images_lastfm[cache_key] = image_url
            print(f"[DEBUG] ✅ Last.fm album '{cleaned_album}': {image_url}")
        else:
            cache_album_images_lastfm[cache_key] = None
            print(f"[DEBUG] ⚠️ Last.fm: aucune image pour '{cleaned_album}'")
        return image_url
    except Exception as e:
        print(f"[DEBUG] ❌ Erreur Last.fm album '{cleaned_album}': {e}")
        cache_album_images_lastfm[cache_key] = None
        return None


def get_lastfm_recent_tracks() -> list:
    """Récupère les 5 dernières lectures de Last.fm pour le mois en cours.
    
    Interroge l'API Last.fm pour obtenir les 5 pistes les plus récemment écoutées
    par l'utilisateur depuis le début du mois jusqu'à maintenant.
    
    Returns:
        Liste de tuples (track_item, timestamp) contenant les 5 dernières lectures Last.fm,
        ou liste vide si l'API n'est pas disponible ou en cas d'erreur.
        
    Examples:
        >>> tracks = get_lastfm_recent_tracks()
        >>> print(len(tracks))
        5
        
    Note:
        Nécessite que lastfm_network soit initialisé avec les credentials valides.
        Limite fixée à 5 lectures récentes pour optimiser les performances.
    """
    if not lastfm_network or not LASTFM_USERNAME:
        return []
    
    try:
        # Calcul du début et de la fin du mois actuel en UTC
        now = datetime.now(timezone.utc)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Conversion en timestamps Unix pour l'API
        time_from = int(start_of_month.timestamp())
        time_to = int(now.timestamp())
        
        # Récupération de l'utilisateur et de ses lectures récentes (5 dernières)
        user = lastfm_network.get_user(LASTFM_USERNAME)
        recent_tracks = user.get_recent_tracks(limit=5, time_from=time_from, time_to=time_to)
        
        print(f"[DEBUG] Last.fm: {len(recent_tracks)} lectures récupérées pour {LASTFM_USERNAME} (5 dernières)")
        return recent_tracks
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération des lectures Last.fm: {e}")
        return []


def is_track_already_saved(artist: str, title: str, album: str, timestamp: int) -> bool:
    """Vérifie si une lecture existe déjà dans l'historique.
    
    Compare une lecture (artiste, titre, album, timestamp) avec l'historique
    existant pour éviter les duplications. Utilise une tolérance de 60 secondes
    sur le timestamp pour détecter les lectures quasi-identiques.
    
    Args:
        artist: Nom de l'artiste.
        title: Titre de la piste.
        album: Nom de l'album.
        timestamp: Timestamp Unix de la lecture.
        
    Returns:
        True si une lecture similaire existe déjà (même piste ± 60 secondes),
        False sinon.
        
    Examples:
        >>> already_saved = is_track_already_saved("Nina Simone", "Feeling Good", "I Put a Spell on You", 1705484800)
        >>> print(already_saved)
        False
        
    Note:
        La tolérance de 60 secondes permet de gérer les petits décalages
        de synchronisation entre Roon et Last.fm.
    """
    history = load_tracks_history()
    
    for track in history.get("tracks", []):
        # Vérifier si la piste correspond (artiste, titre, album)
        if (track.get("artist") == artist and 
            track.get("title") == title and 
            track.get("album") == album):
            # Vérifier si le timestamp est proche (± 60 secondes)
            existing_timestamp = track.get("timestamp", 0)
            if abs(existing_timestamp - timestamp) <= 60:
                return True
    
    return False


def load_tracks_history() -> dict:
    """Charge l'historique des lectures musicales depuis le fichier JSON.
    
    Lit le fichier contenant l'historique complet des pistes jouées avec
    leurs métadonnées enrichies.
    
    Returns:
        Dictionnaire contenant l'historique avec la structure:
        {
            "tracks": [
                {
                    "timestamp": int,
                    "date": str,
                    "artist": str,
                    "title": str,
                    "album": str,
                    "loved": bool,
                    "artist_spotify_image": str | None,
                    "album_spotify_image": str | None,
                    "album_lastfm_image": str | None
                },
                ...
            ]
        }
        Si le fichier n'existe pas ou est corrompu, retourne {"tracks": []}.
        
    Examples:
        >>> history = load_tracks_history()
        >>> print(len(history['tracks']))
        42
        
    Note:
        Les erreurs de lecture sont capturées et affichées, puis un
        dictionnaire vide est retourné.
    """
    if os.path.exists(ROON_TRACKS_FILE):
        try:
            with open(ROON_TRACKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de {ROON_TRACKS_FILE}: {e}")
    return {"tracks": []}


def save_track(track_info: dict) -> bool:
    """Sauvegarde une nouvelle lecture musicale dans le fichier d'historique JSON.
    
    Ajoute une nouvelle entrée en début de liste dans l'historique des lectures,
    puis persiste l'historique complet dans le fichier JSON.
    
    Args:
        track_info: Dictionnaire contenant les informations de la piste:
            - timestamp (int): Timestamp Unix de la lecture
            - date (str): Date formatée 'YYYY-MM-DD HH:MM'
            - artist (str): Nom de l'artiste
            - title (str): Titre de la piste
            - album (str): Nom de l'album
            - loved (bool): Statut favori (toujours False pour Roon)
            - artist_spotify_image (str|None): URL image artiste Spotify
            - album_spotify_image (str|None): URL image album Spotify
            - album_lastfm_image (str|None): URL image album Last.fm
            
    Returns:
        True si la sauvegarde a réussi, False en cas d'erreur.
        
    Examples:
        >>> track = {
        ...     "timestamp": 1768648694,
        ...     "date": "2026-01-17 11:18",
        ...     "artist": "Nina Simone",
        ...     "title": "Ain't No Use",
        ...     "album": "Pastel Blues"
        ... }
        >>> success = save_track(track)
        
    Note:
        Les nouvelles pistes sont insérées en début de liste pour un accès
        rapide aux lectures les plus récentes.
    """
    history = load_tracks_history()
    
    # Ajouter la nouvelle piste au début
    history["tracks"].insert(0, track_info)
    
    try:
        with open(ROON_TRACKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde dans {ROON_TRACKS_FILE}: {e}")
        return False

def load_roon_config() -> dict:
    """Charge la configuration Roon depuis le fichier JSON.
    
    Lit les paramètres de connexion Roon et les préférences d'écoute depuis
    le fichier de configuration. Applique des valeurs par défaut si certains
    paramètres sont manquants.
    
    Returns:
        Dictionnaire contenant la configuration Roon avec les clés:
        - token (str): Token d'authentification Roon
        - host (str): Adresse IP du serveur Roon Core
        - port (str): Port de connexion
        - listen_start_hour (int): Heure de début d'écoute (défaut: 6)
        - listen_end_hour (int): Heure de fin d'écoute (défaut: 23)
        - radio_stations (list): Liste des stations de radio à détecter
        
    Examples:
        >>> config = load_roon_config()
        >>> print(config['listen_start_hour'])
        6
        
    Note:
        Si le fichier n'existe pas ou est corrompu, retourne un dictionnaire
        avec les valeurs par défaut des heures d'écoute et stations radio.
    """
    default_radio_stations = [
        "RTS La Première",
        "RTS Couleur 3",
        "RTS Espace 2",
        "RTS Option Musique",
        "Radio Meuh",
        "Radio Nova"
    ]
    
    if os.path.exists(ROON_CONFIG_FILE):
        try:
            with open(ROON_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                print(f"📂 Configuration chargée depuis {ROON_CONFIG_FILE}")
                # Ajouter les valeurs par défaut si elles n'existent pas
                if 'listen_start_hour' not in config:
                    config['listen_start_hour'] = 6
                if 'listen_end_hour' not in config:
                    config['listen_end_hour'] = 23
                if 'radio_stations' not in config:
                    config['radio_stations'] = default_radio_stations
                return config
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de la configuration: {e}")
    # Valeurs par défaut
    return {
        'listen_start_hour': 6,
        'listen_end_hour': 23,
        'radio_stations': default_radio_stations
    }

def save_roon_config(config: dict) -> bool:
    """Sauvegarde la configuration Roon dans un fichier JSON.
    
    Persiste les paramètres de connexion Roon et les préférences dans un fichier
    JSON formaté pour une lecture facile.
    
    Args:
        config: Dictionnaire contenant les paramètres de configuration à sauvegarder.
            Clés attendues: token, host, port, listen_start_hour, listen_end_hour.
            
    Returns:
        True si la sauvegarde a réussi, False en cas d'erreur.
        
    Examples:
        >>> config = {'token': 'abc123', 'host': '192.168.1.1', 'port': '9330'}
        >>> success = save_roon_config(config)
        >>> print(success)
        True
        
    Note:
        Le fichier est sauvegardé avec une indentation de 2 espaces pour
        faciliter la lecture et l'édition manuelle.
    """
    try:
        with open(ROON_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration sauvegardée dans {ROON_CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde de la configuration: {e}")
        return False


def repair_null_spotify_images() -> int:
    """Parcourt le fichier JSON et répare les images Spotify manquantes (null).
    
    Charge le fichier chk-roon.json, identifie les entrées avec des images
    Spotify null, et tente de les récupérer à nouveau. Sauvegarde le fichier
    uniquement s'il y a eu des modifications.
    
    Returns:
        Nombre d'images réparées avec succès.
        
    Note:
        - Récupère un nouveau token Spotify avant de commencer
        - Ne modifie pas les entrées qui ont déjà des images valides
        - Affiche la progression pour chaque réparation
    """
    print("\n🔧 Détection d'anomalies - Vérification des images Spotify manquantes...")
    
    history = load_tracks_history()
    if not history.get("tracks"):
        print("[DEBUG] Aucune piste à réparer")
        return 0
    
    # Récupérer un token Spotify frais
    spotify_token = get_spotify_token()
    if not spotify_token:
        print("⚠️ Impossible de récupérer un token Spotify pour la réparation")
        return 0
    
    repaired_count = 0
    modified = False
    total_null_artists = 0
    total_null_albums = 0
    
    # Compter les valeurs null
    for track in history["tracks"]:
        if track.get("artist_spotify_image") is None and track.get("artist") != "Inconnu":
            total_null_artists += 1
        if track.get("album_spotify_image") is None and track.get("album") != "Inconnu":
            total_null_albums += 1
    
    if total_null_artists == 0 and total_null_albums == 0:
        print("✅ Aucune image Spotify manquante - Le fichier est OK")
        return 0
    
    print(f"📊 Trouvé {total_null_artists} images d'artistes manquantes et {total_null_albums} images d'albums manquantes")
    print("🔄 Réparation en cours...\n")
    
    for idx, track in enumerate(history["tracks"]):
        artist = track.get("artist", "Inconnu")
        album = track.get("album", "Inconnu")
        
        # Réparer l'image de l'artiste si null
        if track.get("artist_spotify_image") is None and artist != "Inconnu":
            print(f"[{idx + 1}/{len(history['tracks'])}] Réparation artiste: {artist}")
            artist_image = search_spotify_artist_image(spotify_token, artist)
            if artist_image:
                track["artist_spotify_image"] = artist_image
                modified = True
                repaired_count += 1
                print(f"  ✅ Image artiste récupérée")
            time.sleep(0.5)  # Éviter le rate limiting
        
        # Réparer l'image de l'album si null
        if track.get("album_spotify_image") is None and album != "Inconnu":
            print(f"[{idx + 1}/{len(history['tracks'])}] Réparation album: {artist} - {album}")
            album_image = search_spotify_album_image(spotify_token, artist, album)
            if album_image:
                track["album_spotify_image"] = album_image
                modified = True
                repaired_count += 1
                print(f"  ✅ Image album récupérée")
            time.sleep(0.5)  # Éviter le rate limiting
    
    # Sauvegarder uniquement si modifié
    if modified:
        try:
            with open(ROON_TRACKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
            print(f"\n✅ Réparation terminée: {repaired_count} images récupérées et sauvegardées")
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde: {e}")
    else:
        print(f"\n⚠️ Aucune image n'a pu être récupérée")
    
    return repaired_count


def is_within_listening_hours(start_hour: int, end_hour: int) -> bool:
    """Vérifie si l'heure actuelle est dans la plage d'écoute configurée.
    
    Compare l'heure système actuelle avec la plage horaire définie pour
    déterminer si les lectures doivent être enregistrées.
    
    Args:
        start_hour: Heure de début de la plage d'écoute (0-23).
        end_hour: Heure de fin de la plage d'écoute (0-23).
        
    Returns:
        True si l'heure actuelle est dans la plage [start_hour, end_hour],
        False sinon.
        
    Examples:
        >>> # Si l'heure actuelle est 14:00
        >>> is_within_listening_hours(6, 23)
        True
        >>> is_within_listening_hours(20, 22)
        False
        
    Note:
        La comparaison inclut l'heure de fin (end_hour:00 à end_hour:59).
        Par exemple, end_hour=23 inclut toute la période de 23:00 à 23:59.
    """
    now = datetime.now()
    current_hour = now.hour
    
    # Si end_hour est 23, on accepte jusqu'à 23:59
    if current_hour >= start_hour and current_hour <= end_hour:
        return True
    return False

def test_roon_connection() -> RoonApi | None:
    """Initialise et teste la connexion au serveur Roon Core.
    
    Effectue une découverte automatique du serveur Roon Core sur le réseau local,
    puis tente d'établir une connexion authentifiée. Réutilise un token existant
    si disponible dans la configuration.
    
    Returns:
        Instance RoonApi connectée et authentifiée, ou None en cas d'échec.
        
    Raises:
        None: Les erreurs sont capturées et affichées, puis None est retourné.
        
    Examples:
        >>> roonapi = test_roon_connection()
        🎵 Initialisation de la connexion à Roon...
        ⏳ Recherche de Roon Core sur le réseau...
        ✅ Roon Core trouvé: ('192.168.1.253', '9330')
        ✅ Connexion établie avec Roon Core!
        
    Note:
        - Le timeout de connexion est de 30 secondes
        - Si aucun serveur n'est trouvé, vérifiez:
          1. Que Roon Core est en cours d'exécution
          2. Que le script et Roon Core sont sur le même réseau
        - Si le token n'est pas reçu, autorisez l'extension dans:
          Roon > Paramètres > Extensions
    """
    print("🎵 Initialisation de la connexion à Roon...")
    
    # Charger la configuration existante
    config = load_roon_config()
    token = config.get('token')
    saved_host = config.get('host')
    saved_port = config.get('port')
    
    # Créer une instance de l'API Roon
    appinfo = {
        'extension_id': 'python_roon_test',
        'display_name': ROON_APP_NAME,
        'display_version': ROON_APP_VERSION,
        'publisher': ROON_PUBLISHER,
        'email': ROON_EMAIL
    }
    
    # Découverte automatique du Roon Core sur le réseau
    print("⏳ Recherche de Roon Core sur le réseau...")
    discover = RoonDiscovery(None)
    servers = discover.all()
    
    if not servers:
        print("❌ Aucun Roon Core trouvé. Vérifiez que:")
        print("   1. Roon Core est en cours d'exécution")
        print("   2. Ce script et Roon Core sont sur le même réseau")
        return None
    
    # Utiliser le premier serveur trouvé
    server = servers[0]
    print(f"✅ Roon Core trouvé: {server}")
    
    # Le serveur est un tuple (ip, port)
    host, port = server
    
    # Se connecter au serveur (réutiliser le token si disponible)
    roonapi = RoonApi(appinfo, token, host, port, blocking_init=False)
    
    # Attendre que la connexion soit établie
    timeout = 30
    start_time = time.time()
    
    while not roonapi.token and (time.time() - start_time) < timeout:
        time.sleep(1)
        if roonapi.token:
            break
    
    if not roonapi.token:
        print("❌ Token non reçu. Vérifiez que:")
        print("   Vous avez autorisé l'extension dans Roon (Paramètres > Extensions)")
        return None
    
    print("✅ Connexion établie avec Roon Core!")
    print(f"📍 Token: {roonapi.token[:20]}...")
    
    return roonapi

def explore_roon_info(roonapi: RoonApi, config: dict) -> None:
    """Surveille et enregistre en continu les lectures musicales Roon.
    
    Boucle principale qui:
    1. Affiche les informations système (zones, sorties audio)
    2. Surveille en continu les pistes jouées dans toutes les zones
    3. Vérifie la plage horaire d'écoute configurée
    4. Enrichit les métadonnées avec images Spotify et Last.fm
    5. Enregistre les nouvelles lectures dans le fichier JSON
    
    Args:
        roonapi: Instance RoonApi connectée et authentifiée.
        config: Dictionnaire de configuration contenant:
            - listen_start_hour (int): Heure de début d'écoute
            - listen_end_hour (int): Heure de fin d'écoute
            
    Returns:
        None: La fonction s'exécute en boucle infinie jusqu'à interruption.
        
    Raises:
        KeyboardInterrupt: Capturée pour arrêt propre du programme.
        
    Examples:
        >>> config = {'listen_start_hour': 6, 'listen_end_hour': 23}
        >>> explore_roon_info(roonapi, config)
        📊 Informations Roon:
        🔊 Zones disponibles: 1
        🎵 Surveillance des lectures en cours...
        
    Note:
        - Vérifie l'état toutes les 45 secondes
        - N'enregistre que les pistes en lecture (state='playing')
        - Ignore les duplicatas (même piste rejouée)
        - Respecte la plage horaire configurée
        - Affiche des messages de debug détaillés
    """
    if not roonapi:
        return
    
    # Récupérer les heures d'écoute depuis la config
    listen_start_hour = config.get('listen_start_hour', 6)
    listen_end_hour = config.get('listen_end_hour', 23)
    
    print("\n📊 Informations Roon:")
    print("-" * 50)
    
    # Obtenir les zones (endpoints de lecture)
    zones = roonapi.zones
    print(f"\n🔊 Zones disponibles: {len(zones)}")
    for zone_id, zone in zones.items():
        print(f"  • {zone['display_name']} (ID: {zone_id})")
    
    # Obtenir les sorties audio
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
    
    # Récupérer le token Spotify une fois pour toute la session
    spotify_token = get_spotify_token()
    if spotify_token:
        print(f"✅ Token Spotify récupéré: {spotify_token[:20]}...")
    else:
        print("⚠️ Impossible de récupérer le token Spotify - les images Spotify ne seront pas disponibles")
    
    # Variable pour suivre la dernière piste jouée
    last_track_key = None
    
    # Variable pour suivre le dernier timestamp Last.fm traité
    last_lastfm_timestamp = 0
    
    try:
        while True:
            # Vérifier et enregistrer les lectures Last.fm
            if lastfm_network and LASTFM_USERNAME:
                try:
                    print("\n[DEBUG] Vérification des lectures Last.fm...")
                    lastfm_tracks = get_lastfm_recent_tracks()
                    
                    # Parcourir les lectures Last.fm (du plus ancien au plus récent)
                    new_tracks_count = 0
                    for track_item in reversed(lastfm_tracks):
                        timestamp = int(track_item.timestamp)
                        
                        # Ignorer si déjà traité dans une itération précédente
                        if timestamp <= last_lastfm_timestamp:
                            continue
                        
                        # Extraire les informations
                        artist = track_item.track.artist.name
                        title = track_item.track.title
                        album = track_item.album or "Album inconnu"
                        loved = getattr(track_item, 'loved', False)
                        
                        # Vérifier si cette lecture existe déjà
                        if is_track_already_saved(artist, title, album, timestamp):
                            print(f"[DEBUG] Last.fm: Piste déjà enregistrée: {artist} - {title} ({timestamp})")
                            continue
                        
                        # Vérifier si on est dans la plage horaire d'écoute
                        track_datetime = datetime.fromtimestamp(timestamp, timezone.utc).astimezone()
                        track_hour = track_datetime.hour
                        if track_hour < listen_start_hour or track_hour > listen_end_hour:
                            print(f"[DEBUG] Last.fm: Hors plage horaire: {artist} - {title} ({track_hour:02d}:00)")
                            continue
                        
                        # Enrichir avec les images
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
                        
                        # Mettre à jour le dernier timestamp traité
                        if timestamp > last_lastfm_timestamp:
                            last_lastfm_timestamp = timestamp
                    
                    if new_tracks_count > 0:
                        print(f"[DEBUG] {new_tracks_count} nouvelle(s) lecture(s) Last.fm enregistrée(s)")
                    else:
                        print("[DEBUG] Aucune nouvelle lecture Last.fm")
                        
                except Exception as e:
                    print(f"⚠️ Erreur lors du traitement des lectures Last.fm: {e}")
            
            # Parcourir toutes les zones actives Roon
            # Parcourir toutes les zones actives
            for zone_id, zone in roonapi.zones.items():
                # Vérifier s'il y a une lecture en cours
                now_playing = zone.get('now_playing')
                if now_playing:
                    # Extraire les informations de la piste
                    three_line = now_playing.get('three_line', {})
                    line1 = three_line.get('line1', 'Inconnu')  
                    line2 = three_line.get('line2', 'Inconnu')
                    line3 = three_line.get('line3', 'Inconnu')
                    
                    # Debug: afficher ce que Roon retourne
                    print(f"\n[DEBUG] Roon three_line - line1: {line1}, line2: {line2}, line3: {line3}")
                    
                    # Roon utilise généralement: line1=Titre, line2=Artiste, line3=Album
                    # Mais vérifions d'abord avec le debug
                    title = line1
                    artist = line2  
                    album = line3
                    
                    state = zone.get('state', 'unknown')
                    
                    # Créer une clé unique pour cette piste
                    track_key = f"{artist}|{title}|{album}"
                    
                    # N'enregistrer que si c'est une nouvelle piste qui joue (pas en pause)
                    if state == 'playing' and track_key != last_track_key:
                        # Vérifier si on est dans la plage horaire d'écoute
                        if not is_within_listening_hours(listen_start_hour, listen_end_hour):
                            current_time = datetime.now().strftime('%H:%M')
                            print(f"\n⏸️  {current_time} - Hors plage horaire d'écoute ({listen_start_hour:02d}:00-{listen_end_hour:02d}:59)")
                            print(f"   Piste ignorée: {artist} - {title}")
                            # On met à jour last_track_key pour ne pas spam le message
                            last_track_key = track_key
                            continue
                        
                        last_track_key = track_key
                        
                        # Détecter et corriger les enregistrements de radio
                        if is_radio_station(title, config.get('radio_stations', [])):
                            print(f"[DEBUG] 📻 Station de radio détectée: {title}")
                            parsed = parse_radio_artist_field(artist)
                            if parsed:
                                original_artist = artist
                                artist, title = parsed
                                print(f"[DEBUG] 📻 Extraction radio - Artiste: '{artist}', Titre: '{title}'")
                                # Rechercher l'album sur Spotify
                                album = search_spotify_track_album(spotify_token, artist, title)
                                if album:
                                    print(f"[DEBUG] 📻 Album trouvé: '{album}'")
                                else:
                                    print(f"[DEBUG] 📻 Album non trouvé - Écoute radio ignorée")
                                    # Ignorer cette écoute radio car on ne peut pas déterminer l'album
                                    last_track_key = track_key
                                    continue
                            else:
                                print(f"[DEBUG] 📻 Format non musical détecté (émission/journal) - Écoute ignorée")
                                # Ignorer les écoutes où on ne peut pas extraire artiste/titre
                                last_track_key = track_key
                                continue
                        
                        print(f"[DEBUG] Recherche Spotify pour artiste: '{artist}', album: '{album}'")
                        
                        # Récupérer les images
                        artist_spotify_image = search_spotify_artist_image(spotify_token, artist)
                        album_spotify_image = search_spotify_album_image(spotify_token, artist, album) if album != 'Inconnu' else None
                        album_lastfm_image = search_lastfm_album_image(artist, album) if album != 'Inconnu' else None
                        
                        print(f"[DEBUG] Résultats - Artist Spotify: {artist_spotify_image}, Album Spotify: {album_spotify_image}, Album Last.fm: {album_lastfm_image}")
                        
                        # Créer l'entrée de données
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
            
            # Attendre un peu avant de revérifier
            time.sleep(45)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Arrêt de la surveillance")


def main() -> None:
    """Point d'entrée principal du programme.
    
    Orchestre le flux d'exécution complet:
    1. Vérification qu'aucune autre instance n'est en cours
    2. Chargement de la configuration Roon
    3. Connexion au serveur Roon Core
    4. Sauvegarde du token d'authentification si nouveau
    5. Lancement de la surveillance des lectures
    
    Le programme s'exécute en boucle infinie jusqu'à interruption manuelle
    (Ctrl+C) ou erreur fatale.
    
    Raises:
        KeyboardInterrupt: Capture l'interruption utilisateur (Ctrl+C).
        Exception: Capture toutes les autres exceptions et affiche le traceback.
        
    Examples:
        >>> main()
        🎵 Initialisation de la connexion à Roon...
        ✅ Connexion établie avec Roon Core!
        🎵 Surveillance des lectures en cours...
        
    Note:
        La fonction gère automatiquement la persistance de la configuration
        et la reconnexion en cas de changement de serveur Roon.
        Un seul processus peut s'exécuter à la fois grâce au système de verrouillage.
    """
    # Vérifier qu'aucune autre instance n'est en cours
    if not acquire_lock():
        print("❌ Une instance du Roon Tracker est déjà en cours d'exécution.")
        print("   Arrêtez l'instance en cours avant d'en lancer une nouvelle.")
        print(f"   (Fichier de verrouillage: {ROON_LOCK_FILE})")
        sys.exit(1)
    
    try:
        # Charger la configuration
        config = load_roon_config()
        
        # Vérifier et réparer les images Spotify manquantes au démarrage
        repair_null_spotify_images()
        
        # Test de connexion
        roonapi = test_roon_connection()
        
        if roonapi:
            # Sauvegarder le token et les infos de connexion si nécessaire
            if roonapi.token and (not config.get('token') or config.get('token') != roonapi.token):
                # Récupérer les infos du serveur
                discover = RoonDiscovery(None)
                servers = discover.all()
                if servers:
                    host, port = servers[0]
                    config['token'] = roonapi.token
                    config['host'] = host
                    config['port'] = port
                    # Conserver les heures d'écoute si elles existent déjà
                    if 'listen_start_hour' not in config:
                        config['listen_start_hour'] = 6
                    if 'listen_end_hour' not in config:
                        config['listen_end_hour'] = 23
                    save_roon_config(config)
                    print(f"\n✅ Configuration sauvegardée")
            
            # Explorer les informations et surveiller
            explore_roon_info(roonapi, config)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Toujours libérer le verrou à la fin
        release_lock()
        print("\n🔓 Verrou libéré - une nouvelle instance peut être lancée")


if __name__ == "__main__":
    main()
