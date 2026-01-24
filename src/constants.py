"""Constantes globales du projet Musique Collection & Tracker.

Ce module centralise toutes les valeurs constantes utilisées à travers
le projet pour éviter la duplication et faciliter la maintenance.

Version: 1.0.0
Date: 24 janvier 2026
"""

# ===== Valeurs par défaut pour métadonnées =====
UNKNOWN_ARTIST = "Inconnu"
UNKNOWN_ALBUM = "Inconnu"
UNKNOWN_TITLE = "Inconnu"

# ===== Sources de données =====
SOURCE_ROON = "roon"
SOURCE_LASTFM = "lastfm"
SOURCE_SPOTIFY = "spotify"
SOURCE_DISCOGS = "discogs"

# ===== Formats de support audio =====
SUPPORT_VINYL = "Vinyle"
SUPPORT_CD = "CD"
SUPPORT_DIGITAL = "Digital"
SUPPORT_UNKNOWN = "Inconnu"

VALID_SUPPORTS = [SUPPORT_VINYL, SUPPORT_CD, SUPPORT_DIGITAL, SUPPORT_UNKNOWN]

# ===== Configuration Spotify API =====
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
SPOTIFY_TOKEN_REFRESH_MARGIN = 60  # Rafraîchir 60s avant expiration

# ===== Configuration de recherche Spotify =====
# Seuils de scoring pour la correspondance d'albums
SPOTIFY_SCORE_EXACT_MATCH = 100  # Correspondance exacte du nom d'album
SPOTIFY_SCORE_CONTAINS = 80      # Album contient le terme recherché
SPOTIFY_SCORE_PARTIAL = 50       # Correspondance partielle (mots communs)
SPOTIFY_MIN_SCORE_PRIMARY = 50   # Seuil minimum pour recherche primaire
SPOTIFY_MIN_SCORE_FALLBACK = 30  # Seuil minimum pour recherche fallback

# Limites de résultats
SPOTIFY_ARTIST_SEARCH_LIMIT = 1
SPOTIFY_ALBUM_SEARCH_LIMIT = 5

# ===== Configuration Last.fm API =====
LASTFM_IMAGE_SIZE_LARGE = 3  # Index pour grande image (extralarge)
LASTFM_IMAGE_SIZE_XLARGE = 4  # Index pour très grande image (mega)

# ===== Délais et retries =====
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 1  # secondes
DEFAULT_RATE_LIMIT_DELAY = 2  # secondes pour code 429
DEFAULT_HTTP_TIMEOUT = 30  # secondes

# ===== Plages horaires par défaut =====
DEFAULT_LISTEN_START_HOUR = 6   # 6h du matin
DEFAULT_LISTEN_END_HOUR = 23    # 23h (11pm)

# ===== Détection de sessions d'écoute =====
SESSION_GAP_THRESHOLD = 1800  # 30 minutes (en secondes)
FULL_ALBUM_MIN_TRACKS = 5     # Minimum de pistes pour considérer album complet

# ===== Normalisation de chaînes =====
# Caractères à ignorer lors de la comparaison
IGNORE_CHARS = ["'", '"', ',', '.', '!', '?', '-', '_']

# ===== Messages d'erreur =====
ERROR_MISSING_SPOTIFY_CREDENTIALS = "⚠️ SPOTIFY_CLIENT_ID ou SPOTIFY_CLIENT_SECRET manquant dans .env"
ERROR_MISSING_LASTFM_CREDENTIALS = "⚠️ Last.fm API credentials manquantes dans .env"
ERROR_TOKEN_RETRIEVAL = "⚠️ Erreur lors de la récupération du token Spotify"
ERROR_FILE_LOCKED = "⚠️ Un autre processus utilise déjà ce fichier"
ERROR_JSON_CORRUPTED = "⚠️ Fichier JSON corrompu ou invalide"

# ===== Formats de date =====
DATE_FORMAT_DISPLAY = "%Y-%m-%d %H:%M"  # Format d'affichage
DATE_FORMAT_FILENAME = "%Y%m%d-%H%M%S"  # Format pour noms de fichiers
DATE_FORMAT_ISO = "%Y-%m-%dT%H:%M:%S%z"  # Format ISO 8601

# ===== Backup =====
BACKUP_RETENTION_COUNT = 5  # Nombre de backups à conserver

# ===== Noms de fichiers standards =====
ROON_CONFIG_FILENAME = "roon-config.json"
ROON_HISTORY_FILENAME = "chk-roon.json"
ROON_LOCK_FILENAME = "chk-roon.lock"
LASTFM_HISTORY_FILENAME = "chk-last-fm.json"
DISCOGS_COLLECTION_FILENAME = "discogs-collection.json"
SOUNDTRACK_FILENAME = "soundtrack.json"
ENV_FILENAME = ".env"

# ===== URLs des APIs =====
DISCOGS_API_BASE_URL = "https://api.discogs.com"
EURIA_API_URL = "https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions"

# ===== User Agents =====
USER_AGENT_DISCOGS = "DiscogsClient/1.0 +patrick.ostertag@gmail.com"
USER_AGENT_HTTP = "Mozilla/5.0 (compatible; MusicTracker/1.0)"
