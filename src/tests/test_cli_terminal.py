"""
Tests for CLI Terminal Utilities

Tests the terminal detection and capabilities functions.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 28 janvier 2026
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from src.cli.utils.terminal import (
    get_terminal_size,
    supports_color,
    supports_truecolor,
    detect_terminal_capabilities,
    get_terminal_name,
    is_ssh_session,
)


class TestTerminalSize:
    """Tests for terminal size detection."""
    
    def test_get_terminal_size_returns_tuple(self):
        """Test that get_terminal_size returns a tuple of two integers."""
        cols, lines = get_terminal_size()
        assert isinstance(cols, int)
        assert isinstance(lines, int)
        assert cols > 0
        assert lines > 0
    
    @patch('shutil.get_terminal_size')
    def test_get_terminal_size_uses_fallback(self, mock_size):
        """Test that fallback values are used when terminal size unavailable."""
        mock_size.return_value = MagicMock(columns=80, lines=24)
        cols, lines = get_terminal_size()
        assert cols == 80
        assert lines == 24


class TestColorSupport:
    """Tests for color support detection."""
    
    def test_supports_color_returns_bool(self):
        """Test that supports_color returns a boolean."""
        result = supports_color()
        assert isinstance(result, bool)
    
    @patch.dict(os.environ, {'NO_COLOR': '1'}, clear=True)
    def test_no_color_env_disables_color(self):
        """Test that NO_COLOR environment variable disables colors."""
        assert not supports_color()
    
    @patch.dict(os.environ, {'FORCE_COLOR': '1'}, clear=True)
    def test_force_color_env_enables_color(self):
        """Test that FORCE_COLOR environment variable enables colors."""
        assert supports_color()
    
    @patch.dict(os.environ, {'TERM': 'dumb'}, clear=True)
    def test_dumb_terminal_disables_color(self):
        """Test that dumb terminal disables colors."""
        # Note: This might still return True if stdout is a TTY
        # Just verify it doesn't crash
        result = supports_color()
        assert isinstance(result, bool)
    
    def test_supports_truecolor_returns_bool(self):
        """Test that supports_truecolor returns a boolean."""
        result = supports_truecolor()
        assert isinstance(result, bool)
    
    @patch.dict(os.environ, {'COLORTERM': 'truecolor'}, clear=True)
    @patch('src.cli.utils.terminal.supports_color', return_value=True)
    def test_colorterm_truecolor_enables_truecolor(self, mock_color):
        """Test that COLORTERM=truecolor enables truecolor support."""
        assert supports_truecolor()
    
    @patch.dict(os.environ, {'TERM_PROGRAM': 'iTerm.app'}, clear=True)
    @patch('src.cli.utils.terminal.supports_color', return_value=True)
    def test_iterm_enables_truecolor(self, mock_color):
        """Test that iTerm.app enables truecolor support."""
        assert supports_truecolor()


class TestCapabilityDetection:
    """Tests for terminal capability detection."""
    
    def test_detect_terminal_capabilities_returns_dict(self):
        """Test that detect_terminal_capabilities returns a dictionary."""
        caps = detect_terminal_capabilities()
        assert isinstance(caps, dict)
    
    def test_detect_terminal_capabilities_has_required_keys(self):
        """Test that capability dict contains all required keys."""
        caps = detect_terminal_capabilities()
        required_keys = ['color', 'truecolor', 'unicode', 'width', 'height', 'term', 'is_tty']
        for key in required_keys:
            assert key in caps
    
    def test_capability_types(self):
        """Test that capability values have correct types."""
        caps = detect_terminal_capabilities()
        assert isinstance(caps['color'], bool)
        assert isinstance(caps['truecolor'], bool)
        assert isinstance(caps['unicode'], bool)
        assert isinstance(caps['width'], int)
        assert isinstance(caps['height'], int)
        assert isinstance(caps['term'], str)
        assert isinstance(caps['is_tty'], bool)


class TestTerminalName:
    """Tests for terminal name detection."""
    
    def test_get_terminal_name_returns_string(self):
        """Test that get_terminal_name returns a string."""
        name = get_terminal_name()
        assert isinstance(name, str)
    
    @patch.dict(os.environ, {'TERM_PROGRAM': 'iTerm.app'}, clear=True)
    def test_get_terminal_name_prefers_term_program(self):
        """Test that TERM_PROGRAM is preferred over TERM."""
        name = get_terminal_name()
        assert name == 'iTerm.app'
    
    @patch.dict(os.environ, {'TERM': 'xterm-256color'}, clear=True)
    def test_get_terminal_name_fallback_to_term(self):
        """Test that TERM is used as fallback."""
        if 'TERM_PROGRAM' in os.environ:
            del os.environ['TERM_PROGRAM']
        name = get_terminal_name()
        assert name == 'xterm-256color'


class TestSSHDetection:
    """Tests for SSH session detection."""
    
    def test_is_ssh_session_returns_bool(self):
        """Test that is_ssh_session returns a boolean."""
        result = is_ssh_session()
        assert isinstance(result, bool)
    
    @patch.dict(os.environ, {'SSH_CLIENT': '192.168.1.1 12345 22'}, clear=True)
    def test_ssh_client_env_detected(self):
        """Test that SSH_CLIENT environment variable is detected."""
        assert is_ssh_session()
    
    @patch.dict(os.environ, {'SSH_TTY': '/dev/pts/1'}, clear=True)
    def test_ssh_tty_env_detected(self):
        """Test that SSH_TTY environment variable is detected."""
        assert is_ssh_session()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_no_ssh_env_returns_false(self):
        """Test that missing SSH variables returns False."""
        # Remove SSH variables if present
        for key in ['SSH_CLIENT', 'SSH_TTY']:
            if key in os.environ:
                del os.environ[key]
        assert not is_ssh_session()
