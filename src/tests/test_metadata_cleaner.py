"""Tests unitaires pour le module metadata_cleaner.

Ces tests vérifient le bon fonctionnement des fonctions de nettoyage
et de normalisation des métadonnées musicales.

Version: 1.0.0
Date: 24 janvier 2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.metadata_cleaner import (
    clean_artist_name,
    clean_album_name,
    nettoyer_nom_artiste,
    normalize_string_for_comparison,
    artist_matches,
    calculate_album_match_score
)


class TestCleanArtistName:
    """Tests pour la fonction clean_artist_name."""
    
    def test_simple_artist(self):
        """Test avec un nom d'artiste simple."""
        assert clean_artist_name("Nina Simone") == "Nina Simone"
    
    def test_multiple_artists_with_slash(self):
        """Test avec plusieurs artistes séparés par /."""
        assert clean_artist_name("Dalida / Raymond Lefèvre") == "Dalida"
        assert clean_artist_name("Bob Dylan / Joan Baez") == "Bob Dylan"
    
    def test_artist_with_parentheses(self):
        """Test avec métadonnées entre parenthèses."""
        assert clean_artist_name("Nina Simone (Live Version)") == "Nina Simone"
        assert clean_artist_name("The Beatles (Remastered)") == "The Beatles"
    
    def test_inconnu(self):
        """Test avec artiste inconnu."""
        assert clean_artist_name("Inconnu") == "Inconnu"
        assert clean_artist_name("") == ""
    
    def test_complex_case(self):
        """Test avec cas complexe (slash + parenthèses)."""
        result = clean_artist_name("Eros Ramazzotti / Tina Turner (Live at Wembley)")
        assert result == "Eros Ramazzotti"


class TestCleanAlbumName:
    """Tests pour la fonction clean_album_name."""
    
    def test_simple_album(self):
        """Test avec un nom d'album simple."""
        assert clean_album_name("Dark Side of the Moon") == "Dark Side of the Moon"
    
    def test_album_with_parentheses(self):
        """Test avec informations entre parenthèses."""
        assert clean_album_name("Circlesongs (Voice)") == "Circlesongs"
        assert clean_album_name("Greatest Hits (Remastered Edition)") == "Greatest Hits"
    
    def test_album_with_brackets(self):
        """Test avec informations entre crochets."""
        assert clean_album_name("9 [Italian]") == "9"
        assert clean_album_name("Album Title [2020 Reissue]") == "Album Title"
    
    def test_inconnu(self):
        """Test avec album inconnu."""
        assert clean_album_name("Inconnu") == "Inconnu"
        assert clean_album_name("") == ""


class TestNettoyerNomArtiste:
    """Tests pour la fonction nettoyer_nom_artiste (spécifique Discogs)."""
    
    def test_string_input(self):
        """Test avec entrée string."""
        assert nettoyer_nom_artiste("Nina Simone") == "Nina Simone"
    
    def test_list_input(self):
        """Test avec entrée liste (format Discogs)."""
        assert nettoyer_nom_artiste(["Nina Simone"]) == "Nina Simone"
        assert nettoyer_nom_artiste(["The Beatles", "George Martin"]) == "The Beatles"
    
    def test_numeric_suffix(self):
        """Test avec suffixe numérique (format Discogs)."""
        assert nettoyer_nom_artiste("Various (5)") == "Various"
        assert nettoyer_nom_artiste("The Beatles (2)") == "The Beatles"
    
    def test_empty_list(self):
        """Test avec liste vide."""
        assert nettoyer_nom_artiste([]) == ""


class TestNormalizeStringForComparison:
    """Tests pour la fonction normalize_string_for_comparison."""
    
    def test_lowercase(self):
        """Test conversion en minuscules."""
        assert normalize_string_for_comparison("NINA SIMONE") == "nina simone"
        assert normalize_string_for_comparison("The Beatles") == "the beatles"
    
    def test_multiple_spaces(self):
        """Test suppression espaces multiples."""
        assert normalize_string_for_comparison("  Nina  Simone  ") == "nina simone"
    
    def test_leading_trailing_spaces(self):
        """Test suppression espaces de début/fin."""
        assert normalize_string_for_comparison("  The Beatles  ") == "the beatles"


class TestArtistMatches:
    """Tests pour la fonction artist_matches."""
    
    def test_exact_match(self):
        """Test correspondance exacte."""
        assert artist_matches("Nina Simone", "Nina Simone") is True
    
    def test_case_insensitive(self):
        """Test insensibilité à la casse."""
        assert artist_matches("Nina Simone", "nina simone") is True
        assert artist_matches("THE BEATLES", "the beatles") is True
    
    def test_various_artists(self):
        """Test cas spécial Various Artists."""
        assert artist_matches("Various", "Various Artists") is True
        assert artist_matches("Various Artists", "Various") is True
    
    def test_substring_match(self):
        """Test correspondance par sous-chaîne."""
        assert artist_matches("The Beatles", "Beatles") is True
        assert artist_matches("Beatles", "The Beatles") is True
    
    def test_no_match(self):
        """Test absence de correspondance."""
        assert artist_matches("Eros Ramazzotti", "Madonna") is False
        assert artist_matches("Nina Simone", "Aretha Franklin") is False


class TestCalculateAlbumMatchScore:
    """Tests pour la fonction calculate_album_match_score."""
    
    def test_exact_match(self):
        """Test correspondance exacte = 100 points."""
        score = calculate_album_match_score("Dark Side of the Moon", "Dark Side of the Moon")
        assert score == 100
    
    def test_case_insensitive_exact(self):
        """Test exacte insensible à la casse."""
        score = calculate_album_match_score("DARK SIDE", "dark side")
        assert score == 100
    
    def test_contains_match(self):
        """Test correspondance par contenance = 80 points."""
        score = calculate_album_match_score("Dark Side", "Dark Side of the Moon")
        assert score == 80
        score = calculate_album_match_score("Moon", "Dark Side of the Moon")
        assert score == 80
    
    def test_partial_match(self):
        """Test correspondance partielle = 50 points max."""
        score = calculate_album_match_score("Dark Moon", "Dark Side of the Moon")
        assert 50 <= score <= 80  # Au moins 2 mots sur 5 en commun
    
    def test_no_match(self):
        """Test absence de correspondance = 0 points."""
        score = calculate_album_match_score("Abbey Road", "Dark Side of the Moon")
        assert score == 0
    
    def test_empty_strings(self):
        """Test avec chaînes vides."""
        score = calculate_album_match_score("", "Dark Side")
        assert score == 0
        score = calculate_album_match_score("Dark Side", "")
        assert score == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
