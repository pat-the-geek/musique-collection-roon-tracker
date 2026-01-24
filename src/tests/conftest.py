"""Configuration pytest pour les tests du projet Musique Tracker.

Ce fichier configure pytest avec des fixtures communes et des options par défaut.

Version: 1.0.0
Date: 24 janvier 2026
"""

import sys
import os
import pytest

# Ajouter le répertoire src au path pour permettre les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def sample_artist_names():
    """Fixture fournissant des exemples de noms d'artistes."""
    return {
        'simple': 'Nina Simone',
        'multiple': 'Dalida / Raymond Lefèvre',
        'with_meta': 'Nina Simone (Live Version)',
        'inconnu': 'Inconnu',
        'various': 'Various (5)'
    }


@pytest.fixture
def sample_album_names():
    """Fixture fournissant des exemples de noms d'albums."""
    return {
        'simple': 'Dark Side of the Moon',
        'with_parentheses': 'Circlesongs (Voice)',
        'with_brackets': '9 [Italian]',
        'remastered': 'Greatest Hits (Remastered Edition)',
        'inconnu': 'Inconnu'
    }


@pytest.fixture
def mock_spotify_token():
    """Fixture fournissant un faux token Spotify pour les tests."""
    return "BQC1234567890ABCDEF_mock_token_for_testing"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture configurant des variables d'environnement de test."""
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("API_KEY", "test_lastfm_key")
    monkeypatch.setenv("API_SECRET", "test_lastfm_secret")
    monkeypatch.setenv("LASTFM_USERNAME", "test_user")


# Configuration des options pytest par défaut
def pytest_configure(config):
    """Configure pytest avec des marqueurs personnalisés."""
    config.addinivalue_line(
        "markers", "unit: marque un test comme test unitaire"
    )
    config.addinivalue_line(
        "markers", "integration: marque un test comme test d'intégration"
    )
    config.addinivalue_line(
        "markers", "slow: marque un test comme lent (nécessite APIs réelles)"
    )
