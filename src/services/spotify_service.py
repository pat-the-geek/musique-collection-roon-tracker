"""Service d'intégration avec l'API Spotify.

Ce module centralise toutes les interactions avec l'API Spotify:
- Authentification OAuth 2.0 Client Credentials Flow
- Recherche d'images d'artistes
- Recherche d'images d'albums avec validation et scoring
- Gestion du cache et des tokens
- Retry automatique avec exponential backoff

Version: 1.0.0
Date: 24 janvier 2026
Auteur: Patrick Ostertag
"""

import base64
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

# Import des constantes et utilitaires
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    SPOTIFY_TOKEN_URL,
    SPOTIFY_SEARCH_URL,
    SPOTIFY_TOKEN_REFRESH_MARGIN,
    SPOTIFY_ARTIST_SEARCH_LIMIT,
    SPOTIFY_ALBUM_SEARCH_LIMIT,
    SPOTIFY_MIN_SCORE_PRIMARY,
    SPOTIFY_MIN_SCORE_FALLBACK,
    DEFAULT_HTTP_TIMEOUT,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RATE_LIMIT_DELAY,
    ERROR_MISSING_SPOTIFY_CREDENTIALS,
    ERROR_TOKEN_RETRIEVAL
)
from services.metadata_cleaner import (
    clean_artist_name,
    clean_album_name,
    normalize_string_for_comparison,
    artist_matches,
    calculate_album_match_score
)

# Configuration du logger
logger = logging.getLogger(__name__)


class SpotifyCache:
    """Classe de gestion du cache pour Spotify (tokens et résultats de recherche).
    
    Centralise la logique de cache pour:
    - Tokens d'authentification avec expiration
    - Images d'artistes
    - Images d'albums
    
    Attributes:
        token_cache: Cache du token Spotify avec timestamp d'expiration
        artist_images: Cache des URLs d'images d'artistes
        album_images: Cache des URLs d'images d'albums
    """
    
    def __init__(self):
        """Initialise un cache vide."""
        self.token_cache = {
            "access_token": None,
            "expires_at": 0
        }
        self.artist_images = {}
        self.album_images = {}
    
    def get_token(self) -> Optional[str]:
        """Récupère le token en cache s'il est encore valide.
        
        Returns:
            Token valide ou None si expiré ou absent.
        """
        if self.token_cache["access_token"] and \
           time.time() < self.token_cache["expires_at"] - SPOTIFY_TOKEN_REFRESH_MARGIN:
            return self.token_cache["access_token"]
        return None
    
    def set_token(self, token: str, expires_in: int = 3600):
        """Enregistre un nouveau token dans le cache.
        
        Args:
            token: Token d'accès Spotify.
            expires_in: Durée de validité en secondes (défaut: 3600).
        """
        self.token_cache["access_token"] = token
        self.token_cache["expires_at"] = time.time() + expires_in
    
    def get_artist_image(self, artist_name: str) -> Optional[str]:
        """Récupère l'URL de l'image d'un artiste depuis le cache.
        
        Args:
            artist_name: Nom de l'artiste.
            
        Returns:
            URL de l'image ou None si absent du cache.
        """
        return self.artist_images.get(artist_name)
    
    def set_artist_image(self, artist_name: str, url: Optional[str]):
        """Enregistre l'URL de l'image d'un artiste dans le cache.
        
        Args:
            artist_name: Nom de l'artiste.
            url: URL de l'image ou None si non trouvée.
        """
        self.artist_images[artist_name] = url
    
    def get_album_image(self, artist_name: str, album_name: str) -> Optional[str]:
        """Récupère l'URL de l'image d'un album depuis le cache.
        
        Args:
            artist_name: Nom de l'artiste.
            album_name: Nom de l'album.
            
        Returns:
            URL de l'image ou None si absent du cache.
        """
        cache_key = f"{artist_name}|{album_name}"
        return self.album_images.get(cache_key)
    
    def set_album_image(self, artist_name: str, album_name: str, url: Optional[str]):
        """Enregistre l'URL de l'image d'un album dans le cache.
        
        Args:
            artist_name: Nom de l'artiste.
            album_name: Nom de l'album.
            url: URL de l'image ou None si non trouvée.
        """
        cache_key = f"{artist_name}|{album_name}"
        self.album_images[cache_key] = url


# Instance globale du cache (peut être remplacée par injection de dépendance)
_default_cache = SpotifyCache()


def get_spotify_token(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    cache: SpotifyCache = None
) -> Optional[str]:
    """Récupère un token d'accès Spotify via OAuth 2.0 Client Credentials Flow.
    
    Utilise un système de cache pour réutiliser les tokens valides et minimiser
    les appels d'authentification à l'API Spotify. Le token est rafraîchi
    automatiquement 60 secondes avant son expiration.
    
    Args:
        client_id: ID client Spotify (optionnel, utilise env var par défaut).
        client_secret: Secret client Spotify (optionnel, utilise env var par défaut).
        cache: Instance de SpotifyCache (optionnel, utilise cache global par défaut).
        
    Returns:
        Token d'accès Spotify valide, ou None si l'authentification échoue.
        
    Examples:
        >>> token = get_spotify_token()
        >>> if token:
        ...     # Utiliser le token pour les requêtes API
        ...     pass
    """
    if cache is None:
        cache = _default_cache
    
    # Vérifier le cache en premier
    cached_token = cache.get_token()
    if cached_token:
        return cached_token
    
    # Charger les credentials depuis l'environnement si non fournis
    if client_id is None:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
    if client_secret is None:
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.warning(ERROR_MISSING_SPOTIFY_CREDENTIALS)
        return None
    
    # Préparer la requête d'authentification
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(credentials).decode("utf-8")
    
    req = urllib.request.Request(SPOTIFY_TOKEN_URL, data=data, method="POST")
    req.add_header("Authorization", f"Basic {auth_header}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_HTTP_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
        
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in", 3600)
        
        if access_token:
            cache.set_token(access_token, expires_in)
            logger.info("✅ Token Spotify récupéré avec succès")
            return access_token
        
    except urllib.error.URLError as e:
        logger.error(f"{ERROR_TOKEN_RETRIEVAL}: {e}")
    except Exception as e:
        logger.error(f"{ERROR_TOKEN_RETRIEVAL}: {e}")
    
    return None


def search_spotify_artist_image(
    token: Optional[str],
    artist_name: str,
    max_retries: int = DEFAULT_RETRY_COUNT,
    cache: SpotifyCache = None
) -> Optional[str]:
    """Recherche l'image principale d'un artiste sur Spotify.
    
    Effectue une recherche sur l'API Spotify pour récupérer l'image de profil
    d'un artiste. Utilise un cache local pour éviter les requêtes répétitives.
    Le nom de l'artiste est nettoyé avant la recherche pour améliorer les résultats.
    
    Args:
        token: Token d'accès Spotify valide.
        artist_name: Nom de l'artiste à rechercher.
        max_retries: Nombre maximum de tentatives (défaut: 3).
        cache: Instance de SpotifyCache (optionnel).
        
    Returns:
        URL de l'image de profil de l'artiste, ou None si non trouvée.
        
    Examples:
        >>> token = get_spotify_token()
        >>> url = search_spotify_artist_image(token, "Nina Simone")
        >>> print(url)
        'https://i.scdn.co/image/...'
    """
    if cache is None:
        cache = _default_cache
    
    # Vérifier le cache
    cached_url = cache.get_artist_image(artist_name)
    if cached_url is not None:
        return cached_url
    
    if not token:
        cache.set_artist_image(artist_name, None)
        return None
    
    # Nettoyer le nom de l'artiste
    cleaned_artist = clean_artist_name(artist_name)
    
    # Construire la requête
    query = urllib.parse.quote(f"artist:{cleaned_artist}")
    url = f"{SPOTIFY_SEARCH_URL}?q={query}&type=artist&limit={SPOTIFY_ARTIST_SEARCH_LIMIT}"
    
    for attempt in range(max_retries):
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_HTTP_TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            items = data.get("artists", {}).get("items", [])
            if items and items[0].get("images"):
                image_url = items[0]["images"][0]["url"]
                cache.set_artist_image(artist_name, image_url)
                logger.debug(f"✅ Image artiste trouvée: {cleaned_artist}")
                return image_url
            
            # Aucune image trouvée
            cache.set_artist_image(artist_name, None)
            return None
            
        except urllib.error.HTTPError as e:
            if e.code == 401:
                # Token expiré, essayer de rafraîchir
                logger.warning(f"Token expiré (401), tentative {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            elif e.code == 429:
                # Rate limit
                logger.warning(f"Rate limit (429), pause de {DEFAULT_RATE_LIMIT_DELAY}s")
                if attempt < max_retries - 1:
                    time.sleep(DEFAULT_RATE_LIMIT_DELAY)
                    continue
            logger.error(f"Erreur HTTP {e.code} lors de la recherche artiste {cleaned_artist}")
            break
            
        except Exception as e:
            logger.error(f"Erreur recherche artiste {cleaned_artist}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            break
    
    cache.set_artist_image(artist_name, None)
    return None


def search_spotify_album_image(
    token: Optional[str],
    artist_name: str,
    album_name: str,
    max_retries: int = DEFAULT_RETRY_COUNT,
    cache: SpotifyCache = None
) -> Optional[str]:
    """Recherche l'image de couverture d'un album sur Spotify avec validation.
    
    Effectue une recherche d'album avec validation stricte de l'artiste et système
    de scoring pour sélectionner le meilleur résultat. Inclut un système de fallback
    si la recherche primaire échoue.
    
    Args:
        token: Token d'accès Spotify valide.
        artist_name: Nom de l'artiste.
        album_name: Nom de l'album.
        max_retries: Nombre maximum de tentatives (défaut: 3).
        cache: Instance de SpotifyCache (optionnel).
        
    Returns:
        URL de l'image de couverture de l'album, ou None si non trouvée.
        
    Examples:
        >>> token = get_spotify_token()
        >>> url = search_spotify_album_image(token, "Nina Simone", "Little Girl Blue")
        >>> print(url)
        'https://i.scdn.co/image/...'
    """
    if cache is None:
        cache = _default_cache
    
    # Vérifier le cache
    cached_url = cache.get_album_image(artist_name, album_name)
    if cached_url is not None:
        return cached_url
    
    if not token:
        cache.set_album_image(artist_name, album_name, None)
        return None
    
    # Nettoyer les métadonnées
    cleaned_artist = clean_artist_name(artist_name)
    cleaned_album = clean_album_name(album_name)
    
    # Tentative 1: Recherche avec artiste + album
    result = _search_album_with_artist(
        token, cleaned_artist, cleaned_album, 
        SPOTIFY_MIN_SCORE_PRIMARY, max_retries
    )
    
    if result:
        cache.set_album_image(artist_name, album_name, result)
        return result
    
    # Tentative 2: Recherche par album uniquement (fallback pour Various Artists)
    result = _search_album_only(
        token, cleaned_artist, cleaned_album,
        SPOTIFY_MIN_SCORE_FALLBACK, max_retries
    )
    
    cache.set_album_image(artist_name, album_name, result)
    return result


def _search_album_with_artist(
    token: str,
    artist: str,
    album: str,
    min_score: int,
    max_retries: int
) -> Optional[str]:
    """Recherche interne d'album avec artiste (méthode primaire).
    
    Args:
        token: Token Spotify valide.
        artist: Nom de l'artiste nettoyé.
        album: Nom de l'album nettoyé.
        min_score: Score minimum requis pour validation.
        max_retries: Nombre de tentatives.
        
    Returns:
        URL de l'image ou None.
    """
    query = urllib.parse.quote(f"artist:{artist} album:{album}")
    url = f"{SPOTIFY_SEARCH_URL}?q={query}&type=album&limit={SPOTIFY_ALBUM_SEARCH_LIMIT}"
    
    for attempt in range(max_retries):
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_HTTP_TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            albums = data.get("albums", {}).get("items", [])
            best_match = _find_best_album_match(artist, album, albums, min_score)
            
            if best_match:
                logger.debug(f"✅ Album trouvé: {artist} - {album}")
                return best_match
            
            return None
            
        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt < max_retries - 1:
                logger.warning("Token expiré (401), retry...")
                time.sleep(1)
                continue
            elif e.code == 429 and attempt < max_retries - 1:
                logger.warning(f"Rate limit (429), pause {DEFAULT_RATE_LIMIT_DELAY}s")
                time.sleep(DEFAULT_RATE_LIMIT_DELAY)
                continue
            logger.error(f"Erreur HTTP {e.code} lors recherche album")
            break
            
        except Exception as e:
            logger.error(f"Erreur recherche album: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            break
    
    return None


def _search_album_only(
    token: str,
    artist: str,
    album: str,
    min_score: int,
    max_retries: int
) -> Optional[str]:
    """Recherche interne d'album sans artiste (fallback).
    
    Args:
        token: Token Spotify valide.
        artist: Nom de l'artiste (pour validation).
        album: Nom de l'album nettoyé.
        min_score: Score minimum requis.
        max_retries: Nombre de tentatives.
        
    Returns:
        URL de l'image ou None.
    """
    query = urllib.parse.quote(album)
    url = f"{SPOTIFY_SEARCH_URL}?q={query}&type=album&limit={SPOTIFY_ALBUM_SEARCH_LIMIT}"
    
    for attempt in range(max_retries):
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_HTTP_TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            albums = data.get("albums", {}).get("items", [])
            best_match = _find_best_album_match(artist, album, albums, min_score)
            
            if best_match:
                logger.debug(f"✅ Album trouvé (fallback): {album}")
                return best_match
            
            return None
            
        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt < max_retries - 1:
                time.sleep(1)
                continue
            elif e.code == 429 and attempt < max_retries - 1:
                time.sleep(DEFAULT_RATE_LIMIT_DELAY)
                continue
            break
            
        except Exception as e:
            logger.error(f"Erreur recherche album (fallback): {e}")
            break
    
    return None


def _find_best_album_match(
    artist: str,
    album: str,
    albums: list,
    min_score: int
) -> Optional[str]:
    """Trouve le meilleur album correspondant avec validation artiste et scoring.
    
    Args:
        artist: Nom de l'artiste recherché.
        album: Nom de l'album recherché.
        albums: Liste des albums retournés par Spotify.
        min_score: Score minimum pour validation.
        
    Returns:
        URL de l'image du meilleur album ou None.
    """
    best_score = 0
    best_url = None
    
    for album_item in albums:
        # Validation de l'artiste
        album_artists = album_item.get("artists", [])
        if not album_artists:
            continue
        
        found_artist = album_artists[0].get("name", "")
        if not artist_matches(artist, found_artist):
            continue
        
        # Calcul du score de correspondance d'album
        found_album = album_item.get("name", "")
        score = calculate_album_match_score(album, found_album)
        
        if score > best_score:
            best_score = score
            images = album_item.get("images", [])
            if images:
                best_url = images[0]["url"]  # Prendre la plus grande image
    
    # Retourner seulement si score >= seuil
    if best_score >= min_score:
        return best_url
    
    return None
