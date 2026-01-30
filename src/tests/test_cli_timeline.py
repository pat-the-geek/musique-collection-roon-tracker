"""
Integration Tests for Timeline Commands

Tests the timeline command implementation with real data.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 30 janvier 2026
"""

import pytest
import json
from pathlib import Path
from click.testing import CliRunner

from src.cli.commands.timeline import timeline_group
from src.cli.utils.data_loader import DataLoader


@pytest.fixture
def temp_history_file(tmp_path):
    """Create a temporary history file for testing."""
    history_dir = tmp_path / "data" / "history"
    history_dir.mkdir(parents=True)
    
    history_file = history_dir / "chk-roon.json"
    
    # Create tracks spanning multiple hours and days
    test_data = [
        # Day 1 - Multiple hours
        {
            "timestamp": 1737964829,
            "date": "2026-01-27 06:20:29",
            "artist": "Miles Davis",
            "title": "So What",
            "album": "Kind of Blue",
            "loved": False,
            "source": "roon"
        },
        {
            "timestamp": 1737965558,
            "date": "2026-01-27 06:32:38",
            "artist": "Nina Simone",
            "title": "Feeling Good",
            "album": "I Put a Spell on You",
            "loved": True,
            "source": "roon"
        },
        {
            "timestamp": 1737968489,
            "date": "2026-01-27 07:21:29",
            "artist": "John Coltrane",
            "title": "A Love Supreme",
            "album": "A Love Supreme",
            "loved": False,
            "source": "roon"
        },
        # Day 2 - Different hours
        {
            "timestamp": 1738050429,
            "date": "2026-01-28 06:07:09",
            "artist": "Herbie Hancock",
            "title": "Watermelon Man",
            "album": "Head Hunters",
            "loved": True,
            "source": "roon"
        },
        {
            "timestamp": 1738054029,
            "date": "2026-01-28 07:07:09",
            "artist": "Bill Evans",
            "title": "Waltz for Debby",
            "album": "Waltz for Debby",
            "loved": False,
            "source": "lastfm"
        },
        {
            "timestamp": 1738081629,
            "date": "2026-01-28 14:47:09",
            "artist": "Oscar Peterson",
            "title": "Night Train",
            "album": "Night Train",
            "loved": True,
            "source": "roon"
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
    
    monkeypatch.setattr('src.cli.commands.timeline.get_loader', _get_loader)


class TestTimelineDisplay:
    """Tests for timeline display command."""
    
    def test_display_basic(self, runner, mock_loader):
        """Test basic timeline display."""
        result = runner.invoke(timeline_group, ['display', '--date', '2026-01-27'])
        assert result.exit_code == 0
        assert "Timeline" in result.output
    
    def test_display_compact_mode(self, runner, mock_loader):
        """Test compact timeline display."""
        result = runner.invoke(timeline_group, ['display', '--date', '2026-01-27', '--compact'])
        assert result.exit_code == 0
        assert "tracks)" in result.output
    
    def test_display_custom_hours(self, runner, mock_loader):
        """Test timeline with custom hour range."""
        result = runner.invoke(timeline_group, ['display', '--date', '2026-01-27', '--start-hour', '6', '--end-hour', '8'])
        assert result.exit_code == 0
    
    def test_display_invalid_date(self, runner, mock_loader):
        """Test timeline with non-existent date."""
        result = runner.invoke(timeline_group, ['display', '--date', '2026-01-01'])
        assert result.exit_code == 0
        assert "Aucune écoute" in result.output or "Dates disponibles" in result.output
    
    def test_display_auto_date(self, runner, mock_loader):
        """Test timeline with auto date (most recent)."""
        result = runner.invoke(timeline_group, ['display'])
        assert result.exit_code == 0
        # Should use most recent date


class TestTimelineListDates:
    """Tests for timeline list-dates command."""
    
    def test_list_dates_basic(self, runner, mock_loader):
        """Test listing available dates."""
        result = runner.invoke(timeline_group, ['list-dates'])
        assert result.exit_code == 0
        assert "Dates Disponibles" in result.output
        assert "2026-01-27" in result.output
        assert "2026-01-28" in result.output
    
    def test_list_dates_with_limit(self, runner, mock_loader):
        """Test listing dates with limit."""
        result = runner.invoke(timeline_group, ['list-dates', '--limit', '1'])
        assert result.exit_code == 0


class TestTimelineHourlyStats:
    """Tests for timeline hourly-stats command."""
    
    def test_hourly_stats_basic(self, runner, mock_loader):
        """Test basic hourly statistics."""
        result = runner.invoke(timeline_group, ['hourly-stats'])
        assert result.exit_code == 0
        assert "Statistiques Horaires" in result.output
    
    def test_hourly_stats_specific_date(self, runner, mock_loader):
        """Test hourly statistics for specific date."""
        result = runner.invoke(timeline_group, ['hourly-stats', '--date', '2026-01-27'])
        assert result.exit_code == 0
        assert "2026-01-27" in result.output


class TestTimelineHelpers:
    """Tests for timeline helper functions."""
    
    def test_get_tracks_by_date(self, mock_loader):
        """Test get_tracks_by_date function."""
        from src.cli.commands.timeline import get_tracks_by_date
        
        tracks = [
            {"date": "2026-01-27 06:20:29", "artist": "Artist 1"},
            {"date": "2026-01-27 07:15:00", "artist": "Artist 2"},
            {"date": "2026-01-28 08:30:00", "artist": "Artist 3"}
        ]
        
        result = get_tracks_by_date(tracks, "2026-01-27")
        assert len(result) == 2
    
    def test_group_by_hour(self, mock_loader):
        """Test group_by_hour function."""
        from src.cli.commands.timeline import group_by_hour
        
        tracks = [
            {"date": "2026-01-27 06:20:29", "artist": "Artist 1"},
            {"date": "2026-01-27 06:32:38", "artist": "Artist 2"},
            {"date": "2026-01-27 07:15:00", "artist": "Artist 3"}
        ]
        
        hourly = group_by_hour(tracks)
        assert 6 in hourly
        assert 7 in hourly
        assert len(hourly[6]) == 2
        assert len(hourly[7]) == 1
    
    def test_get_available_dates(self, mock_loader):
        """Test get_available_dates function."""
        from src.cli.commands.timeline import get_available_dates
        
        tracks = [
            {"date": "2026-01-27 06:20:29", "artist": "Artist 1"},
            {"date": "2026-01-27 07:15:00", "artist": "Artist 2"},
            {"date": "2026-01-28 08:30:00", "artist": "Artist 3"}
        ]
        
        dates = get_available_dates(tracks)
        assert len(dates) == 2
        assert "2026-01-28" == dates[0]  # Most recent first
        assert "2026-01-27" == dates[1]
    
    def test_group_by_hour_invalid_date(self, mock_loader):
        """Test group_by_hour with invalid date format."""
        from src.cli.commands.timeline import group_by_hour
        
        tracks = [
            {"date": "invalid", "artist": "Artist 1"},
            {"date": "2026-01-27 06:20:29", "artist": "Artist 2"}
        ]
        
        hourly = group_by_hour(tracks)
        assert 6 in hourly
        assert len(hourly[6]) == 1  # Only valid track


class TestTimelineEdgeCases:
    """Tests for timeline edge cases."""
    
    def test_empty_history(self, runner, tmp_path, monkeypatch):
        """Test timeline with no history."""
        # Create empty history
        history_dir = tmp_path / "data" / "history"
        history_dir.mkdir(parents=True)
        history_file = history_dir / "chk-roon.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        def _get_loader():
            return DataLoader(base_path=tmp_path)
        
        monkeypatch.setattr('src.cli.commands.timeline.get_loader', _get_loader)
        
        result = runner.invoke(timeline_group, ['display'])
        assert result.exit_code == 0
        assert "Aucun" in result.output or "disponible" in result.output
    
    def test_tracks_without_date(self, runner, tmp_path, monkeypatch):
        """Test timeline with tracks missing date field."""
        history_dir = tmp_path / "data" / "history"
        history_dir.mkdir(parents=True)
        history_file = history_dir / "chk-roon.json"
        
        test_data = [
            {"artist": "Artist 1", "title": "Track 1"},  # No date
            {"date": "2026-01-27 06:20:29", "artist": "Artist 2", "title": "Track 2"}
        ]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        def _get_loader():
            return DataLoader(base_path=tmp_path)
        
        monkeypatch.setattr('src.cli.commands.timeline.get_loader', _get_loader)
        
        result = runner.invoke(timeline_group, ['display', '--date', '2026-01-27'])
        assert result.exit_code == 0
        # Should handle gracefully


class TestTimelinePerformance:
    """Tests for timeline performance with large datasets."""
    
    def test_display_many_tracks_per_hour(self, runner, tmp_path, monkeypatch):
        """Test timeline with many tracks in same hour."""
        history_dir = tmp_path / "data" / "history"
        history_dir.mkdir(parents=True)
        history_file = history_dir / "chk-roon.json"
        
        # Create 50 tracks in same hour
        test_data = []
        for i in range(50):
            test_data.append({
                "timestamp": 1737964829 + i * 60,
                "date": f"2026-01-27 06:{i:02d}:00",
                "artist": f"Artist {i}",
                "title": f"Track {i}",
                "album": f"Album {i}",
                "loved": False,
                "source": "roon"
            })
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        def _get_loader():
            return DataLoader(base_path=tmp_path)
        
        monkeypatch.setattr('src.cli.commands.timeline.get_loader', _get_loader)
        
        result = runner.invoke(timeline_group, ['display', '--date', '2026-01-27'])
        assert result.exit_code == 0
        # Should handle large numbers gracefully (shows up to 20)
