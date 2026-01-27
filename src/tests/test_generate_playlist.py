"""
Tests unitaires pour le module generate-playlist.py

Ce module teste les fonctionnalités de génération de playlists,
notamment la détection et suppression de doublons.

Version: 1.0.0
Date: 27 janvier 2026
Auteur: Patrick Ostertag
"""

import pytest
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
PROJECT_ROOT = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, PROJECT_ROOT)

# Import direct depuis le fichier 
import importlib.util
spec = importlib.util.spec_from_file_location(
    "generate_playlist",
    os.path.join(PROJECT_ROOT, "src", "analysis", "generate-playlist.py")
)
generate_playlist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_playlist)

remove_duplicate_tracks = generate_playlist.remove_duplicate_tracks


class TestRemoveDuplicateTracks:
    """Tests pour la fonction remove_duplicate_tracks."""
    
    def test_no_duplicates(self):
        """Test avec des pistes uniques - aucun doublon à supprimer."""
        tracks = [
            {'artist': 'The Clash', 'title': 'London Calling', 'album': 'London Calling'},
            {'artist': 'Roxy Music', 'title': 'Love Is the Drug', 'album': 'Best Of'},
            {'artist': 'David Bowie', 'title': "Let's Dance", 'album': "Let's Dance"},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 3
        assert result == tracks
    
    def test_exact_duplicates(self):
        """Test avec des doublons exacts."""
        tracks = [
            {'artist': 'The Clash', 'title': 'London Calling', 'album': 'London Calling'},
            {'artist': 'The Clash', 'title': 'London Calling', 'album': 'London Calling'},
            {'artist': 'Roxy Music', 'title': 'Love Is the Drug', 'album': 'Best Of'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 2
        assert result[0]['artist'] == 'The Clash'
        assert result[1]['artist'] == 'Roxy Music'
    
    def test_case_insensitive_duplicates(self):
        """Test avec des doublons différant par la casse."""
        tracks = [
            {'artist': 'The Clash', 'title': 'London Calling (remastered)', 'album': 'London Calling (Remastered)'},
            {'artist': 'The Clash', 'title': 'London Calling (Remastered)', 'album': 'London Calling (Remastered)'},
            {'artist': 'Roxy Music', 'title': 'Love Is the Drug', 'album': 'Best Of'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 2
        assert result[0]['artist'] == 'The Clash'
        assert result[1]['artist'] == 'Roxy Music'
    
    def test_minor_variation_duplicates(self):
        """Test avec des doublons ayant des variations mineures."""
        tracks = [
            {'artist': 'Roxy Music', 'title': 'Love Is the Drug', 'album': 'The Best Of Roxy Music'},
            {'artist': 'Roxy Music', 'title': 'Love Is The Drug', 'album': 'The Best Of Roxy Music'},
            {'artist': 'David Bowie', 'title': "Let's Dance (2018 Remaster)", 'album': "Let's Dance (2018 remaster)"},
            {'artist': 'David Bowie', 'title': "Let's Dance (2018 Remaster)", 'album': "Let's Dance (2018 Remaster)"},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 2
        assert result[0]['artist'] == 'Roxy Music'
        assert result[1]['artist'] == 'David Bowie'
    
    def test_preserves_order(self):
        """Test que l'ordre des pistes est préservé."""
        tracks = [
            {'artist': 'Artist A', 'title': 'Track 1', 'album': 'Album 1'},
            {'artist': 'Artist B', 'title': 'Track 2', 'album': 'Album 2'},
            {'artist': 'Artist A', 'title': 'Track 1', 'album': 'Album 1'},  # doublon
            {'artist': 'Artist C', 'title': 'Track 3', 'album': 'Album 3'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 3
        assert result[0]['artist'] == 'Artist A'
        assert result[1]['artist'] == 'Artist B'
        assert result[2]['artist'] == 'Artist C'
    
    def test_keeps_first_occurrence(self):
        """Test que c'est la première occurrence qui est conservée."""
        tracks = [
            {'artist': 'The Clash', 'title': 'London Calling (remastered)', 'album': 'Album 1', 'timestamp': 1},
            {'artist': 'The Clash', 'title': 'London Calling (Remastered)', 'album': 'Album 1', 'timestamp': 2},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 1
        assert result[0]['timestamp'] == 1  # Garde la première
    
    def test_multiple_duplicates_of_same_track(self):
        """Test avec plusieurs doublons de la même piste."""
        tracks = [
            {'artist': 'The Clash', 'title': 'London Calling', 'album': 'Album 1'},
            {'artist': 'The Clash', 'title': 'LONDON CALLING', 'album': 'Album 1'},
            {'artist': 'The Clash', 'title': 'london calling', 'album': 'album 1'},
            {'artist': 'The Clash', 'title': 'London Calling', 'album': 'Album 1'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 1
    
    def test_empty_list(self):
        """Test avec une liste vide."""
        tracks = []
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 0
        assert result == []
    
    def test_single_track(self):
        """Test avec une seule piste."""
        tracks = [
            {'artist': 'The Clash', 'title': 'London Calling', 'album': 'Album 1'},
        ]
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 1
        assert result == tracks
    
    def test_different_albums_same_title(self):
        """Test que des pistes avec le même titre mais albums différents sont conservées."""
        tracks = [
            {'artist': 'The Beatles', 'title': 'Yesterday', 'album': 'Help!'},
            {'artist': 'The Beatles', 'title': 'Yesterday', 'album': 'Greatest Hits'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 2  # Devrait garder les deux car albums différents
    
    def test_different_artists_same_title(self):
        """Test que des pistes avec le même titre mais artistes différents sont conservées."""
        tracks = [
            {'artist': 'Frank Sinatra', 'title': 'My Way', 'album': 'Album 1'},
            {'artist': 'Elvis Presley', 'title': 'My Way', 'album': 'Album 2'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 2  # Devrait garder les deux car artistes différents
    
    def test_whitespace_normalization(self):
        """Test que les espaces multiples sont normalisés."""
        tracks = [
            {'artist': 'The  Clash', 'title': 'London  Calling', 'album': 'Album 1'},
            {'artist': 'The Clash', 'title': 'London Calling', 'album': 'Album 1'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        assert len(result) == 1
    
    def test_issue_38_examples(self):
        """Test avec les exemples réels du problème GitHub Issue #38."""
        tracks = [
            {'artist': 'The Clash', 'title': 'London Calling (remastered)', 'album': 'London Calling (Remastered)', 
             'album_spotify_image': 'https://i.scdn.co/image/ab67616d0000b273628103d0e62602f00408345d'},
            {'artist': 'The Clash', 'title': 'London Calling (Remastered)', 'album': 'London Calling (Remastered)',
             'album_spotify_image': 'https://i.scdn.co/image/ab67616d0000b273628103d0e62602f00408345d'},
            {'artist': 'Roxy Music', 'title': 'Love Is the Drug', 'album': 'The Best Of Roxy Music',
             'album_spotify_image': 'https://i.scdn.co/image/ab67616d0000b273cdd6f71f3d22476a9a1319cd'},
            {'artist': 'Roxy Music', 'title': 'Love Is The Drug', 'album': 'The Best Of Roxy Music',
             'album_spotify_image': 'https://i.scdn.co/image/ab67616d0000b273cdd6f71f3d22476a9a1319cd'},
            {'artist': 'David Bowie', 'title': "Let's Dance (2018 Remaster)", 'album': "Let's Dance (2018 remaster)",
             'album_spotify_image': 'https://i.scdn.co/image/ab67616d0000b27300ee30a26080e72795649b35'},
            {'artist': 'David Bowie', 'title': "Let's Dance (2018 Remaster)", 'album': "Let's Dance (2018 Remaster)",
             'album_spotify_image': 'https://i.scdn.co/image/ab67616d0000b27300ee30a26080e72795649b35'},
        ]
        
        result = remove_duplicate_tracks(tracks)
        
        # Devrait avoir exactement 3 pistes uniques (une par artiste)
        assert len(result) == 3
        
        # Vérifier que chaque artiste apparaît une seule fois
        artists = [track['artist'] for track in result]
        assert 'The Clash' in artists
        assert 'Roxy Music' in artists
        assert 'David Bowie' in artists
        assert len(set(artists)) == 3
