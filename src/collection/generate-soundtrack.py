#!/usr/bin/env python3
"""Générateur de cross-référence films/soundtracks.

Ce script établit des correspondances entre la collection musicale Discogs et
le catalogue de films pour identifier automatiquement les bandes originales (BOF).
Il effectue une cross-référence entre deux projets distincts (Musique et Cinéma).

Fonctionnalités principales:
    - Chargement de deux sources de données (films et albums)
    - Matching basé sur les titres (OriginalTitle vs Titre album)
    - Enrichissement avec métadonnées TMDB (année, réalisateur)
    - Tri alphabétique avec normalisation des accents
    - Export JSON structuré

Architecture:
    Ce script fait partie de l'écosystème Musique mais dépend du projet Cinéma.
    Il crée un pont entre deux collections indépendantes pour détecter les BOF.
    
    Dépendance externe (hors projet):
    - ../../../Cinéma/catalogue.json (projet DataForIA/Cinéma/)
    - Structure attendue: Array[{OriginalTitle, ProductionYear, TMDB: {realisateur}}]
    
    Dépendance interne (projet Musique):
    - ../../data/collection/discogs-collection.json
    - Structure attendue: Array[{Titre, Artiste, Année, ...}]

Fichiers utilisés:
    Input:
    - ../../../Cinéma/catalogue.json: Catalogue films avec métadonnées TMDB
    - ../../data/collection/discogs-collection.json: Collection musicale Discogs
    
    Output:
    - ../../data/collection/soundtrack.json: Soundtracks détectées avec métadonnées

Algorithme de matching:
    1. Normalisation lowercase de tous les titres
    2. Matching par préfixe: album_title.startswith(film_title)
    3. Exemples:
       - Film "La Môme" → Album "La Môme" ✓
       - Film "The Godfather" → Album "The Godfather (Original Soundtrack)" ✓
       - Film "Blade Runner" → Album "Blade Runner (Vangelis)" ✓

Structure de sortie:
    [
        {
            "film_title": str,      # Titre original du film
            "album_title": str,     # Titre de l'album (lowercase)
            "year": int,            # Année de production du film
            "director": str         # Réalisateur (depuis TMDB)
        }
    ]
    Trié alphabétiquement (normalisation accents avec unicodedata).

Dépendances:
    - json: Lecture/écriture fichiers JSON
    - unicodedata: Normalisation accents pour tri
    - os: Gestion des chemins de fichiers

Dépendances inter-projets:
    ⚠️ ATTENTION: Ce script nécessite que le projet Cinéma soit présent.
    
    Structure attendue des répertoires:
    ```
    Documents/DataForIA/
    ├── Cinéma/
    │   └── catalogue.json        ← REQUIS (source films)
    │
    └── Musique/
        └── src/collection/
            └── generate-soundtrack.py  ← Ce script
    ```
    
    Si le projet Cinéma n'est pas présent ou catalogue.json absent,
    le script échouera avec FileNotFoundError.
    
    Raison de la dépendance:
    - Réutilisation des métadonnées TMDB déjà récupérées (film project)
    - Évite duplication des appels API TMDB
    - Partage de données entre projets pour enrichissement mutuel

Usage:
    $ cd src/collection
    $ python3 generate-soundtrack.py
    # Génère: ../../data/collection/soundtrack.json
    
    Prérequis:
    - Projet Cinéma avec catalogue.json présent
    - Collection Discogs déjà importée (discogs-collection.json)

Exemple de sortie:
    [
        {
            "film_title": "La Môme",
            "album_title": "la môme",
            "year": 2007,
            "director": "Olivier Dahan"
        },
        ...
    ]

Intégration:
    Les données générées sont utilisées par:
    - src/gui/musique-gui.py: Affichage badge BOF + métadonnées film
    - Filtrage de la collection par soundtracks
    - Cross-référence pour enrichissement futur

Auteur: Patrick Ostertag
Version: 1.0.0
Date: 24 janvier 2026
"""

import json
import unicodedata
import os

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
# DataForIA est un niveau au-dessus de Musique
DATAFORLA_ROOT = os.path.dirname(PROJECT_ROOT)

def normalize_title(title: str) -> str:
    """Normalise un titre en supprimant les accents pour tri alphabétique.
    
    Utilise la décomposition Unicode (NFKD) pour séparer les caractères de base
    et leurs diacritiques, puis encode en ASCII pour supprimer les accents.
    
    Args:
        title: Titre à normaliser (peut contenir accents, trémas, cédilles).
        
    Returns:
        Titre normalisé sans accents, en minuscules.
        
    Examples:
        >>> normalize_title("La Môme")
        'la mome'
        >>> normalize_title("Amélie Poulain")
        'amelie poulain'
        >>> normalize_title("El Niño")
        'el nino'
        
    Note:
        Utilisé uniquement pour le tri, pas pour l'affichage final.
        Les titres originaux avec accents sont préservés dans le JSON.
    """
    return unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII').lower()

def main():
    """Fonction principale pour générer la cross-référence films/soundtracks."""
    print("📂 Chargement des données...")
    
    # 1. Charger les fichiers JSON
    try:
        with open(os.path.join(DATAFORLA_ROOT, 'Cinéma', 'catalogue.json'), 'r', encoding='utf-8') as f:
            catalogue = json.load(f)
        print(f"✅ {len(catalogue)} films chargés depuis catalogue.json")
    except FileNotFoundError:
        print("❌ Erreur : Le fichier catalogue.json n'existe pas dans le projet Cinéma")
        print(f"   Chemin attendu: {os.path.join(DATAFORLA_ROOT, 'Cinéma', 'catalogue.json')}")
        return
    
    try:
        with open(os.path.join(PROJECT_ROOT, 'data', 'collection', 'discogs-collection.json'), 'r', encoding='utf-8') as f:
            discogs_collection = json.load(f)
        print(f"✅ {len(discogs_collection)} albums chargés depuis discogs-collection.json")
    except FileNotFoundError:
        print("❌ Erreur : Le fichier discogs-collection.json n'existe pas")
        return
    
    # 2. Extraire les titres des films (OriginalTitle) et des albums
    film_titles = {item['OriginalTitle'].lower() for item in catalogue}
    album_titles = {item['Titre'].lower() for item in discogs_collection}
    
    # 3. Trouver les titres communs (OriginalTitle au début du titre de l'album)
    print("\n🔍 Recherche des correspondances films/albums...")
    common_titles = [
        (film, album)
        for film in film_titles
        for album in album_titles
        if album.startswith(film)
    ]
    
    # 4. Créer des dictionnaires pour l'année et le réalisateur (OriginalTitle)
    film_titles_with_year = {item['OriginalTitle'].lower(): item.get('ProductionYear', 'N/A') for item in catalogue}
    film_titles_with_director = {
        item['OriginalTitle'].lower(): item['TMDB'].get('realisateur', 'N/A') if item.get('TMDB') else 'N/A'
        for item in catalogue
    }
    
    # 5. Ajouter l'année et le réalisateur aux correspondances
    common_titles_with_info = [
        {
            "film_title": film,
            "album_title": album,
            "year": film_titles_with_year[film],
            "director": film_titles_with_director[film]
        }
        for film, album in common_titles
    ]
    
    print(f"✅ {len(common_titles_with_info)} soundtracks détectées")
    
    # 6. Trier par ordre alphabétique (en ignorant les accents)
    common_titles_sorted = sorted(
        common_titles_with_info,
        key=lambda x: normalize_title(x["film_title"])
    )
    
    # 7. Sauvegarder dans un fichier JSON nommé soundtrack.json
    output_path = os.path.join(PROJECT_ROOT, 'data', 'collection', 'soundtrack.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(common_titles_sorted, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés dans : {output_path}")
    print("\n🎬 Exemples de soundtracks détectées :")
    for i, item in enumerate(common_titles_sorted[:5]):
        print(f"   {i+1}. {item['film_title']} ({item['year']}) - {item['director']}")

if __name__ == "__main__":
    main()
