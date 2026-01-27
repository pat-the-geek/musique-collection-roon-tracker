"""Tests unitaires complets pour le module spotify_service.

Ces tests vérifient toutes les fonctionnalités du service Spotify:
- Authentification OAuth et gestion du cache de token
- Recherche d'images d'artistes
- Recherche d'images d'albums avec validation et scoring
- Gestion des erreurs et retry logic
- Mécanismes de cache

Version: 1.0.0
Date: 26 janvier 2026
"""

import sys
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock
from urllib.error import HTTPError, URLError
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.spotify_service import (
    SpotifyCache,
    get_spotify_token,
    search_spotify_artist_image,
    search_spotify_album_image,
    _search_album_with_artist,
    _search_album_only,
    _find_best_album_match
)
from constants import (
    SPOTIFY_TOKEN_REFRESH_MARGIN,
    SPOTIFY_MIN_SCORE_PRIMARY,
    SPOTIFY_MIN_SCORE_FALLBACK,
    DEFAULT_RETRY_COUNT
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def fresh_cache():
    """Retourne une instance vierge de SpotifyCache pour chaque test."""
    return SpotifyCache()


@pytest.fixture
def valid_token():
    """Retourne un token Spotify valide pour les tests."""
    return "BQC1234567890ABCDEF_valid_test_token"


@pytest.fixture
def mock_spotify_token_response():
    """Retourne une réponse d'authentification Spotify simulée."""
    return {
        "access_token": "BQC_test_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600
    }


@pytest.fixture
def mock_artist_search_response():
    """Retourne une réponse de recherche d'artiste simulée."""
    return {
        "artists": {
            "items": [
                {
                    "name": "Nina Simone",
                    "images": [
                        {"url": "https://i.scdn.co/image/artist_image.jpg"}
                    ]
                }
            ]
        }
    }


@pytest.fixture
def mock_album_search_response():
    """Retourne une réponse de recherche d'album simulée."""
    return {
        "albums": {
            "items": [
                {
                    "name": "Little Girl Blue",
                    "artists": [{"name": "Nina Simone"}],
                    "images": [
                        {"url": "https://i.scdn.co/image/album_cover.jpg"}
                    ]
                }
            ]
        }
    }


@pytest.fixture
def mock_env_with_spotify(monkeypatch):
    """Configure les variables d'environnement Spotify pour les tests."""
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id_12345")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret_67890")


# ============================================================================
# Tests pour SpotifyCache
# ============================================================================

class TestSpotifyCache:
    """Tests de la classe SpotifyCache."""
    
    def test_cache_initialization(self, fresh_cache):
        """Teste l'initialisation du cache."""
        assert fresh_cache.token_cache["access_token"] is None
        assert fresh_cache.token_cache["expires_at"] == 0
        assert len(fresh_cache.artist_images) == 0
        assert len(fresh_cache.album_images) == 0
    
    def test_token_set_and_get(self, fresh_cache):
        """Teste l'enregistrement et la récupération d'un token."""
        token = "test_token_123"
        fresh_cache.set_token(token, expires_in=3600)
        
        retrieved = fresh_cache.get_token()
        assert retrieved == token
        assert fresh_cache.token_cache["expires_at"] > time.time()
    
    def test_token_expiration(self, fresh_cache):
        """Teste qu'un token expiré n'est pas retourné."""
        token = "test_token_expired"
        # Token qui expire dans 30 secondes (moins que le margin de 60s)
        fresh_cache.set_token(token, expires_in=30)
        
        # Le token ne doit pas être retourné car trop proche de l'expiration
        retrieved = fresh_cache.get_token()
        assert retrieved is None
    
    def test_token_valid_with_margin(self, fresh_cache):
        """Teste qu'un token avec suffisamment de marge est retourné."""
        token = "test_token_valid"
        fresh_cache.set_token(token, expires_in=3600)
        
        retrieved = fresh_cache.get_token()
        assert retrieved == token
    
    def test_artist_image_cache(self, fresh_cache):
        """Teste le cache d'images d'artistes."""
        artist = "Nina Simone"
        url = "https://example.com/nina.jpg"
        
        # Initialement absent
        assert fresh_cache.get_artist_image(artist) is None
        
        # Après ajout
        fresh_cache.set_artist_image(artist, url)
        assert fresh_cache.get_artist_image(artist) == url
    
    def test_artist_image_cache_none_value(self, fresh_cache):
        """Teste le cache avec valeur None (artiste non trouvé)."""
        artist = "Unknown Artist"
        
        fresh_cache.set_artist_image(artist, None)
        assert fresh_cache.get_artist_image(artist) is None
        assert artist in fresh_cache.artist_images
    
    def test_album_image_cache_composite_key(self, fresh_cache):
        """Teste le cache d'albums avec clé composite."""
        artist = "Nina Simone"
        album = "Little Girl Blue"
        url = "https://example.com/album.jpg"
        
        # Initialement absent
        assert fresh_cache.get_album_image(artist, album) is None
        
        # Après ajout
        fresh_cache.set_album_image(artist, album, url)
        assert fresh_cache.get_album_image(artist, album) == url
    
    def test_album_image_cache_different_albums(self, fresh_cache):
        """Teste que différents albums sont distingués dans le cache."""
        artist = "Nina Simone"
        album1 = "Little Girl Blue"
        album2 = "Pastel Blues"
        url1 = "https://example.com/album1.jpg"
        url2 = "https://example.com/album2.jpg"
        
        fresh_cache.set_album_image(artist, album1, url1)
        fresh_cache.set_album_image(artist, album2, url2)
        
        assert fresh_cache.get_album_image(artist, album1) == url1
        assert fresh_cache.get_album_image(artist, album2) == url2


# ============================================================================
# Tests pour get_spotify_token()
# ============================================================================

class TestGetSpotifyToken:
    """Tests de la fonction get_spotify_token."""
    
    def test_token_from_cache(self, fresh_cache, valid_token):
        """Teste la récupération d'un token depuis le cache."""
        fresh_cache.set_token(valid_token, expires_in=3600)
        
        result = get_spotify_token(
            client_id="test_id",
            client_secret="test_secret",
            cache=fresh_cache
        )
        
        assert result == valid_token
    
    def test_token_missing_credentials(self, fresh_cache):
        """Teste le comportement avec credentials manquants."""
        result = get_spotify_token(
            client_id=None,
            client_secret=None,
            cache=fresh_cache
        )
        
        assert result is None
    
    def test_token_missing_client_id(self, fresh_cache):
        """Teste avec client_id manquant."""
        result = get_spotify_token(
            client_id=None,
            client_secret="secret",
            cache=fresh_cache
        )
        
        assert result is None
    
    def test_token_missing_client_secret(self, fresh_cache):
        """Teste avec client_secret manquant."""
        result = get_spotify_token(
            client_id="client_id",
            client_secret=None,
            cache=fresh_cache
        )
        
        assert result is None
    
    @patch('urllib.request.urlopen')
    def test_token_successful_authentication(self, mock_urlopen, fresh_cache, mock_spotify_token_response):
        """Teste une authentification réussie."""
        # Mock de la réponse HTTP
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_spotify_token_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = get_spotify_token(
            client_id="test_id",
            client_secret="test_secret",
            cache=fresh_cache
        )
        
        assert result == mock_spotify_token_response["access_token"]
        assert fresh_cache.get_token() == result
    
    @patch('urllib.request.urlopen')
    def test_token_authentication_network_error(self, mock_urlopen, fresh_cache):
        """Teste la gestion d'une erreur réseau."""
        mock_urlopen.side_effect = URLError("Network error")
        
        result = get_spotify_token(
            client_id="test_id",
            client_secret="test_secret",
            cache=fresh_cache
        )
        
        assert result is None
    
    @patch('urllib.request.urlopen')
    def test_token_authentication_timeout(self, mock_urlopen, fresh_cache):
        """Teste la gestion d'un timeout."""
        mock_urlopen.side_effect = TimeoutError("Request timeout")
        
        result = get_spotify_token(
            client_id="test_id",
            client_secret="test_secret",
            cache=fresh_cache
        )
        
        assert result is None
    
    @patch('urllib.request.urlopen')
    def test_token_invalid_json_response(self, mock_urlopen, fresh_cache):
        """Teste la gestion d'une réponse JSON invalide."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"Invalid JSON"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = get_spotify_token(
            client_id="test_id",
            client_secret="test_secret",
            cache=fresh_cache
        )
        
        assert result is None
    
    @patch('urllib.request.urlopen')
    def test_token_response_missing_access_token(self, mock_urlopen, fresh_cache):
        """Teste une réponse sans access_token."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"error": "invalid_client"}).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = get_spotify_token(
            client_id="test_id",
            client_secret="test_secret",
            cache=fresh_cache
        )
        
        assert result is None
    
    def test_token_uses_env_vars(self, fresh_cache, mock_env_with_spotify):
        """Teste l'utilisation des variables d'environnement."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "access_token": "env_token",
                "expires_in": 3600
            }).encode('utf-8')
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            result = get_spotify_token(cache=fresh_cache)
            
            assert result == "env_token"


# ============================================================================
# Tests pour search_spotify_artist_image()
# ============================================================================

class TestSearchSpotifyArtistImage:
    """Tests de la fonction search_spotify_artist_image."""
    
    def test_artist_search_cache_hit(self, fresh_cache, valid_token):
        """Teste la récupération depuis le cache."""
        artist = "Nina Simone"
        cached_url = "https://cached.com/nina.jpg"
        fresh_cache.set_artist_image(artist, cached_url)
        
        result = search_spotify_artist_image(valid_token, artist, cache=fresh_cache)
        
        assert result == cached_url
    
    def test_artist_search_no_token(self, fresh_cache):
        """Teste le comportement sans token."""
        result = search_spotify_artist_image(None, "Nina Simone", cache=fresh_cache)
        
        assert result is None
        assert fresh_cache.get_artist_image("Nina Simone") is None
    
    @patch('urllib.request.urlopen')
    def test_artist_search_successful(self, mock_urlopen, fresh_cache, valid_token, mock_artist_search_response):
        """Teste une recherche réussie d'artiste."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_artist_search_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = search_spotify_artist_image(valid_token, "Nina Simone", cache=fresh_cache)
        
        assert result == "https://i.scdn.co/image/artist_image.jpg"
        assert fresh_cache.get_artist_image("Nina Simone") == result
    
    @patch('urllib.request.urlopen')
    def test_artist_search_not_found(self, mock_urlopen, fresh_cache, valid_token):
        """Teste une recherche d'artiste sans résultat."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"artists": {"items": []}}).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = search_spotify_artist_image(valid_token, "Unknown Artist", cache=fresh_cache)
        
        assert result is None
        assert fresh_cache.get_artist_image("Unknown Artist") is None
    
    @patch('urllib.request.urlopen')
    def test_artist_search_no_images(self, mock_urlopen, fresh_cache, valid_token):
        """Teste une recherche avec artiste sans image."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "artists": {"items": [{"name": "Test Artist", "images": []}]}
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = search_spotify_artist_image(valid_token, "Test Artist", cache=fresh_cache)
        
        assert result is None
    
    @patch('urllib.request.urlopen')
    @patch('services.spotify_service.clean_artist_name')
    def test_artist_search_cleans_name(self, mock_clean, mock_urlopen, fresh_cache, valid_token):
        """Teste que le nom d'artiste est nettoyé avant recherche."""
        mock_clean.return_value = "Nina Simone"
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"artists": {"items": []}}).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        search_spotify_artist_image(valid_token, "Nina Simone (Live)", cache=fresh_cache)
        
        mock_clean.assert_called_once_with("Nina Simone (Live)")
    
    @patch('urllib.request.urlopen')
    def test_artist_search_http_401_retry(self, mock_urlopen, fresh_cache, valid_token):
        """Teste le retry sur erreur 401 (token expiré)."""
        mock_urlopen.side_effect = HTTPError(
            'url', 401, 'Unauthorized', {}, io.BytesIO(b'')
        )
        
        result = search_spotify_artist_image(
            valid_token, "Nina Simone", 
            max_retries=2, cache=fresh_cache
        )
        
        assert result is None
        assert mock_urlopen.call_count == 2
    
    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_artist_search_http_429_retry(self, mock_sleep, mock_urlopen, fresh_cache, valid_token):
        """Teste le retry sur erreur 429 (rate limit)."""
        mock_urlopen.side_effect = HTTPError(
            'url', 429, 'Too Many Requests', {}, io.BytesIO(b'')
        )
        
        result = search_spotify_artist_image(
            valid_token, "Nina Simone",
            max_retries=2, cache=fresh_cache
        )
        
        assert result is None
        assert mock_urlopen.call_count == 2
        # Vérifie qu'on a attendu entre les tentatives
        assert mock_sleep.call_count >= 1
    
    @patch('urllib.request.urlopen')
    def test_artist_search_http_500_no_retry(self, mock_urlopen, fresh_cache, valid_token):
        """Teste qu'une erreur 500 n'entraîne pas de retry supplémentaire."""
        mock_urlopen.side_effect = HTTPError(
            'url', 500, 'Internal Server Error', {}, io.BytesIO(b'')
        )
        
        result = search_spotify_artist_image(
            valid_token, "Nina Simone",
            max_retries=3, cache=fresh_cache
        )
        
        assert result is None
        # Une seule tentative car erreur non-récupérable
        assert mock_urlopen.call_count == 1
    
    @patch('urllib.request.urlopen')
    def test_artist_search_network_error(self, mock_urlopen, fresh_cache, valid_token):
        """Teste la gestion d'une erreur réseau."""
        mock_urlopen.side_effect = URLError("Network error")
        
        result = search_spotify_artist_image(
            valid_token, "Nina Simone",
            max_retries=2, cache=fresh_cache
        )
        
        assert result is None


# ============================================================================
# Tests pour search_spotify_album_image()
# ============================================================================

class TestSearchSpotifyAlbumImage:
    """Tests de la fonction search_spotify_album_image."""
    
    def test_album_search_cache_hit(self, fresh_cache, valid_token):
        """Teste la récupération depuis le cache."""
        artist = "Nina Simone"
        album = "Little Girl Blue"
        cached_url = "https://cached.com/album.jpg"
        fresh_cache.set_album_image(artist, album, cached_url)
        
        result = search_spotify_album_image(valid_token, artist, album, cache=fresh_cache)
        
        assert result == cached_url
    
    def test_album_search_no_token(self, fresh_cache):
        """Teste le comportement sans token."""
        result = search_spotify_album_image(
            None, "Nina Simone", "Little Girl Blue",
            cache=fresh_cache
        )
        
        assert result is None
    
    @patch('services.spotify_service._search_album_with_artist')
    def test_album_search_primary_success(self, mock_primary, fresh_cache, valid_token):
        """Teste une recherche primaire réussie."""
        mock_primary.return_value = "https://album.jpg"
        
        result = search_spotify_album_image(
            valid_token, "Nina Simone", "Little Girl Blue",
            cache=fresh_cache
        )
        
        assert result == "https://album.jpg"
        assert fresh_cache.get_album_image("Nina Simone", "Little Girl Blue") == result
    
    @patch('services.spotify_service._search_album_with_artist')
    @patch('services.spotify_service._search_album_only')
    def test_album_search_fallback_on_primary_fail(self, mock_fallback, mock_primary, fresh_cache, valid_token):
        """Teste le fallback si la recherche primaire échoue."""
        mock_primary.return_value = None
        mock_fallback.return_value = "https://fallback_album.jpg"
        
        result = search_spotify_album_image(
            valid_token, "Various Artists", "Soundtrack Album",
            cache=fresh_cache
        )
        
        assert result == "https://fallback_album.jpg"
        assert mock_primary.called
        assert mock_fallback.called
    
    @patch('services.spotify_service._search_album_with_artist')
    @patch('services.spotify_service._search_album_only')
    def test_album_search_both_methods_fail(self, mock_fallback, mock_primary, fresh_cache, valid_token):
        """Teste le cas où les deux méthodes échouent."""
        mock_primary.return_value = None
        mock_fallback.return_value = None
        
        result = search_spotify_album_image(
            valid_token, "Unknown", "Unknown Album",
            cache=fresh_cache
        )
        
        assert result is None
    
    @patch('services.spotify_service.clean_artist_name')
    @patch('services.spotify_service.clean_album_name')
    @patch('services.spotify_service._search_album_with_artist')
    def test_album_search_cleans_metadata(self, mock_search, mock_clean_album, mock_clean_artist, fresh_cache, valid_token):
        """Teste que les métadonnées sont nettoyées."""
        mock_clean_artist.return_value = "Nina Simone"
        mock_clean_album.return_value = "Little Girl Blue"
        mock_search.return_value = "https://album.jpg"
        
        result = search_spotify_album_image(
            valid_token, "Nina Simone (Live)", "Little Girl Blue (Remastered)",
            cache=fresh_cache
        )
        
        mock_clean_artist.assert_called_once()
        mock_clean_album.assert_called_once()


# ============================================================================
# Tests pour _find_best_album_match()
# ============================================================================

class TestFindBestAlbumMatch:
    """Tests de la fonction _find_best_album_match."""
    
    def test_find_best_match_exact(self):
        """Teste la sélection d'une correspondance exacte."""
        albums = [
            {
                "name": "Little Girl Blue",
                "artists": [{"name": "Nina Simone"}],
                "images": [{"url": "https://exact.jpg"}]
            }
        ]
        
        result = _find_best_album_match("Nina Simone", "Little Girl Blue", albums, 50)
        
        assert result == "https://exact.jpg"
    
    def test_find_best_match_no_artist_match(self):
        """Teste qu'aucun résultat n'est retourné si l'artiste ne correspond pas."""
        albums = [
            {
                "name": "Little Girl Blue",
                "artists": [{"name": "Wrong Artist"}],
                "images": [{"url": "https://wrong.jpg"}]
            }
        ]
        
        result = _find_best_album_match("Nina Simone", "Little Girl Blue", albums, 50)
        
        assert result is None
    
    def test_find_best_match_score_below_threshold(self):
        """Teste qu'aucun résultat n'est retourné si le score est insuffisant."""
        albums = [
            {
                "name": "Completely Different Album",
                "artists": [{"name": "Nina Simone"}],
                "images": [{"url": "https://low_score.jpg"}]
            }
        ]
        
        result = _find_best_album_match("Nina Simone", "Little Girl Blue", albums, 50)
        
        assert result is None
    
    def test_find_best_match_selects_highest_score(self):
        """Teste la sélection de l'album avec le meilleur score."""
        albums = [
            {
                "name": "Little Girl",
                "artists": [{"name": "Nina Simone"}],
                "images": [{"url": "https://partial.jpg"}]
            },
            {
                "name": "Little Girl Blue",
                "artists": [{"name": "Nina Simone"}],
                "images": [{"url": "https://exact.jpg"}]
            }
        ]
        
        result = _find_best_album_match("Nina Simone", "Little Girl Blue", albums, 50)
        
        assert result == "https://exact.jpg"
    
    def test_find_best_match_no_images(self):
        """Teste le cas d'un album sans images."""
        albums = [
            {
                "name": "Little Girl Blue",
                "artists": [{"name": "Nina Simone"}],
                "images": []
            }
        ]
        
        result = _find_best_album_match("Nina Simone", "Little Girl Blue", albums, 50)
        
        assert result is None
    
    def test_find_best_match_empty_albums_list(self):
        """Teste avec une liste vide."""
        result = _find_best_album_match("Nina Simone", "Little Girl Blue", [], 50)
        
        assert result is None
    
    def test_find_best_match_no_artists_in_album(self):
        """Teste un album sans artistes."""
        albums = [
            {
                "name": "Little Girl Blue",
                "artists": [],
                "images": [{"url": "https://no_artist.jpg"}]
            }
        ]
        
        result = _find_best_album_match("Nina Simone", "Little Girl Blue", albums, 50)
        
        assert result is None


# ============================================================================
# Tests d'intégration pour _search_album_with_artist() et _search_album_only()
# ============================================================================

class TestSearchAlbumInternal:
    """Tests des fonctions internes de recherche d'albums."""
    
    @patch('urllib.request.urlopen')
    def test_search_album_with_artist_success(self, mock_urlopen, valid_token, mock_album_search_response):
        """Teste _search_album_with_artist avec succès."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_album_search_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = _search_album_with_artist(
            valid_token, "Nina Simone", "Little Girl Blue",
            SPOTIFY_MIN_SCORE_PRIMARY, DEFAULT_RETRY_COUNT
        )
        
        assert result == "https://i.scdn.co/image/album_cover.jpg"
    
    @patch('urllib.request.urlopen')
    def test_search_album_with_artist_not_found(self, mock_urlopen, valid_token):
        """Teste _search_album_with_artist sans résultat."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"albums": {"items": []}}).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = _search_album_with_artist(
            valid_token, "Unknown", "Unknown Album",
            SPOTIFY_MIN_SCORE_PRIMARY, DEFAULT_RETRY_COUNT
        )
        
        assert result is None
    
    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_search_album_with_artist_retry_on_401(self, mock_sleep, mock_urlopen, valid_token):
        """Teste le retry sur erreur 401."""
        mock_urlopen.side_effect = HTTPError(
            'url', 401, 'Unauthorized', {}, io.BytesIO(b'')
        )
        
        result = _search_album_with_artist(
            valid_token, "Nina Simone", "Little Girl Blue",
            SPOTIFY_MIN_SCORE_PRIMARY, 2
        )
        
        assert result is None
        assert mock_urlopen.call_count == 2
    
    @patch('urllib.request.urlopen')
    def test_search_album_only_success(self, mock_urlopen, valid_token, mock_album_search_response):
        """Teste _search_album_only avec succès."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_album_search_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = _search_album_only(
            valid_token, "Nina Simone", "Little Girl Blue",
            SPOTIFY_MIN_SCORE_FALLBACK, DEFAULT_RETRY_COUNT
        )
        
        assert result == "https://i.scdn.co/image/album_cover.jpg"


# ============================================================================
# Tests de couverture additionnels
# ============================================================================

class TestEdgeCasesAndBoundaryConditions:
    """Tests de cas limites et conditions aux limites."""
    
    def test_cache_handles_unicode_characters(self, fresh_cache):
        """Teste le cache avec caractères Unicode."""
        artist = "Björk"
        album = "Homogéne"
        url = "https://example.com/bjork.jpg"
        
        fresh_cache.set_album_image(artist, album, url)
        result = fresh_cache.get_album_image(artist, album)
        
        assert result == url
    
    def test_cache_handles_very_long_strings(self, fresh_cache):
        """Teste le cache avec chaînes très longues."""
        artist = "A" * 500
        album = "B" * 500
        url = "https://example.com/long.jpg"
        
        fresh_cache.set_album_image(artist, album, url)
        result = fresh_cache.get_album_image(artist, album)
        
        assert result == url
    
    def test_search_with_special_characters(self, fresh_cache, valid_token):
        """Teste la recherche avec caractères spéciaux."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "artists": {"items": []}
            }).encode('utf-8')
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            result = search_spotify_artist_image(
                valid_token, "AC/DC & Friends (Live!)",
                cache=fresh_cache
            )
            
            # Vérifie que la requête est exécutée sans erreur
            assert result is None
    
    @patch('urllib.request.urlopen')
    def test_multiple_retries_exhausted(self, mock_urlopen, fresh_cache, valid_token):
        """Teste l'épuisement de toutes les tentatives de retry."""
        mock_urlopen.side_effect = [
            HTTPError('url', 401, 'Unauthorized', {}, io.BytesIO(b'')),
            HTTPError('url', 401, 'Unauthorized', {}, io.BytesIO(b'')),
            HTTPError('url', 401, 'Unauthorized', {}, io.BytesIO(b''))
        ]
        
        result = search_spotify_artist_image(
            valid_token, "Nina Simone",
            max_retries=3, cache=fresh_cache
        )
        
        assert result is None
        assert mock_urlopen.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=services.spotify_service", "--cov-report=term-missing"])
