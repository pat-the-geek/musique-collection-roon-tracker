# AI Information Integration - Issue #21

## Overview

This document describes the implementation of AI-generated album information in the music collection tracker.

## Feature Summary

For each album detected by the Roon/Last.fm tracker:
1. The system first checks if the album exists in the Discogs collection
2. If found, it uses the existing `Resume` field from Discogs
3. If not found, it generates a short description via the EurIA API
4. All AI information is stored in both the track history and daily log files

## Implementation Details

### Files Modified

#### 1. `src/services/ai_service.py` (NEW)
Centralized AI service for the entire project.

**Functions:**
- `ask_for_ia(prompt, max_attempts, timeout)` - Core API call to EurIA
- `generate_album_info(artist, album, max_characters)` - Generate album descriptions (default: 500 chars)
- `get_album_info_from_discogs(album_title, discogs_path)` - Check Discogs collection

#### 2. `src/trackers/chk-roon.py`
**Version:** 2.2.0 → 2.3.0

**New Functions:**
- `get_album_ai_info(artist, album)` - Gets AI info with Discogs fallback
- `log_ai_info_to_file(artist, album, ai_info, timestamp)` - Logs to daily file
- `cleanup_old_ai_logs()` - Removes logs older than 24h

**Modified Behavior:**
- Each detected track now includes an `ai_info` field
- AI information is generated for all albums (not "Inconnu")
- Logs are created daily in `output/ai-logs/ai-log-YYYY-MM-DD.txt`
- Old logs are automatically cleaned at startup

#### 3. `src/gui/musique-gui.py`
**Version:** 3.1.0 → 3.2.0

**New Features:**
- AI information displayed in expandable sections in Roon Journal (both compact and detailed views)
- New navigation menu item: "🤖 Journal IA"
- New view function: `display_ai_logs()` - Shows daily AI logs with formatted entries

### Data Structure

#### Track Info (chk-roon.json)
```json
{
    "timestamp": 1737931200,
    "date": "2026-01-26 18:00",
    "artist": "Miles Davis",
    "title": "So What",
    "album": "Kind of Blue",
    "loved": false,
    "artist_spotify_image": "https://...",
    "album_spotify_image": "https://...",
    "album_lastfm_image": "https://...",
    "source": "roon",
    "ai_info": "[IA] Kind of Blue est un album emblématique du jazz modal sorti en 1959..."
}
```

#### Daily Log File (output/ai-logs/ai-log-2026-01-26.txt)
```
=== 2026-01-26 18:00:00 ===
Artiste: Miles Davis
Album: Kind of Blue
Info: [IA] Kind of Blue est un album emblématique du jazz modal...

=== 2026-01-26 18:05:00 ===
Artiste: Nina Simone
Album: Pastel Blues
Info: [Discogs] Pastel Blues is a studio album by Nina Simone...
```

## Configuration

### Environment Variables (.env)
```env
# EurIA API (for AI generation)
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=your_euria_bearer_token
max_attempts=5
default_error_message=Aucune information disponible
```

## Usage

### Automatic Operation
The AI information generation happens automatically when:
- The Roon tracker detects a new album
- A Last.fm track is imported
- Album is not "Inconnu" (Unknown)

### Manual Testing
```bash
# Test AI service integration
cd src/tests
python3 test_ai_service.py

# Run the tracker (with AI enabled)
cd src/trackers
python3 chk-roon.py
```

### Viewing AI Information

#### In GUI
1. Launch the GUI: `./start-streamlit.sh`
2. Navigate to "📻 Journal Roon"
3. Click on "🤖 Info IA" expander for any track
4. Or navigate to "🤖 Journal IA" to see all daily logs

## Performance Considerations

### API Rate Limiting
- EurIA API calls are made only once per unique album
- Results are stored in track history (no repeated calls)
- Logs preserved for 24h (configurable via cleanup function)

### Discogs Priority
- Discogs collection checked first (instant, no API call)
- Only generates AI info if album not in Discogs
- Reduces unnecessary API calls

### Log Cleanup
- Automatic cleanup at tracker startup
- Keeps only current day and previous day logs
- Prevents disk space bloat

## Error Handling

### Missing API Credentials
- If EurIA credentials missing, returns default error message
- Tracker continues to function (only AI info affected)

### API Failures
- Retry logic: 3 attempts with exponential backoff
- Timeout: 60 seconds per request (configurable)
- Graceful degradation: Returns error message, continues tracking

### Missing Discogs Collection
- If discogs-collection.json absent, skips Discogs check
- Falls back to AI generation directly
- No errors thrown

## Future Enhancements

### Potential Improvements
1. **Caching**: Add persistent cache for AI responses (beyond 24h logs)
2. **Batch Processing**: Generate AI info for existing history retroactively
3. **Translation**: Support multiple languages (currently French)
4. **Quality Control**: User feedback mechanism for AI descriptions
5. **Statistics**: Track AI vs Discogs usage ratio

### Configuration Options
1. **Log Retention**: Make retention period configurable (currently hardcoded 24h)
2. **Word Limit**: Allow customization of description length (currently 35 words)
3. **Source Priority**: Option to prefer AI over Discogs (or vice versa)

## Testing

### Unit Tests
Location: `src/tests/test_ai_service.py`

Tests:
1. Basic API connectivity
2. Album info generation
3. Discogs collection lookup

### Integration Testing
1. Run tracker with test albums
2. Verify AI info appears in chk-roon.json
3. Check daily logs created in output/ai-logs/
4. Confirm cleanup removes old logs
5. Verify GUI displays AI info correctly

## Troubleshooting

### "Aucune information disponible"
- Check EurIA credentials in .env
- Verify URL and bearer token are correct
- Test API connectivity manually

### No AI Info in GUI
- Ensure tracker has run since feature was added
- Old tracks (before v2.3.0) won't have AI info
- Check `ai_info` field exists in chk-roon.json

### Logs Not Appearing
- Verify `output/ai-logs/` directory exists
- Check file permissions
- Ensure tracker is running and detecting albums

### High API Usage
- Verify Discogs collection is loaded correctly
- Check for albums with "Inconnu" (should be skipped)
- Monitor for duplicate detections

## References

- EurIA API Documentation: https://api.infomaniak.com/doc/ai
- Issue #21: https://github.com/pat-the-geek/musique-collection-roon-tracker/issues/21
- Main Documentation: docs/README-ROON-TRACKER.md
