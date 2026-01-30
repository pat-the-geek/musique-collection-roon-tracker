"""
Integration Tests for AI Logs Commands

Tests the AI logs command implementation with real data.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 30 janvier 2026
"""

import pytest
from pathlib import Path
from click.testing import CliRunner

from src.cli.commands.ai_logs import ai_logs_group, parse_ai_log_file, extract_date_from_filename


@pytest.fixture
def temp_ai_logs(tmp_path):
    """Create temporary AI log files for testing."""
    logs_dir = tmp_path / "output" / "ai-logs"
    logs_dir.mkdir(parents=True)
    
    # Create a sample log file
    log_file = logs_dir / "ai-log-2026-01-27.txt"
    
    log_content = """=== 2026-01-27 06:20:29 ===
Artiste: Miles Davis
Album: Kind of Blue
Info: [IA] Iconic jazz modal album from 1959.

=== 2026-01-27 06:32:38 ===
Artiste: Nina Simone
Album: I Put a Spell on You
Info: [IA] Powerful soul and jazz performances.

=== 2026-01-27 07:15:00 ===
Artiste: John Coltrane
Album: A Love Supreme
Info: [Discogs] Spiritual jazz masterpiece recorded in 1964.
"""
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    # Create another log file
    log_file2 = logs_dir / "ai-log-2026-01-28.txt"
    log_content2 = """=== 2026-01-28 06:07:09 ===
Artiste: Herbie Hancock
Album: Head Hunters
Info: [IA] Jazz funk fusion from 1973.
"""
    
    with open(log_file2, 'w', encoding='utf-8') as f:
        f.write(log_content2)
    
    return tmp_path


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_logs_path(temp_ai_logs, monkeypatch):
    """Mock the get_ai_logs_path function."""
    def _get_path():
        return temp_ai_logs / "output" / "ai-logs"
    
    monkeypatch.setattr('src.cli.commands.ai_logs.get_ai_logs_path', _get_path)


class TestAILogsList:
    """Tests for ai-logs list command."""
    
    def test_list_basic(self, runner, mock_logs_path):
        """Test basic log file listing."""
        result = runner.invoke(ai_logs_group, ['list'])
        assert result.exit_code == 0
        assert "Logs d'Enrichissement IA" in result.output
        assert "ai-log-2026-01-27.txt" in result.output
        assert "ai-log-2026-01-28.txt" in result.output
    
    def test_list_shows_dates(self, runner, mock_logs_path):
        """Test that list shows dates."""
        result = runner.invoke(ai_logs_group, ['list'])
        assert result.exit_code == 0
        assert "2026-01-27" in result.output
        assert "2026-01-28" in result.output
    
    def test_list_empty_directory(self, runner, tmp_path, monkeypatch):
        """Test listing with no log files."""
        logs_dir = tmp_path / "output" / "ai-logs"
        logs_dir.mkdir(parents=True)
        
        def _get_path():
            return logs_dir
        
        monkeypatch.setattr('src.cli.commands.ai_logs.get_ai_logs_path', _get_path)
        
        result = runner.invoke(ai_logs_group, ['list'])
        assert result.exit_code == 0
        assert "Aucun log" in result.output


class TestAILogsView:
    """Tests for ai-logs view command."""
    
    def test_view_by_date(self, runner, mock_logs_path):
        """Test viewing log by date."""
        result = runner.invoke(ai_logs_group, ['view', '--date', '2026-01-27'])
        assert result.exit_code == 0
        assert "Log IA - 2026-01-27" in result.output
        assert "Miles Davis" in result.output
        assert "Nina Simone" in result.output
    
    def test_view_with_limit(self, runner, mock_logs_path):
        """Test viewing log with limit."""
        result = runner.invoke(ai_logs_group, ['view', '--date', '2026-01-27', '--limit', '1'])
        assert result.exit_code == 0
        assert "affichage: 1" in result.output
    
    def test_view_by_filename(self, runner, mock_logs_path):
        """Test viewing log by filename."""
        result = runner.invoke(ai_logs_group, ['view', '--file', 'ai-log-2026-01-28.txt'])
        assert result.exit_code == 0
        assert "Herbie Hancock" in result.output
    
    def test_view_nonexistent_file(self, runner, mock_logs_path):
        """Test viewing non-existent log file."""
        result = runner.invoke(ai_logs_group, ['view', '--date', '2026-01-01'])
        assert result.exit_code == 0
        assert "non trouvé" in result.output
    
    def test_view_auto_most_recent(self, runner, mock_logs_path):
        """Test viewing without specifying file (uses most recent)."""
        result = runner.invoke(ai_logs_group, ['view'])
        assert result.exit_code == 0
        # Should display content from most recent log


class TestAILogsStats:
    """Tests for ai-logs stats command."""
    
    def test_stats_basic(self, runner, mock_logs_path):
        """Test basic statistics display."""
        result = runner.invoke(ai_logs_group, ['stats', '--date', '2026-01-27'])
        assert result.exit_code == 0
        assert "Statistiques" in result.output
        assert "Total entrées:" in result.output
    
    def test_stats_shows_sources(self, runner, mock_logs_path):
        """Test that stats shows sources breakdown."""
        result = runner.invoke(ai_logs_group, ['stats', '--date', '2026-01-27'])
        assert result.exit_code == 0
        assert "IA générée" in result.output
        assert "Discogs" in result.output
    
    def test_stats_auto_most_recent(self, runner, mock_logs_path):
        """Test stats without date (uses most recent)."""
        result = runner.invoke(ai_logs_group, ['stats'])
        assert result.exit_code == 0
    
    def test_stats_nonexistent_file(self, runner, mock_logs_path):
        """Test stats with non-existent file."""
        result = runner.invoke(ai_logs_group, ['stats', '--date', '2026-01-01'])
        assert result.exit_code == 0
        assert "non trouvé" in result.output


class TestParseAILogFile:
    """Tests for parse_ai_log_file function."""
    
    def test_parse_valid_log(self, temp_ai_logs):
        """Test parsing a valid log file."""
        log_file = temp_ai_logs / "output" / "ai-logs" / "ai-log-2026-01-27.txt"
        entries = parse_ai_log_file(log_file)
        
        assert len(entries) == 3
        assert entries[0]['artist'] == "Miles Davis"
        assert entries[0]['album'] == "Kind of Blue"
        assert "[IA]" in entries[0]['info']
        assert entries[2]['artist'] == "John Coltrane"
        assert "[Discogs]" in entries[2]['info']
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file."""
        fake_file = Path("/nonexistent/file.txt")
        entries = parse_ai_log_file(fake_file)
        
        assert entries == []
    
    def test_parse_malformed_log(self, tmp_path):
        """Test parsing malformed log file."""
        log_file = tmp_path / "malformed.txt"
        
        # Missing required fields
        content = """=== 2026-01-27 06:20:29 ===
Artiste: Miles Davis
Missing album and info fields
"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        entries = parse_ai_log_file(log_file)
        
        # Should not include incomplete entries
        assert len(entries) == 0
    
    def test_parse_entry_with_all_fields(self, tmp_path):
        """Test parsing entry with all fields present."""
        log_file = tmp_path / "complete.txt"
        
        content = """=== 2026-01-27 06:20:29 ===
Artiste: Test Artist
Album: Test Album
Info: Test information
"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        entries = parse_ai_log_file(log_file)
        
        assert len(entries) == 1
        assert 'timestamp' in entries[0]
        assert 'artist' in entries[0]
        assert 'album' in entries[0]
        assert 'info' in entries[0]


class TestExtractDateFromFilename:
    """Tests for extract_date_from_filename function."""
    
    def test_extract_valid_filename(self):
        """Test extracting date from valid filename."""
        date = extract_date_from_filename("ai-log-2026-01-27.txt")
        assert date == "2026-01-27"
    
    def test_extract_invalid_filename(self):
        """Test extracting date from invalid filename."""
        date = extract_date_from_filename("invalid-filename.txt")
        assert date is None
    
    def test_extract_wrong_format(self):
        """Test extracting date from wrong date format."""
        date = extract_date_from_filename("ai-log-27-01-2026.txt")
        assert date is None
    
    def test_extract_missing_extension(self):
        """Test extracting date from filename without extension."""
        date = extract_date_from_filename("ai-log-2026-01-27")
        assert date is None


class TestAILogsEdgeCases:
    """Tests for AI logs edge cases."""
    
    def test_empty_log_file(self, runner, tmp_path, monkeypatch):
        """Test viewing empty log file."""
        logs_dir = tmp_path / "output" / "ai-logs"
        logs_dir.mkdir(parents=True)
        log_file = logs_dir / "ai-log-2026-01-27.txt"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        def _get_path():
            return logs_dir
        
        monkeypatch.setattr('src.cli.commands.ai_logs.get_ai_logs_path', _get_path)
        
        result = runner.invoke(ai_logs_group, ['view', '--date', '2026-01-27'])
        assert result.exit_code == 0
        assert "Aucune entrée" in result.output
    
    def test_log_with_special_characters(self, runner, tmp_path, monkeypatch):
        """Test log with special characters in content."""
        logs_dir = tmp_path / "output" / "ai-logs"
        logs_dir.mkdir(parents=True)
        log_file = logs_dir / "ai-log-2026-01-27.txt"
        
        content = """=== 2026-01-27 06:20:29 ===
Artiste: Café del Mar / José Padilla
Album: Café del Mar – Volume 1
Info: [IA] Chillout compilation featuring José Padilla's ambient selections from Café del Mar in Ibiza.
"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        def _get_path():
            return logs_dir
        
        monkeypatch.setattr('src.cli.commands.ai_logs.get_ai_logs_path', _get_path)
        
        result = runner.invoke(ai_logs_group, ['view', '--date', '2026-01-27'])
        assert result.exit_code == 0
        assert "José Padilla" in result.output or "José" in result.output
    
    def test_multiple_log_files_ordering(self, runner, mock_logs_path):
        """Test that log files are ordered by date (newest first)."""
        result = runner.invoke(ai_logs_group, ['list'])
        assert result.exit_code == 0
        
        # Check that 2026-01-28 appears before 2026-01-27
        output = result.output
        idx_28 = output.find("2026-01-28")
        idx_27 = output.find("2026-01-27")
        assert idx_28 < idx_27  # More recent date appears first
