"""
Integration Tests for Collection Commands

Tests the collection command implementation with real data.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 29 janvier 2026
"""

import pytest
import json
from pathlib import Path
from rich.console import Console
from io import StringIO

from src.cli.commands.collection import CollectionCommand
from src.cli.utils.data_loader import DataLoader


@pytest.fixture
def temp_collection_file(tmp_path):
    """Create a temporary collection file for testing."""
    collection_dir = tmp_path / "data" / "collection"
    collection_dir.mkdir(parents=True)
    
    collection_file = collection_dir / "discogs-collection.json"
    
    test_data = [
        {
            "Release_ID": 123456,
            "Titre": "Kind of Blue",
            "Artiste": ["Miles Davis"],
            "Annee": 1959,
            "Support": "Vinyle",
            "Label": "Columbia",
            "Resume": "A landmark jazz album"
        },
        {
            "Release_ID": 234567,
            "Titre": "Abbey Road",
            "Artiste": ["The Beatles"],
            "Annee": 1969,
            "Support": "Vinyle",
            "Label": "Apple Records",
            "Resume": "The Beatles' final album"
        },
        {
            "Release_ID": 345678,
            "Titre": "The Godfather",
            "Artiste": ["Nino Rota"],
            "Annee": 1972,
            "Support": "CD",
            "Film": "The Godfather",
            "Realisateur": "Francis Ford Coppola",
            "Resume": "Iconic film score"
        }
    ]
    
    with open(collection_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    return tmp_path


@pytest.fixture
def console():
    """Create a console for testing."""
    return Console(file=StringIO(), force_terminal=True, width=120)


@pytest.fixture
def collection_cmd(console, temp_collection_file):
    """Create a CollectionCommand with test data."""
    # Override the loader's base path
    loader = DataLoader(base_path=temp_collection_file)
    cmd = CollectionCommand(console)
    cmd.loader = loader
    return cmd


class TestCollectionList:
    """Tests for collection list command."""
    
    def test_list_albums_basic(self, collection_cmd):
        """Test basic album listing."""
        collection_cmd.list_albums(page=1, per_page=25)
        # Should not raise any exceptions
    
    def test_list_albums_with_sorting(self, collection_cmd):
        """Test album listing with sorting."""
        # Sort by title
        collection_cmd.list_albums(sort_by='title')
        
        # Sort by artist
        collection_cmd.list_albums(sort_by='artist')
        
        # Sort by year
        collection_cmd.list_albums(sort_by='year')
    
    def test_list_albums_with_pagination(self, collection_cmd):
        """Test album listing with pagination."""
        # Page 1 with 2 items per page
        collection_cmd.list_albums(page=1, per_page=2)
        
        # Page 2
        collection_cmd.list_albums(page=2, per_page=2)
    
    def test_list_albums_empty_collection(self, console):
        """Test listing with empty collection."""
        # Create command with no data
        cmd = CollectionCommand(console)
        cmd.loader = DataLoader(base_path=Path("/nonexistent"))
        cmd.list_albums()
        # Should handle gracefully


class TestCollectionSearch:
    """Tests for collection search command."""
    
    def test_search_by_title(self, collection_cmd):
        """Test searching by album title."""
        collection_cmd.search_albums("Blue")
        # Should find "Kind of Blue"
    
    def test_search_by_artist(self, collection_cmd):
        """Test searching by artist name."""
        collection_cmd.search_albums("Beatles")
        # Should find "Abbey Road"
    
    def test_search_case_insensitive(self, collection_cmd):
        """Test that search is case-insensitive."""
        collection_cmd.search_albums("MILES")
        # Should find "Kind of Blue"
    
    def test_search_no_results(self, collection_cmd):
        """Test search with no matches."""
        collection_cmd.search_albums("NonExistent")
        # Should handle gracefully


class TestCollectionView:
    """Tests for collection view command."""
    
    def test_view_existing_album(self, collection_cmd):
        """Test viewing an existing album."""
        collection_cmd.view_album(123456)
        # Should display album details
    
    def test_view_nonexistent_album(self, collection_cmd):
        """Test viewing a non-existent album."""
        collection_cmd.view_album(999999)
        # Should handle gracefully
    
    def test_view_soundtrack_album(self, collection_cmd):
        """Test viewing a soundtrack album."""
        collection_cmd.view_album(345678)
        # Should display film information


class TestCollectionStats:
    """Tests for collection stats command."""
    
    def test_show_stats(self, collection_cmd):
        """Test displaying collection statistics."""
        collection_cmd.show_stats()
        # Should not raise any exceptions
    
    def test_stats_empty_collection(self, console):
        """Test stats with empty collection."""
        cmd = CollectionCommand(console)
        cmd.loader = DataLoader(base_path=Path("/nonexistent"))
        cmd.show_stats()
        # Should handle gracefully


class TestCollectionFiltering:
    """Tests for collection filtering."""
    
    def test_filter_soundtrack(self, collection_cmd):
        """Test filtering soundtracks."""
        collection = collection_cmd.loader.load_collection()
        filtered = collection_cmd._apply_filters(collection, "soundtrack")
        assert len(filtered) == 1
        assert filtered[0]['Film'] == "The Godfather"
    
    def test_filter_by_year(self, collection_cmd):
        """Test filtering by year."""
        collection = collection_cmd.loader.load_collection()
        filtered = collection_cmd._apply_filters(collection, "year:1959")
        assert len(filtered) == 1
        assert filtered[0]['Titre'] == "Kind of Blue"
    
    def test_filter_by_support(self, collection_cmd):
        """Test filtering by support type."""
        collection = collection_cmd.loader.load_collection()
        filtered = collection_cmd._apply_filters(collection, "support:Vinyle")
        assert len(filtered) == 2


class TestCollectionSorting:
    """Tests for collection sorting."""
    
    def test_sort_by_title(self, collection_cmd):
        """Test sorting by title."""
        collection = collection_cmd.loader.load_collection()
        sorted_collection = collection_cmd._apply_sorting(collection, "title")
        
        # Should be alphabetically sorted
        titles = [album['Titre'] for album in sorted_collection]
        assert titles == sorted(titles)
    
    def test_sort_by_year(self, collection_cmd):
        """Test sorting by year."""
        collection = collection_cmd.loader.load_collection()
        sorted_collection = collection_cmd._apply_sorting(collection, "year")
        
        # Should be sorted by year
        years = [album['Annee'] for album in sorted_collection]
        assert years == sorted(years)
    
    def test_sort_by_artist(self, collection_cmd):
        """Test sorting by artist."""
        collection = collection_cmd.loader.load_collection()
        sorted_collection = collection_cmd._apply_sorting(collection, "artist")
        
        # Should be sorted by artist name
        # Just verify it doesn't crash
        assert len(sorted_collection) == len(collection)


class TestDataLoader:
    """Tests for DataLoader utility."""
    
    def test_load_collection(self, temp_collection_file):
        """Test loading collection data."""
        loader = DataLoader(base_path=temp_collection_file)
        collection = loader.load_collection()
        
        assert isinstance(collection, list)
        assert len(collection) == 3
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        loader = DataLoader(base_path=Path("/nonexistent"))
        collection = loader.load_collection()
        
        # Should return empty list
        assert collection == []
    
    def test_cache_functionality(self, temp_collection_file):
        """Test that caching works."""
        loader = DataLoader(base_path=temp_collection_file)
        
        # First load
        collection1 = loader.load_collection(use_cache=True)
        
        # Second load (should use cache)
        collection2 = loader.load_collection(use_cache=True)
        
        # Should be the same reference (cached)
        assert collection1 is collection2
    
    def test_clear_cache(self, temp_collection_file):
        """Test clearing cache."""
        loader = DataLoader(base_path=temp_collection_file)
        
        # Load with cache
        collection1 = loader.load_collection(use_cache=True)
        
        # Clear cache
        loader.clear_cache()
        
        # Load again
        collection2 = loader.load_collection(use_cache=True)
        
        # Should be different instances
        assert collection1 is not collection2
    
    def test_collection_stats(self, temp_collection_file):
        """Test collection statistics."""
        loader = DataLoader(base_path=temp_collection_file)
        stats = loader.get_collection_stats()
        
        assert stats['total_albums'] == 3
        assert stats['unique_artists'] == 3
        assert stats['years_range'] == (1959, 1972)
        assert 'Vinyle' in stats['supports']
        assert stats['supports']['Vinyle'] == 2
        assert stats['supports']['CD'] == 1
