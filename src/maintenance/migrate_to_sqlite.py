#!/usr/bin/env python3
"""Script de migration des données JSON vers SQLite.

Ce script migre les données du format JSON actuel (chk-roon.json, 
discogs-collection.json) vers une base de données SQLite relationnelle.

Stratégie de migration:
    Phase 1: Import Collection Discogs (data/collection/discogs-collection.json)
        - Créer artistes uniques
        - Créer albums avec métadonnées
        - Créer relations album_artist (Many-to-Many)
        - Créer images (pochettes Discogs + Spotify)
        - Créer metadata (résumés IA, BOF)
    
    Phase 2: Import Historique Roon (data/history/chk-roon.json)
        - Créer artistes manquants
        - Créer albums manquants
        - Créer tracks (dédupliquer par album + titre)
        - Créer listening_history (timestamp, source, loved)
        - Créer images (Spotify + Last.fm)
        - Compléter metadata.ai_info si présent
    
    Phase 3: Validation et Nettoyage
        - Normaliser noms d'artistes (supprimer suffixes)
        - Fusionner doublons éventuels
        - Vérifier intégrité référentielle
        - Afficher statistiques de migration

Sauvegarde automatique:
    Avant migration, crée une sauvegarde timestampée des JSON:
        backups/json/pre-migration-YYYYMMDD-HHMMSS/

Exemple d'utilisation:
    $ python3 migrate_to_sqlite.py
    # Crée data/musique.db avec toutes les données migrées
    
    $ python3 migrate_to_sqlite.py --dry-run
    # Mode simulation sans modifications
    
    $ python3 migrate_to_sqlite.py --db-path custom.db
    # Utilise un chemin personnalisé pour la base

Dépendances:
    - sqlalchemy: ORM
    - python-dotenv: Variables d'environnement
    
Auteur: Patrick Ostertag
Version: 1.0.0
Date: 27 janvier 2026
"""

import os
import sys
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Déterminer le répertoire racine du projet
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, PROJECT_ROOT)

from src.models.schema import (
    Base,
    Artist,
    Album,
    Track,
    ListeningHistory,
    Image,
    Metadata,
)

# Charger les variables d'environnement
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Chemins des fichiers
DISCOGS_JSON = os.path.join(PROJECT_ROOT, "data", "collection", "discogs-collection.json")
ROON_JSON = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")
SOUNDTRACK_JSON = os.path.join(PROJECT_ROOT, "data", "collection", "soundtrack.json")
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "data", "musique.db")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "backups", "json")


def backup_json_files() -> str:
    """Crée une sauvegarde des fichiers JSON avant migration.
    
    Returns:
        str: Chemin du répertoire de sauvegarde créé.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"pre-migration-{timestamp}")
    os.makedirs(backup_path, exist_ok=True)
    
    print(f"📦 Sauvegarde des JSON vers: {backup_path}")
    
    files_to_backup = [
        (DISCOGS_JSON, "discogs-collection.json"),
        (ROON_JSON, "chk-roon.json"),
        (SOUNDTRACK_JSON, "soundtrack.json"),
    ]
    
    for src, filename in files_to_backup:
        if os.path.exists(src):
            dst = os.path.join(backup_path, filename)
            shutil.copy2(src, dst)
            print(f"  ✓ {filename}")
    
    return backup_path


def create_database(db_path: str) -> Tuple[any, any]:
    """Crée la base de données SQLite et les tables.
    
    Args:
        db_path: Chemin vers le fichier SQLite.
        
    Returns:
        Tuple[Engine, Session]: Moteur et session SQLAlchemy.
    """
    print(f"🗄️  Création de la base de données: {db_path}")
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("  ✓ Toutes les tables créées")
    
    return engine, session


def migrate_discogs_collection(session: any, dry_run: bool = False) -> Dict:
    """Migre la collection Discogs vers SQLite.
    
    Args:
        session: Session SQLAlchemy.
        dry_run: Si True, ne modifie pas la base.
        
    Returns:
        Dict: Statistiques de migration {albums, artists, images, metadata}.
    """
    print("\n📚 Phase 1: Migration Collection Discogs")
    
    if not os.path.exists(DISCOGS_JSON):
        print(f"  ⚠️  Fichier non trouvé: {DISCOGS_JSON}")
        return {}
    
    with open(DISCOGS_JSON, 'r', encoding='utf-8') as f:
        discogs_data = json.load(f)
    
    stats = {
        'albums': 0,
        'artists': 0,
        'images': 0,
        'metadata': 0,
    }
    
    # TODO: Implémenter la logique de migration
    # 1. Créer ou récupérer artistes
    # 2. Créer albums avec relations
    # 3. Créer images
    # 4. Créer metadata
    
    print(f"  📊 Statistiques: {len(discogs_data)} albums à migrer")
    print("  ⚠️  TODO: Logique de migration à implémenter")
    
    if not dry_run:
        session.commit()
    
    return stats


def migrate_roon_history(session: any, dry_run: bool = False) -> Dict:
    """Migre l'historique Roon vers SQLite.
    
    Args:
        session: Session SQLAlchemy.
        dry_run: Si True, ne modifie pas la base.
        
    Returns:
        Dict: Statistiques de migration {tracks, listening_history, images}.
    """
    print("\n🎵 Phase 2: Migration Historique Roon")
    
    if not os.path.exists(ROON_JSON):
        print(f"  ⚠️  Fichier non trouvé: {ROON_JSON}")
        return {}
    
    with open(ROON_JSON, 'r', encoding='utf-8') as f:
        roon_data = json.load(f)
    
    stats = {
        'tracks': 0,
        'listening_history': 0,
        'images': 0,
    }
    
    # TODO: Implémenter la logique de migration
    # 1. Créer artistes/albums manquants
    # 2. Créer tracks
    # 3. Créer listening_history
    # 4. Créer images (Spotify + Last.fm)
    
    tracks = roon_data.get('tracks', [])
    print(f"  📊 Statistiques: {len(tracks)} écoutes à migrer")
    print("  ⚠️  TODO: Logique de migration à implémenter")
    
    if not dry_run:
        session.commit()
    
    return stats


def validate_migration(session: any) -> bool:
    """Valide l'intégrité de la migration.
    
    Args:
        session: Session SQLAlchemy.
        
    Returns:
        bool: True si validation réussie.
    """
    print("\n✅ Phase 3: Validation de la Migration")
    
    # TODO: Implémenter les vérifications
    # 1. Compter les enregistrements dans chaque table
    # 2. Vérifier les relations (albums sans artistes, etc.)
    # 3. Vérifier contraintes d'unicité
    
    artist_count = session.query(Artist).count()
    album_count = session.query(Album).count()
    track_count = session.query(Track).count()
    history_count = session.query(ListeningHistory).count()
    
    print(f"  📊 Artistes: {artist_count}")
    print(f"  📊 Albums: {album_count}")
    print(f"  📊 Pistes: {track_count}")
    print(f"  📊 Historique: {history_count}")
    
    print("  ⚠️  TODO: Validation détaillée à implémenter")
    
    return True


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Migre les données JSON vers SQLite"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Mode simulation sans modifications"
    )
    parser.add_argument(
        '--db-path',
        default=DEFAULT_DB_PATH,
        help=f"Chemin vers la base SQLite (défaut: {DEFAULT_DB_PATH})"
    )
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help="Ne pas créer de sauvegarde des JSON"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 Migration JSON → SQLite")
    print("=" * 70)
    
    if args.dry_run:
        print("⚠️  MODE DRY-RUN: Aucune modification ne sera effectuée")
    
    # Sauvegarde des JSON
    if not args.skip_backup and not args.dry_run:
        backup_path = backup_json_files()
        print(f"  ✓ Sauvegarde créée: {backup_path}")
    
    # Créer la base de données
    engine, session = create_database(args.db_path)
    
    try:
        # Phase 1: Collection Discogs
        discogs_stats = migrate_discogs_collection(session, args.dry_run)
        
        # Phase 2: Historique Roon
        roon_stats = migrate_roon_history(session, args.dry_run)
        
        # Phase 3: Validation
        if not args.dry_run:
            is_valid = validate_migration(session)
            if not is_valid:
                print("\n❌ Validation échouée - Migration annulée")
                session.rollback()
                return 1
        
        print("\n" + "=" * 70)
        print("✅ Migration terminée avec succès!")
        print("=" * 70)
        
        if args.dry_run:
            print("\n💡 Exécutez sans --dry-run pour appliquer les modifications")
        else:
            print(f"\n📁 Base de données créée: {args.db_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        session.rollback()
        return 1
        
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
