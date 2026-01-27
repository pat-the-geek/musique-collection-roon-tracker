# Fix: Zero Tracks Count in AI Optimizer Report

**Date**: 27 janvier 2026  
**Version**: ai_optimizer v1.0.3  
**Status**: ✅ Fixed

## Problem Description

The AI optimization report was incorrectly showing zero tracks analyzed even when there were tracks in the listening history:

```
Date: 2026-01-27 22:18:09
Période d'analyse: 30 jours

1. ANALYSE DES PATTERNS D'ÉCOUTE
--------------------------------------------------------------------------------
Total tracks analysés: 0           ❌ INCORRECT
Jours actifs: 0/30                 ❌ INCORRECT
Volume quotidien moyen: 0 tracks/jour  ❌ INCORRECT
Score d'activité: 0.0/1.0          ❌ INCORRECT
```

## Root Cause

The issue was in `src/services/ai_optimizer.py` in the `__init__` method at line 160.

### The Bug

The `chk-roon.json` file has a nested structure:
```json
{
  "username": "your_lastfm_username",
  "month": "January 2026",
  "tracks": [
    { "timestamp": ..., "artist": ..., "title": ... },
    { "timestamp": ..., "artist": ..., "title": ... }
  ]
}
```

The original code was loading the entire JSON object:
```python
self.history = self._load_json(self.history_path)
```

This resulted in `self.history` being a **dict** (`{"username": ..., "month": ..., "tracks": [...]}`), not the **list of tracks**.

When `analyze_listening_patterns()` tried to iterate over `self.history`, it was iterating over the dict keys (`username`, `month`, `tracks`) instead of the actual track objects, resulting in zero tracks being analyzed.

### Why Other Scripts Worked

The `src/analysis/analyze-listening-patterns.py` script worked correctly because it explicitly extracted the tracks array:
```python
def load_tracks() -> List[Dict]:
    with open(..., 'chk-roon.json', 'r') as f:
        data = json.load(f)
    return data['tracks']  # ✅ Correctly extracts tracks array
```

## Solution

Modified the `__init__` method in `src/services/ai_optimizer.py` to detect the file format and extract the tracks array:

```python
# Charger l'historique et extraire le tableau tracks
history_data = self._load_json(self.history_path) if self.history_path.exists() else []
if isinstance(history_data, dict) and 'tracks' in history_data:
    # Nouveau format: dict avec clé 'tracks'
    self.history = history_data['tracks']
elif isinstance(history_data, list):
    # Ancien format: liste directe
    self.history = history_data
else:
    # Format invalide ou vide
    self.history = []
```

This solution:
- ✅ Handles the current dict format with 'tracks' key
- ✅ Maintains backward compatibility with old list format
- ✅ Gracefully handles invalid/empty data

## Changes Made

### 1. Core Fix (`src/services/ai_optimizer.py`)
- **Lines 157-171**: Replaced simple assignment with format detection logic
- **Line 40**: Updated version from 1.0.2 to 1.0.3
- **Lines 44-47**: Added changelog entry for v1.0.3

### 2. Test Coverage (`src/tests/test_ai_optimizer.py`)
- Added new test: `test_init_with_dict_format_history()`
- Verifies correct extraction of tracks from dict format
- Creates test data with dict structure and validates:
  - `self.history` is a list
  - Contains correct number of tracks (2)
  - Individual tracks have correct data

### 3. Manual Verification Script (`test_fix_manual.py`)
- Comprehensive end-to-end test with realistic data
- Creates 100 tracks in dict format over 5 days (sparse activity)
- Validates all metrics:
  - Total tracks: 100 ✅
  - Daily volume: 3.3 tracks/jour (100/30 days) ✅
  - Active days: 5/30 ✅
  - Activity score: 0.11/1.0 ✅

## Validation Results

### Automated Tests
```bash
$ python3 -m pytest src/tests/test_ai_optimizer.py -v
# Result: 35 passed (34 existing + 1 new)
```

All tests pass, including:
- Existing pattern analysis tests (use list format, still work)
- New dict format test (verifies fix)

### Manual Test
```bash
$ python3 test_fix_manual.py
# Result: ✅ SUCCÈS: Tous les tests sont passés
```

Output shows correct analysis:
```
Total tracks analysés: 100        ✅ CORRECT
Jours actifs: 5/30                ✅ CORRECT
Volume quotidien moyen: 3.3 tracks/jour  ✅ CORRECT
Score d'activité: 0.11/1.0        ✅ CORRECT
Plages typiques: 12h - 16h
Heures de pic: 13h, 14h, 15h, 12h
```

## Impact

### Who Benefits
- All users running AI optimizer reports
- Automated optimization system relying on accurate metrics
- Anyone using the optimization recommendations for system tuning

### Before vs After

**Before (v1.0.2)**:
```
Total tracks analysés: 0
Jours actifs: 0/30
Volume quotidien moyen: 0 tracks/jour
Score d'activité: 0.0/1.0
```

**After (v1.0.3)**:
```
Total tracks analysés: 100
Jours actifs: 5/30
Volume quotidien moyen: 3.3 tracks/jour
Score d'activité: 0.11/1.0
```

## Related Issues

This fix complements the previous Issue #47 fixes:
- **v1.0.1**: Fixed daily_volume calculation to use full analysis period
- **v1.0.2**: Improved report formatting (peak hours, active days display)
- **v1.0.3**: Fixed history loading to extract tracks array (this issue)

Together, these fixes ensure accurate analysis and reporting of listening patterns.

## Files Changed

1. `src/services/ai_optimizer.py` - Core fix
2. `src/tests/test_ai_optimizer.py` - Test coverage
3. `test_fix_manual.py` - Manual verification (can be removed after merge)
4. `ISSUE-TRACKS-ZERO-FIX.md` - This document

## Backward Compatibility

The fix maintains full backward compatibility:
- Old format (direct list): Still works ✅
- New format (dict with 'tracks'): Now works ✅
- Empty/invalid data: Handled gracefully ✅

No breaking changes to API or behavior.
