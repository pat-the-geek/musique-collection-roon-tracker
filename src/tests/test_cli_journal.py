"""
Integration Tests for Journal Commands

Tests the journal command implementation with real data.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 30 janvier 2026
"""

import pytest
import json
from pathlib import Path
from click.testing import CliRunner

from src.cli.commands.journal import journal_group
from src.cli.utils.data_loader import DataLoader


@pytest.fixture
def temp_history_file(tmp_path):
    """Create a temporary history file for testing."""
    history_dir = tmp_path / "data" / "history"
    history_dir.mkdir(parents=True)
    
    history_file = history_dir / "chk-roon.json"
    
    test_data = [
        {
            "timestamp": 1737964829,
            "date": "2026-01-27 06:20:29",
            "artist": "Miles Davis",
            "title": "So What",
            "album": "Kind of Blue",
            "loved": False,
            "source": "roon",
            "ai_info": "[IA] Iconic jazz modal album."
        },
        {
            "timestamp": 1737965558,
            "date": "2026-01-27 06:32:38",
            "artist": "Nina Simone",
            "title": "Feeling Good",
            "album": "I Put a Spell on You",
            "loved": True,
            "source": "roon",
            "ai_info": "[IA] Powerful soul and jazz."
        },
        {
            "timestamp": 1737965697,
            "date": "2026-01-27 07:15:00",
            "artist": "John Coltrane",
            "title": "A Love Supreme",
            "album": "A Love Supreme",
            "loved": False,
            "source": "lastfm",
            "ai_info": "[Discogs] Spiritual jazz masterpiece."
        },
        {
            "timestamp": 1738050429,
            "date": "2026-01-28 06:07:09",
            "artist": "Herbie Hancock",
            "title": "Watermelon Man",
            "album": "Head Hunters",
            "loved": True,
            "source": "roon",
            "ai_info": "[IA] Jazz funk fusion."
        },
        {
            "timestamp": 1738050829,
            "date": "2026-01-28 08:13:49",
            "artist": "Ella Fitzgerald",
            "title": "Summertime",
            "album": "Porgy and Bess",
            "loved": False,
            "source": "lastfm",
            "ai_info": "[IA] Classic vocal jazz."
        }
    ]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    return tmp_path


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_loader(temp_history_file, monkeypatch):
    """Mock the get_loader function."""
    def _get_loader():
        return DataLoader(base_path=temp_history_file)
    
    monkeypatch.setattr('src.cli.commands.journal.get_loader', _get_loader)


class TestJournalList:
    """Tests for journal list command."""
    
    def test_list_basic(self, runner, mock_loader):
        """Test basic track listing."""
        result = runner.invoke(journal_group, ['list'])
        assert result.exit_code == 0
        assert "Journal d'écoute" in result.output
    
    def test_list_with_limit(self, runner, mock_loader):
        """Test track listing with limit."""
        result = runner.invoke(journal_group, ['list', '--limit', '2'])
        assert result.exit_code == 0
        assert "2 tracks" in result.output
    
    def test_list_filter_source_roon(self, runner, mock_loader):
        """Test filtering by Roon source."""
        result = runner.invoke(journal_group, ['list', '--source', 'roon'])
        assert result.exit_code == 0
        assert "ROON" in result.output
    
    def test_list_filter_source_lastfm(self, runner, mock_loader):
        """Test filtering by Last.fm source."""
        result = runner.invoke(journal_group, ['list', '--source', 'lastfm'])
        assert result.exit_code == 0
        assert "LASTFM" in result.output
    
    def test_list_filter_loved(self, runner, mock_loader):
        """Test filtering by loved status."""
        result = runner.invoke(journal_group, ['list', '--loved'])
        assert result.exit_code == 0
        # Should show tracks with ♥
    
    def test_list_filter_not_loved(self, runner, mock_loader):
        """Test filtering by non-loved status."""
        result = runner.invoke(journal_group, ['list', '--not-loved'])
        assert result.exit_code == 0
    
    def test_list_filter_date_from(self, runner, mock_loader):
        """Test filtering by start date."""
        result = runner.invoke(journal_group, ['list', '--date-from', '2026-01-28'])
        assert result.exit_code == 0
        # Should only show tracks from Jan 28 onwards
    
    def test_list_filter_date_to(self, runner, mock_loader):
        """Test filtering by end date."""
        result = runner.invoke(journal_group, ['list', '--date-to', '2026-01-27'])
        assert result.exit_code == 0
        # Should only show tracks up to Jan 27


class TestJournalStats:
    """Tests for journal stats command."""
    
    def test_stats_basic(self, runner, mock_loader):
        """Test basic statistics display."""
        result = runner.invoke(journal_group, ['stats'])
        assert result.exit_code == 0
        assert "Statistiques" in result.output
        assert "Total tracks:" in result.output
    
    def test_stats_with_source_filter(self, runner, mock_loader):
        """Test statistics with source filter."""
        result = runner.invoke(journal_group, ['stats', '--source', 'roon'])
        assert result.exit_code == 0
        assert "ROON" in result.output
    
    def test_stats_with_date_range(self, runner, mock_loader):
        """Test statistics with date range."""
        result = runner.invoke(journal_group, ['stats', '--date-from', '2026-01-28'])
        assert result.exit_code == 0


class TestJournalView:
    """Tests for journal view command."""
    
    def test_view_first_track(self, runner, mock_loader):
        """Test viewing first track details."""
        result = runner.invoke(journal_group, ['view', '1'])
        assert result.exit_code == 0
        assert "Track #1" in result.output
    
    def test_view_last_track(self, runner, mock_loader):
        """Test viewing last track details."""
        result = runner.invoke(journal_group, ['view', '5'])
        assert result.exit_code == 0
        assert "Track #5" in result.output
    
    def test_view_invalid_index_negative(self, runner, mock_loader):
        """Test viewing with invalid negative index."""
        result = runner.invoke(journal_group, ['view', '0'])
        assert result.exit_code == 0
        assert "invalide" in result.output
    
    def test_view_invalid_index_too_large(self, runner, mock_loader):
        """Test viewing with index too large."""
        result = runner.invoke(journal_group, ['view', '100'])
        assert result.exit_code == 0
        assert "invalide" in result.output


class TestJournalFiltering:
    """Tests for journal filtering functions."""
    
    def test_filter_by_source(self, mock_loader):
        """Test filter_tracks by source."""
        from src.cli.commands.journal import filter_tracks
        
        tracks = [
            {"source": "roon", "artist": "Artist 1"},
            {"source": "lastfm", "artist": "Artist 2"},
            {"source": "roon", "artist": "Artist 3"}
        ]
        
        filtered = filter_tracks(tracks, source="roon")
        assert len(filtered) == 2
        assert all(t["source"] == "roon" for t in filtered)
    
    def test_filter_by_loved(self, mock_loader):
        """Test filter_tracks by loved status."""
        from src.cli.commands.journal import filter_tracks
        
        tracks = [
            {"loved": True, "artist": "Artist 1"},
            {"loved": False, "artist": "Artist 2"},
            {"loved": True, "artist": "Artist 3"}
        ]
        
        filtered = filter_tracks(tracks, loved=True)
        assert len(filtered) == 2
        assert all(t["loved"] for t in filtered)
    
    def test_filter_by_date_range(self, mock_loader):
        """Test filter_tracks by date range."""
        from src.cli.commands.journal import filter_tracks
        
        tracks = [
            {"date": "2026-01-27 06:20:29", "artist": "Artist 1"},
            {"date": "2026-01-28 08:13:49", "artist": "Artist 2"},
            {"date": "2026-01-29 10:00:00", "artist": "Artist 3"}
        ]
        
        filtered = filter_tracks(tracks, date_from="2026-01-28")
        assert len(filtered) == 2


class TestJournalStatistics:
    """Tests for journal statistics functions."""
    
    def test_get_track_statistics_basic(self, mock_loader):
        """Test get_track_statistics with basic data."""
        from src.cli.commands.journal import get_track_statistics
        
        tracks = [
            {"artist": "Artist 1", "album": "Album 1", "source": "roon", "loved": True, "date": "2026-01-27 06:20:29"},
            {"artist": "Artist 1", "album": "Album 2", "source": "lastfm", "loved": False, "date": "2026-01-27 07:15:00"},
            {"artist": "Artist 2", "album": "Album 1", "source": "roon", "loved": True, "date": "2026-01-27 08:30:00"}
        ]
        
        stats = get_track_statistics(tracks)
        
        assert stats['total'] == 3
        assert stats['unique_artists'] == 2
        assert stats['unique_albums'] == 2
        assert stats['loved_count'] == 2
        assert stats['sources']['roon'] == 2
        assert stats['sources']['lastfm'] == 1
    
    def test_get_track_statistics_empty(self, mock_loader):
        """Test get_track_statistics with empty data."""
        from src.cli.commands.journal import get_track_statistics
        
        stats = get_track_statistics([])
        
        assert stats['total'] == 0
        assert stats['unique_artists'] == 0
        assert stats['loved_count'] == 0


class TestJournalHelpers:
    """Tests for journal helper functions."""
    
    def test_format_timestamp(self):
        """Test format_timestamp function."""
        from src.cli.commands.journal import format_timestamp
        
        # Valid timestamp
        result = format_timestamp(1737964829)
        assert "2026-01-27" in result
        
        # Invalid timestamp
        result = format_timestamp(-1)
        assert "Invalid" in result or "1969" in result
    
    def test_format_date_short(self):
        """Test format_date_short function."""
        from src.cli.commands.journal import format_date_short
        
        # Full date-time string
        assert format_date_short("2026-01-27 06:20:29") == "2026-01-27"
        
        # Already short
        assert format_date_short("2026-01-27") == "2026-01-27"
