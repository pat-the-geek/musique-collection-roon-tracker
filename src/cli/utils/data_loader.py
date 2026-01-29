"""
Data Loading Utilities for CLI

Handles loading and caching of JSON data files (collection, history, etc.)

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 29 janvier 2026
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class DataLoader:
    """
    Data loader with caching for JSON files.
    
    Provides lazy loading and caching of data files to minimize I/O operations.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize data loader.
        
        Args:
            base_path: Base path for data files (default: project root)
        """
        if base_path is None:
            # Assume we're in src/cli/utils, go up 3 levels to project root
            base_path = Path(__file__).parent.parent.parent.parent
        
        self.base_path = Path(base_path)
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def _get_data_path(self, data_type: str) -> Path:
        """
        Get the path for a specific data type.
        
        Args:
            data_type: Type of data ('collection', 'history', 'soundtrack', 'config')
            
        Returns:
            Path to the data file
        """
        paths = {
            'collection': self.base_path / 'data' / 'collection' / 'discogs-collection.json',
            'history': self.base_path / 'data' / 'history' / 'chk-roon.json',
            'soundtrack': self.base_path / 'data' / 'collection' / 'soundtrack.json',
            'config': self.base_path / 'data' / 'config' / 'roon-config.json',
        }
        
        return paths.get(data_type)
    
    def load_json(self, path: Path, use_cache: bool = True) -> Optional[Any]:
        """
        Load JSON file with optional caching.
        
        Args:
            path: Path to JSON file
            use_cache: Use cached version if available
            
        Returns:
            Parsed JSON data or None if file not found/invalid
        """
        path = Path(path)
        cache_key = str(path)
        
        # Check cache
        if use_cache and cache_key in self._cache:
            # Check if file has been modified
            if path.exists():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime <= self._cache_timestamps.get(cache_key, datetime.min):
                    return self._cache[cache_key]
        
        # Load file
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update cache
            if use_cache:
                self._cache[cache_key] = data
                self._cache_timestamps[cache_key] = datetime.fromtimestamp(path.stat().st_mtime)
            
            return data
        except (json.JSONDecodeError, IOError) as e:
            # Return None on error (graceful degradation)
            return None
    
    def load_collection(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Load Discogs collection.
        
        Args:
            use_cache: Use cached version if available
            
        Returns:
            List of albums or empty list if not found
        """
        path = self._get_data_path('collection')
        data = self.load_json(path, use_cache)
        return data if isinstance(data, list) else []
    
    def load_history(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Load listening history (Roon/Last.fm).
        
        Args:
            use_cache: Use cached version if available
            
        Returns:
            List of tracks or empty list if not found
        """
        path = self._get_data_path('history')
        data = self.load_json(path, use_cache)
        return data if isinstance(data, list) else []
    
    def load_soundtrack(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Load soundtrack mapping.
        
        Args:
            use_cache: Use cached version if available
            
        Returns:
            List of soundtrack mappings or empty list if not found
        """
        path = self._get_data_path('soundtrack')
        data = self.load_json(path, use_cache)
        return data if isinstance(data, list) else []
    
    def load_config(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load configuration.
        
        Args:
            use_cache: Use cached version if available
            
        Returns:
            Configuration dict or empty dict if not found
        """
        path = self._get_data_path('config')
        data = self.load_json(path, use_cache)
        return data if isinstance(data, dict) else {}
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dict with counts and metadata
        """
        collection = self.load_collection()
        
        if not collection:
            return {
                'total_albums': 0,
                'unique_artists': 0,
                'years_range': None,
                'supports': {}
            }
        
        # Calculate stats
        artists = set()
        years = []
        supports = {}
        
        for album in collection:
            # Artists
            artist = album.get('Artiste', [])
            if isinstance(artist, list):
                artists.update(artist)
            else:
                artists.add(str(artist))
            
            # Years
            year = album.get('Annee')
            if year and isinstance(year, int):
                years.append(year)
            
            # Supports
            support = album.get('Support', 'Inconnu')
            supports[support] = supports.get(support, 0) + 1
        
        return {
            'total_albums': len(collection),
            'unique_artists': len(artists),
            'years_range': (min(years), max(years)) if years else None,
            'supports': supports
        }
    
    def get_history_stats(self) -> Dict[str, Any]:
        """
        Get statistics about listening history.
        
        Returns:
            Dict with counts and metadata
        """
        history = self.load_history()
        
        if not history:
            return {
                'total_tracks': 0,
                'unique_artists': 0,
                'unique_albums': 0,
                'sources': {},
                'loved_count': 0
            }
        
        # Calculate stats
        artists = set()
        albums = set()
        sources = {}
        loved_count = 0
        
        for track in history:
            # Artists
            artist = track.get('artist')
            if artist:
                artists.add(artist)
            
            # Albums
            album = track.get('album')
            if album:
                albums.add(album)
            
            # Sources
            source = track.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
            
            # Loved
            if track.get('loved'):
                loved_count += 1
        
        return {
            'total_tracks': len(history),
            'unique_artists': len(artists),
            'unique_albums': len(albums),
            'sources': sources,
            'loved_count': loved_count
        }


# Global singleton instance for convenience
_loader_instance: Optional[DataLoader] = None


def get_loader() -> DataLoader:
    """
    Get the global DataLoader instance (singleton pattern).
    
    Returns:
        DataLoader instance
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DataLoader()
    return _loader_instance
