# Music Collection & Listening Tracker - AI Agent Guide

**Version: 3.3.0** | **Date: 27 janvier 2026**

This project tracks music listening history from Roon and Last.fm, manages a Discogs collection, and generates creative content (haikus) from album metadata. It features automatic AI-powered album information enrichment and a complete task scheduler.

---

## 🎯 What's New in v3.3.0

**AI INTEGRATION**: Automatic album information enrichment with intelligent fallback system.

**Key Changes:**
- ✅ **AI Service Module** (`src/services/ai_service.py`) - Centralized EurIA API integration
- ✅ **Automatic Album Enrichment** - Every detected album gets AI-generated description
- ✅ **Smart Fallback** - Discogs → IA priority (80%+ hit rate)
- ✅ **Daily AI Logs** - `output/ai-logs/ai-log-YYYY-MM-DD.txt` with 24h retention
- ✅ **GUI Integration** - AI info displayed in Roon Journal with expandable sections
- ✅ **New chk-roon.py v2.3.0** - Integrated AI info generation for all tracks

**Impact:** Every album now includes contextual information automatically, vastly improving the user experience.

See [ISSUE-21-IMPLEMENTATION.md](../ISSUE-21-IMPLEMENTATION.md) and [docs/AI-INTEGRATION.md](../docs/AI-INTEGRATION.md) for complete details.

---

## 🎯 What's New in v3.2.0

**TASK SCHEDULER**: Complete automation system for periodic tasks.

**Key Changes:**
- ✅ **Scheduler Module** (`src/utils/scheduler.py`, 650 lines) - Task orchestration system
- ✅ **4 Automated Tasks** - Haiku generation, listening analysis, Discogs sync, soundtrack matching
- ✅ **Roon Integration** - Scheduler checks every ~45 minutes in tracker loop
- ✅ **GUI Controls** - Configure scheduler tasks via web interface
- ✅ **Unit Tests** - 302 lines of comprehensive tests

**Impact:** 80% reduction in manual interventions for analysis tasks.

See [docs/README-SCHEDULER.md](../docs/README-SCHEDULER.md) and [docs/SCHEDULER-IMPLEMENTATION-REPORT.md](../docs/SCHEDULER-IMPLEMENTATION-REPORT.md) for complete details.

---

## 🎯 What's New in v3.0.0

**MAJOR REORGANIZATION**: Complete project restructure from flat directory to modular architecture.

**Key Changes:**
- ✅ **7 functional modules** in `src/` (trackers, collection, enrichment, analysis, maintenance, utils, gui)
- ✅ **Centralized data** in `data/` (config, collection, history, exports)
- ✅ **100+ path updates** - All scripts now use relative paths (`../../`)
- ✅ **Organized backups** in `backups/` (json/, python/, legacy/)
- ✅ **Documentation centralized** in `docs/`

**Impact:** All file paths have changed. Old instructions referencing root-level files are obsolete.

See [docs/CHANGELOG-ARCHITECTURE-v3.0.0.md](../docs/CHANGELOG-ARCHITECTURE-v3.0.0.md) for complete details.

---

## Architecture Overview v3.0.0

### Directory Structure

The project uses a **modular architecture** with clear separation:

```
.
├── src/                    # Source code organized by function
│   ├── trackers/          # Roon & Last.fm monitoring
│   ├── collection/        # Discogs management
│   ├── enrichment/        # Metadata completion
│   ├── analysis/          # Reports & haiku generation
│   ├── maintenance/       # Data cleanup utilities
│   ├── utils/             # Helper scripts
│   └── gui/               # Streamlit interface
├── data/                   # All data files (JSON, config)
│   ├── config/            # .env, roon-config.json
│   ├── collection/        # discogs-collection.json, soundtrack.json
│   ├── history/           # chk-roon.json, chk-last-fm.json
│   └── exports/           # MD, CSV, PDF exports
├── output/                 # Generated files (temporary)
│   ├── haikus/            # iA Presenter haikus
│   ├── reports/           # Analysis reports
│   └── ai-logs/           # AI information daily logs (24h retention)
├── backups/                # Timestamped backups
│   ├── json/              # JSON backups by type
│   ├── python/            # Script backups
│   └── legacy/            # Pre-v3.0 structure
├── docs/                   # All documentation
├── resources/              # Static resources
│   └── prompts/           # AI prompt templates
└── scripts/                # Shell scripts
```

### Core Modules

#### 1. **Trackers** (`src/trackers/`) - Real-time listening surveillance
   - [chk-roon.py](../src/trackers/chk-roon.py): Monitors Roon Core + Last.fm → `data/history/chk-roon.json` (v2.3.0)
     - **Key Design**: Searches for **public image URLs** (Spotify, Last.fm) instead of using Roon's internal images
     - **Purpose**: Enables downstream processing by AI and other scripts without requiring direct Roon access
     - **v2.3.0 Features**: 
       - Automatic AI album info generation for each track
       - Fallback Discogs → IA for optimal performance
       - Daily AI logs with 24h retention
       - Integrated scheduler checks (~45 min intervals)
   - [chk-last-fm.py](../src/trackers/chk-last-fm.py): Standalone Last.fm tracker → `data/history/chk-last-fm.json`

#### 2. **Collection** (`src/collection/`) - Discogs integration
   - [Read-discogs-ia.py](../src/collection/Read-discogs-ia.py): Fetches albums from Discogs API
   - [generate-soundtrack.py](../src/collection/generate-soundtrack.py): Cross-references film/album titles

#### 3. **Enrichment** (`src/enrichment/`) - Metadata completion
   - [complete-resumes.py](../src/enrichment/complete-resumes.py): AI-generated album summaries
   - [complete-images-roon.py](../src/enrichment/complete-images-roon.py): Spotify/Last.fm image completion
   - [normalize-supports.py](../src/enrichment/normalize-supports.py): Format standardization

#### 4. **Analysis** (`src/analysis/`) - Creative generation & insights
   - [generate-haiku.py](../src/analysis/generate-haiku.py): Uses EurIA API (Qwen3) to generate haikus from albums
   - [analyze-listening-patterns.py](../src/analysis/analyze-listening-patterns.py): Session detection, correlations, temporal patterns

#### 5. **Maintenance** (`src/maintenance/`) - Data cleanup
   - [remove-consecutive-duplicates.py](../src/maintenance/remove-consecutive-duplicates.py): Removes duplicate tracks
   - [fix-radio-tracks.py](../src/maintenance/fix-radio-tracks.py): Radio track corrections
   - [clean-radio-tracks.py](../src/maintenance/clean-radio-tracks.py): Radio track cleanup

#### 6. **Services** (`src/services/`) - Shared services and utilities
   - [spotify_service.py](../src/services/spotify_service.py): Centralized Spotify API integration (v3.1.0)
   - [metadata_cleaner.py](../src/services/metadata_cleaner.py): Metadata normalization functions (v3.1.0)
   - [ai_service.py](../src/services/ai_service.py): EurIA API integration for AI content generation (v3.3.0)
     - `ask_for_ia(prompt, max_attempts, timeout)`: Generic EurIA API call with retry
     - `generate_album_info(artist, album, max_characters)`: Generate album descriptions (500 chars max)
     - `get_album_info_from_discogs(album_title, discogs_path)`: Check Discogs for existing summaries
     - **Smart Fallback**: Discogs → IA priority (80%+ Discogs hit rate)
     - **Configuration**: Requires `.env` with `URL`, `bearer`, `max_attempts`, `default_error_message`

#### 7. **Utilities** (`src/utils/`) - Helper scripts and tools
   - [scheduler.py](../src/utils/scheduler.py): Task orchestration system (v3.2.0, 650 lines)
     - **4 Automated Tasks**: Haiku generation, listening analysis, Discogs sync, soundtrack matching
     - **Configuration**: Via `roon-config.json` (`scheduled_tasks` section)
     - **State Persistence**: `scheduler-state.json` tracks last execution times
     - **Frequency Units**: hour, day, month, year
     - **Integration**: Runs in chk-roon.py main loop (checks every ~45 minutes)
     - **CLI**: Can be run standalone for testing: `python3 scheduler.py --list-tasks`
   - [List_all_music_on_drive.py](../src/utils/List_all_music_on_drive.py): Disk music file scanner

#### 8. **GUI** (`src/gui/`) - Web interface
   - [musique-gui.py](../src/gui/musique-gui.py): Streamlit interface (v3.2.0)
     - Collection management with inline editing
     - Roon Journal with AI info expandable sections
     - **New in v3.2.0**: "🤖 Journal IA" view for daily AI logs
     - Scheduler configuration interface
     - Haiku and report visualization

**`generate-haiku.py`** - Album Haiku Generator (v2.1.0)
- **Location**: `src/analysis/generate-haiku.py`
- **Purpose**: Generates short presentations (haiku-style) for randomly selected albums
- **APIs**: EurIA API (Qwen3 with web search)
- **Sources**: 
  - 10 albums from `data/collection/discogs-collection.json` (Discogs collection)
  - 10 albums from `data/history/chk-roon.json` (Roon listening history)
- **Features**:
  - Secure random selection using `secrets.SystemRandom()`
  - **Duplicate detection** - Prevents same album from both sources (v2.1.0+)
  - AI-generated descriptions limited to 35 words in French
  - Automatic formatting for iA Presenter
  - Supports images from Spotify and Last.fm
  - Handles metadata (year, reissue, support format)
  - Links to Spotify and Discogs
  - Smart artist name cleaning (removes Discogs numeric suffixes)
  - Text wrapping to 45 characters per line with indentation
- **Functions**:
  - `normalize_album_key(artist, album)`: Creates normalized key for duplicate detection
  - `decouper_en_lignes(texte)`: Wraps text in 45-char lines with indentation
  - `ask_for_ia(prompt, max_attempts, timeout)`: Queries EurIA API with retry logic
  - `nettoyer_nom_artiste(nom_artiste)`: Cleans artist names (handles lists, removes "(number)")
  - `get_current_datetime_forFileName()`: Generates timestamp for output filename
  - `poetic_date()`: Formats date poetically in English ("The 21 of January, 2026")
  - `generate_haiku_from_artist_and_album(artist, album)`: Generates album description via AI
- **Usage**: `cd src/analysis && python3 generate-haiku.py`
- **Output**: `../../output/haikus/generate-haiku-YYYYMMDD-HHMMSS.txt` formatted for iA Presenter
- **Configuration**: Requires `../../data/config/.env` with `URL`, `bearer`, `max_attempts`, `default_error_message`
- **Typical workflow**:
  1. Load both JSON files (Discogs collection + Roon history)
  2. Extract unique albums from Roon tracks (ignores "Inconnu")
  3. Randomly select 10 albums from Discogs
  4. Create normalized keys for Discogs albums to detect duplicates
  5. Filter Roon albums to exclude any that match Discogs albums
  6. Randomly select up to 10 albums from filtered Roon list
  7. Generate AI descriptions for each album
  8. Format output with images, links, and metadata
  9. Save to timestamped text file

#### 7. **Utilities** (`src/utils/`) - Helper scripts
   - [List_all_music_on_drive.py](../src/utils/List_all_music_on_drive.py): Disk music file scanner
   - [test-spotify-search-v2.2.py](../src/utils/test-spotify-search-v2.2.py): Spotify API testing

**`musique-gui.py`** - Streamlit Music Collection Interface (v1.0.0)
- **Location**: `src/gui/musique-gui.py`
- **Purpose**: Web-based interface for managing Discogs collection and visualizing Roon/Last.fm listening history
- **Framework**: Streamlit with custom CSS styling
- **Dependencies**: `streamlit`, `pillow`, `requests`, `python-dotenv`
- **Features**:
  - **Collection Management**:
    - Search and filter albums (title, artist)
    - Soundtrack/BOF filter with film metadata integration
    - Inline editing with JSON persistence
    - Dual image display (Discogs + Spotify)
    - Direct links to Spotify and Discogs
    - **AI-powered resume generation** (EurIA API button)
  - **Roon Journal**:
    - Chronological listening history display
    - Multi-source filtering (Roon/Last.fm)
    - Triple image display (artist, album Spotify, album Last.fm)
    - **v3.2.0**: AI info expandable sections (🤖 Info IA)
    - Compact layout optimized for density (v2.0)
    - Real-time statistics
  - **AI Journal** (v3.2.0):
    - New menu item: "🤖 Journal IA"
    - Display daily AI logs (`output/ai-logs/`)
    - File selector for browsing past logs
    - Formatted entry display (timestamp, artist, album, info)
    - Entry counter per log file
  - **UI Optimizations** (v2.0-2.1):
    - Images reduced 4x (100px width)
    - Text-left/images-right layout (2:1 ratio)
    - Unified color scheme (gray background, black text)
    - 50% height reduction for compact display
    - Minimal spacing between entries
- **Configuration**: Requires `../../data/config/.env` with EurIA API credentials (`URL`, `bearer`)
- **Usage**: `./scripts/start-streamlit.sh` (recommended) or `cd src/gui && streamlit run musique-gui.py`
- **Port**: Default `http://localhost:8501`
- **Data sources**:
  - `../../data/collection/discogs-collection.json` (albums)
  - `../../data/history/chk-roon.json` (listening history)
  - `../../data/collection/soundtrack.json` (film metadata, optional)
- **Key functions**:
  - `load_data()`: Cached Discogs collection loader
  - `load_roon_data()`: Cached Roon history loader
  - `generate_resume_with_euria()`: AI resume generator (v2.1)
  - `display_discogs_collection()`: Collection management interface
  - `display_roon_journal()`: Listening history visualization
  - `load_image_from_url()`: Cached image loader with User-Agent
  - `save_data()`: JSON persistence with cache invalidation
- **Output**: Real-time updates to JSON files with automatic UI refresh

#### 9. **Tests** (`src/tests/`) - Test infrastructure
   - [conftest.py](../src/tests/conftest.py): Pytest configuration with shared fixtures
   - [test_spotify_service.py](../src/tests/test_spotify_service.py): 49 tests for Spotify integration (88% coverage)
   - [test_constants.py](../src/tests/test_constants.py): 57 tests for constants validation (100% coverage)
   - [test_metadata_cleaner.py](../src/tests/test_metadata_cleaner.py): 27 tests for metadata normalization (~95% coverage)
   - [test_scheduler.py](../src/tests/test_scheduler.py): 29 tests for task scheduler (~90% coverage)
   - [test_models.py](../src/tests/test_models.py): 26 tests for SQLite data models (100% coverage)
   - [test_ai_service.py](../src/tests/test_ai_service.py): Manual test script for AI service (needs pytest conversion)

**Test Infrastructure Details**:
- **Total**: 260 tests unitaires, ~3100 lignes de code de tests
- **Coverage**: ~92% pour les modules testés (spotify_service, constants, metadata_cleaner, scheduler, models)
- **Framework**: pytest + pytest-cov + pytest-mock
- **Fixtures**: Shared fixtures in conftest.py (mock tokens, sample data, env vars)
- **Markers**: @pytest.mark.unit, @pytest.mark.integration, @pytest.mark.slow
- **Documentation**: Complete guide in [src/tests/README.md](../src/tests/README.md)

**Test Execution**:
```bash
# All tests
python3 -m pytest src/tests/ -v

# With coverage
python3 -m pytest src/tests/ -v --cov=src/services --cov=src/constants --cov=src/models --cov-report=term-missing

# Specific module
python3 -m pytest src/tests/test_models.py -v
```

**Next Steps** (see ROADMAP.md):
- Convert test_ai_service.py to proper pytest unit tests
- Add integration tests for chk-roon.py
- Implement CI/CD with GitHub Actions to run tests automatically

#### 10. **Models** (`src/models/`) - Database schema (NEW v3.4.0)
   - [schema.py](../src/models/schema.py): SQLAlchemy ORM models for SQLite migration
     - **7 tables**: artists, albums, tracks, listening_history, images, metadata, album_artist
     - **Relations**: Many-to-Many (artists/albums), One-to-Many (albums/tracks), One-to-One (albums/metadata)
     - **Index**: artist_name, album_name, timestamp, source for performance
     - **Constraints**: Unique keys, foreign keys, cascade delete
   - [__init__.py](../src/models/__init__.py): Module exports

**Database Schema Features**:
- **Normalization**: Élimine la redondance (artistes/albums uniques)
- **Relations**: Support natif des albums multi-artistes (Many-to-Many)
- **Performance**: Index optimisés pour recherches par nom, date, source
- **Intégrité**: Contraintes relationnelles et validation automatique
- **Scalabilité**: Gestion de millions d'écoutes sans dégradation

**Migration Script**:
- [migrate_to_sqlite.py](../src/maintenance/migrate_to_sqlite.py): Script de migration JSON → SQLite
  - Phase 1: Import Collection Discogs (artistes, albums, images, metadata)
  - Phase 2: Import Historique Roon (tracks, listening_history, images)
  - Phase 3: Validation et statistiques
  - Support: `--dry-run` (simulation), `--db-path` (custom path), `--skip-backup`
  - Backup automatique des JSON avant migration

**Documentation**: Voir [docs/DATABASE-SCHEMA.md](../docs/DATABASE-SCHEMA.md) avec diagramme Mermaid complet, exemples SQL, stratégie de migration

### Data Files (JSON)

All data files are now organized in the `data/` directory:

#### Configuration (`data/config/`)
- **`.env`**: API credentials (Spotify, Last.fm, Discogs, EurIA) - **NEVER commit**
- **`roon-config.json`**: Roon Core connection + listening hours + scheduler configuration
  - `listen_start_hour`, `listen_end_hour`: Active listening tracking hours
  - `scheduled_tasks`: Task configuration (enabled, frequency, last_execution)
- **`scheduler-state.json`**: Scheduler state persistence (auto-generated, tracks execution history)

#### Collection (`data/collection/`)
- **`discogs-collection.json`**: Master collection file with Spotify URLs and cover art
- **`soundtrack.json`**: Generated cross-reference of film soundtracks in collection

#### History (`data/history/`)
- **`chk-roon.json`**: Listening history with enriched metadata (artist/album images from Spotify/Last.fm, AI album info)
  - **New in v2.3.0**: `ai_info` field with album descriptions (Discogs or AI-generated)
- **`chk-last-fm.json`**: Last.fm standalone tracking history
- **`chk-roon.lock`**: Process lock file (prevents concurrent tracker runs)

#### Exports (`data/exports/`)
- CSV, Markdown, PDF exports of collection data

## Critical Patterns

### Environment Configuration

All scripts use **`data/config/.env` file** for credentials (never commit this file). Scripts access it via relative path `../../data/config/.env` from their module directories:

```env
# Spotify API (for image enrichment)
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...

# Last.fm API (for listening history)
API_KEY=...
API_SECRET=...
LASTFM_USERNAME=...

# Discogs API (for collection fetching)
DISCOGS_API_KEY=...
DISCOGS_USERNAME=...

# EurIA API (for haiku generation and album info enrichment)
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=...
max_attempts=5
default_error_message=Aucune information disponible
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=...
```

**Pattern v3.0.0**: Use `python-dotenv` with explicit path to load credentials at script start:

```python
from dotenv import load_dotenv
import os

# Load environment from centralized config directory
load_dotenv('../../data/config/.env')

# Verify credentials loaded
if not os.getenv('SPOTIFY_CLIENT_ID'):
    print("⚠️ Missing Spotify credentials in .env")
```

Check `os.getenv()` returns before API calls.

### Metadata Cleaning Strategy

Music metadata requires extensive cleanup before API searches:

```python
def clean_artist_name(artist_name: str) -> str:
    # Remove multiple artists: "Dalida / Raymond Lefèvre" → "Dalida"
    if '/' in artist_name:
        artist_name = artist_name.split('/')[0].strip()
    # Remove annotations: "Nina Simone (Live)" → "Nina Simone"
    return re.sub(r'\s*\([^)]*\)\s*$', '', artist_name).strip()

def clean_album_name(album_name: str) -> str:
    # Remove metadata in parentheses and brackets
    # "9 [Italian]" → "9"
    # "Circlesongs (Voice)" → "Circlesongs"
    return re.sub(r'\s*[\(\[][^\)\]]*[\)\]]\s*$', '', album_name).strip()

def nettoyer_nom_artiste(nom_artiste):
    # Discogs-specific: Handle list format and numeric suffixes
    if isinstance(nom_artiste, list) and len(nom_artiste) > 0:
        nom_artiste = nom_artiste[0]
    # Remove "(number)" pattern: "Various (5)" → "Various"
    return re.sub(r'\s*\(\d+\)$', '', nom_artiste)
```

**Apply before**: Spotify searches, Last.fm queries, cache key generation.  
**See**: [chk-roon.py](../src/trackers/chk-roon.py) for both artist and album cleaning functions (lines 181-270).  
**Note**: `nettoyer_nom_artiste()` used in Discogs scripts handles both array format and numeric suffixes.

### Spotify Image Enrichment with Validation

Images come from two sources with strict validation logic:

```python
# 1. Artist images: Direct artist search
search_spotify_artist_image(token, artist_name)

# 2. Album covers: Multi-result search with artist validation and scoring
#    Try 1: Search "artist album", fetch 5 results
#    - Validate artist matches using artist_matches()
#    - Score each result based on title similarity (100 = exact, 80 = contains, 50 = partial)
#    - Select best match with score > 50
#    Try 2: Search "album" only with same validation (handles Various Artists)
#    - Lower threshold (score > 30) but still validates artist
search_spotify_album_image(token, artist_name, album_name)
```

**Artist Validation** (Version 2.2.0+):
- `normalize_string_for_comparison()`: Normalizes strings for case-insensitive comparison
- `artist_matches()`: Validates artist correspondence with tolerance for variations
  - Exact match: "Nina Simone" = "Nina Simone"
  - Case insensitive: "Nina Simone" = "nina simone"
  - Various Artists handling: "Various" = "Various Artists"
  - Partial match: "The Beatles" contains "Beatles"

**Scoring System** (Version 2.2.0+):
- 100 points: Exact album name match (after normalization)
- 80 points: Album name contains searched term or vice versa
- 50 points: Partial match based on common words ratio
- Minimum threshold: 50 for primary search, 30 for fallback

**Always cache results** with composite keys: `(artist_name, album_name)` to minimize API calls.  
**Token management**: Cache with expiration, refresh 60s before expiry.

**Retry Strategy** (Version 2.1.0+):
- All Spotify search functions accept `max_retries` parameter (default: 3)
- Automatic retry on HTTP 401 (expired token) - refreshes token and retries
- Automatic retry on HTTP 429 (rate limit) - waits 2 seconds and retries
- Token refresh happens transparently during retry cycles
- Sleep delay of 1 second between general retries

**Image Repair System** (Version 2.1.0+):
- `repair_null_spotify_images()` runs automatically at startup
- Scans `chk-roon.json` for tracks with null Spotify images
- Attempts to fetch missing images with fresh token
- Displays progress: `[n/total] Réparation artiste: Artist Name`
- Saves only if modifications were made
- Rate-limited with 0.5s delay between requests

### Duplicate Detection

Trackers prevent re-recording same track:

1. **Roon**: Compare consecutive `zone_id + track_key` hashes
2. **Last.fm**: Check timestamp within ±60s tolerance in `chk-roon.json`

```python
def is_track_already_saved(artist: str, title: str, album: str, timestamp: int) -> bool:
    # Load history, check if (artist, title, album) exists within ±60s
    # See chk-roon.py line 575 for implementation
```

### Process Locking (Single Instance Protection)

`chk-roon.py` uses **file-based exclusive locks** to prevent concurrent runs:

```python
def acquire_lock() -> bool:
    # Use fcntl.flock() with LOCK_EX | LOCK_NB
    # Write PID to chk-roon.lock
    # Return False if lock already held

def release_lock() -> None:
    # Always call in finally block
    # Remove lock file after release
```

**Critical**: OS automatically releases lock if process crashes.

## Development Workflows

### Running Trackers

**Roon Tracker** (preferred, monitors both Roon + Last.fm):
```bash
# From project root (recommended)
./start-roon-tracker.sh

# Or from module directory
cd src/trackers
source ../../.venv/bin/activate
python3 chk-roon.py
```

First run requires Roon authorization: Go to Roon → Settings → Extensions → Authorize "Python Roon Tracker"

**Automatic Image Repair** (v2.1.0+): On startup, the tracker automatically scans and repairs any missing Spotify images in the history.

**Last.fm Only**:
```bash
cd src/trackers
source ../../.venv/bin/activate
python3 chk-last-fm.py
```

**Important**: Only ONE instance of `chk-roon.py` can run at a time due to file locking (`data/history/chk-roon.lock`).

### Setup New Environment

Use the automated setup script:
```bash
chmod +x scripts/setup-roon-tracker.sh
./scripts/setup-roon-tracker.sh
```

Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-roon.txt  # roonapi, python-dotenv, certifi, pylast
```

### Testing API Connections

Each script has embedded test functions:
- Spotify: Check token retrieval logs at startup
- Last.fm: Look for "✅ Connexion Last.fm initialisée"
- Roon: First run shows discovery messages

### Generating Creative Content

```bash
cd src/analysis
python3 generate-haiku.py
# Output: ../../output/haikus/generate-haiku-YYYYMMDD-HHMMSS.txt
```

Uses `ask_for_ia()` function with EurIA API. Enable web search with `"enable_web_search": True` in request payload.



## Project-Specific Conventions

### File Organization (v3.0.0)

- **`src/`**: Source code organized by function (7 modules)
- **`data/`**: All data files (config, collection, history, exports)
- **`output/`**: Generated files (haikus, reports)
- **`backups/`**: Timestamped backups (json/, python/, legacy/)
- **`docs/`**: Centralized documentation
- **`resources/`**: Static resources (prompts, templates)
- **`scripts/`**: Shell scripts for setup and launching
- **`.venv/`**: Python virtual environment (not versioned)
- **`.env`**: API credentials → Now in `data/config/.env` (never commit)

### JSON Structure Conventions

All collection JSONs use consistent field names:
- `Titre` (not "Title")
- `Artiste` (array, not string)
- `Annee` (not "Year")
- `Pochette` / `Spotify_Cover_URL` (image URLs)
- `source` field: `"roon"` or `"lastfm"` to track data origin

### JSON File Backup Policy

**CRITICAL**: Before ANY modification to JSON files (especially `data/collection/discogs-collection.json`, `data/history/chk-roon.json`, `data/collection/soundtrack.json`), ALWAYS create a timestamped backup in `backups/json/` directory:

```bash
# Backup by file type
cp data/collection/discogs-collection.json "backups/json/discogs-collection/discogs-collection-$(date +%Y%m%d-%H%M%S).json"
cp data/history/chk-roon.json "backups/json/chk-roon/chk-roon-$(date +%Y%m%d-%H%M%S).json"
```

**This applies to:**
- Manual edits via scripts (Python, bash)
- Automated processing (normalization, enrichment, cleanup)
- Data imports/exports
- Any operation that modifies JSON content

**Retention policy**: Keep only the **5 most recent backups** per file. After creating a new backup, automatically clean up older versions:

```bash
# Keep only the 5 most recent backups
ls -t backups/json/discogs-collection/discogs-collection-*.json | tail -n +6 | xargs -r rm
ls -t backups/json/chk-roon/chk-roon-*.json | tail -n +6 | xargs -r rm
```

**Rationale**: JSON files contain valuable curated data (AI-generated summaries, metadata enrichments, manual corrections). Backups enable rollback and historical tracking while preventing disk space bloat.

**Example from `data/history/chk-roon.json`**:
```json
{
    "timestamp": 1768674069,
    "date": "2026-01-17 18:21",
    "artist": "Serge Gainsbourg",
    "title": "Couleur Cafe (Live)",
    "album": "Le Zenith De Gainsbourg",
    "loved": false,
    "artist_spotify_image": "https://...",
    "album_spotify_image": "https://...",
    "album_lastfm_image": "https://...",
    "source": "roon"
}
```

### Script Naming Pattern

Version suffixes indicate evolution:
- Current: No suffix (e.g., `chk-roon.py`, `Read-discogs-ia.py`)
- Legacy: Archived in `backups/legacy/` or `backups/python/backup-YYYYMMDD-HHMMSS/`

**Example**: `Read-discogs-ia.py` (current) replaced older versions `Read-discogs-lechat-v1/v2/v3.py` now in backups.

### Error Handling Style

Scripts use **graceful degradation**:
- Missing API keys → Disable feature, log warning, continue
- API failures → Cache fallback, retry logic, return None
- Network timeouts → Configurable max_attempts with backoff

**Don't crash on missing images** - services should continue tracking without enrichment.

## Integration Points

### Roon API (roonapi library)

- **Discovery**: `RoonDiscovery()` finds Roon Core on LAN
- **Authentication**: Token stored in `roon-config.json`, auto-saved on first authorization
- **State monitoring**: Poll `zones` every 45s, check `state='playing'`

### Discogs API

- User agent required: `'DiscogsClient/1.0 +your-email'`
- Rate limiting: Max 60 requests/min for authenticated users
- Album data structure: `basic_information` contains artist, title, year, cover_image

### Spotify Web API

- **Auth**: Client Credentials flow (no user login required)
- **Search endpoints**: `/v1/search?q=...&type=artist|album`
- **Image priority**: Use largest image (last in images array)

### Last.fm API (pylast)

- **Recent tracks**: `user.get_recent_tracks()` with date range
- **Loved status**: Check `track.loved` boolean
- **Album images**: Use `album.get_cover_image()` size 4 (largest)

### Cross-Project Integration (Cinéma ⟷ Musique)

**Current Status**: Planned data sharing between `/Cinéma/` and `/Musique/` directories. Currently implemented for soundtrack/BOF detection only.

**`generate-soundtrack.py`** - Film Soundtrack Matcher:
- **Location**: `src/collection/generate-soundtrack.py`
- **Version**: 1.0.0
- **External Dependency**: ⚠️ Requires `../../../Cinéma/catalogue.json` (external project)
  
**Directory Structure Required:**
```
Documents/DataForIA/
├── Cinéma/                    ← EXTERNAL PROJECT (required)
│   └── catalogue.json         ← Film collection with TMDB metadata
│
└── Musique/                   ← THIS PROJECT
    ├── src/collection/
    │   └── generate-soundtrack.py
    └── data/collection/
        ├── discogs-collection.json  ← Input (internal)
        └── soundtrack.json           ← Output (generated)
```

**Why External Dependency?**
- Reuses TMDB metadata already fetched by Cinéma project
- Avoids duplicate API calls to TMDB
- Enables bidirectional enrichment between projects
- Future: More cross-references planned (directors, actors)

**Expected Structure - catalogue.json (Cinéma project):**
```json
[
  {
    "OriginalTitle": "La Môme",
    "ProductionYear": 2007,
    "TMDB": {
      "realisateur": "Olivier Dahan"
    }
  }
]
```

**Functionality:**
- Cross-references with `../../data/collection/discogs-collection.json` (music albums)
- Matches film titles (`OriginalTitle`) against album titles (prefix matching)
- Algorithm: `album_title.startswith(film_title)` (case-insensitive)
- Outputs `../../data/collection/soundtrack.json` with matched soundtracks:
  - `film_title`: Original film title
  - `album_title`: Matching album name (lowercase)
  - `year`: Film production year
  - `director`: Film director from TMDB data
- Results sorted alphabetically (accent-insensitive using `unicodedata.normalize`)

**Usage**:
```bash
cd src/collection
python3 generate-soundtrack.py
# Requires: ../../../Cinéma/catalogue.json exists
# Generates: ../../data/collection/soundtrack.json
```

**Error Handling:**
- If Cinéma project absent: `FileNotFoundError` with path displayed
- If catalogue.json malformed: `json.JSONDecodeError`
- No automatic fallback - manual correction required

**Integration in musique-gui.py:**
- Loads `soundtrack.json` via `load_soundtrack_data()`
- Displays "🎬 SOUNDTRACK" badge for matched albums
- Shows film metadata: title, year, director
- Filter checkbox: "🎬 Seulement Soundtracks"

**Future enhancements**: Additional data sharing planned between repositories beyond soundtracks.

## Common Modifications

### ⚠️ CRITICAL: Always Backup Before Modifying Python Code

**MANDATORY PROCEDURE** before ANY modification to Python scripts:

1. **Create timestamped backup** in `backups/python/backup-YYYYMMDD-HHMMSS/`:
   ```bash
   mkdir -p "backups/python/backup-$(date +%Y%m%d-%H%M%S)"
   cp [fichiers_modifiés] "backups/python/backup-$(date +%Y%m%d-%H%M%S)/"
   ```

2. **Files to always backup**:
   - `src/trackers/chk-roon.py` - Roon/Last.fm tracker
   - `src/trackers/chk-last-fm.py` - Last.fm standalone tracker
   - `src/collection/Read-discogs-ia.py` - Discogs collection fetcher
   - `src/analysis/generate-haiku.py` - Haiku generator
   - `src/collection/generate-soundtrack.py` - Film soundtrack matcher
   - `src/maintenance/remove-consecutive-duplicates.py` - Duplicate remover
   - `src/enrichment/complete-resumes.py` - Resume generator
   - `src/enrichment/complete-images-roon.py` - Image completion
   - `src/enrichment/normalize-supports.py` - Support normalizer

3. **Backup command template**:
   ```bash
   # All main scripts
   mkdir -p "backups/python/backup-$(date +%Y%m%d-%H%M%S)"
   cp src/trackers/chk-roon.py src/trackers/chk-last-fm.py src/collection/Read-discogs-ia.py "backups/python/backup-$(date +%Y%m%d-%H%M%S)/"
   
   # Single file example
   cp src/trackers/chk-roon.py "backups/python/backup-$(date +%Y%m%d-%H%M%S)/chk-roon.py"
   ```

4. **Verify backup**:
   ```bash
   ls -lh "backups/python/backup-$(date +%Y%m%d-%H%M%S)/"
   ```

**This is non-negotiable.** Never skip backups, even for "small" changes.

### ⚠️ CRITICAL: Version Increment Policy

**MANDATORY PROCEDURE** when modifying Python scripts:

**Version Format**: `MAJOR.MINOR.PATCH` (Semantic Versioning)

**Increment rules:**
1. **PATCH** (x.x.X) - Bug fixes, documentation updates, no new features
   - Example: 2.1.0 → 2.1.1
   
2. **MINOR** (x.X.0) - New features, enhancements, backward-compatible changes
   - Example: 2.1.0 → 2.2.0
   - **Must update**: Script docstring, README, copilot-instructions.md
   
3. **MAJOR** (X.0.0) - Breaking changes, major rewrites, incompatible API changes
   - Example: 2.1.0 → 3.0.0
   - **Must update**: All documentation, migration guide

**When to increment:**
- ✅ **ALWAYS** when adding new functions or features
- ✅ **ALWAYS** when modifying existing behavior
- ✅ **ALWAYS** when fixing significant bugs
- ❌ No increment for: typo fixes, comment updates (unless in docstrings)

**Files to update when incrementing version:**
1. **Script file** (`chk-roon.py`, etc.) - Update docstring header:
   ```python
   Version: 2.2.0
   Date: YYYY-MM-DD
   ```

2. **README-ROON-TRACKER.md** - Update:
   - Features list (if new functionality)
   - Modules table (if new functions)
   - Footer version number

3. **.github/copilot-instructions.md** - Document:
   - New features in relevant sections
   - Breaking changes (if MAJOR)
   - Usage examples

**Example workflow:**
```bash
# 1. Make changes to src/trackers/chk-roon.py (add new feature)
# 2. Update version: 2.1.0 → 2.2.0
# 3. Update date in docstring
# 4. Update docs/README-ROON-TRACKER.md
# 5. Update .github/copilot-instructions.md
# 6. Backup before committing
```

**This is non-negotiable.** Every feature addition requires version increment and documentation update.

### Changing Listening Hours

Edit `data/config/roon-config.json`:
```json
{
  "listen_start_hour": 6,   // Start recording at 8am
  "listen_end_hour": 23      // Stop at 10pm
}
```

### Adding New AI Provider

1. Add credentials to `data/config/.env` with descriptive prefix
2. Create request function similar to `ask_for_ia()` in [generate-haiku.py](../src/analysis/generate-haiku.py)
3. Include retry logic (3-5 attempts) and timeout handling

### Extending Collection Fields

To add fields to `data/collection/discogs-collection.json`:
1. Update `src/collection/Read-discogs-ia.py` fetch logic
2. Modify `src/gui/musique-gui.py` interface to display/edit new field
3. Update `save_data()` method to persist new field

## Utility Scripts Reference

### Data Completion & Enrichment

**`complete-resumes.py`** - Album Summary Generator
- **Location**: `src/enrichment/complete-resumes.py`
- **Purpose**: Fills missing `Resume` fields in `data/collection/discogs-collection.json`
- **API**: Uses EurIA API (Qwen3) with web search enabled
- **Logic**: Generates 30-line summaries covering context, artistic approach, critical reception, and sonic elements
- **Usage**: `cd src/enrichment && python3 complete-resumes.py`
- **Handles**: Albums with `Resume == "Aucune information disponible"` or empty
- **Output**: Updates JSON in-place with generated summaries

**`complete-images-roon.py`** - Image Completion for Listening History
- **Location**: `src/enrichment/complete-images-roon.py`
- **Purpose**: Fills missing Spotify/Last.fm images in `data/history/chk-roon.json`
- **APIs**: Spotify (artist images, album covers), Last.fm (album covers)
- **Features**:
  - Artist name cleaning (removes "/" separators, parentheses)
  - Album name cleaning (removes version annotations)
  - Two-tier fallback for album searches (with/without artist)
  - Cache system to minimize API calls
  - Rate limiting protection (0.3s delay between requests)
- **Usage**: `cd src/enrichment && python3 complete-images-roon.py`
- **Typical results**: 93%+ artist images, 100% album images (Spotify)
- **Note**: `chk-roon.py` v2.1.0+ includes automatic repair at startup via `repair_null_spotify_images()`

### Data Normalization

**`normalize-supports.py`** - Support Format Standardization
- **Location**: `src/enrichment/normalize-supports.py`
- **Purpose**: Converts all support formats to "Vinyle" or "CD" only
- **Intelligence**:
  - CDr → CD (recordable CD)
  - Blu-ray → CD (modern reissue)
  - Box Set → Vinyle (if year ≥ 2015) or CD (otherwise)
  - All Media → CD (2000s format)
  - Inconnu → Smart detection based on:
    - Keywords: "Reissue"/"Redux" → Vinyle
    - Keywords: "Soundtrack"/"Original" → CD
    - Year: ≥2015 → Vinyle, 1985-2015 → CD, <1985 → Vinyle
- **Usage**: `cd src/enrichment && python3 normalize-supports.py` (interactive confirmation)
- **Safety**: Displays changes before applying, requires user confirmation

### Analytics & Insights

**`analyze-listening-patterns.py`** - Comprehensive Listening Behavior Analysis
- **Location**: `src/analysis/analyze-listening-patterns.py`
- **Purpose**: Detects patterns, correlations, and statistics in listening history
- **Analyses**:
  1. **Sessions**: Continuous listening periods (30-min gap threshold)
     - Count, duration estimation (~4 min/track)
     - Top longest sessions with start times
  2. **Complete Albums**: Albums played ≥5 tracks (likely full listen)
  3. **Time Patterns**:
     - Peak hours and days
     - Hourly distribution (grouped by 3-hour blocks)
     - Day-of-week distribution
  4. **Artist Correlations**: Artists often played in same sessions
  5. **Transitions**: Common artist → artist flows
  6. **Statistics**: Total duration, diversity score, unique artists/albums
- **Usage**: `cd src/analysis && python3 analyze-listening-patterns.py`
- **Output**: 
  - Console report with ASCII graphs
  - Text file: `../../output/reports/listening-patterns-YYYYMMDD-HHMMSS.txt`

### Data Cleaning & Maintenance

**`remove-consecutive-duplicates.py`** - Consecutive Duplicate Remover
- **Location**: `src/maintenance/remove-consecutive-duplicates.py`
- **Purpose**: Removes consecutive duplicate tracks in `data/history/chk-roon.json`
- **Detection**: Identifies tracks with identical artist, title, and album appearing consecutively
- **Features**:
  - Automatic backup creation before modification (to `backups/json/chk-roon/`)
  - Detailed duplicate listing (shows first 10)
  - Interactive confirmation before deletion
  - Statistics display (before/after counts)
- **Safety**:
  - Creates timestamped backup: `chk-roon-YYYYMMDD-HHMMSS.json`
  - Preserves original file until user confirmation
  - Only removes true consecutive duplicates (same track back-to-back)
- **Usage**: `cd src/maintenance && python3 remove-consecutive-duplicates.py`
- **Output**: 
  - Modified `../../data/history/chk-roon.json` (if confirmed)
  - Backup in `../../backups/json/chk-roon/`
  - Console report with removed duplicates

### Best Practices for Utility Scripts

1. **Always backup before running** (follows JSON Backup Policy)
2. **Check API credentials** in `data/config/.env` before image/AI scripts
3. **Review changes** before confirming (normalize-supports.py shows preview)
4. **Run during off-peak** if rate limiting is a concern
5. **Keep logs** of generated reports for historical tracking

### Creating New Utility Scripts

When creating new data processing scripts:
- Follow naming pattern: `{action}-{target}.py` (e.g., `complete-resumes.py`)
- Include docstring with purpose, author, date
- Load `data/config/.env` with `python-dotenv` for API keys
- Implement graceful error handling (print warnings, don't crash)
- Show progress indicators for long operations
- Generate summary statistics at completion
- Follow JSON Backup Policy (backup before modifications)

### ⚠️ MANDATORY: Document Every New Script

**CRITICAL RULE**: Each time a new utility script is created, you MUST immediately document it in the "Utility Scripts Reference" section above. This ensures persistent memory across sessions.

**Documentation template for new scripts:**
```markdown
**`script-name.py`** - Brief Title
- **Purpose**: One-line description
- **API**: APIs used (if any)
- **Features**:
  - Key feature 1
  - Key feature 2
- **Usage**: `python3 script-name.py`
- **Output**: What the script produces
```

**Process:**
1. Create the script
2. Test it works correctly
3. Immediately update "Utility Scripts Reference" section with documentation
4. Verify documentation is saved in `.github/copilot-instructions.md`

This documentation is NOT optional - it's the only way scripts persist across Copilot sessions.

## Documentation References

- **[docs/README-ROON-TRACKER.md](../docs/README-ROON-TRACKER.md)**: Complete setup guide for Roon/Last.fm tracking
- **[docs/README-MUSIQUE-GUI.md](../docs/README-MUSIQUE-GUI.md)**: Streamlit interface documentation and usage guide
- **[docs/ARCHITECTURE-OVERVIEW.md](../docs/ARCHITECTURE-OVERVIEW.md)**: Architecture v3.0.0 with modular structure
- **[docs/CHANGELOG-ARCHITECTURE-v3.0.0.md](../docs/CHANGELOG-ARCHITECTURE-v3.0.0.md)**: Complete v3.0.0 reorganization changelog
- **[resources/prompts/PROMPT-ROON-TRACKER-v2.2.0.md](../resources/prompts/PROMPT-ROON-TRACKER-v2.2.0.md)**: Original specification used to generate chk-roon.py
- **[requirements-roon.txt](../requirements-roon.txt)**: Python dependencies for trackers

## Debugging Tips

- **Roon not connecting**: Check firewall, ensure Roon Core running, verify same network
- **Spotify 401 errors**: Token expired, regenerate credentials in developer dashboard
- **Last.fm empty results**: Verify username spelling, check if account is public
- **Lock file issues**: Stale `chk-roon.lock`? Manually delete if process confirmed dead
- **Missing images**: Normal for obscure artists, fallback chain should prevent null writes
