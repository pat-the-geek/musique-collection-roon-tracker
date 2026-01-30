"""
Journal Commands - Roon/Last.fm Listening History

Displays chronological listening history with filtering and statistics.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 30 janvier 2026
"""

import click
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style

from ..utils.data_loader import get_loader
from ..ui.colors import SemanticColor, apply_color, get_style


console = Console()


def format_timestamp(timestamp: int) -> str:
    """Format Unix timestamp to readable date/time."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        return "Invalid date"


def format_date_short(date_str: str) -> str:
    """Format date string to short format."""
    try:
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
        else:
            date_part = date_str
        return date_part
    except:
        return date_str


def filter_tracks(
    tracks: List[Dict],
    source: Optional[str] = None,
    loved: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[Dict]:
    """
    Filter tracks based on criteria.
    
    Args:
        tracks: List of track dictionaries
        source: Filter by source ('roon' or 'lastfm')
        loved: Filter by loved status (True/False)
        date_from: Start date (YYYY-MM-DD format)
        date_to: End date (YYYY-MM-DD format)
        
    Returns:
        Filtered list of tracks
    """
    filtered = tracks.copy()
    
    # Filter by source
    if source:
        source_lower = source.lower()
        filtered = [t for t in filtered if t.get('source', '').lower() == source_lower]
    
    # Filter by loved status
    if loved is not None:
        filtered = [t for t in filtered if t.get('loved', False) == loved]
    
    # Filter by date range
    if date_from or date_to:
        date_filtered = []
        for track in filtered:
            track_date = track.get('date', '')
            if not track_date:
                continue
            
            # Extract date part (YYYY-MM-DD)
            track_date_part = format_date_short(track_date)
            
            # Check date range
            if date_from and track_date_part < date_from:
                continue
            if date_to and track_date_part > date_to:
                continue
            
            date_filtered.append(track)
        
        filtered = date_filtered
    
    return filtered


def get_track_statistics(tracks: List[Dict]) -> Dict[str, any]:
    """
    Calculate statistics from tracks.
    
    Returns:
        Dictionary with statistics
    """
    if not tracks:
        return {
            'total': 0,
            'unique_artists': 0,
            'unique_albums': 0,
            'sources': {},
            'loved_count': 0,
            'top_artists': [],
            'top_albums': [],
            'peak_hour': None,
            'date_range': None
        }
    
    # Basic counts
    total = len(tracks)
    artists = [t.get('artist', 'Unknown') for t in tracks]
    albums = [t.get('album', 'Unknown') for t in tracks]
    sources = [t.get('source', 'unknown') for t in tracks]
    loved_count = sum(1 for t in tracks if t.get('loved', False))
    
    # Top items
    artist_counts = Counter(artists)
    album_counts = Counter(albums)
    source_counts = Counter(sources)
    
    # Peak hour analysis
    hours = []
    for track in tracks:
        if 'date' in track and ' ' in track['date']:
            try:
                time_part = track['date'].split(' ')[1]
                hour = int(time_part.split(':')[0])
                hours.append(hour)
            except (ValueError, IndexError):
                pass
    
    hour_counts = Counter(hours)
    peak_hour = hour_counts.most_common(1)[0][0] if hour_counts else None
    
    # Date range
    dates = []
    for track in tracks:
        date_str = track.get('date', '')
        if date_str:
            dates.append(format_date_short(date_str))
    
    date_range = None
    if dates:
        dates.sort()
        date_range = f"{dates[0]} → {dates[-1]}"
    
    return {
        'total': total,
        'unique_artists': len(set(artists)),
        'unique_albums': len(set(albums)),
        'sources': dict(source_counts),
        'loved_count': loved_count,
        'top_artists': artist_counts.most_common(5),
        'top_albums': album_counts.most_common(5),
        'peak_hour': peak_hour,
        'date_range': date_range
    }


@click.group(name='journal')
def journal_group():
    """Journal d'écoute Roon/Last.fm."""
    pass


@journal_group.command(name='list')
@click.option('--source', type=click.Choice(['roon', 'lastfm'], case_sensitive=False),
              help='Filtrer par source')
@click.option('--loved', is_flag=True, help='Afficher uniquement les favoris')
@click.option('--not-loved', is_flag=True, help='Afficher uniquement les non-favoris')
@click.option('--date-from', help='Date de début (YYYY-MM-DD)')
@click.option('--date-to', help='Date de fin (YYYY-MM-DD)')
@click.option('--limit', type=int, default=50, help='Nombre maximum de tracks à afficher')
def list_tracks(source, loved, not_loved, date_from, date_to, limit):
    """
    Affiche l'historique d'écoute.
    
    Exemples:
        journal list
        journal list --source roon
        journal list --loved
        journal list --date-from 2026-01-01
    """
    # Load data
    loader = get_loader()
    history = loader.load_history()
    
    if history is None or not history:
        console.print("[yellow]⚠️  Aucun historique trouvé[/yellow]")
        console.print("\n💡 Astuce: Lancez le tracker Roon pour générer des données")
        return
    
    # Apply filters
    loved_filter = None
    if loved:
        loved_filter = True
    elif not_loved:
        loved_filter = False
    
    filtered = filter_tracks(history, source, loved_filter, date_from, date_to)
    
    if not filtered:
        console.print("[yellow]⚠️  Aucune track ne correspond aux critères[/yellow]")
        return
    
    # Limit results
    display_tracks = filtered[:limit] if limit else filtered
    showing_all = len(display_tracks) == len(filtered)
    
    # Create table
    table = Table(
        title=f"📀 Journal d'écoute ({len(display_tracks)} tracks{'' if showing_all else f' sur {len(filtered)}'})",
        show_header=True,
        header_style=get_style(SemanticColor.PRIMARY)
    )
    
    table.add_column("Date", style=get_style(SemanticColor.MUTED), width=16)
    table.add_column("Artiste", style=get_style(SemanticColor.ARTIST), width=25)
    table.add_column("Titre", style=get_style(SemanticColor.TRACK), width=30)
    table.add_column("Album", style=get_style(SemanticColor.ALBUM), width=25)
    table.add_column("♥", justify="center", width=3)
    table.add_column("Source", justify="center", width=7)
    
    # Add rows
    for track in display_tracks:
        date = track.get('date', 'N/A')
        artist = track.get('artist', 'Unknown')
        title = track.get('title', 'Unknown')
        album = track.get('album', 'Unknown')
        loved_status = "♥" if track.get('loved', False) else ""
        source_val = track.get('source', '?')
        
        # Truncate long text
        artist = artist[:23] + "..." if len(artist) > 25 else artist
        title = title[:28] + "..." if len(title) > 30 else title
        album = album[:23] + "..." if len(album) > 25 else album
        
        # Color for source
        if source_val.lower() == 'roon':
            source_style = get_style(SemanticColor.SOURCE_ROON)
        elif source_val.lower() == 'lastfm':
            source_style = get_style(SemanticColor.SOURCE_LASTFM)
        else:
            source_style = ""
        
        table.add_row(
            date,
            artist,
            title,
            album,
            Text(loved_status, style=get_style(SemanticColor.LOVED) if loved_status else ""),
            Text(source_val.upper()[:7], style=source_style)
        )
    
    console.print(table)
    
    if not showing_all:
        console.print(f"\n💡 Utilisez [cyan]--limit {len(filtered)}[/cyan] pour tout afficher")


@journal_group.command(name='stats')
@click.option('--source', type=click.Choice(['roon', 'lastfm'], case_sensitive=False),
              help='Filtrer par source')
@click.option('--date-from', help='Date de début (YYYY-MM-DD)')
@click.option('--date-to', help='Date de fin (YYYY-MM-DD)')
def show_stats(source, date_from, date_to):
    """
    Affiche les statistiques d'écoute.
    
    Exemples:
        journal stats
        journal stats --source roon
        journal stats --date-from 2026-01-01
    """
    # Load data
    loader = get_loader()
    history = loader.load_history()
    
    if history is None or not history:
        console.print("[yellow]⚠️  Aucun historique trouvé[/yellow]")
        return
    
    # Apply filters
    filtered = filter_tracks(history, source, None, date_from, date_to)
    
    if not filtered:
        console.print("[yellow]⚠️  Aucune track ne correspond aux critères[/yellow]")
        return
    
    # Calculate statistics
    stats = get_track_statistics(filtered)
    
    # Display statistics panel
    stats_text = Text()
    stats_text.append("📊 Statistiques Générales\n\n", style=get_style(SemanticColor.PRIMARY))
    
    stats_text.append(f"Total tracks: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{stats['total']}\n", style=get_style(SemanticColor.EMPHASIS))
    
    stats_text.append(f"Artistes uniques: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{stats['unique_artists']}\n", style=get_style(SemanticColor.EMPHASIS))
    
    stats_text.append(f"Albums uniques: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{stats['unique_albums']}\n", style=get_style(SemanticColor.EMPHASIS))
    
    stats_text.append(f"Favoris: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{stats['loved_count']}\n", style=get_style(SemanticColor.LOVED))
    
    if stats['date_range']:
        stats_text.append(f"Période: ", style=get_style(SemanticColor.MUTED))
        stats_text.append(f"{stats['date_range']}\n", style=get_style(SemanticColor.EMPHASIS))
    
    if stats['peak_hour'] is not None:
        stats_text.append(f"Heure de pointe: ", style=get_style(SemanticColor.MUTED))
        stats_text.append(f"{stats['peak_hour']}h\n", style=get_style(SemanticColor.EMPHASIS))
    
    # Sources breakdown
    if stats['sources']:
        stats_text.append("\n📡 Sources\n\n", style=get_style(SemanticColor.PRIMARY))
        for src, count in stats['sources'].items():
            stats_text.append(f"{src.upper()}: ", style=get_style(SemanticColor.MUTED))
            stats_text.append(f"{count} tracks\n", style=get_style(SemanticColor.EMPHASIS))
    
    # Top artists
    if stats['top_artists']:
        stats_text.append("\n🎤 Top 5 Artistes\n\n", style=get_style(SemanticColor.PRIMARY))
        for i, (artist, count) in enumerate(stats['top_artists'], 1):
            stats_text.append(f"{i}. ", style=get_style(SemanticColor.MUTED))
            stats_text.append(f"{artist} ", style=get_style(SemanticColor.ARTIST))
            stats_text.append(f"({count})\n", style=get_style(SemanticColor.MUTED))
    
    # Top albums
    if stats['top_albums']:
        stats_text.append("\n💿 Top 5 Albums\n\n", style=get_style(SemanticColor.PRIMARY))
        for i, (album, count) in enumerate(stats['top_albums'], 1):
            stats_text.append(f"{i}. ", style=get_style(SemanticColor.MUTED))
            stats_text.append(f"{album} ", style=get_style(SemanticColor.ALBUM))
            stats_text.append(f"({count})\n", style=get_style(SemanticColor.MUTED))
    
    panel = Panel(
        stats_text,
        title="📊 Statistiques d'Écoute",
        border_style=get_style(SemanticColor.PRIMARY)
    )
    
    console.print(panel)


@journal_group.command(name='view')
@click.argument('index', type=int)
def view_track(index):
    """
    Affiche les détails d'une track.
    
    Exemples:
        journal view 1
        journal view 10
    """
    # Load data
    loader = get_loader()
    history = loader.load_history()
    
    if history is None or not history:
        console.print("[yellow]⚠️  Aucun historique trouvé[/yellow]")
        return
    
    # Check index
    if index < 1 or index > len(history):
        console.print(f"[red]❌ Index invalide. Valeurs acceptées: 1-{len(history)}[/red]")
        return
    
    # Get track (1-based index)
    track = history[index - 1]
    
    # Create detail panel
    detail_text = Text()
    
    # Title
    detail_text.append(f"🎵 {track.get('title', 'Unknown')}\n\n", 
                      style=get_style(SemanticColor.PRIMARY) + Style(bold=True))
    
    # Artist
    detail_text.append("Artiste: ", style=get_style(SemanticColor.MUTED))
    detail_text.append(f"{track.get('artist', 'Unknown')}\n", 
                      style=get_style(SemanticColor.ARTIST))
    
    # Album
    detail_text.append("Album: ", style=get_style(SemanticColor.MUTED))
    detail_text.append(f"{track.get('album', 'Unknown')}\n", 
                      style=get_style(SemanticColor.ALBUM))
    
    # Date
    detail_text.append("Date: ", style=get_style(SemanticColor.MUTED))
    detail_text.append(f"{track.get('date', 'N/A')}\n", 
                      style=get_style(SemanticColor.EMPHASIS))
    
    # Source
    source = track.get('source', 'unknown')
    detail_text.append("Source: ", style=get_style(SemanticColor.MUTED))
    source_color = SemanticColor.SOURCE_ROON if source.lower() == 'roon' else SemanticColor.SOURCE_LASTFM
    detail_text.append(f"{source.upper()}\n", style=apply_color(source_color))
    
    # Loved status
    loved = track.get('loved', False)
    detail_text.append("Favori: ", style=get_style(SemanticColor.MUTED))
    if loved:
        detail_text.append("♥ Oui\n", style=get_style(SemanticColor.LOVED))
    else:
        detail_text.append("Non\n", style=get_style(SemanticColor.MUTED))
    
    # AI info if available
    if 'ai_info' in track and track['ai_info']:
        detail_text.append("\n🤖 Information IA\n\n", style=get_style(SemanticColor.PRIMARY))
        detail_text.append(f"{track['ai_info']}\n", style=get_style(SemanticColor.MUTED))
    
    # Image URLs if available
    images = []
    if track.get('artist_spotify_image'):
        images.append(('Artiste (Spotify)', track['artist_spotify_image']))
    if track.get('album_spotify_image'):
        images.append(('Album (Spotify)', track['album_spotify_image']))
    if track.get('album_lastfm_image'):
        images.append(('Album (Last.fm)', track['album_lastfm_image']))
    
    if images:
        detail_text.append("\n🖼️  Images\n\n", style=get_style(SemanticColor.PRIMARY))
        for label, url in images:
            detail_text.append(f"{label}: ", style=get_style(SemanticColor.MUTED))
            detail_text.append(f"{url[:60]}...\n" if len(url) > 60 else f"{url}\n", 
                             style=get_style(SemanticColor.EMPHASIS))
    
    panel = Panel(
        detail_text,
        title=f"Track #{index}",
        border_style=get_style(SemanticColor.PRIMARY)
    )
    
    console.print(panel)
