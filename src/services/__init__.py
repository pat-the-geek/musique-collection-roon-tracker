"""Services partagés pour l'intégration avec les APIs externes.

Ce module contient les services réutilisables pour interagir avec:
- Spotify API (authentification, recherche artistes/albums)
- Last.fm API (recherche images albums)
- Nettoyage et normalisation de métadonnées

Version: 1.0.0
Date: 24 janvier 2026
"""

from .spotify_service import (
    get_spotify_token,
    search_spotify_artist_image,
    search_spotify_album_image,
    SpotifyCache
)

from .metadata_cleaner import (
    clean_artist_name,
    clean_album_name,
    normalize_string_for_comparison,
    artist_matches
)

__all__ = [
    'get_spotify_token',
    'search_spotify_artist_image',
    'search_spotify_album_image',
    'SpotifyCache',
    'clean_artist_name',
    'clean_album_name',
    'normalize_string_for_comparison',
    'artist_matches'
]
