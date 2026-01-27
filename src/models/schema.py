"""Schéma de base de données SQLite pour le projet Musique.

Ce module définit le modèle de données relationnel pour la migration depuis JSON vers SQLite.
Utilise SQLAlchemy ORM pour définir les tables, relations et index.

Tables principales:
    - artists: Artistes musicaux avec métadonnées Spotify/Last.fm
    - albums: Albums avec métadonnées enrichies (Discogs, Spotify, IA)
    - tracks: Pistes individuelles
    - listening_history: Historique d'écoute (Roon, Last.fm)
    - images: URLs d'images (artiste, album) avec source
    - metadata: Métadonnées supplémentaires (résumés IA, BOF, etc.)
    - album_artist: Table de liaison Many-to-Many pour artistes/albums

Relations:
    - Artist <-> Album: Many-to-Many via album_artist
    - Album -> Track: One-to-Many
    - Album -> Image: One-to-Many
    - Album -> Metadata: One-to-One
    - Track -> ListeningHistory: One-to-Many
    - Artist -> Image: One-to-Many

Index pour performance:
    - artist_name (recherche par nom)
    - album_name (recherche par titre)
    - timestamp (tri chronologique historique)
    - source (filtrage par source: roon/lastfm)

Exemple d'utilisation:
    >>> from sqlalchemy import create_engine
    >>> from sqlalchemy.orm import sessionmaker
    >>> from src.models.schema import Base, Artist, Album
    >>> 
    >>> engine = create_engine('sqlite:///data/musique.db')
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> 
    >>> artist = Artist(name="Nina Simone", spotify_id="abc123")
    >>> session.add(artist)
    >>> session.commit()

Auteur: Patrick Ostertag
Version: 1.0.0
Date: 27 janvier 2026
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    Text,
    ForeignKey,
    Table,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

# Base pour tous les modèles
Base = declarative_base()


# Table de liaison Many-to-Many pour Artist <-> Album
album_artist = Table(
    'album_artist',
    Base.metadata,
    Column('album_id', Integer, ForeignKey('albums.id'), primary_key=True),
    Column('artist_id', Integer, ForeignKey('artists.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now(), nullable=False),
)


class Artist(Base):
    """Table des artistes musicaux.
    
    Attributes:
        id: Clé primaire auto-incrémentée
        name: Nom de l'artiste (unique)
        spotify_id: Identifiant Spotify (nullable)
        lastfm_url: URL Last.fm (nullable)
        created_at: Date de création de l'enregistrement
        updated_at: Date de dernière mise à jour
        
    Relations:
        albums: Liste des albums via album_artist (Many-to-Many)
        images: Liste des images d'artiste (One-to-Many)
    """
    __tablename__ = 'artists'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    spotify_id = Column(String(100), nullable=True)
    lastfm_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    albums = relationship('Album', secondary=album_artist, back_populates='artists')
    images = relationship('Image', back_populates='artist', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Artist(id={self.id}, name='{self.name}')>"


class Album(Base):
    """Table des albums musicaux.
    
    Attributes:
        id: Clé primaire auto-incrémentée
        title: Titre de l'album (indexé)
        year: Année de sortie/réédition (nullable)
        support: Format (Vinyle, CD, etc.)
        discogs_id: Identifiant Discogs (nullable)
        spotify_url: URL Spotify (nullable)
        discogs_url: URL Discogs (nullable)
        created_at: Date de création de l'enregistrement
        updated_at: Date de dernière mise à jour
        
    Relations:
        artists: Liste des artistes via album_artist (Many-to-Many)
        tracks: Liste des pistes (One-to-Many)
        images: Liste des images d'album (One-to-Many)
        metadata: Métadonnées supplémentaires (One-to-One)
        listening_history: Historique d'écoute (One-to-Many via tracks)
    """
    __tablename__ = 'albums'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    year = Column(Integer, nullable=True)
    support = Column(String(50), nullable=True)  # Vinyle, CD, Digital, etc.
    discogs_id = Column(String(100), nullable=True, unique=True)
    spotify_url = Column(String(500), nullable=True)
    discogs_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    artists = relationship('Artist', secondary=album_artist, back_populates='albums')
    tracks = relationship('Track', back_populates='album', cascade='all, delete-orphan')
    images = relationship('Image', back_populates='album', cascade='all, delete-orphan')
    album_metadata = relationship('Metadata', back_populates='album', uselist=False, cascade='all, delete-orphan')
    
    # Index composite pour recherche rapide
    __table_args__ = (
        Index('idx_album_title_year', 'title', 'year'),
    )
    
    def __repr__(self):
        return f"<Album(id={self.id}, title='{self.title}', year={self.year})>"


class Track(Base):
    """Table des pistes musicales.
    
    Attributes:
        id: Clé primaire auto-incrémentée
        album_id: Clé étrangère vers albums
        title: Titre de la piste
        track_number: Numéro de piste (nullable)
        duration_seconds: Durée en secondes (nullable)
        spotify_id: Identifiant Spotify (nullable)
        created_at: Date de création de l'enregistrement
        updated_at: Date de dernière mise à jour
        
    Relations:
        album: Album parent (Many-to-One)
        listening_history: Historique d'écoute (One-to-Many)
    """
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    album_id = Column(Integer, ForeignKey('albums.id'), nullable=False)
    title = Column(String(500), nullable=False)
    track_number = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    spotify_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    album = relationship('Album', back_populates='tracks')
    listening_history = relationship('ListeningHistory', back_populates='track', cascade='all, delete-orphan')
    
    # Index composite pour recherche rapide
    __table_args__ = (
        Index('idx_track_album_title', 'album_id', 'title'),
    )
    
    def __repr__(self):
        return f"<Track(id={self.id}, title='{self.title}', album_id={self.album_id})>"


class ListeningHistory(Base):
    """Table de l'historique d'écoute.
    
    Attributes:
        id: Clé primaire auto-incrémentée
        track_id: Clé étrangère vers tracks
        timestamp: Timestamp Unix de l'écoute (indexé)
        date: Date formatée lisible (YYYY-MM-DD HH:MM)
        source: Source de l'écoute (roon/lastfm) (indexé)
        loved: Marqueur "favori" (Last.fm)
        created_at: Date de création de l'enregistrement
        
    Relations:
        track: Piste écoutée (Many-to-One)
        
    Contraintes:
        - Unicité sur (track_id, timestamp) pour éviter doublons
    """
    __tablename__ = 'listening_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False)
    timestamp = Column(Integer, nullable=False, index=True)
    date = Column(String(20), nullable=False)  # Format: "2026-01-27 15:30"
    source = Column(String(20), nullable=False, index=True)  # roon ou lastfm
    loved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    track = relationship('Track', back_populates='listening_history')
    
    # Contrainte d'unicité et index
    __table_args__ = (
        UniqueConstraint('track_id', 'timestamp', name='uq_track_timestamp'),
        Index('idx_timestamp_source', 'timestamp', 'source'),
    )
    
    def __repr__(self):
        return f"<ListeningHistory(id={self.id}, track_id={self.track_id}, date='{self.date}', source='{self.source}')>"


class Image(Base):
    """Table des URLs d'images.
    
    Attributes:
        id: Clé primaire auto-incrémentée
        url: URL de l'image
        image_type: Type d'image (artist_image, album_cover)
        source: Source de l'image (spotify, lastfm, discogs)
        artist_id: Clé étrangère vers artists (nullable)
        album_id: Clé étrangère vers albums (nullable)
        created_at: Date de création de l'enregistrement
        updated_at: Date de dernière mise à jour
        
    Relations:
        artist: Artiste associé (Many-to-One) si image_type=artist_image
        album: Album associé (Many-to-One) si image_type=album_cover
        
    Contraintes:
        - Au moins artist_id OU album_id doit être renseigné
    """
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(1000), nullable=False)
    image_type = Column(String(50), nullable=False)  # artist_image, album_cover
    source = Column(String(50), nullable=False)  # spotify, lastfm, discogs
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=True)
    album_id = Column(Integer, ForeignKey('albums.id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    artist = relationship('Artist', back_populates='images')
    album = relationship('Album', back_populates='images')
    
    # Index composite pour recherche rapide
    __table_args__ = (
        Index('idx_image_artist', 'artist_id', 'image_type', 'source'),
        Index('idx_image_album', 'album_id', 'image_type', 'source'),
    )
    
    def __repr__(self):
        return f"<Image(id={self.id}, type='{self.image_type}', source='{self.source}')>"


class Metadata(Base):
    """Table des métadonnées supplémentaires.
    
    Attributes:
        id: Clé primaire auto-incrémentée
        album_id: Clé étrangère vers albums (unique)
        ai_info: Informations générées par IA (500 caractères)
        resume: Résumé détaillé de l'album (Text)
        is_soundtrack: Indicateur BOF/Soundtrack
        film_title: Titre du film associé (nullable)
        film_year: Année du film (nullable)
        film_director: Réalisateur (nullable)
        created_at: Date de création de l'enregistrement
        updated_at: Date de dernière mise à jour
        
    Relations:
        album: Album associé (One-to-One)
    """
    __tablename__ = 'metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    album_id = Column(Integer, ForeignKey('albums.id'), nullable=False, unique=True)
    ai_info = Column(String(500), nullable=True)  # Info courte générée par IA
    resume = Column(Text, nullable=True)  # Résumé détaillé
    is_soundtrack = Column(Boolean, default=False, nullable=False)
    film_title = Column(String(500), nullable=True)
    film_year = Column(Integer, nullable=True)
    film_director = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    album = relationship('Album', back_populates='album_metadata')
    
    def __repr__(self):
        return f"<Metadata(id={self.id}, album_id={self.album_id}, is_soundtrack={self.is_soundtrack})>"


# Export de la table de liaison pour faciliter les imports
AlbumArtist = album_artist
