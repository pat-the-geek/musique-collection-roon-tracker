"""
Timeline Commands - ASCII Art Timeline Visualization

Displays hourly timeline visualization of listening patterns.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 30 janvier 2026
"""

import click
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.columns import Columns

from ..utils.data_loader import get_loader
from ..ui.colors import SemanticColor, apply_color, get_style


console = Console()


def get_tracks_by_date(tracks: List[Dict], date: str) -> List[Dict]:
    """
    Filter tracks for a specific date.
    
    Args:
        tracks: List of track dictionaries
        date: Date string (YYYY-MM-DD)
        
    Returns:
        List of tracks for the specified date
    """
    date_tracks = []
    for track in tracks:
        track_date = track.get('date', '')
        if track_date.startswith(date):
            date_tracks.append(track)
    return date_tracks


def group_by_hour(tracks: List[Dict]) -> Dict[int, List[Dict]]:
    """
    Group tracks by hour of the day.
    
    Args:
        tracks: List of track dictionaries
        
    Returns:
        Dictionary mapping hour (0-23) to list of tracks
    """
    hourly = defaultdict(list)
    
    for track in tracks:
        date_str = track.get('date', '')
        if not date_str or ' ' not in date_str:
            continue
        
        try:
            time_part = date_str.split(' ')[1]
            hour = int(time_part.split(':')[0])
            hourly[hour].append(track)
        except (ValueError, IndexError):
            continue
    
    return dict(hourly)


def get_available_dates(tracks: List[Dict]) -> List[str]:
    """
    Get list of available dates in the history.
    
    Returns:
        Sorted list of unique dates (YYYY-MM-DD)
    """
    dates = set()
    for track in tracks:
        date_str = track.get('date', '')
        if date_str and ' ' in date_str:
            date_part = date_str.split(' ')[0]
            dates.add(date_part)
    
    return sorted(dates, reverse=True)


@click.group(name='timeline')
def timeline_group():
    """Timeline de visualisation horaire."""
    pass


@timeline_group.command(name='display')
@click.option('--date', help='Date à afficher (YYYY-MM-DD, défaut: aujourd\'hui)')
@click.option('--compact', is_flag=True, help='Mode compact (titres uniquement)')
@click.option('--start-hour', type=int, default=6, help='Heure de début (défaut: 6)')
@click.option('--end-hour', type=int, default=23, help='Heure de fin (défaut: 23)')
def display_timeline(date, compact, start_hour, end_hour):
    """
    Affiche la timeline horaire des écoutes.
    
    Exemples:
        timeline display
        timeline display --date 2026-01-27
        timeline display --compact
        timeline display --start-hour 8 --end-hour 22
    """
    # Load data
    loader = get_loader()
    history = loader.load_history()
    
    if history is None or not history:
        console.print("[yellow]⚠️  Aucun historique trouvé[/yellow]")
        return
    
    # Determine date to display
    if not date:
        # Use today or most recent date in history
        available_dates = get_available_dates(history)
        if not available_dates:
            console.print("[yellow]⚠️  Aucune date disponible dans l'historique[/yellow]")
            return
        date = available_dates[0]  # Most recent
    
    # Filter tracks for the date
    day_tracks = get_tracks_by_date(history, date)
    
    if not day_tracks:
        console.print(f"[yellow]⚠️  Aucune écoute le {date}[/yellow]")
        console.print("\n💡 Dates disponibles:")
        available = get_available_dates(history)
        for d in available[:10]:
            console.print(f"   • {d}")
        if len(available) > 10:
            console.print(f"   ... et {len(available) - 10} autres dates")
        return
    
    # Group by hour
    hourly_tracks = group_by_hour(day_tracks)
    
    # Calculate statistics
    total_tracks = len(day_tracks)
    unique_artists = len(set(t.get('artist', 'Unknown') for t in day_tracks))
    unique_albums = len(set(t.get('album', 'Unknown') for t in day_tracks))
    peak_hour = max(hourly_tracks.items(), key=lambda x: len(x[1]))[0] if hourly_tracks else None
    
    # Display header
    header_text = Text()
    header_text.append(f"📅 Timeline - {date}\n\n", style=get_style(SemanticColor.PRIMARY) + Style(bold=True))
    header_text.append(f"Total: ", style=get_style(SemanticColor.MUTED))
    header_text.append(f"{total_tracks} tracks ", style=get_style(SemanticColor.EMPHASIS))
    header_text.append(f"• ", style=get_style(SemanticColor.MUTED))
    header_text.append(f"{unique_artists} artistes ", style=get_style(SemanticColor.ARTIST))
    header_text.append(f"• ", style=get_style(SemanticColor.MUTED))
    header_text.append(f"{unique_albums} albums", style=get_style(SemanticColor.ALBUM))
    if peak_hour is not None:
        header_text.append(f"\nHeure de pointe: ", style=get_style(SemanticColor.MUTED))
        header_text.append(f"{peak_hour}h", style=get_style(SemanticColor.EMPHASIS))
    
    console.print(Panel(header_text, border_style=get_style(SemanticColor.PRIMARY)))
    console.print()
    
    # Display timeline
    for hour in range(start_hour, end_hour + 1):
        tracks = hourly_tracks.get(hour, [])
        track_count = len(tracks)
        
        # Hour header with alternating colors
        hour_style = get_style(SemanticColor.PRIMARY) if hour % 2 == 0 else get_style(SemanticColor.SECONDARY)
        hour_text = Text()
        hour_text.append(f"{hour:02d}h ", style=hour_style + Style(bold=True))
        
        if track_count == 0:
            hour_text.append("─" * 50, style=get_style(SemanticColor.MUTED))
        else:
            hour_text.append(f"({track_count} tracks) ", style=get_style(SemanticColor.MUTED))
            
            if compact:
                # Compact mode: show track titles only
                titles = [t.get('title', 'Unknown')[:30] for t in tracks[:20]]
                hour_text.append(" • ".join(titles), style=get_style(SemanticColor.TRACK))
                if track_count > 20:
                    hour_text.append(f" ... +{track_count - 20} more", style=get_style(SemanticColor.MUTED))
            else:
                # Detailed mode: show artist - title - album
                console.print(hour_text)
                for i, track in enumerate(tracks[:20], 1):
                    artist = track.get('artist', 'Unknown')
                    title = track.get('title', 'Unknown')
                    album = track.get('album', 'Unknown')
                    time_part = track.get('date', '').split(' ')[1] if ' ' in track.get('date', '') else '??:??'
                    
                    # Truncate long strings
                    artist = artist[:25] + "..." if len(artist) > 25 else artist
                    title = title[:30] + "..." if len(title) > 30 else title
                    album = album[:30] + "..." if len(album) > 30 else album
                    
                    track_text = Text()
                    track_text.append(f"  {i:2d}. ", style=get_style(SemanticColor.MUTED))
                    track_text.append(f"{time_part} ", style=get_style(SemanticColor.MUTED))
                    track_text.append(f"{artist}", style=get_style(SemanticColor.ARTIST))
                    track_text.append(f" - ", style=get_style(SemanticColor.MUTED))
                    track_text.append(f"{title}", style=get_style(SemanticColor.TRACK))
                    track_text.append(f" ({album})", style=get_style(SemanticColor.ALBUM))
                    
                    if track.get('loved', False):
                        track_text.append(" ♥", style=get_style(SemanticColor.LOVED))
                    
                    console.print(track_text)
                
                if track_count > 20:
                    console.print(f"  ... +{track_count - 20} tracks supplémentaires", 
                                style=get_style(SemanticColor.MUTED))
                console.print()
                continue
        
        console.print(hour_text)


@timeline_group.command(name='list-dates')
@click.option('--limit', type=int, default=30, help='Nombre de dates à afficher')
def list_dates(limit):
    """
    Liste les dates disponibles dans l'historique.
    
    Exemples:
        timeline list-dates
        timeline list-dates --limit 10
    """
    # Load data
    loader = get_loader()
    history = loader.load_history()
    
    if history is None or not history:
        console.print("[yellow]⚠️  Aucun historique trouvé[/yellow]")
        return
    
    # Get available dates
    dates = get_available_dates(history)
    
    if not dates:
        console.print("[yellow]⚠️  Aucune date disponible[/yellow]")
        return
    
    # Count tracks per date
    date_counts = {}
    for date in dates:
        date_tracks = get_tracks_by_date(history, date)
        date_counts[date] = len(date_tracks)
    
    # Create table
    table = Table(
        title=f"📅 Dates Disponibles ({len(dates)} jours)",
        show_header=True,
        header_style=get_style(SemanticColor.PRIMARY)
    )
    
    table.add_column("Date", style=get_style(SemanticColor.EMPHASIS), width=12)
    table.add_column("Tracks", justify="right", style=get_style(SemanticColor.MUTED), width=8)
    table.add_column("Graphique", width=50)
    
    # Show limited dates
    display_dates = dates[:limit]
    max_count = max(date_counts.values()) if date_counts else 1
    
    for date in display_dates:
        count = date_counts.get(date, 0)
        
        # Create bar chart
        bar_length = int((count / max_count) * 40) if max_count > 0 else 0
        bar = "█" * bar_length
        
        table.add_row(
            date,
            str(count),
            Text(bar, style=get_style(SemanticColor.PRIMARY))
        )
    
    console.print(table)
    
    if len(dates) > limit:
        console.print(f"\n💡 {len(dates) - limit} dates supplémentaires disponibles")
        console.print(f"   Utilisez [cyan]--limit {len(dates)}[/cyan] pour tout afficher")


@timeline_group.command(name='hourly-stats')
@click.option('--date', help='Date à analyser (YYYY-MM-DD, défaut: toutes)')
def hourly_stats(date):
    """
    Affiche les statistiques par heure.
    
    Exemples:
        timeline hourly-stats
        timeline hourly-stats --date 2026-01-27
    """
    # Load data
    loader = get_loader()
    history = loader.load_history()
    
    if history is None or not history:
        console.print("[yellow]⚠️  Aucun historique trouvé[/yellow]")
        return
    
    # Filter by date if specified
    if date:
        history = get_tracks_by_date(history, date)
        if not history:
            console.print(f"[yellow]⚠️  Aucune écoute le {date}[/yellow]")
            return
    
    # Group by hour
    hourly_tracks = group_by_hour(history)
    
    if not hourly_tracks:
        console.print("[yellow]⚠️  Aucune donnée horaire disponible[/yellow]")
        return
    
    # Calculate stats per hour
    hourly_stats_data = {}
    for hour, tracks in hourly_tracks.items():
        artists = set(t.get('artist', 'Unknown') for t in tracks)
        albums = set(t.get('album', 'Unknown') for t in tracks)
        hourly_stats_data[hour] = {
            'count': len(tracks),
            'artists': len(artists),
            'albums': len(albums)
        }
    
    # Create table
    title = f"⏰ Statistiques Horaires"
    if date:
        title += f" - {date}"
    
    table = Table(
        title=title,
        show_header=True,
        header_style=get_style(SemanticColor.PRIMARY)
    )
    
    table.add_column("Heure", style=get_style(SemanticColor.EMPHASIS), width=8)
    table.add_column("Tracks", justify="right", style=get_style(SemanticColor.MUTED), width=8)
    table.add_column("Artistes", justify="right", style=get_style(SemanticColor.ARTIST), width=10)
    table.add_column("Albums", justify="right", style=get_style(SemanticColor.ALBUM), width=10)
    table.add_column("Activité", width=40)
    
    # Find max for scaling
    max_count = max(s['count'] for s in hourly_stats_data.values())
    
    # Display all hours (0-23)
    for hour in range(24):
        if hour in hourly_stats_data:
            stats = hourly_stats_data[hour]
            count = stats['count']
            artists = stats['artists']
            albums = stats['albums']
            
            # Activity bar
            bar_length = int((count / max_count) * 30) if max_count > 0 else 0
            bar = "█" * bar_length
            bar_style = get_style(SemanticColor.PRIMARY) if count > 0 else get_style(SemanticColor.MUTED)
            
            table.add_row(
                f"{hour:02d}h",
                str(count),
                str(artists),
                str(albums),
                Text(bar, style=bar_style)
            )
        else:
            # No activity for this hour
            table.add_row(
                f"{hour:02d}h",
                "0",
                "0",
                "0",
                Text("─", style=get_style(SemanticColor.MUTED))
            )
    
    console.print(table)
