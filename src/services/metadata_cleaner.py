"""Module de nettoyage et normalisation des métadonnées musicales.

Ce module fournit des fonctions pour nettoyer et normaliser les noms d'artistes
et d'albums provenant de diverses sources (Roon, Last.fm, Discogs) afin d'améliorer
la qualité des recherches API et la correspondance des données.

Fonctionnalités:
- Nettoyage des noms d'artistes (suppression métadonnées, gestion multi-artistes)
- Nettoyage des noms d'albums (suppression annotations, formats)
- Normalisation pour comparaisons (minuscules, espaces)
- Validation de correspondance d'artistes avec tolérance

Version: 1.0.0
Date: 24 janvier 2026
Auteur: Patrick Ostertag
"""

import re
from typing import Optional


def clean_artist_name(artist_name: str) -> str:
    """Nettoie et normalise le nom d'un artiste pour améliorer les recherches.
    
    Cette fonction traite les cas courants de métadonnées incluant plusieurs
    artistes séparés par des slashes ou des informations additionnelles entre parenthèses.
    
    Args:
        artist_name: Nom brut de l'artiste tel que fourni par les APIs.
        
    Returns:
        Nom d'artiste nettoyé et normalisé.
        
    Examples:
        >>> clean_artist_name("Dalida / Raymond Lefèvre")
        'Dalida'
        >>> clean_artist_name("Nina Simone (Live Version)")
        'Nina Simone'
        >>> clean_artist_name("Inconnu")
        'Inconnu'
        
    Note:
        - Si plusieurs artistes sont séparés par '/', seul le premier est conservé
        - Les informations entre parenthèses en fin de chaîne sont supprimées
        - Les espaces superflus sont normalisés
    """
    if not artist_name or artist_name == 'Inconnu':
        return artist_name
    
    # Si plusieurs artistes séparés par /, prendre le premier
    if '/' in artist_name:
        artist_name = artist_name.split('/')[0].strip()
    
    # Enlever les métadonnées entre parenthèses à la fin
    artist_name = re.sub(r'\s*\([^)]*\)\s*$', '', artist_name)
    
    return artist_name.strip()


def clean_album_name(album_name: str) -> str:
    """Nettoie et normalise le nom d'un album pour améliorer les recherches.
    
    Supprime les métadonnées additionnelles souvent présentes dans les noms d'albums,
    comme les mentions de format, version, ou année entre parenthèses ou crochets.
    
    Args:
        album_name: Nom brut de l'album tel que fourni par les APIs.
        
    Returns:
        Nom d'album nettoyé et normalisé.
        
    Examples:
        >>> clean_album_name("Circlesongs (Voice)")
        'Circlesongs'
        >>> clean_album_name("9 [Italian]")
        '9'
        >>> clean_album_name("Greatest Hits (Remastered Edition)")
        'Greatest Hits'
        >>> clean_album_name("Inconnu")
        'Inconnu'
        
    Note:
        Les informations entre parenthèses () et crochets [] en fin de chaîne sont supprimées
        pour améliorer la correspondance lors des recherches d'images.
    """
    if not album_name or album_name == 'Inconnu':
        return album_name
    
    # Enlever les métadonnées entre parenthèses () ou crochets [] à la fin
    album_name = re.sub(r'\s*[\(\[][^\)\]]*[\)\]]\s*$', '', album_name)
    
    return album_name.strip()


def nettoyer_nom_artiste(nom_artiste) -> str:
    """Nettoie le nom d'artiste pour usage Discogs (gère format liste et suffixes numériques).
    
    Fonction spécifique pour le nettoyage des données Discogs qui peuvent
    être au format liste ou contenir des suffixes numériques.
    
    Args:
        nom_artiste: Nom d'artiste (str ou list) provenant de Discogs.
        
    Returns:
        Nom d'artiste nettoyé.
        
    Examples:
        >>> nettoyer_nom_artiste(["Nina Simone"])
        'Nina Simone'
        >>> nettoyer_nom_artiste("Various (5)")
        'Various'
        >>> nettoyer_nom_artiste("The Beatles (2)")
        'The Beatles'
    """
    # Gérer le cas où l'artiste est une liste
    if isinstance(nom_artiste, list):
        if len(nom_artiste) == 0:
            return ""
        nom_artiste = nom_artiste[0]
    
    # Supprimer le pattern "(number)" à la fin (ex: "Various (5)" -> "Various")
    nom_artiste = re.sub(r'\s*\(\d+\)$', '', str(nom_artiste))
    
    return nom_artiste.strip()


def normalize_string_for_comparison(s: str) -> str:
    """Normalise une chaîne pour comparaison insensible à la casse.
    
    Args:
        s: Chaîne à normaliser.
        
    Returns:
        Chaîne normalisée (minuscules, espaces multiples supprimés).
        
    Examples:
        >>> normalize_string_for_comparison("  Nina  SIMONE  ")
        'nina simone'
        >>> normalize_string_for_comparison("The Beatles")
        'the beatles'
    """
    return ' '.join(s.lower().strip().split())


def artist_matches(search_artist: str, found_artist: str) -> bool:
    """Vérifie si deux noms d'artistes correspondent (avec tolérance).
    
    Compare deux noms d'artistes avec une tolérance pour gérer:
    - Différences de casse
    - "Various" vs "Various Artists"
    - Sous-chaînes (ex: "The Beatles" contient "Beatles")
    
    Args:
        search_artist: Nom de l'artiste recherché.
        found_artist: Nom de l'artiste trouvé dans les résultats.
        
    Returns:
        True si les artistes correspondent, False sinon.
        
    Examples:
        >>> artist_matches("Nina Simone", "Nina Simone")
        True
        >>> artist_matches("Nina Simone", "nina simone")
        True
        >>> artist_matches("Various", "Various Artists")
        True
        >>> artist_matches("The Beatles", "Beatles")
        True
        >>> artist_matches("Eros Ramazzotti", "Madonna")
        False
    """
    norm_search = normalize_string_for_comparison(search_artist)
    norm_found = normalize_string_for_comparison(found_artist)
    
    # Correspondance exacte
    if norm_search == norm_found:
        return True
    
    # Cas spécial: "Various" = "Various Artists"
    if norm_search.startswith('various') and norm_found.startswith('various'):
        return True
    
    # L'un contient l'autre (pour gérer "The Beatles" vs "Beatles")
    if norm_search in norm_found or norm_found in norm_search:
        return True
    
    return False


def calculate_album_match_score(searched_album: str, found_album: str) -> int:
    """Calcule un score de correspondance entre deux noms d'albums.
    
    Utilise un système de scoring pour évaluer la qualité de correspondance:
    - 100: Correspondance exacte (après normalisation)
    - 80: Un album contient l'autre
    - 50: Correspondance partielle basée sur les mots communs
    - 0: Aucune correspondance
    
    Args:
        searched_album: Nom de l'album recherché.
        found_album: Nom de l'album trouvé.
        
    Returns:
        Score de correspondance (0-100).
        
    Examples:
        >>> calculate_album_match_score("Dark Side of the Moon", "Dark Side of the Moon")
        100
        >>> calculate_album_match_score("Dark Side", "Dark Side of the Moon")
        80
        >>> calculate_album_match_score("Moon", "Dark Side of the Moon")
        80
    """
    norm_search = normalize_string_for_comparison(searched_album)
    norm_found = normalize_string_for_comparison(found_album)
    
    # Gérer les chaînes vides
    if not norm_search or not norm_found:
        return 0
    
    # Correspondance exacte
    if norm_search == norm_found:
        return 100
    
    # Un titre contient l'autre
    if norm_search in norm_found or norm_found in norm_search:
        return 80
    
    # Correspondance partielle basée sur mots communs
    search_words = set(norm_search.split())
    found_words = set(norm_found.split())
    
    if not search_words or not found_words:
        return 0
    
    common_words = search_words & found_words
    if common_words:
        ratio = len(common_words) / max(len(search_words), len(found_words))
        return int(50 * ratio)
    
    return 0
