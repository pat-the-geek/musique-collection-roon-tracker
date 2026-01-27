"""Tests unitaires pour le module constants.

Vérifie la cohérence et la validité des constantes utilisées dans le projet,
ainsi que leur utilisation dans un contexte réel.

Version: 1.0.0
Date: 26 janvier 2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from constants import (
    # Valeurs par défaut métadonnées
    UNKNOWN_ARTIST, UNKNOWN_ALBUM, UNKNOWN_TITLE,
    # Sources de données
    SOURCE_ROON, SOURCE_LASTFM, SOURCE_SPOTIFY, SOURCE_DISCOGS,
    # Formats de support
    SUPPORT_VINYL, SUPPORT_CD, SUPPORT_DIGITAL, SUPPORT_UNKNOWN, VALID_SUPPORTS,
    # Configuration Spotify
    SPOTIFY_TOKEN_URL, SPOTIFY_SEARCH_URL, SPOTIFY_TOKEN_REFRESH_MARGIN,
    SPOTIFY_SCORE_EXACT_MATCH, SPOTIFY_SCORE_CONTAINS, SPOTIFY_SCORE_PARTIAL,
    SPOTIFY_MIN_SCORE_PRIMARY, SPOTIFY_MIN_SCORE_FALLBACK,
    SPOTIFY_ARTIST_SEARCH_LIMIT, SPOTIFY_ALBUM_SEARCH_LIMIT,
    # Configuration Last.fm
    LASTFM_IMAGE_SIZE_LARGE, LASTFM_IMAGE_SIZE_XLARGE,
    # Délais et retries
    DEFAULT_RETRY_COUNT, DEFAULT_RETRY_DELAY, DEFAULT_RATE_LIMIT_DELAY, DEFAULT_HTTP_TIMEOUT,
    # Plages horaires
    DEFAULT_LISTEN_START_HOUR, DEFAULT_LISTEN_END_HOUR,
    # Détection sessions
    SESSION_GAP_THRESHOLD, FULL_ALBUM_MIN_TRACKS,
    # Normalisation
    IGNORE_CHARS,
    # Messages d'erreur
    ERROR_MISSING_SPOTIFY_CREDENTIALS, ERROR_MISSING_LASTFM_CREDENTIALS,
    ERROR_TOKEN_RETRIEVAL, ERROR_FILE_LOCKED, ERROR_JSON_CORRUPTED,
    # Formats de date
    DATE_FORMAT_DISPLAY, DATE_FORMAT_FILENAME, DATE_FORMAT_ISO,
    # Backup
    BACKUP_RETENTION_COUNT,
    # Noms de fichiers
    ROON_CONFIG_FILENAME, ROON_HISTORY_FILENAME, ROON_LOCK_FILENAME,
    LASTFM_HISTORY_FILENAME, DISCOGS_COLLECTION_FILENAME, SOUNDTRACK_FILENAME, ENV_FILENAME,
    # URLs APIs
    DISCOGS_API_BASE_URL, EURIA_API_URL,
    # User Agents
    USER_AGENT_DISCOGS, USER_AGENT_HTTP
)


# ============================================================================
# Tests de cohérence des valeurs par défaut
# ============================================================================

class TestDefaultValues:
    """Tests des valeurs par défaut pour métadonnées."""
    
    def test_unknown_values_are_strings(self):
        """Vérifie que les valeurs 'Inconnu' sont des chaînes."""
        assert isinstance(UNKNOWN_ARTIST, str)
        assert isinstance(UNKNOWN_ALBUM, str)
        assert isinstance(UNKNOWN_TITLE, str)
    
    def test_unknown_values_not_empty(self):
        """Vérifie que les valeurs 'Inconnu' ne sont pas vides."""
        assert len(UNKNOWN_ARTIST) > 0
        assert len(UNKNOWN_ALBUM) > 0
        assert len(UNKNOWN_TITLE) > 0
    
    def test_unknown_values_consistency(self):
        """Vérifie que toutes les valeurs 'Inconnu' sont identiques."""
        assert UNKNOWN_ARTIST == "Inconnu"
        assert UNKNOWN_ALBUM == "Inconnu"
        assert UNKNOWN_TITLE == "Inconnu"


# ============================================================================
# Tests des sources de données
# ============================================================================

class TestDataSources:
    """Tests des constantes de sources de données."""
    
    def test_sources_are_lowercase(self):
        """Vérifie que les sources sont en minuscules."""
        assert SOURCE_ROON == SOURCE_ROON.lower()
        assert SOURCE_LASTFM == SOURCE_LASTFM.lower()
        assert SOURCE_SPOTIFY == SOURCE_SPOTIFY.lower()
        assert SOURCE_DISCOGS == SOURCE_DISCOGS.lower()
    
    def test_sources_are_unique(self):
        """Vérifie que chaque source est unique."""
        sources = [SOURCE_ROON, SOURCE_LASTFM, SOURCE_SPOTIFY, SOURCE_DISCOGS]
        assert len(sources) == len(set(sources))
    
    def test_sources_not_empty(self):
        """Vérifie que les sources ne sont pas vides."""
        assert len(SOURCE_ROON) > 0
        assert len(SOURCE_LASTFM) > 0
        assert len(SOURCE_SPOTIFY) > 0
        assert len(SOURCE_DISCOGS) > 0


# ============================================================================
# Tests des formats de support
# ============================================================================

class TestSupportFormats:
    """Tests des constantes de formats de support audio."""
    
    def test_valid_supports_list_not_empty(self):
        """Vérifie que la liste des supports valides n'est pas vide."""
        assert len(VALID_SUPPORTS) > 0
    
    def test_valid_supports_contains_defined_formats(self):
        """Vérifie que tous les formats définis sont dans VALID_SUPPORTS."""
        assert SUPPORT_VINYL in VALID_SUPPORTS
        assert SUPPORT_CD in VALID_SUPPORTS
        assert SUPPORT_DIGITAL in VALID_SUPPORTS
        assert SUPPORT_UNKNOWN in VALID_SUPPORTS
    
    def test_valid_supports_count(self):
        """Vérifie le nombre de supports valides."""
        assert len(VALID_SUPPORTS) == 4
    
    def test_support_formats_not_empty(self):
        """Vérifie que les formats ne sont pas vides."""
        assert len(SUPPORT_VINYL) > 0
        assert len(SUPPORT_CD) > 0
        assert len(SUPPORT_DIGITAL) > 0
        assert len(SUPPORT_UNKNOWN) > 0
    
    def test_support_formats_consistency(self):
        """Vérifie la cohérence des valeurs de support."""
        assert SUPPORT_VINYL == "Vinyle"
        assert SUPPORT_CD == "CD"
        assert SUPPORT_DIGITAL == "Digital"
        assert SUPPORT_UNKNOWN == "Inconnu"


# ============================================================================
# Tests de la configuration Spotify
# ============================================================================

class TestSpotifyConfiguration:
    """Tests des constantes de configuration Spotify."""
    
    def test_spotify_urls_are_valid(self):
        """Vérifie que les URLs Spotify sont valides."""
        assert SPOTIFY_TOKEN_URL.startswith("https://")
        assert SPOTIFY_SEARCH_URL.startswith("https://")
        assert "spotify.com" in SPOTIFY_TOKEN_URL
        assert "spotify.com" in SPOTIFY_SEARCH_URL
    
    def test_spotify_token_refresh_margin_positive(self):
        """Vérifie que la marge de rafraîchissement est positive."""
        assert SPOTIFY_TOKEN_REFRESH_MARGIN > 0
        assert isinstance(SPOTIFY_TOKEN_REFRESH_MARGIN, int)
    
    def test_spotify_scores_hierarchy(self):
        """Vérifie la hiérarchie des scores de correspondance."""
        assert SPOTIFY_SCORE_EXACT_MATCH > SPOTIFY_SCORE_CONTAINS
        assert SPOTIFY_SCORE_CONTAINS > SPOTIFY_SCORE_PARTIAL
        assert SPOTIFY_SCORE_PARTIAL > 0
    
    def test_spotify_min_scores_logical(self):
        """Vérifie que les seuils minimum sont logiques."""
        assert SPOTIFY_MIN_SCORE_PRIMARY > SPOTIFY_MIN_SCORE_FALLBACK
        assert SPOTIFY_MIN_SCORE_FALLBACK > 0
        assert SPOTIFY_MIN_SCORE_PRIMARY <= SPOTIFY_SCORE_EXACT_MATCH
    
    def test_spotify_search_limits_positive(self):
        """Vérifie que les limites de recherche sont positives."""
        assert SPOTIFY_ARTIST_SEARCH_LIMIT > 0
        assert SPOTIFY_ALBUM_SEARCH_LIMIT > 0
    
    def test_spotify_search_limits_reasonable(self):
        """Vérifie que les limites de recherche sont raisonnables."""
        # Éviter des valeurs extrêmes qui pourraient causer des problèmes
        assert SPOTIFY_ARTIST_SEARCH_LIMIT <= 50
        assert SPOTIFY_ALBUM_SEARCH_LIMIT <= 50


# ============================================================================
# Tests de la configuration Last.fm
# ============================================================================

class TestLastfmConfiguration:
    """Tests des constantes de configuration Last.fm."""
    
    def test_lastfm_image_sizes_are_integers(self):
        """Vérifie que les tailles d'images sont des entiers."""
        assert isinstance(LASTFM_IMAGE_SIZE_LARGE, int)
        assert isinstance(LASTFM_IMAGE_SIZE_XLARGE, int)
    
    def test_lastfm_image_sizes_hierarchy(self):
        """Vérifie la hiérarchie des tailles d'images."""
        assert LASTFM_IMAGE_SIZE_XLARGE > LASTFM_IMAGE_SIZE_LARGE
    
    def test_lastfm_image_sizes_non_negative(self):
        """Vérifie que les index de tailles sont non-négatifs."""
        assert LASTFM_IMAGE_SIZE_LARGE >= 0
        assert LASTFM_IMAGE_SIZE_XLARGE >= 0


# ============================================================================
# Tests des délais et retries
# ============================================================================

class TestRetryConfiguration:
    """Tests des constantes de délais et tentatives."""
    
    def test_retry_count_positive(self):
        """Vérifie que le nombre de tentatives est positif."""
        assert DEFAULT_RETRY_COUNT > 0
        assert isinstance(DEFAULT_RETRY_COUNT, int)
    
    def test_delays_positive(self):
        """Vérifie que tous les délais sont positifs."""
        assert DEFAULT_RETRY_DELAY > 0
        assert DEFAULT_RATE_LIMIT_DELAY > 0
        assert DEFAULT_HTTP_TIMEOUT > 0
    
    def test_delays_are_numbers(self):
        """Vérifie que les délais sont des nombres."""
        assert isinstance(DEFAULT_RETRY_DELAY, (int, float))
        assert isinstance(DEFAULT_RATE_LIMIT_DELAY, (int, float))
        assert isinstance(DEFAULT_HTTP_TIMEOUT, (int, float))
    
    def test_rate_limit_delay_greater_than_retry(self):
        """Vérifie que le délai rate limit est plus long que retry normal."""
        assert DEFAULT_RATE_LIMIT_DELAY >= DEFAULT_RETRY_DELAY
    
    def test_http_timeout_reasonable(self):
        """Vérifie que le timeout HTTP est raisonnable."""
        assert 10 <= DEFAULT_HTTP_TIMEOUT <= 120  # Entre 10s et 2 minutes


# ============================================================================
# Tests des plages horaires
# ============================================================================

class TestListeningHours:
    """Tests des constantes de plages horaires."""
    
    def test_hours_are_integers(self):
        """Vérifie que les heures sont des entiers."""
        assert isinstance(DEFAULT_LISTEN_START_HOUR, int)
        assert isinstance(DEFAULT_LISTEN_END_HOUR, int)
    
    def test_hours_in_valid_range(self):
        """Vérifie que les heures sont dans la plage 0-23."""
        assert 0 <= DEFAULT_LISTEN_START_HOUR <= 23
        assert 0 <= DEFAULT_LISTEN_END_HOUR <= 23
    
    def test_end_hour_after_start_hour(self):
        """Vérifie que l'heure de fin est après l'heure de début."""
        # Note: Cette logique peut être adaptée selon les besoins du projet
        # (par exemple pour gérer les plages qui traversent minuit)
        assert DEFAULT_LISTEN_END_HOUR > DEFAULT_LISTEN_START_HOUR


# ============================================================================
# Tests de la détection de sessions
# ============================================================================

class TestSessionDetection:
    """Tests des constantes de détection de sessions."""
    
    def test_session_gap_positive(self):
        """Vérifie que le seuil de gap de session est positif."""
        assert SESSION_GAP_THRESHOLD > 0
        assert isinstance(SESSION_GAP_THRESHOLD, int)
    
    def test_session_gap_reasonable(self):
        """Vérifie que le seuil est dans une plage raisonnable."""
        # Entre 5 minutes et 2 heures
        assert 300 <= SESSION_GAP_THRESHOLD <= 7200
    
    def test_full_album_min_tracks_positive(self):
        """Vérifie que le minimum de pistes est positif."""
        assert FULL_ALBUM_MIN_TRACKS > 0
        assert isinstance(FULL_ALBUM_MIN_TRACKS, int)
    
    def test_full_album_min_tracks_reasonable(self):
        """Vérifie que le minimum de pistes est raisonnable."""
        # Un album typique a au moins 5 pistes
        assert 3 <= FULL_ALBUM_MIN_TRACKS <= 15


# ============================================================================
# Tests de normalisation
# ============================================================================

class TestNormalizationConstants:
    """Tests des constantes de normalisation."""
    
    def test_ignore_chars_is_list(self):
        """Vérifie que IGNORE_CHARS est une liste."""
        assert isinstance(IGNORE_CHARS, list)
    
    def test_ignore_chars_not_empty(self):
        """Vérifie que la liste de caractères à ignorer n'est pas vide."""
        assert len(IGNORE_CHARS) > 0
    
    def test_ignore_chars_are_strings(self):
        """Vérifie que tous les éléments sont des chaînes."""
        for char in IGNORE_CHARS:
            assert isinstance(char, str)
    
    def test_ignore_chars_contains_punctuation(self):
        """Vérifie que les caractères de ponctuation courants sont présents."""
        common_punctuation = ["'", '"', ',', '.']
        for punct in common_punctuation:
            assert punct in IGNORE_CHARS


# ============================================================================
# Tests des messages d'erreur
# ============================================================================

class TestErrorMessages:
    """Tests des constantes de messages d'erreur."""
    
    def test_error_messages_not_empty(self):
        """Vérifie que les messages d'erreur ne sont pas vides."""
        assert len(ERROR_MISSING_SPOTIFY_CREDENTIALS) > 0
        assert len(ERROR_MISSING_LASTFM_CREDENTIALS) > 0
        assert len(ERROR_TOKEN_RETRIEVAL) > 0
        assert len(ERROR_FILE_LOCKED) > 0
        assert len(ERROR_JSON_CORRUPTED) > 0
    
    def test_error_messages_have_indicator(self):
        """Vérifie que les messages d'erreur ont un indicateur visuel."""
        error_messages = [
            ERROR_MISSING_SPOTIFY_CREDENTIALS,
            ERROR_MISSING_LASTFM_CREDENTIALS,
            ERROR_TOKEN_RETRIEVAL,
            ERROR_FILE_LOCKED,
            ERROR_JSON_CORRUPTED
        ]
        
        for msg in error_messages:
            assert "⚠️" in msg or "ERROR" in msg.upper() or "ERREUR" in msg.upper()


# ============================================================================
# Tests des formats de date
# ============================================================================

class TestDateFormats:
    """Tests des constantes de formats de date."""
    
    def test_date_formats_not_empty(self):
        """Vérifie que les formats de date ne sont pas vides."""
        assert len(DATE_FORMAT_DISPLAY) > 0
        assert len(DATE_FORMAT_FILENAME) > 0
        assert len(DATE_FORMAT_ISO) > 0
    
    def test_date_formats_contain_directives(self):
        """Vérifie que les formats contiennent des directives strftime."""
        assert "%" in DATE_FORMAT_DISPLAY
        assert "%" in DATE_FORMAT_FILENAME
        assert "%" in DATE_FORMAT_ISO
    
    def test_filename_format_no_spaces_or_colons(self):
        """Vérifie que le format de nom de fichier évite espaces et deux-points."""
        # Pour compatibilité multi-plateforme
        assert " " not in DATE_FORMAT_FILENAME.replace("%", "")
        assert ":" not in DATE_FORMAT_FILENAME.replace("%", "")


# ============================================================================
# Tests de backup
# ============================================================================

class TestBackupConfiguration:
    """Tests des constantes de backup."""
    
    def test_backup_retention_positive(self):
        """Vérifie que le nombre de backups à conserver est positif."""
        assert BACKUP_RETENTION_COUNT > 0
        assert isinstance(BACKUP_RETENTION_COUNT, int)
    
    def test_backup_retention_reasonable(self):
        """Vérifie que le nombre de backups est raisonnable."""
        assert 3 <= BACKUP_RETENTION_COUNT <= 20


# ============================================================================
# Tests des noms de fichiers
# ============================================================================

class TestFilenames:
    """Tests des constantes de noms de fichiers."""
    
    def test_filenames_not_empty(self):
        """Vérifie que les noms de fichiers ne sont pas vides."""
        filenames = [
            ROON_CONFIG_FILENAME, ROON_HISTORY_FILENAME, ROON_LOCK_FILENAME,
            LASTFM_HISTORY_FILENAME, DISCOGS_COLLECTION_FILENAME,
            SOUNDTRACK_FILENAME, ENV_FILENAME
        ]
        for filename in filenames:
            assert len(filename) > 0
    
    def test_json_filenames_have_extension(self):
        """Vérifie que les fichiers JSON ont l'extension .json."""
        json_files = [
            ROON_CONFIG_FILENAME, ROON_HISTORY_FILENAME,
            LASTFM_HISTORY_FILENAME, DISCOGS_COLLECTION_FILENAME,
            SOUNDTRACK_FILENAME
        ]
        for filename in json_files:
            assert filename.endswith(".json")
    
    def test_lock_filename_has_extension(self):
        """Vérifie que le fichier de lock a l'extension .lock."""
        assert ROON_LOCK_FILENAME.endswith(".lock")
    
    def test_filenames_no_path_separators(self):
        """Vérifie que les noms de fichiers ne contiennent pas de séparateurs de chemin."""
        filenames = [
            ROON_CONFIG_FILENAME, ROON_HISTORY_FILENAME, ROON_LOCK_FILENAME,
            LASTFM_HISTORY_FILENAME, DISCOGS_COLLECTION_FILENAME,
            SOUNDTRACK_FILENAME, ENV_FILENAME
        ]
        for filename in filenames:
            assert "/" not in filename
            assert "\\" not in filename


# ============================================================================
# Tests des URLs d'APIs
# ============================================================================

class TestAPIUrls:
    """Tests des constantes d'URLs d'APIs."""
    
    def test_api_urls_are_https(self):
        """Vérifie que les URLs d'API utilisent HTTPS."""
        assert DISCOGS_API_BASE_URL.startswith("https://")
        assert EURIA_API_URL.startswith("https://")
    
    def test_api_urls_contain_domain(self):
        """Vérifie que les URLs contiennent un domaine valide."""
        assert "discogs.com" in DISCOGS_API_BASE_URL
        assert "infomaniak.com" in EURIA_API_URL
    
    def test_api_urls_not_empty(self):
        """Vérifie que les URLs ne sont pas vides."""
        assert len(DISCOGS_API_BASE_URL) > 0
        assert len(EURIA_API_URL) > 0


# ============================================================================
# Tests des User Agents
# ============================================================================

class TestUserAgents:
    """Tests des constantes de User Agents."""
    
    def test_user_agents_not_empty(self):
        """Vérifie que les User Agents ne sont pas vides."""
        assert len(USER_AGENT_DISCOGS) > 0
        assert len(USER_AGENT_HTTP) > 0
    
    def test_user_agents_contain_identifier(self):
        """Vérifie que les User Agents contiennent un identifiant."""
        # Discogs requiert un identifiant d'application
        assert "Discogs" in USER_AGENT_DISCOGS or "Client" in USER_AGENT_DISCOGS
        assert "Mozilla" in USER_AGENT_HTTP or "compatible" in USER_AGENT_HTTP


# ============================================================================
# Tests d'utilisation en contexte réel
# ============================================================================

class TestConstantsInContext:
    """Tests d'utilisation des constantes dans un contexte réel."""
    
    def test_support_validation_function(self):
        """Teste que VALID_SUPPORTS peut être utilisé pour validation."""
        test_support = "CD"
        assert test_support in VALID_SUPPORTS
        
        invalid_support = "Cassette"
        assert invalid_support not in VALID_SUPPORTS
    
    def test_source_comparison(self):
        """Teste que les sources peuvent être comparées."""
        track_source = "roon"
        assert track_source == SOURCE_ROON
        
        another_source = "spotify"
        assert another_source == SOURCE_SPOTIFY
    
    def test_retry_logic_simulation(self):
        """Simule l'utilisation des constantes de retry."""
        attempts = 0
        max_attempts = DEFAULT_RETRY_COUNT
        
        while attempts < max_attempts:
            attempts += 1
        
        assert attempts == DEFAULT_RETRY_COUNT
    
    def test_timeout_value_usage(self):
        """Vérifie que le timeout peut être utilisé dans un contexte."""
        timeout = DEFAULT_HTTP_TIMEOUT
        assert timeout > 0
        # Peut être passé à des fonctions comme requests.get(timeout=timeout)
    
    def test_session_gap_calculation(self):
        """Simule le calcul de gap entre sessions."""
        time1 = 1000
        time2 = time1 + SESSION_GAP_THRESHOLD + 1
        
        gap = time2 - time1
        assert gap > SESSION_GAP_THRESHOLD  # Nouvelle session


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
