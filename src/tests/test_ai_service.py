"""Tests unitaires pour le module ai_service.

Ces tests vérifient toutes les fonctionnalités du service AI EurIA:
- Appels API avec retry automatique
- Génération de descriptions d'albums
- Recherche dans la collection Discogs
- Gestion des erreurs et timeouts

Version: 1.0.0
Date: 27 janvier 2026
"""

import sys
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import requests.exceptions
from services.ai_service import (
    ask_for_ia,
    generate_album_info,
    get_album_info_from_discogs,
    get_euria_config,
    ensure_env_loaded
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_euria_env(monkeypatch):
    """Configure les variables d'environnement EurIA pour les tests."""
    monkeypatch.setenv("URL", "https://api.example.com/test")
    monkeypatch.setenv("bearer", "test_bearer_token_12345")
    monkeypatch.setenv("max_attempts", "3")
    monkeypatch.setenv("default_error_message", "Test error message")


@pytest.fixture
def mock_euria_response():
    """Retourne une réponse EurIA API simulée."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Test AI response content"
                }
            }
        ]
    }


@pytest.fixture
def mock_album_info_response():
    """Retourne une réponse de description d'album simulée."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Kind of Blue, sorti en 1959, est un album majeur du jazz modal."
                }
            }
        ]
    }


@pytest.fixture
def sample_discogs_collection():
    """Retourne un exemple de collection Discogs."""
    return [
        {
            "Titre": "Kind of Blue",
            "Artiste": ["Miles Davis"],
            "Annee": 1959,
            "Resume": "Album emblématique du jazz modal, considéré comme l'un des meilleurs albums de jazz de tous les temps."
        },
        {
            "Titre": "Dark Side of the Moon",
            "Artiste": ["Pink Floyd"],
            "Annee": 1973,
            "Resume": "Aucune information disponible"
        },
        {
            "Titre": "Abbey Road",
            "Artiste": ["The Beatles"],
            "Annee": 1969,
            "Resume": ""
        }
    ]


@pytest.fixture
def temp_discogs_file(tmp_path, sample_discogs_collection):
    """Crée un fichier temporaire de collection Discogs."""
    file_path = tmp_path / "discogs-collection.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_discogs_collection, f, ensure_ascii=False)
    return str(file_path)


# ============================================================================
# Tests pour get_euria_config()
# ============================================================================

class TestGetEuriaConfig:
    """Tests de la fonction get_euria_config."""
    
    def test_config_loaded_from_env(self, mock_euria_env):
        """Teste que la configuration est chargée depuis les variables d'environnement."""
        url, bearer, max_attempts, default_error = get_euria_config()
        
        assert url == "https://api.example.com/test"
        assert bearer == "test_bearer_token_12345"
        assert max_attempts == 3
        assert default_error == "Test error message"
    
    def test_config_default_values(self, monkeypatch):
        """Teste les valeurs par défaut si certaines variables sont absentes."""
        monkeypatch.setenv("URL", "https://api.example.com/test")
        monkeypatch.setenv("bearer", "token")
        # max_attempts et default_error_message absents
        
        url, bearer, max_attempts, default_error = get_euria_config()
        
        assert max_attempts == 5  # Valeur par défaut
        assert default_error == "Aucune information disponible"  # Valeur par défaut


# ============================================================================
# Tests pour ask_for_ia()
# ============================================================================

class TestAskForIA:
    """Tests de la fonction ask_for_ia."""
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_successful(self, mock_post, mock_euria_env, mock_euria_response):
        """Teste un appel API réussi."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_euria_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt")
        
        assert result == "Test AI response content"
        mock_post.assert_called_once()
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_strips_whitespace(self, mock_post, mock_euria_env):
        """Teste que les espaces superflus sont supprimés."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "  Response with spaces  \n"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt")
        
        assert result == "Response with spaces"
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_missing_credentials(self, mock_post, monkeypatch):
        """Teste le comportement avec credentials manquants."""
        # Ne pas définir URL et bearer
        monkeypatch.delenv("URL", raising=False)
        monkeypatch.delenv("bearer", raising=False)
        monkeypatch.setenv("default_error_message", "Error")
        
        result = ask_for_ia("Test prompt")
        
        assert result == "Error"
        mock_post.assert_not_called()
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_timeout_retry(self, mock_post, mock_euria_env, mock_euria_response):
        """Teste le retry automatique sur timeout."""
        # Premier appel: timeout, deuxième: succès
        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout"),
            MagicMock(json=lambda: mock_euria_response, raise_for_status=lambda: None)
        ]
        
        result = ask_for_ia("Test prompt", max_attempts=2)
        
        assert result == "Test AI response content"
        assert mock_post.call_count == 2
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_network_error_retry(self, mock_post, mock_euria_env):
        """Teste le retry sur erreur réseau."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        result = ask_for_ia("Test prompt", max_attempts=2)
        
        assert result == "Test error message"  # Message d'erreur par défaut
        assert mock_post.call_count == 2
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_invalid_json_response(self, mock_post, mock_euria_env):
        """Teste la gestion d'une réponse JSON invalide."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt", max_attempts=2)
        
        assert result == "Test error message"
        assert mock_post.call_count == 2
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_missing_choices_field(self, mock_post, mock_euria_env):
        """Teste la gestion d'une réponse sans champ 'choices'."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "No choices"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt", max_attempts=2)
        
        assert result == "Test error message"
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_custom_timeout(self, mock_post, mock_euria_env, mock_euria_response):
        """Teste l'utilisation d'un timeout personnalisé."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_euria_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt", timeout=30)
        
        assert result == "Test AI response content"
        # Vérifier que le timeout est passé à requests.post
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['timeout'] == 30
    
    @patch('services.ai_service.requests.post')
    @patch('services.ai_service.time.sleep')
    def test_ask_for_ia_retry_delay(self, mock_sleep, mock_post, mock_euria_env, mock_euria_response):
        """Teste qu'il y a un délai entre les tentatives."""
        # Premier appel: erreur, deuxième: succès
        mock_post.side_effect = [
            requests.exceptions.RequestException("Error"),
            MagicMock(json=lambda: mock_euria_response, raise_for_status=lambda: None)
        ]
        
        result = ask_for_ia("Test prompt", max_attempts=2)
        
        assert result == "Test AI response content"
        mock_sleep.assert_called_once_with(2)
    
    @patch('services.ai_service.requests.post')
    def test_ask_for_ia_web_search_enabled(self, mock_post, mock_euria_env, mock_euria_response):
        """Teste que la recherche web est activée dans la requête."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_euria_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt")
        
        # Vérifier que enable_web_search est True dans les données
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['json']['enable_web_search'] is True


# ============================================================================
# Tests pour generate_album_info()
# ============================================================================

class TestGenerateAlbumInfo:
    """Tests de la fonction generate_album_info."""
    
    @patch('services.ai_service.ask_for_ia')
    def test_generate_album_info_successful(self, mock_ask_for_ia):
        """Teste la génération d'info d'album réussie."""
        mock_ask_for_ia.return_value = "Kind of Blue est un album majeur du jazz modal."
        
        result = generate_album_info("Miles Davis", "Kind of Blue")
        
        assert result == "Kind of Blue est un album majeur du jazz modal."
        mock_ask_for_ia.assert_called_once()
    
    @patch('services.ai_service.ask_for_ia')
    def test_generate_album_info_custom_max_characters(self, mock_ask_for_ia):
        """Teste l'utilisation d'une limite de caractères personnalisée."""
        mock_ask_for_ia.return_value = "Description courte"
        
        result = generate_album_info("Artist", "Album", max_characters=500)
        
        # Vérifier que le prompt contient la limite de caractères
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "500" in call_args
    
    @patch('services.ai_service.ask_for_ia')
    def test_generate_album_info_default_max_characters(self, mock_ask_for_ia):
        """Teste la valeur par défaut de max_characters."""
        mock_ask_for_ia.return_value = "Description"
        
        result = generate_album_info("Artist", "Album")
        
        # Vérifier que le prompt contient la valeur par défaut
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "2000" in call_args
    
    @patch('services.ai_service.ask_for_ia')
    def test_generate_album_info_unknown_artist(self, mock_ask_for_ia):
        """Teste la génération avec un artiste inconnu."""
        mock_ask_for_ia.return_value = "Station de radio généraliste"
        
        result = generate_album_info("Inconnu", "Radio Station")
        
        assert "Radio" in result or "Station" in result
    
    @patch('services.ai_service.ask_for_ia')
    def test_generate_album_info_timeout_parameters(self, mock_ask_for_ia):
        """Teste que les paramètres de timeout sont corrects."""
        mock_ask_for_ia.return_value = "Description"
        
        result = generate_album_info("Artist", "Album")
        
        # Vérifier les paramètres d'appel
        call_kwargs = mock_ask_for_ia.call_args[1]
        assert call_kwargs['max_attempts'] == 3
        assert call_kwargs['timeout'] == 45
    
    @patch('services.ai_service.ask_for_ia')
    def test_generate_album_info_error_handling(self, mock_ask_for_ia):
        """Teste la gestion des erreurs."""
        mock_ask_for_ia.return_value = "Désolé, impossible de générer"
        
        result = generate_album_info("Artist", "Album")
        
        assert result == "Désolé, impossible de générer"


# ============================================================================
# Tests pour get_album_info_from_discogs()
# ============================================================================

class TestGetAlbumInfoFromDiscogs:
    """Tests de la fonction get_album_info_from_discogs."""
    
    def test_album_found_with_resume(self, temp_discogs_file):
        """Teste la récupération d'un album avec résumé."""
        result = get_album_info_from_discogs("Kind of Blue", temp_discogs_file)
        
        assert result is not None
        assert "jazz modal" in result
        assert "emblématique" in result
    
    def test_album_not_found(self, temp_discogs_file):
        """Teste la recherche d'un album inexistant."""
        result = get_album_info_from_discogs("Nonexistent Album", temp_discogs_file)
        
        assert result is None
    
    def test_album_found_but_no_resume(self, temp_discogs_file):
        """Teste un album sans résumé valide."""
        result = get_album_info_from_discogs("Dark Side of the Moon", temp_discogs_file)
        
        assert result is None  # "Aucune information disponible" ne devrait pas être retourné
    
    def test_album_found_but_empty_resume(self, temp_discogs_file):
        """Teste un album avec résumé vide."""
        result = get_album_info_from_discogs("Abbey Road", temp_discogs_file)
        
        assert result is None
    
    def test_case_insensitive_search(self, temp_discogs_file):
        """Teste que la recherche est insensible à la casse."""
        result = get_album_info_from_discogs("kind of blue", temp_discogs_file)
        
        assert result is not None
        assert "jazz modal" in result
    
    def test_file_not_found(self):
        """Teste le comportement quand le fichier n'existe pas."""
        result = get_album_info_from_discogs("Album", "/nonexistent/path.json")
        
        assert result is None
    
    def test_invalid_json_file(self, tmp_path):
        """Teste le comportement avec un fichier JSON invalide."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("Invalid JSON content")
        
        result = get_album_info_from_discogs("Album", str(invalid_file))
        
        assert result is None
    
    def test_whitespace_handling(self, temp_discogs_file):
        """Teste que les espaces en trop sont gérés."""
        result = get_album_info_from_discogs("  Kind of Blue  ", temp_discogs_file)
        
        assert result is not None
        assert "jazz modal" in result
    
    def test_empty_collection(self, tmp_path):
        """Teste avec une collection vide."""
        empty_file = tmp_path / "empty.json"
        with open(empty_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        result = get_album_info_from_discogs("Album", str(empty_file))
        
        assert result is None
    
    def test_album_without_titre_field(self, tmp_path):
        """Teste avec un album sans champ Titre."""
        malformed_collection = [
            {
                "Artiste": ["Artist"],
                "Annee": 2000
                # Pas de champ Titre
            }
        ]
        malformed_file = tmp_path / "malformed.json"
        with open(malformed_file, 'w', encoding='utf-8') as f:
            json.dump(malformed_collection, f)
        
        result = get_album_info_from_discogs("Album", str(malformed_file))
        
        assert result is None


# ============================================================================
# Tests d'intégration et cas limites
# ============================================================================

class TestEdgeCasesAndIntegration:
    """Tests de cas limites et d'intégration."""
    
    @patch('services.ai_service.requests.post')
    def test_unicode_handling_in_prompts(self, mock_post, mock_euria_env, mock_euria_response):
        """Teste la gestion des caractères Unicode dans les prompts."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_euria_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Album avec émojis 🎵🎸")
        
        assert result == "Test AI response content"
    
    def test_very_long_album_title(self, temp_discogs_file):
        """Teste avec un titre d'album très long."""
        long_title = "A" * 500
        result = get_album_info_from_discogs(long_title, temp_discogs_file)
        
        assert result is None
    
    @patch('services.ai_service.ask_for_ia')
    def test_generate_album_info_with_special_characters(self, mock_ask_for_ia):
        """Teste la génération avec caractères spéciaux."""
        mock_ask_for_ia.return_value = "Description"
        
        result = generate_album_info("L'artiste", "L'album (Édition spéciale)")
        
        assert result == "Description"
        # Vérifier que les caractères spéciaux sont dans le prompt
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "L'album" in call_args or "album" in call_args
