"""Module de définition du modèle de données pour la base SQLite.

Ce module contient les définitions des tables et relations pour la migration
vers une base de données relationnelle SQLite.

Modules:
    schema: Définitions SQLAlchemy des tables et relations
    
Auteur: Patrick Ostertag
Version: 1.0.0
Date: 27 janvier 2026
"""

from .schema import (
    Base,
    Artist,
    Album,
    Track,
    ListeningHistory,
    Image,
    Metadata,
    AlbumArtist,
)

__all__ = [
    'Base',
    'Artist',
    'Album',
    'Track',
    'ListeningHistory',
    'Image',
    'Metadata',
    'AlbumArtist',
]
