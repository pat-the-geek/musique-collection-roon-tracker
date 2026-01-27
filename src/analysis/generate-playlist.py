#!/usr/bin/env python3
"""
Générateur de Playlists Basé sur les Patterns d'Écoute

Ce module génère automatiquement des playlists à partir de l'historique d'écoute
analysé dans chk-roon.json. Plusieurs algorithmes sont disponibles pour créer
des playlists adaptées à différents besoins.

⚠️ LIMITATION ROON API:
   L'API Roon ne permet PAS la création automatique de playlists.
   Ce script génère des exports dans plusieurs formats (JSON, M3U, CSV)
   qui peuvent être importés manuellement dans Roon ou utilisés avec
   d'autres lecteurs (VLC, iTunes, etc.).

Algorithmes Disponibles:
    - top_sessions: Pistes des sessions d'écoute les plus longues
    - artist_correlations: Artistes souvent écoutés ensemble
    - artist_flow: Transitions naturelles entre artistes
    - time_based: Pistes selon périodes temporelles (peak hours, weekend, etc.)
    - complete_albums: Albums écoutés en entier
    - rediscovery: Pistes aimées mais non écoutées récemment
    - ai_generated: 🆕 Playlist générée par IA basée sur un prompt utilisateur

Formats d'Export:
    - JSON: Métadonnées complètes avec images
    - M3U: Format standard compatible VLC, iTunes, etc.
    - CSV: Import Excel/Sheets
    - TXT: Instructions pour import manuel dans Roon

Fichiers utilisés:
    - chk-roon.json: Historique des lectures
    - discogs-collection.json: Collection Discogs (optionnel)
    
Sortie:
    - output/playlists/playlist-{algorithm}-YYYYMMDD-HHMMSS.{ext}

Configuration via scheduler (roon-config.json):
    {
        "scheduled_tasks": {
            "generate_playlist": {
                "enabled": true,
                "frequency_unit": "day",
                "frequency_count": 7,
                "playlist_type": "top_sessions",
                "max_tracks": 25,
                "output_formats": ["json", "m3u", "csv", "roon-txt"],
                "ai_prompt": "playlist calme pour méditer"  # Pour ai_generated
            }
        }
    }

Utilisation:
    # Génération manuelle
    $ python3 generate-playlist.py --algorithm top_sessions --max-tracks 25
    
    # Génération avec IA
    $ python3 generate-playlist.py --algorithm ai_generated --ai-prompt "jazz cool pour le soir"
    
    # Génération planifiée via scheduler
    # (automatique via chk-roon.py)

Auteur: Patrick Ostertag
Version: 1.2.0
Date: 27 janvier 2026

Changelog v1.2.0:
    - Ajout de la détection et suppression automatique des doublons
    - Les doublons sont identifiés par normalisation (artiste + titre + album)
    - Ignore les variations de casse et espaces
    - Affiche le nombre de doublons supprimés
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, PROJECT_ROOT)
from src.services.ai_service import generate_ai_playlist
from src.services.metadata_cleaner import normalize_string_for_comparison

# Chemins des fichiers
ROON_HISTORY_PATH = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")
DISCOGS_COLLECTION_PATH = os.path.join(PROJECT_ROOT, "data", "collection", "discogs-collection.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "playlists")

# Configuration par défaut
DEFAULT_MAX_TRACKS = 25
DEFAULT_ALGORITHM = "top_sessions"
DEFAULT_OUTPUT_FORMATS = ["json", "m3u", "csv", "roon-txt"]


def load_tracks() -> List[Dict]:
    """Charge les pistes depuis chk-roon.json."""
    with open(ROON_HISTORY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('tracks', [])


def load_discogs_collection() -> List[Dict]:
    """Charge la collection Discogs (optionnel)."""
    if os.path.exists(DISCOGS_COLLECTION_PATH):
        with open(DISCOGS_COLLECTION_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def remove_duplicate_tracks(tracks: List[Dict]) -> List[Dict]:
    """
    Supprime les doublons de la liste de pistes.
    
    Utilise une clé normalisée (artist + title + album) pour détecter les doublons,
    ignorant les variations de casse et les différences mineures comme "(remastered)" vs "(Remastered)".
    
    Args:
        tracks: Liste de pistes pouvant contenir des doublons
        
    Returns:
        Liste de pistes sans doublons, préservant l'ordre d'origine
        
    Examples:
        >>> tracks = [
        ...     {'artist': 'The Clash', 'title': 'London Calling (remastered)', 'album': 'London Calling'},
        ...     {'artist': 'The Clash', 'title': 'London Calling (Remastered)', 'album': 'London Calling'},
        ...     {'artist': 'Roxy Music', 'title': 'Love Is the Drug', 'album': 'Best Of'},
        ... ]
        >>> result = remove_duplicate_tracks(tracks)
        >>> len(result)
        2
    """
    seen_keys = set()
    unique_tracks = []
    
    for track in tracks:
        # Créer une clé normalisée pour détecter les doublons
        artist = normalize_string_for_comparison(track.get('artist', ''))
        title = normalize_string_for_comparison(track.get('title', ''))
        album = normalize_string_for_comparison(track.get('album', ''))
        
        track_key = f"{artist}||{title}||{album}"
        
        if track_key not in seen_keys:
            seen_keys.add(track_key)
            unique_tracks.append(track)
    
    return unique_tracks


def detect_listening_sessions(tracks: List[Dict], gap_minutes: int = 30) -> List[List[Dict]]:
    """
    Détecte les sessions d'écoute continues.
    Une session se termine si le gap entre deux pistes dépasse gap_minutes.
    """
    if not tracks:
        return []
    
    sorted_tracks = sorted(tracks, key=lambda t: t['timestamp'])
    sessions = []
    current_session = [sorted_tracks[0]]
    
    for i in range(1, len(sorted_tracks)):
        prev_time = sorted_tracks[i-1]['timestamp']
        curr_time = sorted_tracks[i]['timestamp']
        gap = (curr_time - prev_time) / 60
        
        if gap <= gap_minutes:
            current_session.append(sorted_tracks[i])
        else:
            sessions.append(current_session)
            current_session = [sorted_tracks[i]]
    
    if current_session:
        sessions.append(current_session)
    
    return sessions


def generate_top_sessions_playlist(tracks: List[Dict], max_tracks: int) -> List[Dict]:
    """
    Algorithme: TOP_SESSIONS
    Génère une playlist des pistes les plus fréquentes dans les sessions longues.
    """
    sessions = detect_listening_sessions(tracks)
    
    # Trier les sessions par longueur (nombre de pistes)
    long_sessions = sorted(sessions, key=len, reverse=True)[:10]
    
    # Compter la fréquence des pistes dans ces sessions
    track_frequency = Counter()
    track_data = {}
    
    for session in long_sessions:
        for track in session:
            track_key = f"{track['artist']}||{track['title']}||{track['album']}"
            track_frequency[track_key] += 1
            if track_key not in track_data:
                track_data[track_key] = track
    
    # Sélectionner les pistes les plus fréquentes
    most_common = track_frequency.most_common(max_tracks)
    playlist_tracks = [track_data[track_key] for track_key, _ in most_common]
    
    return playlist_tracks


def generate_artist_correlations_playlist(tracks: List[Dict], max_tracks: int) -> List[Dict]:
    """
    Algorithme: ARTIST_CORRELATIONS
    Génère une playlist d'artistes souvent écoutés ensemble.
    """
    sessions = detect_listening_sessions(tracks)
    
    # Analyser les corrélations entre artistes
    artist_pairs = defaultdict(int)
    artist_tracks = defaultdict(list)
    
    for session in sessions:
        session_artists = list(set(t['artist'] for t in session))
        for track in session:
            artist_tracks[track['artist']].append(track)
        
        # Compter les paires d'artistes
        for i, artist1 in enumerate(session_artists):
            for artist2 in session_artists[i+1:]:
                pair = tuple(sorted([artist1, artist2]))
                artist_pairs[pair] += 1
    
    # Trouver les artistes les plus corrélés
    top_pairs = sorted(artist_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Sélectionner des pistes de ces artistes corrélés
    playlist_tracks = []
    for (artist1, artist2), _ in top_pairs:
        # Prendre quelques pistes de chaque artiste
        tracks_per_artist = max_tracks // (len(top_pairs) * 2)
        playlist_tracks.extend(artist_tracks[artist1][:tracks_per_artist])
        playlist_tracks.extend(artist_tracks[artist2][:tracks_per_artist])
    
    return playlist_tracks[:max_tracks]


def generate_artist_flow_playlist(tracks: List[Dict], max_tracks: int) -> List[Dict]:
    """
    Algorithme: ARTIST_FLOW
    Génère une playlist basée sur les transitions naturelles entre artistes.
    """
    sorted_tracks = sorted(tracks, key=lambda t: t['timestamp'])
    
    # Analyser les transitions
    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(sorted_tracks) - 1):
        current_artist = sorted_tracks[i]['artist']
        next_artist = sorted_tracks[i+1]['artist']
        if current_artist != next_artist:
            transitions[current_artist][next_artist] += 1
    
    # Construire un flow naturel
    if not transitions:
        return sorted_tracks[:max_tracks]
    
    # Commencer avec l'artiste le plus fréquent
    artist_counts = Counter(t['artist'] for t in tracks)
    current_artist = artist_counts.most_common(1)[0][0]
    
    # Construire la playlist en suivant les transitions
    playlist_tracks = []
    used_artists = set()
    artist_track_map = defaultdict(list)
    for track in tracks:
        artist_track_map[track['artist']].append(track)
    
    while len(playlist_tracks) < max_tracks and current_artist not in used_artists:
        # Ajouter une piste de l'artiste actuel
        if artist_track_map[current_artist]:
            playlist_tracks.append(artist_track_map[current_artist][0])
            artist_track_map[current_artist] = artist_track_map[current_artist][1:]
        
        used_artists.add(current_artist)
        
        # Trouver le prochain artiste (transition la plus fréquente)
        if current_artist in transitions and transitions[current_artist]:
            next_artist = max(transitions[current_artist].items(), key=lambda x: x[1])[0]
            if next_artist not in used_artists:
                current_artist = next_artist
            else:
                break
        else:
            break
    
    return playlist_tracks


def generate_time_based_playlist(tracks: List[Dict], max_tracks: int, time_filter: str = "peak_hours") -> List[Dict]:
    """
    Algorithme: TIME_BASED
    Génère une playlist basée sur des périodes temporelles.
    
    time_filter options:
        - peak_hours: Heures de pic d'écoute
        - weekend: Pistes du weekend
        - evening: Pistes du soir (18h-23h)
        - morning: Pistes du matin (6h-12h)
    """
    time_filtered_tracks = []
    
    for track in tracks:
        dt = datetime.fromtimestamp(track['timestamp'])
        hour = dt.hour
        weekday = dt.weekday()  # 0=Monday, 6=Sunday
        
        if time_filter == "peak_hours":
            # Heures de pic (typiquement 18h-22h)
            if 18 <= hour <= 22:
                time_filtered_tracks.append(track)
        elif time_filter == "weekend":
            # Weekend
            if weekday >= 5:  # Saturday=5, Sunday=6
                time_filtered_tracks.append(track)
        elif time_filter == "evening":
            # Soirée (18h-23h)
            if 18 <= hour <= 23:
                time_filtered_tracks.append(track)
        elif time_filter == "morning":
            # Matin (6h-12h)
            if 6 <= hour <= 12:
                time_filtered_tracks.append(track)
    
    # Trier par fréquence
    track_frequency = Counter()
    track_data = {}
    
    for track in time_filtered_tracks:
        track_key = f"{track['artist']}||{track['title']}||{track['album']}"
        track_frequency[track_key] += 1
        if track_key not in track_data:
            track_data[track_key] = track
    
    most_common = track_frequency.most_common(max_tracks)
    return [track_data[track_key] for track_key, _ in most_common]


def generate_complete_albums_playlist(tracks: List[Dict], max_tracks: int, min_album_tracks: int = 5) -> List[Dict]:
    """
    Algorithme: COMPLETE_ALBUMS
    Génère une playlist d'albums écoutés en entier.
    """
    album_plays = defaultdict(list)
    
    for track in tracks:
        album_key = f"{track['artist']}||{track['album']}"
        album_plays[album_key].append(track)
    
    # Filtrer les albums avec au moins min_album_tracks
    complete_albums = {album: tracks_list for album, tracks_list in album_plays.items() 
                       if len(tracks_list) >= min_album_tracks}
    
    # Trier par nombre de pistes (albums les plus écoutés)
    sorted_albums = sorted(complete_albums.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Construire la playlist
    playlist_tracks = []
    for album_key, album_tracks in sorted_albums:
        if len(playlist_tracks) >= max_tracks:
            break
        # Ajouter les premières pistes de l'album
        remaining = max_tracks - len(playlist_tracks)
        playlist_tracks.extend(album_tracks[:remaining])
    
    return playlist_tracks


def generate_rediscovery_playlist(tracks: List[Dict], max_tracks: int, days_ago: int = 30) -> List[Dict]:
    """
    Algorithme: REDISCOVERY
    Génère une playlist de pistes non écoutées récemment.
    """
    # Calculer la date limite
    now = datetime.now()
    cutoff_date = now - timedelta(days=days_ago)
    cutoff_timestamp = cutoff_date.timestamp()
    
    # Trouver les pistes écoutées avant la date limite
    old_tracks = [t for t in tracks if t['timestamp'] < cutoff_timestamp]
    
    # Trouver celles qui étaient fréquentes
    track_frequency = Counter()
    track_data = {}
    
    for track in old_tracks:
        track_key = f"{track['artist']}||{track['title']}||{track['album']}"
        track_frequency[track_key] += 1
        if track_key not in track_data:
            track_data[track_key] = track
    
    # Sélectionner les plus fréquentes
    most_common = track_frequency.most_common(max_tracks)
    return [track_data[track_key] for track_key, _ in most_common]


def calculate_playlist_duration(playlist_tracks: List[Dict], avg_track_duration: int = 4) -> int:
    """Calcule la durée estimée de la playlist en minutes."""
    return len(playlist_tracks) * avg_track_duration


def get_current_datetime_for_filename() -> str:
    """Retourne la date/heure actuelle formatée pour un nom de fichier."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def export_to_json(playlist_tracks: List[Dict], algorithm: str, output_path: Path, 
                   playlist_name_override: str = None, playlist_description_override: str = None,
                   ai_reasoning: str = None) -> None:
    """Exporte la playlist au format JSON avec métadonnées complètes."""
    default_name = f"Playlist {algorithm.replace('_', ' ').title()} - {datetime.now().strftime('%B %Y')}"
    default_description = f"Playlist générée automatiquement avec l'algorithme '{algorithm}'"
    
    playlist_data = {
        "name": playlist_name_override or default_name,
        "description": playlist_description_override or default_description,
        "created_at": datetime.now().isoformat(),
        "algorithm": algorithm,
        "total_tracks": len(playlist_tracks),
        "total_duration_minutes": calculate_playlist_duration(playlist_tracks),
        "tracks": playlist_tracks
    }
    
    # Ajouter le raisonnement IA si disponible
    if ai_reasoning:
        playlist_data["ai_reasoning"] = ai_reasoning
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(playlist_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON exporté: {output_path}")


def export_to_m3u(playlist_tracks: List[Dict], algorithm: str, output_path: Path,
                  playlist_name_override: str = None, **kwargs) -> None:
    """Exporte la playlist au format M3U (compatible VLC, iTunes, etc.)."""
    default_name = f"Playlist {algorithm.replace('_', ' ').title()} - {datetime.now().strftime('%B %Y')}"
    playlist_name = playlist_name_override or default_name
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write(f"#PLAYLIST:{playlist_name}\n")
        f.write(f"#EXTIMG:{playlist_tracks[0].get('album_spotify_image', '')}\n" if playlist_tracks else "")
        f.write("\n")
        
        for track in playlist_tracks:
            artist = track.get('artist', 'Unknown Artist')
            title = track.get('title', 'Unknown Title')
            # Durée estimée: 240 secondes (4 minutes)
            f.write(f"#EXTINF:240,{artist} - {title}\n")
            # Note: Le chemin du fichier local n'est pas disponible
            # L'utilisateur devra le mapper manuellement
            f.write(f"# {artist} - {title} ({track.get('album', 'Unknown Album')})\n")
            f.write("\n")
    
    print(f"✅ M3U exporté: {output_path}")


def export_to_csv(playlist_tracks: List[Dict], algorithm: str, output_path: Path, **kwargs) -> None:
    """Exporte la playlist au format CSV (import Excel/Sheets)."""
    import csv
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Artist', 'Title', 'Album', 'Date', 'Source', 'Spotify Image', 'Last.fm Image']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for track in playlist_tracks:
            writer.writerow({
                'Artist': track.get('artist', ''),
                'Title': track.get('title', ''),
                'Album': track.get('album', ''),
                'Date': datetime.fromtimestamp(track['timestamp']).strftime('%Y-%m-%d %H:%M'),
                'Source': track.get('source', 'roon'),
                'Spotify Image': track.get('album_spotify_image', ''),
                'Last.fm Image': track.get('album_lastfm_image', '')
            })
    
    print(f"✅ CSV exporté: {output_path}")


def export_to_roon_txt(playlist_tracks: List[Dict], algorithm: str, output_path: Path,
                        playlist_name_override: str = None, playlist_description_override: str = None,
                        ai_reasoning: str = None) -> None:
    """Exporte la playlist au format texte avec instructions d'import Roon."""
    default_name = f"Playlist {algorithm.replace('_', ' ').title()} - {datetime.now().strftime('%B %Y')}"
    default_description = f"Générée avec l'algorithme '{algorithm}'"
    
    playlist_name = playlist_name_override or default_name
    playlist_description = playlist_description_override or default_description
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"PLAYLIST POUR ROON\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Nom: {playlist_name}\n")
        f.write(f"Description: {playlist_description}\n")
        f.write(f"Créée le: {datetime.now().strftime('%Y-%m-%d à %H:%M')}\n")
        f.write(f"Nombre de pistes: {len(playlist_tracks)}\n")
        f.write(f"Durée estimée: {calculate_playlist_duration(playlist_tracks)} minutes\n\n")
        
        # Afficher le raisonnement IA si disponible
        if ai_reasoning:
            f.write("🤖 RAISONNEMENT IA:\n")
            f.write(f"{ai_reasoning}\n\n")
        
        f.write("⚠️ LIMITATION ROON API:\n")
        f.write("L'API Roon ne permet PAS la création automatique de playlists.\n")
        f.write("Vous devez importer cette playlist MANUELLEMENT.\n\n")
        
        f.write("INSTRUCTIONS D'IMPORT DANS ROON:\n")
        f.write("1. Ouvrir Roon\n")
        f.write("2. Aller dans la section 'Browse' > 'Tracks'\n")
        f.write("3. Pour chaque piste ci-dessous:\n")
        f.write("   a. Utiliser la fonction 'Focus' ou 'Search' pour trouver la piste\n")
        f.write("   b. Ajouter la piste à la queue de lecture\n")
        f.write("4. Une fois la queue complète, faire clic-droit > 'Save as Playlist'\n")
        f.write(f"5. Nommer la playlist: '{playlist_name}'\n\n")
        
        f.write("=" * 80 + "\n")
        f.write(f"PISTES ({len(playlist_tracks)})\n")
        f.write("=" * 80 + "\n\n")
        
        for i, track in enumerate(playlist_tracks, 1):
            artist = track.get('artist', 'Unknown Artist')
            title = track.get('title', 'Unknown Title')
            album = track.get('album', 'Unknown Album')
            f.write(f"{i:3d}. {artist} - {title}\n")
            f.write(f"      Album: {album}\n")
            if track.get('album_spotify_image'):
                f.write(f"      Image: {track['album_spotify_image']}\n")
            f.write("\n")
    
    print(f"✅ TXT (Roon) exporté: {output_path}")


def generate_playlist(algorithm: str, max_tracks: int, output_formats: List[str], ai_prompt: str = None) -> Dict:
    """
    Génère une playlist avec l'algorithme spécifié et l'exporte dans les formats demandés.
    
    Args:
        algorithm: Type d'algorithme à utiliser
        max_tracks: Nombre maximum de pistes
        output_formats: Liste des formats d'export
        ai_prompt: Prompt pour l'algorithme ai_generated (requis si algorithm="ai_generated")
    
    Returns:
        Dict avec les informations de la playlist générée
    """
    print(f"\n{'='*80}")
    print(f"Génération de Playlist - Algorithme: {algorithm.upper()}")
    print(f"{'='*80}\n")
    
    # Charger les données
    print("📂 Chargement de l'historique d'écoute...")
    tracks = load_tracks()
    print(f"   ✅ {len(tracks)} pistes chargées\n")
    
    # Générer la playlist selon l'algorithme
    print(f"🎵 Génération avec l'algorithme '{algorithm}'...")
    
    ai_reasoning = None
    playlist_name_override = None
    playlist_description_override = None
    
    if algorithm == "top_sessions":
        playlist_tracks = generate_top_sessions_playlist(tracks, max_tracks)
    elif algorithm == "artist_correlations":
        playlist_tracks = generate_artist_correlations_playlist(tracks, max_tracks)
    elif algorithm == "artist_flow":
        playlist_tracks = generate_artist_flow_playlist(tracks, max_tracks)
    elif algorithm == "time_based_peak":
        playlist_tracks = generate_time_based_playlist(tracks, max_tracks, "peak_hours")
    elif algorithm == "time_based_weekend":
        playlist_tracks = generate_time_based_playlist(tracks, max_tracks, "weekend")
    elif algorithm == "time_based_evening":
        playlist_tracks = generate_time_based_playlist(tracks, max_tracks, "evening")
    elif algorithm == "time_based_morning":
        playlist_tracks = generate_time_based_playlist(tracks, max_tracks, "morning")
    elif algorithm == "complete_albums":
        playlist_tracks = generate_complete_albums_playlist(tracks, max_tracks)
    elif algorithm == "rediscovery":
        playlist_tracks = generate_rediscovery_playlist(tracks, max_tracks)
    elif algorithm == "ai_generated":
        if not ai_prompt:
            raise ValueError("Le paramètre --ai-prompt est requis pour l'algorithme ai_generated")
        
        print(f"🤖 Prompt utilisateur: '{ai_prompt}'")
        ai_result = generate_ai_playlist(ai_prompt, tracks, max_tracks)
        playlist_tracks = ai_result['tracks']
        ai_reasoning = ai_result['ai_reasoning']
        playlist_name_override = ai_result['playlist_name']
        playlist_description_override = ai_result['playlist_description']
    else:
        raise ValueError(f"Algorithme inconnu: {algorithm}")
    
    print(f"   ✅ {len(playlist_tracks)} pistes sélectionnées")
    
    # Supprimer les doublons
    original_count = len(playlist_tracks)
    playlist_tracks = remove_duplicate_tracks(playlist_tracks)
    duplicates_removed = original_count - len(playlist_tracks)
    
    if duplicates_removed > 0:
        print(f"   🔍 {duplicates_removed} doublon(s) supprimé(s)")
    print()
    
    # Créer le répertoire de sortie si nécessaire
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Timestamp pour les noms de fichiers
    timestamp = get_current_datetime_for_filename()
    base_filename = f"playlist-{algorithm}-{timestamp}"
    
    # Exporter dans les formats demandés
    print("💾 Export des playlists...\n")
    exported_files = {}
    
    # Préparer les paramètres pour export
    export_params = {
        'playlist_name_override': playlist_name_override,
        'playlist_description_override': playlist_description_override,
        'ai_reasoning': ai_reasoning
    }
    
    if "json" in output_formats:
        output_path = Path(OUTPUT_DIR) / f"{base_filename}.json"
        export_to_json(playlist_tracks, algorithm, output_path, **export_params)
        exported_files['json'] = str(output_path)
    
    if "m3u" in output_formats:
        output_path = Path(OUTPUT_DIR) / f"{base_filename}.m3u"
        export_to_m3u(playlist_tracks, algorithm, output_path, **export_params)
        exported_files['m3u'] = str(output_path)
    
    if "csv" in output_formats:
        output_path = Path(OUTPUT_DIR) / f"{base_filename}.csv"
        export_to_csv(playlist_tracks, algorithm, output_path, **export_params)
        exported_files['csv'] = str(output_path)
    
    if "roon-txt" in output_formats:
        output_path = Path(OUTPUT_DIR) / f"{base_filename}-roon.txt"
        export_to_roon_txt(playlist_tracks, algorithm, output_path, **export_params)
        exported_files['roon-txt'] = str(output_path)
    
    # Résumé
    print(f"\n{'='*80}")
    print("✅ GÉNÉRATION TERMINÉE")
    print(f"{'='*80}")
    print(f"Algorithme: {algorithm}")
    print(f"Pistes: {len(playlist_tracks)}")
    print(f"Durée estimée: {calculate_playlist_duration(playlist_tracks)} minutes")
    print(f"Formats exportés: {', '.join(output_formats)}")
    print(f"Répertoire: {OUTPUT_DIR}")
    print(f"{'='*80}\n")
    
    return {
        'algorithm': algorithm,
        'total_tracks': len(playlist_tracks),
        'duration_minutes': calculate_playlist_duration(playlist_tracks),
        'exported_files': exported_files,
        'timestamp': timestamp
    }


def main():
    """Point d'entrée principal pour l'exécution en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Génère des playlists basées sur les patterns d'écoute",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Algorithmes disponibles:
  top_sessions          - Pistes des sessions d'écoute les plus longues
  artist_correlations   - Artistes souvent écoutés ensemble
  artist_flow           - Transitions naturelles entre artistes
  time_based_peak       - Pistes des heures de pic (18h-22h)
  time_based_weekend    - Pistes du weekend
  time_based_evening    - Pistes du soir (18h-23h)
  time_based_morning    - Pistes du matin (6h-12h)
  complete_albums       - Albums écoutés en entier
  rediscovery           - Pistes non écoutées récemment
  ai_generated          - 🆕 Playlist générée par IA (requiert --ai-prompt)

Formats d'export:
  json        - Métadonnées complètes avec images
  m3u         - Format standard (VLC, iTunes, etc.)
  csv         - Import Excel/Sheets
  roon-txt    - Instructions pour import manuel dans Roon

Exemples:
  python3 generate-playlist.py --algorithm top_sessions
  python3 generate-playlist.py --algorithm artist_flow --max-tracks 30
  python3 generate-playlist.py --algorithm rediscovery --formats json m3u
  python3 generate-playlist.py --algorithm ai_generated --ai-prompt "jazz cool pour le soir"
        """
    )
    
    parser.add_argument(
        '--algorithm',
        type=str,
        default=DEFAULT_ALGORITHM,
        choices=[
            'top_sessions', 'artist_correlations', 'artist_flow',
            'time_based_peak', 'time_based_weekend', 'time_based_evening', 'time_based_morning',
            'complete_albums', 'rediscovery', 'ai_generated'
        ],
        help=f"Algorithme de génération (défaut: {DEFAULT_ALGORITHM})"
    )
    
    parser.add_argument(
        '--max-tracks',
        type=int,
        default=DEFAULT_MAX_TRACKS,
        help=f"Nombre maximum de pistes (défaut: {DEFAULT_MAX_TRACKS})"
    )
    
    parser.add_argument(
        '--formats',
        nargs='+',
        default=DEFAULT_OUTPUT_FORMATS,
        choices=['json', 'm3u', 'csv', 'roon-txt'],
        help=f"Formats d'export (défaut: {' '.join(DEFAULT_OUTPUT_FORMATS)})"
    )
    
    parser.add_argument(
        '--ai-prompt',
        type=str,
        default=None,
        help="Prompt pour l'algorithme ai_generated (ex: 'playlist calme pour méditer')"
    )
    
    args = parser.parse_args()
    
    try:
        result = generate_playlist(args.algorithm, args.max_tracks, args.formats, args.ai_prompt)
        return 0
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
