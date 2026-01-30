"""
AI Logs Commands - Display AI-generated album information logs

Shows daily AI logs with album information enrichment.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 30 janvier 2026
"""

import click
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.table import Table

from ..ui.colors import SemanticColor, apply_color, get_style


console = Console()


def get_ai_logs_path() -> Path:
    """Get path to AI logs directory."""
    # From src/cli/commands, go up to project root
    base_path = Path(__file__).parent.parent.parent.parent
    return base_path / 'output' / 'ai-logs'


def list_ai_log_files() -> List[str]:
    """
    List available AI log files.
    
    Returns:
        Sorted list of log file names (newest first)
    """
    logs_path = get_ai_logs_path()
    
    if not logs_path.exists():
        return []
    
    log_files = []
    for file in logs_path.glob('ai-log-*.txt'):
        log_files.append(file.name)
    
    return sorted(log_files, reverse=True)


def parse_ai_log_file(file_path: Path) -> List[Dict[str, str]]:
    """
    Parse an AI log file into structured entries.
    
    Format expected:
        === YYYY-MM-DD HH:MM:SS ===
        Artiste: Artist Name
        Album: Album Name
        Info: [IA] Description text
        
    Returns:
        List of entries with timestamp, artist, album, info
    """
    entries = []
    
    if not file_path.exists():
        return entries
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a timestamp line (between ===)
            if line.startswith('===') and line.endswith('==='):
                # Save previous entry if complete
                if current_entry and 'artist' in current_entry:
                    entries.append(current_entry)
                
                # Start new entry with timestamp
                timestamp = line.replace('===', '').strip()
                current_entry = {'timestamp': timestamp}
            
            elif line.startswith('Artiste:'):
                current_entry['artist'] = line.replace('Artiste:', '').strip()
            
            elif line.startswith('Album:'):
                current_entry['album'] = line.replace('Album:', '').strip()
            
            elif line.startswith('Info:'):
                current_entry['info'] = line.replace('Info:', '').strip()
        
        # Don't forget the last entry
        if current_entry and 'artist' in current_entry:
            entries.append(current_entry)
    
    except Exception as e:
        console.print(f"[red]❌ Erreur lors de la lecture du fichier: {e}[/red]")
        return []
    
    return entries


def extract_date_from_filename(filename: str) -> Optional[str]:
    """
    Extract date from log filename.
    
    Args:
        filename: e.g. 'ai-log-2026-01-27.txt'
        
    Returns:
        Date string (YYYY-MM-DD) or None
    """
    try:
        # Remove 'ai-log-' prefix and '.txt' suffix
        date_part = filename.replace('ai-log-', '').replace('.txt', '')
        # Validate format
        datetime.strptime(date_part, '%Y-%m-%d')
        return date_part
    except (ValueError, AttributeError):
        return None


@click.group(name='ai-logs')
def ai_logs_group():
    """Journaux d'enrichissement IA."""
    pass


@ai_logs_group.command(name='list')
def list_logs():
    """
    Liste les fichiers de logs IA disponibles.
    
    Exemples:
        ai-logs list
    """
    log_files = list_ai_log_files()
    
    if not log_files:
        console.print("[yellow]⚠️  Aucun log IA trouvé[/yellow]")
        console.print("\n💡 Les logs sont générés automatiquement par chk-roon.py")
        console.print("   Emplacement: output/ai-logs/ai-log-YYYY-MM-DD.txt")
        return
    
    # Create table
    table = Table(
        title=f"🤖 Logs d'Enrichissement IA ({len(log_files)} fichiers)",
        show_header=True,
        header_style=get_style(SemanticColor.PRIMARY)
    )
    
    table.add_column("Fichier", style=get_style(SemanticColor.EMPHASIS), width=25)
    table.add_column("Date", style=get_style(SemanticColor.MUTED), width=12)
    table.add_column("Taille", justify="right", style=get_style(SemanticColor.MUTED), width=10)
    
    logs_path = get_ai_logs_path()
    
    for filename in log_files:
        file_path = logs_path / filename
        
        # Extract date
        date = extract_date_from_filename(filename)
        date_display = date if date else "N/A"
        
        # Get file size
        try:
            size_bytes = file_path.stat().st_size
            if size_bytes < 1024:
                size_display = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_display = f"{size_bytes / 1024:.1f} KB"
            else:
                size_display = f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            size_display = "N/A"
        
        table.add_row(filename, date_display, size_display)
    
    console.print(table)
    console.print(f"\n💡 Utilisez [cyan]ai-logs view --date {extract_date_from_filename(log_files[0])}[/cyan] pour voir le contenu")


@ai_logs_group.command(name='view')
@click.option('--date', help='Date du log à afficher (YYYY-MM-DD)')
@click.option('--file', help='Nom du fichier log à afficher')
@click.option('--limit', type=int, help='Nombre d\'entrées à afficher (défaut: toutes)')
def view_log(date, file, limit):
    """
    Affiche le contenu d'un log IA.
    
    Exemples:
        ai-logs view --date 2026-01-27
        ai-logs view --file ai-log-2026-01-27.txt
        ai-logs view --date 2026-01-27 --limit 10
    """
    logs_path = get_ai_logs_path()
    
    # Determine file to read
    if file:
        file_path = logs_path / file
    elif date:
        file_path = logs_path / f'ai-log-{date}.txt'
    else:
        # Use most recent file
        log_files = list_ai_log_files()
        if not log_files:
            console.print("[yellow]⚠️  Aucun log IA trouvé[/yellow]")
            return
        file_path = logs_path / log_files[0]
    
    if not file_path.exists():
        console.print(f"[red]❌ Fichier non trouvé: {file_path.name}[/red]")
        console.print("\n💡 Fichiers disponibles:")
        for f in list_ai_log_files()[:10]:
            console.print(f"   • {f}")
        return
    
    # Parse log file
    entries = parse_ai_log_file(file_path)
    
    if not entries:
        console.print(f"[yellow]⚠️  Aucune entrée trouvée dans {file_path.name}[/yellow]")
        return
    
    # Apply limit if specified
    display_entries = entries[:limit] if limit else entries
    showing_all = len(display_entries) == len(entries)
    
    # Display header
    date_display = extract_date_from_filename(file_path.name) or "N/A"
    header_text = Text()
    header_text.append(f"🤖 Log IA - {date_display}\n\n", 
                      style=get_style(SemanticColor.PRIMARY) + Style(bold=True))
    header_text.append(f"Total: ", style=get_style(SemanticColor.MUTED))
    header_text.append(f"{len(entries)} entrées", style=get_style(SemanticColor.EMPHASIS))
    if not showing_all:
        header_text.append(f" (affichage: {len(display_entries)})", 
                          style=get_style(SemanticColor.MUTED))
    
    console.print(Panel(header_text, border_style=get_style(SemanticColor.PRIMARY)))
    console.print()
    
    # Display entries
    for i, entry in enumerate(display_entries, 1):
        entry_text = Text()
        
        # Timestamp
        entry_text.append(f"[{i}/{len(entries)}] ", style=get_style(SemanticColor.MUTED))
        entry_text.append(f"{entry.get('timestamp', 'N/A')}\n", 
                         style=get_style(SemanticColor.EMPHASIS))
        
        # Artist
        entry_text.append("Artiste: ", style=get_style(SemanticColor.MUTED))
        entry_text.append(f"{entry.get('artist', 'Unknown')}\n", 
                         style=get_style(SemanticColor.ARTIST))
        
        # Album
        entry_text.append("Album: ", style=get_style(SemanticColor.MUTED))
        entry_text.append(f"{entry.get('album', 'Unknown')}\n", 
                         style=get_style(SemanticColor.ALBUM))
        
        # Info
        info = entry.get('info', 'N/A')
        entry_text.append("\nInfo: ", style=get_style(SemanticColor.MUTED))
        entry_text.append(f"{info}\n", style=get_style(SemanticColor.EMPHASIS))
        
        console.print(Panel(
            entry_text,
            border_style=get_style(SemanticColor.SECONDARY)
        ))
        console.print()
    
    if not showing_all:
        console.print(f"💡 {len(entries) - len(display_entries)} entrées supplémentaires")
        console.print(f"   Utilisez [cyan]--limit {len(entries)}[/cyan] pour tout afficher")


@ai_logs_group.command(name='stats')
@click.option('--date', help='Date du log à analyser (YYYY-MM-DD)')
def show_stats(date):
    """
    Affiche les statistiques d'un log IA.
    
    Exemples:
        ai-logs stats
        ai-logs stats --date 2026-01-27
    """
    logs_path = get_ai_logs_path()
    
    # Determine file to read
    if date:
        file_path = logs_path / f'ai-log-{date}.txt'
    else:
        # Use most recent file
        log_files = list_ai_log_files()
        if not log_files:
            console.print("[yellow]⚠️  Aucun log IA trouvé[/yellow]")
            return
        file_path = logs_path / log_files[0]
    
    if not file_path.exists():
        console.print(f"[red]❌ Fichier non trouvé: {file_path.name}[/red]")
        return
    
    # Parse log file
    entries = parse_ai_log_file(file_path)
    
    if not entries:
        console.print(f"[yellow]⚠️  Aucune entrée trouvée dans {file_path.name}[/yellow]")
        return
    
    # Calculate statistics
    total = len(entries)
    artists = set(e.get('artist', 'Unknown') for e in entries)
    albums = set(e.get('album', 'Unknown') for e in entries)
    
    # Average info length
    info_lengths = [len(e.get('info', '')) for e in entries]
    avg_length = sum(info_lengths) / len(info_lengths) if info_lengths else 0
    
    # Check for [IA] vs [Discogs] sources
    ia_count = sum(1 for e in entries if '[IA]' in e.get('info', ''))
    discogs_count = sum(1 for e in entries if '[Discogs]' in e.get('info', ''))
    other_count = total - ia_count - discogs_count
    
    # Display statistics panel
    date_display = extract_date_from_filename(file_path.name) or "N/A"
    
    stats_text = Text()
    stats_text.append(f"🤖 Statistiques - {date_display}\n\n", 
                     style=get_style(SemanticColor.PRIMARY) + Style(bold=True))
    
    stats_text.append("Total entrées: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{total}\n", style=get_style(SemanticColor.EMPHASIS))
    
    stats_text.append("Artistes uniques: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{len(artists)}\n", style=get_style(SemanticColor.ARTIST))
    
    stats_text.append("Albums uniques: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{len(albums)}\n", style=get_style(SemanticColor.ALBUM))
    
    stats_text.append("\n📊 Sources d'information\n\n", 
                     style=get_style(SemanticColor.PRIMARY))
    
    stats_text.append("IA générée: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{ia_count} ({ia_count * 100 / total:.1f}%)\n" if total > 0 else "0\n", 
                     style=get_style(SemanticColor.SUCCESS))
    
    stats_text.append("Discogs: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{discogs_count} ({discogs_count * 100 / total:.1f}%)\n" if total > 0 else "0\n", 
                     style=get_style(SemanticColor.SECONDARY))
    
    if other_count > 0:
        stats_text.append("Autre: ", style=get_style(SemanticColor.MUTED))
        stats_text.append(f"{other_count}\n", style=get_style(SemanticColor.WARNING))
    
    stats_text.append("\n📏 Longueur moyenne: ", style=get_style(SemanticColor.MUTED))
    stats_text.append(f"{avg_length:.0f} caractères", style=get_style(SemanticColor.EMPHASIS))
    
    panel = Panel(
        stats_text,
        title="🤖 Statistiques du Log IA",
        border_style=get_style(SemanticColor.PRIMARY)
    )
    
    console.print(panel)
