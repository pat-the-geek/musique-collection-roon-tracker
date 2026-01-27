"""Tests unitaires pour les modèles SQLAlchemy.

Ce module teste la création des tables, les relations, les contraintes,
et les opérations CRUD de base.

Auteur: Patrick Ostertag
Version: 1.0.0
Date: 27 janvier 2026
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models.schema import (
    Base,
    Artist,
    Album,
    Track,
    ListeningHistory,
    Image,
    Metadata,
    album_artist,
)


@pytest.fixture
def engine():
    """Créer un moteur SQLite en mémoire pour les tests."""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Créer une session de test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestDatabaseSchema:
    """Tests de création et structure des tables."""
    
    def test_tables_created(self, engine):
        """Vérifie que toutes les tables sont créées."""
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        expected_tables = [
            'artists',
            'albums',
            'tracks',
            'listening_history',
            'images',
            'metadata',
            'album_artist',
        ]
        
        for table in expected_tables:
            assert table in table_names, f"Table {table} non créée"
    
    def test_artist_table_columns(self, engine):
        """Vérifie les colonnes de la table artists."""
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('artists')}
        
        assert 'id' in columns
        assert 'name' in columns
        assert 'spotify_id' in columns
        assert 'lastfm_url' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
    
    def test_album_table_columns(self, engine):
        """Vérifie les colonnes de la table albums."""
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('albums')}
        
        assert 'id' in columns
        assert 'title' in columns
        assert 'year' in columns
        assert 'support' in columns
        assert 'discogs_id' in columns
        assert 'spotify_url' in columns
    
    def test_indexes_created(self, engine):
        """Vérifie que les index sont créés."""
        inspector = inspect(engine)
        
        # Index sur artists
        artist_indexes = inspector.get_indexes('artists')
        assert any('name' in idx.get('column_names', []) for idx in artist_indexes)
        
        # Index sur albums
        album_indexes = inspector.get_indexes('albums')
        assert any('title' in idx.get('column_names', []) for idx in album_indexes)
        
        # Index sur listening_history
        history_indexes = inspector.get_indexes('listening_history')
        assert any('timestamp' in idx.get('column_names', []) for idx in history_indexes)


class TestArtistModel:
    """Tests du modèle Artist."""
    
    def test_create_artist(self, session):
        """Test création d'un artiste."""
        artist = Artist(
            name="Nina Simone",
            spotify_id="abc123",
            lastfm_url="https://last.fm/nina-simone"
        )
        session.add(artist)
        session.commit()
        
        assert artist.id is not None
        assert artist.name == "Nina Simone"
        assert artist.spotify_id == "abc123"
        assert artist.created_at is not None
    
    def test_artist_unique_name(self, session):
        """Test contrainte d'unicité sur le nom."""
        artist1 = Artist(name="Miles Davis")
        session.add(artist1)
        session.commit()
        
        artist2 = Artist(name="Miles Davis")
        session.add(artist2)
        
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_artist_repr(self, session):
        """Test représentation string."""
        artist = Artist(name="John Coltrane")
        session.add(artist)
        session.commit()
        
        repr_str = repr(artist)
        assert "John Coltrane" in repr_str
        assert str(artist.id) in repr_str


class TestAlbumModel:
    """Tests du modèle Album."""
    
    def test_create_album(self, session):
        """Test création d'un album."""
        album = Album(
            title="Kind of Blue",
            year=1959,
            support="Vinyle",
            discogs_id="123456",
            spotify_url="https://open.spotify.com/album/xyz"
        )
        session.add(album)
        session.commit()
        
        assert album.id is not None
        assert album.title == "Kind of Blue"
        assert album.year == 1959
    
    def test_album_artist_relationship(self, session):
        """Test relation Many-to-Many avec artistes."""
        artist1 = Artist(name="Miles Davis")
        artist2 = Artist(name="John Coltrane")
        
        album = Album(title="Kind of Blue", year=1959)
        album.artists.append(artist1)
        album.artists.append(artist2)
        
        session.add(album)
        session.commit()
        
        assert len(album.artists) == 2
        assert artist1 in album.artists
        assert artist2 in album.artists
    
    def test_album_unique_discogs_id(self, session):
        """Test contrainte d'unicité sur discogs_id."""
        album1 = Album(title="Album 1", discogs_id="123456")
        session.add(album1)
        session.commit()
        
        album2 = Album(title="Album 2", discogs_id="123456")
        session.add(album2)
        
        with pytest.raises(IntegrityError):
            session.commit()


class TestTrackModel:
    """Tests du modèle Track."""
    
    def test_create_track(self, session):
        """Test création d'une piste."""
        album = Album(title="Pastel Blues", year=1965)
        session.add(album)
        session.commit()
        
        track = Track(
            album_id=album.id,
            title="Ain't No Use",
            track_number=1,
            duration_seconds=245
        )
        session.add(track)
        session.commit()
        
        assert track.id is not None
        assert track.album_id == album.id
        assert track.title == "Ain't No Use"
    
    def test_track_album_relationship(self, session):
        """Test relation avec album."""
        album = Album(title="Test Album")
        track1 = Track(title="Track 1", track_number=1)
        track2 = Track(title="Track 2", track_number=2)
        
        album.tracks.append(track1)
        album.tracks.append(track2)
        
        session.add(album)
        session.commit()
        
        assert len(album.tracks) == 2
        assert track1.album == album
        assert track2.album == album


class TestListeningHistoryModel:
    """Tests du modèle ListeningHistory."""
    
    def test_create_listening_history(self, session):
        """Test création d'un historique d'écoute."""
        album = Album(title="Test Album")
        track = Track(title="Test Track")
        album.tracks.append(track)
        session.add(album)
        session.commit()
        
        history = ListeningHistory(
            track_id=track.id,
            timestamp=1768674069,
            date="2026-01-17 18:21",
            source="roon",
            loved=False
        )
        session.add(history)
        session.commit()
        
        assert history.id is not None
        assert history.track_id == track.id
        assert history.source == "roon"
    
    def test_listening_history_unique_constraint(self, session):
        """Test contrainte d'unicité (track_id, timestamp)."""
        album = Album(title="Test Album")
        track = Track(title="Test Track")
        album.tracks.append(track)
        session.add(album)
        session.commit()
        
        history1 = ListeningHistory(
            track_id=track.id,
            timestamp=1768674069,
            date="2026-01-17 18:21",
            source="roon"
        )
        session.add(history1)
        session.commit()
        
        history2 = ListeningHistory(
            track_id=track.id,
            timestamp=1768674069,
            date="2026-01-17 18:21",
            source="lastfm"
        )
        session.add(history2)
        
        with pytest.raises(IntegrityError):
            session.commit()


class TestImageModel:
    """Tests du modèle Image."""
    
    def test_create_artist_image(self, session):
        """Test création d'une image d'artiste."""
        artist = Artist(name="Test Artist")
        session.add(artist)
        session.commit()
        
        image = Image(
            url="https://example.com/image.jpg",
            image_type="artist_image",
            source="spotify",
            artist_id=artist.id
        )
        session.add(image)
        session.commit()
        
        assert image.id is not None
        assert image.artist_id == artist.id
        assert len(artist.images) == 1
    
    def test_create_album_image(self, session):
        """Test création d'une image d'album."""
        album = Album(title="Test Album")
        session.add(album)
        session.commit()
        
        image = Image(
            url="https://example.com/cover.jpg",
            image_type="album_cover",
            source="spotify",
            album_id=album.id
        )
        session.add(image)
        session.commit()
        
        assert image.id is not None
        assert image.album_id == album.id
        assert len(album.images) == 1


class TestMetadataModel:
    """Tests du modèle Metadata."""
    
    def test_create_metadata(self, session):
        """Test création de métadonnées."""
        album = Album(title="Test Album")
        session.add(album)
        session.commit()
        
        metadata = Metadata(
            album_id=album.id,
            ai_info="AI generated description",
            resume="Long resume text",
            is_soundtrack=True,
            film_title="Test Film",
            film_year=2020,
            film_director="Test Director"
        )
        session.add(metadata)
        session.commit()
        
        assert metadata.id is not None
        assert metadata.album_id == album.id
        assert metadata.is_soundtrack is True
    
    def test_metadata_unique_album_id(self, session):
        """Test contrainte d'unicité sur album_id."""
        album = Album(title="Test Album")
        session.add(album)
        session.commit()
        
        metadata1 = Metadata(album_id=album.id, ai_info="Info 1")
        session.add(metadata1)
        session.commit()
        
        metadata2 = Metadata(album_id=album.id, ai_info="Info 2")
        session.add(metadata2)
        
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_metadata_album_relationship(self, session):
        """Test relation One-to-One avec album."""
        album = Album(title="Test Album")
        metadata = Metadata(ai_info="Test info")
        album.album_metadata = metadata
        
        session.add(album)
        session.commit()
        
        assert album.album_metadata == metadata
        assert metadata.album == album


class TestCascadeDelete:
    """Tests des suppressions en cascade."""
    
    def test_delete_album_cascades_to_tracks(self, session):
        """Test suppression album supprime tracks."""
        album = Album(title="Test Album")
        track1 = Track(title="Track 1")
        track2 = Track(title="Track 2")
        album.tracks.extend([track1, track2])
        
        session.add(album)
        session.commit()
        
        album_id = album.id
        session.delete(album)
        session.commit()
        
        tracks_remaining = session.query(Track).filter_by(album_id=album_id).count()
        assert tracks_remaining == 0
    
    def test_delete_album_cascades_to_metadata(self, session):
        """Test suppression album supprime metadata."""
        album = Album(title="Test Album")
        metadata = Metadata(ai_info="Test info")
        album.album_metadata = metadata
        
        session.add(album)
        session.commit()
        
        album_id = album.id
        session.delete(album)
        session.commit()
        
        metadata_remaining = session.query(Metadata).filter_by(album_id=album_id).count()
        assert metadata_remaining == 0
    
    def test_delete_track_cascades_to_history(self, session):
        """Test suppression track supprime listening_history."""
        album = Album(title="Test Album")
        track = Track(title="Test Track")
        album.tracks.append(track)
        
        history = ListeningHistory(
            timestamp=1768674069,
            date="2026-01-17 18:21",
            source="roon"
        )
        track.listening_history.append(history)
        
        session.add(album)
        session.commit()
        
        track_id = track.id
        session.delete(track)
        session.commit()
        
        history_remaining = session.query(ListeningHistory).filter_by(track_id=track_id).count()
        assert history_remaining == 0


class TestComplexQueries:
    """Tests de requêtes complexes."""
    
    def test_query_albums_by_artist(self, session):
        """Test recherche albums par artiste."""
        artist = Artist(name="Nina Simone")
        album1 = Album(title="Pastel Blues", year=1965)
        album2 = Album(title="Wild is the Wind", year=1966)
        
        artist.albums.extend([album1, album2])
        session.add(artist)
        session.commit()
        
        albums = session.query(Album).join(album_artist).join(Artist).filter(
            Artist.name == "Nina Simone"
        ).all()
        
        assert len(albums) == 2
        assert album1 in albums
        assert album2 in albums
    
    def test_query_listening_history_by_date(self, session):
        """Test recherche historique par date."""
        album = Album(title="Test Album")
        track = Track(title="Test Track")
        album.tracks.append(track)
        
        history1 = ListeningHistory(
            timestamp=1768674069,
            date="2026-01-17 18:21",
            source="roon"
        )
        history2 = ListeningHistory(
            timestamp=1768674169,
            date="2026-01-17 18:23",
            source="lastfm"
        )
        track.listening_history.extend([history1, history2])
        
        session.add(album)
        session.commit()
        
        count = session.query(ListeningHistory).filter(
            ListeningHistory.timestamp.between(1768674000, 1768675000)
        ).count()
        
        assert count == 2
