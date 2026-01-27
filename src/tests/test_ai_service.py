"""Tests unitaires complets pour le module ai_service.

Ces tests vérifient toutes les fonctionnalités du service AI:
- Appel API EurIA avec recherche web
- Génération de résumés d'albums
- Recherche dans la collection Discogs
- Gestion des erreurs et retry logic
- Configuration et variables d'environnement

Version: 2.0.0
Date: 27 janvier 2026
"""

import sys
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock, mock_open
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.ai_service import (
    ensure_env_loaded,
    get_euria_config,
    ask_for_ia,
    generate_album_info,
    get_album_info_from_discogs
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_euria_response():
    """Retourne une réponse EurIA API simulée."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Test response from EurIA API"
                }
            }
        ]
    }


@pytest.fixture
def mock_album_info_response():
    """Retourne une réponse de génération d'info d'album simulée."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Kind of Blue, sorti en 1959, est un album emblématique du jazz modal enregistré par Miles Davis."
                }
            }
        ]
    }


@pytest.fixture
def mock_env_with_euria(monkeypatch):
    """Configure les variables d'environnement EurIA pour les tests."""
    monkeypatch.setenv("URL", "https://api.example.com/v1/chat/completions")
    monkeypatch.setenv("bearer", "test_bearer_token_12345")
    monkeypatch.setenv("max_attempts", "5")
    monkeypatch.setenv("default_error_message", "Aucune information disponible")


@pytest.fixture
def sample_discogs_collection():
    """Retourne un exemple de collection Discogs."""
    return [
        {
            "Titre": "Kind of Blue",
            "Artiste": ["Miles Davis"],
            "Annee": 1959,
            "Resume": "Un album emblématique du jazz modal enregistré par Miles Davis."
        },
        {
            "Titre": "Abbey Road",
            "Artiste": ["The Beatles"],
            "Annee": 1969,
            "Resume": "Le dernier album enregistré par les Beatles."
        },
        {
            "Titre": "Dark Side of the Moon",
            "Artiste": ["Pink Floyd"],
            "Annee": 1973,
            "Resume": ""  # Empty resume to test filtering
        },
        {
            "Titre": "The Wall",
            "Artiste": ["Pink Floyd"],
            "Annee": 1979,
            "Resume": "Aucune information disponible"  # Generic message to test filtering
        }
    ]


# ============================================================================
# Tests pour ensure_env_loaded()
# ============================================================================

class TestEnsureEnvLoaded:
    """Tests de la fonction ensure_env_loaded."""
    
    @patch('services.ai_service.load_dotenv')
    @patch('os.getenv')
    def test_env_already_loaded(self, mock_getenv, mock_load_dotenv):
        """Teste quand l'environnement est déjà chargé."""
        mock_getenv.return_value = "https://api.example.com"
        
        ensure_env_loaded()
        
        # load_dotenv ne devrait pas être appelé
        mock_load_dotenv.assert_not_called()
    
    @patch('services.ai_service.load_dotenv')
    @patch('os.getenv')
    def test_env_not_loaded(self, mock_getenv, mock_load_dotenv):
        """Teste quand l'environnement n'est pas chargé."""
        mock_getenv.return_value = None
        
        ensure_env_loaded()
        
        # load_dotenv devrait être appelé avec le bon chemin
        mock_load_dotenv.assert_called_once()


# ============================================================================
# Tests pour get_euria_config()
# ============================================================================

class TestGetEuriaConfig:
    """Tests de la fonction get_euria_config."""
    
    def test_config_with_all_vars(self, mock_env_with_euria):
        """Teste la récupération de la configuration complète."""
        url, bearer, max_attempts, default_error = get_euria_config()
        
        assert url == "https://api.example.com/v1/chat/completions"
        assert bearer == "test_bearer_token_12345"
        assert max_attempts == 5
        assert default_error == "Aucune information disponible"
    
    @patch('os.getenv')
    def test_config_with_default_values(self, mock_getenv):
        """Teste les valeurs par défaut."""
        def getenv_side_effect(key, default=None):
            if key == "URL":
                return "https://test.com"
            elif key == "bearer":
                return "test_token"
            elif key == "max_attempts":
                return default
            elif key == "default_error_message":
                return default
            return default
        
        mock_getenv.side_effect = getenv_side_effect
        
        url, bearer, max_attempts, default_error = get_euria_config()
        
        assert url == "https://test.com"
        assert bearer == "test_token"
        assert max_attempts == 5  # Default value
        assert default_error == "Aucune information disponible"  # Default value


# ============================================================================
# Tests pour ask_for_ia()
# ============================================================================

class TestAskForIa:
    """Tests de la fonction ask_for_ia."""
    
    @patch('requests.post')
    def test_successful_api_call(self, mock_post, mock_env_with_euria, mock_euria_response):
        """Teste un appel API réussi."""
        mock_response = Mock()
        mock_response.json.return_value = mock_euria_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt")
        
        assert result == "Test response from EurIA API"
        mock_post.assert_called_once()
        
        # Vérifier les paramètres de l'appel
        call_args = mock_post.call_args
        assert call_args[1]['json']['messages'][0]['content'] == "Test prompt"
        assert call_args[1]['json']['model'] == "qwen3"
        assert call_args[1]['json']['enable_web_search'] is True
    
    @patch('requests.post')
    def test_api_call_with_whitespace_stripping(self, mock_post, mock_env_with_euria):
        """Teste le nettoyage des espaces superflus dans la réponse."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "  Response with spaces  \n"
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt")
        
        assert result == "Response with spaces"
    
    @patch('requests.post')
    def test_missing_url_config(self, mock_post, monkeypatch):
        """Teste avec URL manquante."""
        monkeypatch.setenv("URL", "")
        monkeypatch.setenv("bearer", "test_token")
        monkeypatch.setenv("default_error_message", "Error message")
        
        result = ask_for_ia("Test prompt")
        
        assert result == "Error message"
        mock_post.assert_not_called()
    
    @patch('requests.post')
    def test_missing_bearer_config(self, mock_post, monkeypatch):
        """Teste avec bearer token manquant."""
        monkeypatch.setenv("URL", "https://test.com")
        monkeypatch.setenv("bearer", "")
        monkeypatch.setenv("default_error_message", "Error message")
        
        result = ask_for_ia("Test prompt")
        
        assert result == "Error message"
        mock_post.assert_not_called()
    
    @patch('requests.post')
    @patch('time.sleep')
    def test_timeout_retry(self, mock_sleep, mock_post, mock_env_with_euria):
        """Teste le retry en cas de timeout."""
        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout error"),
            requests.exceptions.Timeout("Timeout error"),
            Mock(json=lambda: {"choices": [{"message": {"content": "Success"}}]}, raise_for_status=Mock())
        ]
        
        result = ask_for_ia("Test prompt", max_attempts=3)
        
        assert result == "Success"
        assert mock_post.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep between retries
    
    @patch('requests.post')
    @patch('time.sleep')
    def test_network_error_retry(self, mock_sleep, mock_post, mock_env_with_euria):
        """Teste le retry en cas d'erreur réseau."""
        mock_post.side_effect = [
            requests.exceptions.RequestException("Network error"),
            Mock(json=lambda: {"choices": [{"message": {"content": "Success"}}]}, raise_for_status=Mock())
        ]
        
        result = ask_for_ia("Test prompt", max_attempts=2)
        
        assert result == "Success"
        assert mock_post.call_count == 2
    
    @patch('requests.post')
    @patch('time.sleep')
    def test_all_retries_exhausted(self, mock_sleep, mock_post, mock_env_with_euria):
        """Teste quand toutes les tentatives échouent."""
        mock_post.side_effect = requests.exceptions.Timeout("Persistent timeout")
        
        result = ask_for_ia("Test prompt", max_attempts=3)
        
        assert result == "Aucune information disponible"
        assert mock_post.call_count == 3
    
    @patch('requests.post')
    def test_invalid_response_format(self, mock_post, mock_env_with_euria):
        """Teste avec une réponse JSON invalide."""
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "format"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt", max_attempts=1)
        
        assert result == "Aucune information disponible"
    
    @patch('requests.post')
    def test_empty_choices_array(self, mock_post, mock_env_with_euria):
        """Teste avec un tableau choices vide."""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt", max_attempts=1)
        
        assert result == "Aucune information disponible"
    
    @patch('requests.post')
    def test_custom_timeout(self, mock_post, mock_env_with_euria, mock_euria_response):
        """Teste avec un timeout personnalisé."""
        mock_response = Mock()
        mock_response.json.return_value = mock_euria_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = ask_for_ia("Test prompt", timeout=120)
        
        assert result == "Test response from EurIA API"
        # Vérifier que le timeout est passé à requests.post
        call_args = mock_post.call_args
        assert call_args[1]['timeout'] == 120


# ============================================================================
# Tests pour generate_album_info()
# ============================================================================

class TestGenerateAlbumInfo:
    """Tests de la fonction generate_album_info."""
    
    @patch('services.ai_service.ask_for_ia')
    def test_successful_generation(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste une génération réussie d'information d'album."""
        mock_ask_for_ia.return_value = "Album description in French"
        
        result = generate_album_info("Miles Davis", "Kind of Blue")
        
        assert result == "Album description in French"
        mock_ask_for_ia.assert_called_once()
        
        # Vérifier que le prompt contient l'artiste et l'album
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "Miles Davis" in call_args
        assert "Kind of Blue" in call_args
    
    @patch('services.ai_service.ask_for_ia')
    def test_custom_max_characters(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste avec une limite de caractères personnalisée."""
        mock_ask_for_ia.return_value = "Short description"
        
        result = generate_album_info("Artist", "Album", max_characters=500)
        
        assert result == "Short description"
        
        # Vérifier que la limite est dans le prompt
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "500" in call_args
    
    @patch('services.ai_service.ask_for_ia')
    def test_default_max_characters(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste la limite de caractères par défaut."""
        mock_ask_for_ia.return_value = "Description"
        
        generate_album_info("Artist", "Album")
        
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "2000" in call_args  # Default value
    
    @patch('services.ai_service.ask_for_ia')
    def test_radio_station_handling(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste avec une station de radio."""
        mock_ask_for_ia.return_value = "Description of radio content"
        
        result = generate_album_info("Radio Station", "Live Broadcast")
        
        assert result == "Description of radio content"
        # Le prompt devrait mentionner les stations de radio
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "radio" in call_args.lower()
    
    @patch('services.ai_service.ask_for_ia')
    def test_unknown_artist_handling(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste avec un artiste inconnu."""
        mock_ask_for_ia.return_value = "Description of unknown artist"
        
        result = generate_album_info("Inconnu", "Album Title")
        
        assert result == "Description of unknown artist"
        call_args = mock_ask_for_ia.call_args[0][0]
        assert "inconnu" in call_args.lower()
    
    @patch('services.ai_service.ask_for_ia')
    def test_api_failure(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste quand l'API échoue."""
        mock_ask_for_ia.return_value = "Aucune information disponible"
        
        result = generate_album_info("Artist", "Album")
        
        assert result == "Aucune information disponible"
    
    @patch('services.ai_service.ask_for_ia')
    def test_calls_with_correct_parameters(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste que les paramètres corrects sont passés à ask_for_ia."""
        mock_ask_for_ia.return_value = "Response"
        
        generate_album_info("Artist", "Album")
        
        # Vérifier max_attempts et timeout
        call_kwargs = mock_ask_for_ia.call_args[1]
        assert call_kwargs['max_attempts'] == 3
        assert call_kwargs['timeout'] == 45


# ============================================================================
# Tests pour get_album_info_from_discogs()
# ============================================================================

class TestGetAlbumInfoFromDiscogs:
    """Tests de la fonction get_album_info_from_discogs."""
    
    def test_file_not_found(self):
        """Teste quand le fichier Discogs n'existe pas."""
        result = get_album_info_from_discogs("Album Title", "/nonexistent/path.json")
        
        assert result is None
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_album_found_with_resume(self, mock_exists, mock_file, sample_discogs_collection):
        """Teste quand l'album est trouvé avec un résumé."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        
        result = get_album_info_from_discogs("Kind of Blue", "fake_path.json")
        
        assert result == "Un album emblématique du jazz modal enregistré par Miles Davis."
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_album_not_found(self, mock_exists, mock_file, sample_discogs_collection):
        """Teste quand l'album n'est pas dans la collection."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        
        result = get_album_info_from_discogs("Nonexistent Album", "fake_path.json")
        
        assert result is None
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_case_insensitive_search(self, mock_exists, mock_file, sample_discogs_collection):
        """Teste la recherche insensible à la casse."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        
        result = get_album_info_from_discogs("kind of blue", "fake_path.json")
        
        assert result is not None
        assert "Miles Davis" in result
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_whitespace_handling(self, mock_exists, mock_file, sample_discogs_collection):
        """Teste la gestion des espaces."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        
        result = get_album_info_from_discogs("  Kind of Blue  ", "fake_path.json")
        
        assert result is not None
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_empty_resume_filtered(self, mock_exists, mock_file, sample_discogs_collection):
        """Teste que les résumés vides sont filtrés."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        
        result = get_album_info_from_discogs("Dark Side of the Moon", "fake_path.json")
        
        assert result is None
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_generic_message_filtered(self, mock_exists, mock_file, sample_discogs_collection):
        """Teste que les messages génériques sont filtrés."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        
        result = get_album_info_from_discogs("The Wall", "fake_path.json")
        
        assert result is None
    
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_json_decode_error(self, mock_exists, mock_file):
        """Teste la gestion d'une erreur JSON."""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = "Invalid JSON"
        
        result = get_album_info_from_discogs("Album", "fake_path.json")
        
        assert result is None
    
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_file_read_error(self, mock_exists, mock_file):
        """Teste la gestion d'une erreur de lecture."""
        mock_exists.return_value = True
        mock_file.side_effect = IOError("Cannot read file")
        
        result = get_album_info_from_discogs("Album", "fake_path.json")
        
        assert result is None
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_album_without_resume_field(self, mock_exists, mock_file):
        """Teste un album sans champ Resume."""
        mock_exists.return_value = True
        collection = [{"Titre": "Test Album", "Artiste": ["Test"]}]
        mock_file.return_value.read.return_value = json.dumps(collection)
        
        result = get_album_info_from_discogs("Test Album", "fake_path.json")
        
        assert result is None


# ============================================================================
# Tests d'intégration
# ============================================================================

class TestIntegrationScenarios:
    """Tests de scénarios d'intégration."""
    
    @patch('services.ai_service.ask_for_ia')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_discogs_fallback_to_api(self, mock_exists, mock_file, mock_ask_for_ia, 
                                     sample_discogs_collection, mock_env_with_euria):
        """Teste le fallback de Discogs vers l'API."""
        # Discogs n'a pas l'album
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        mock_ask_for_ia.return_value = "Generated description"
        
        # D'abord, chercher dans Discogs (non trouvé)
        discogs_result = get_album_info_from_discogs("Unknown Album", "fake_path.json")
        assert discogs_result is None
        
        # Ensuite, générer via API
        api_result = generate_album_info("Artist", "Unknown Album")
        assert api_result == "Generated description"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_discogs_hit_no_api_call(self, mock_exists, mock_file, sample_discogs_collection):
        """Teste qu'aucun appel API n'est fait si Discogs a le résumé."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_discogs_collection)
        
        # Chercher dans Discogs (trouvé)
        result = get_album_info_from_discogs("Kind of Blue", "fake_path.json")
        
        assert result is not None
        assert "Miles Davis" in result
        # Pas d'appel API nécessaire


# ============================================================================
# Tests des edge cases
# ============================================================================

class TestEdgeCases:
    """Tests des cas limites."""
    
    @patch('services.ai_service.ask_for_ia')
    def test_unicode_characters(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste avec des caractères Unicode."""
        mock_ask_for_ia.return_value = "Description en français avec accents"
        
        result = generate_album_info("Serge Gainsbourg", "L'Homme à tête de chou")
        
        assert "français" in result
    
    @patch('services.ai_service.ask_for_ia')
    def test_very_long_album_name(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste avec un titre d'album très long."""
        long_name = "A" * 500
        mock_ask_for_ia.return_value = "Description"
        
        result = generate_album_info("Artist", long_name)
        
        assert result == "Description"
        call_args = mock_ask_for_ia.call_args[0][0]
        assert long_name in call_args
    
    @patch('services.ai_service.ask_for_ia')
    def test_special_characters_in_prompt(self, mock_ask_for_ia, mock_env_with_euria):
        """Teste avec des caractères spéciaux."""
        mock_ask_for_ia.return_value = "Description"
        
        result = generate_album_info("AC/DC", "Back in Black (Remastered)")
        
        assert result == "Description"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_empty_discogs_collection(self, mock_exists, mock_file):
        """Teste avec une collection Discogs vide."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps([])
        
        result = get_album_info_from_discogs("Any Album", "fake_path.json")
        
        assert result is None
