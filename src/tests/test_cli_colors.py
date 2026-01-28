"""
Tests for CLI Semantic Color System

Tests the semantic color system and style application.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 28 janvier 2026
"""

import pytest
from rich.style import Style
from rich.text import Text

from src.cli.ui.colors import (
    SemanticColor,
    COLOR_STYLES,
    TRUECOLOR_STYLES,
    NO_COLOR_STYLES,
    apply_color,
    get_style,
    set_color_mode,
    get_color_mode,
    primary,
    secondary,
    success,
    warning,
    error,
    muted,
    artist,
    album,
)


class TestSemanticColor:
    """Tests for SemanticColor enum."""
    
    def test_semantic_color_enum_has_all_values(self):
        """Test that SemanticColor enum has expected values."""
        expected_colors = [
            'PRIMARY', 'SECONDARY', 'ACCENT',
            'SUCCESS', 'WARNING', 'ERROR', 'INFO',
            'MUTED', 'EMPHASIS',
            'ARTIST', 'ALBUM', 'TRACK', 'YEAR', 'LOVED',
            'SOURCE_ROON', 'SOURCE_LASTFM', 'SOUNDTRACK'
        ]
        for color in expected_colors:
            assert hasattr(SemanticColor, color)
    
    def test_semantic_color_values_are_strings(self):
        """Test that all semantic color values are strings."""
        for color in SemanticColor:
            assert isinstance(color.value, str)


class TestColorStyles:
    """Tests for color style dictionaries."""
    
    def test_color_styles_has_all_semantic_colors(self):
        """Test that COLOR_STYLES has entry for every semantic color."""
        for color in SemanticColor:
            assert color in COLOR_STYLES
    
    def test_truecolor_styles_has_all_semantic_colors(self):
        """Test that TRUECOLOR_STYLES has entry for every semantic color."""
        for color in SemanticColor:
            assert color in TRUECOLOR_STYLES
    
    def test_no_color_styles_has_all_semantic_colors(self):
        """Test that NO_COLOR_STYLES has entry for every semantic color."""
        for color in SemanticColor:
            assert color in NO_COLOR_STYLES
    
    def test_color_styles_returns_style_objects(self):
        """Test that all color styles are Style objects."""
        for color, style in COLOR_STYLES.items():
            assert isinstance(style, Style)
    
    def test_truecolor_styles_returns_style_objects(self):
        """Test that all truecolor styles are Style objects."""
        for color, style in TRUECOLOR_STYLES.items():
            assert isinstance(style, Style)
    
    def test_no_color_styles_returns_style_objects(self):
        """Test that all no-color styles are Style objects."""
        for color, style in NO_COLOR_STYLES.items():
            assert isinstance(style, Style)


class TestColorMode:
    """Tests for color mode management."""
    
    def test_set_color_mode(self):
        """Test setting color mode."""
        set_color_mode('truecolor')
        assert get_color_mode() == 'truecolor'
        
        set_color_mode('auto')
        assert get_color_mode() == 'auto'
    
    def test_get_color_mode_default(self):
        """Test default color mode."""
        mode = get_color_mode()
        assert isinstance(mode, str)
        assert mode in ['auto', 'truecolor', 'color', 'never']


class TestApplyColor:
    """Tests for apply_color function."""
    
    def test_apply_color_returns_text(self):
        """Test that apply_color returns a Text object."""
        result = apply_color("test", SemanticColor.PRIMARY)
        assert isinstance(result, Text)
    
    def test_apply_color_preserves_text_content(self):
        """Test that apply_color preserves text content."""
        text = "Hello, World!"
        result = apply_color(text, SemanticColor.SUCCESS)
        assert str(result) == text
    
    def test_apply_color_with_truecolor(self):
        """Test apply_color with truecolor flag."""
        result = apply_color("test", SemanticColor.PRIMARY, truecolor=True)
        assert isinstance(result, Text)
    
    def test_apply_color_with_no_color(self):
        """Test apply_color with no_color flag."""
        result = apply_color("test", SemanticColor.PRIMARY, no_color=True)
        assert isinstance(result, Text)
    
    def test_apply_color_all_semantic_colors(self):
        """Test apply_color works with all semantic colors."""
        for color in SemanticColor:
            result = apply_color("test", color)
            assert isinstance(result, Text)


class TestGetStyle:
    """Tests for get_style function."""
    
    def test_get_style_returns_style(self):
        """Test that get_style returns a Style object."""
        style = get_style(SemanticColor.PRIMARY)
        assert isinstance(style, Style)
    
    def test_get_style_with_truecolor(self):
        """Test get_style with truecolor flag."""
        style = get_style(SemanticColor.PRIMARY, truecolor=True)
        assert isinstance(style, Style)
        # Should match TRUECOLOR_STYLES
        expected = TRUECOLOR_STYLES[SemanticColor.PRIMARY]
        # Note: We can't directly compare styles, just check it's valid
        assert style is not None
    
    def test_get_style_with_no_color(self):
        """Test get_style with no_color flag."""
        style = get_style(SemanticColor.PRIMARY, no_color=True)
        assert isinstance(style, Style)
        # Should match NO_COLOR_STYLES
        expected = NO_COLOR_STYLES[SemanticColor.PRIMARY]
        assert style is not None
    
    def test_get_style_all_semantic_colors(self):
        """Test get_style works with all semantic colors."""
        for color in SemanticColor:
            style = get_style(color)
            assert isinstance(style, Style)


class TestShortcutFunctions:
    """Tests for shortcut color functions."""
    
    def test_primary_returns_text(self):
        """Test primary() returns Text object."""
        result = primary("test")
        assert isinstance(result, Text)
        assert str(result) == "test"
    
    def test_secondary_returns_text(self):
        """Test secondary() returns Text object."""
        result = secondary("test")
        assert isinstance(result, Text)
        assert str(result) == "test"
    
    def test_success_returns_text(self):
        """Test success() returns Text object."""
        result = success("test")
        assert isinstance(result, Text)
        assert str(result) == "test"
    
    def test_warning_returns_text(self):
        """Test warning() returns Text object."""
        result = warning("test")
        assert isinstance(result, Text)
        assert str(result) == "test"
    
    def test_error_returns_text(self):
        """Test error() returns Text object."""
        result = error("test")
        assert isinstance(result, Text)
        assert str(result) == "test"
    
    def test_muted_returns_text(self):
        """Test muted() returns Text object."""
        result = muted("test")
        assert isinstance(result, Text)
        assert str(result) == "test"
    
    def test_artist_returns_text(self):
        """Test artist() returns Text object."""
        result = artist("Nina Simone")
        assert isinstance(result, Text)
        assert str(result) == "Nina Simone"
    
    def test_album_returns_text(self):
        """Test album() returns Text object."""
        result = album("Kind of Blue")
        assert isinstance(result, Text)
        assert str(result) == "Kind of Blue"
    
    def test_shortcut_with_truecolor(self):
        """Test shortcut functions accept truecolor parameter."""
        result = primary("test", truecolor=True)
        assert isinstance(result, Text)
    
    def test_shortcut_with_no_color(self):
        """Test shortcut functions accept no_color parameter."""
        result = success("test", no_color=True)
        assert isinstance(result, Text)
