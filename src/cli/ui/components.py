"""
Reusable UI Components for CLI

Provides reusable components like tables, panels, and interactive menus.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 29 janvier 2026
"""

from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.table import Table as RichTable
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout

from .colors import SemanticColor, apply_color


class PaginatedTable:
    """
    Paginated table component with navigation.
    
    Features:
        - Automatic pagination
        - Column formatting
        - Sorting support
        - Custom row formatting
    """
    
    def __init__(
        self,
        console: Console,
        title: str,
        columns: List[str],
        data: List[Dict[str, Any]],
        page_size: int = 25,
        show_index: bool = False
    ):
        """
        Initialize paginated table.
        
        Args:
            console: Rich Console instance
            title: Table title
            columns: Column names (keys in data dicts)
            data: List of data dicts
            page_size: Items per page
            show_index: Show row index column
        """
        self.console = console
        self.title = title
        self.columns = columns
        self.data = data
        self.page_size = page_size
        self.show_index = show_index
        self.current_page = 0
    
    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        if not self.data:
            return 0
        return (len(self.data) + self.page_size - 1) // self.page_size
    
    def get_page_data(self, page: int) -> List[Dict[str, Any]]:
        """
        Get data for specific page.
        
        Args:
            page: Page number (0-indexed)
            
        Returns:
            List of data dicts for the page
        """
        start = page * self.page_size
        end = start + self.page_size
        return self.data[start:end]
    
    def render_page(self, page: int = 0) -> RichTable:
        """
        Render table for specific page.
        
        Args:
            page: Page number (0-indexed)
            
        Returns:
            Rich Table instance
        """
        # Create table
        table = RichTable(
            title=f"{self.title} ({len(self.data)} items)",
            show_header=True,
            header_style="bold cyan",
            show_lines=False,
            padding=(0, 1)
        )
        
        # Add index column if requested
        if self.show_index:
            table.add_column("#", style="dim", width=5)
        
        # Add data columns
        for col in self.columns:
            table.add_column(col)
        
        # Add rows for current page
        page_data = self.get_page_data(page)
        start_index = page * self.page_size
        
        for i, row in enumerate(page_data, start=start_index + 1):
            values = []
            
            if self.show_index:
                values.append(str(i))
            
            for col in self.columns:
                value = row.get(col, "")
                # Handle list values (e.g., artists)
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                values.append(str(value))
            
            table.add_row(*values)
        
        return table
    
    def show_page(self, page: int = 0):
        """
        Display specific page.
        
        Args:
            page: Page number (0-indexed)
        """
        if page < 0 or page >= self.total_pages:
            return
        
        self.current_page = page
        table = self.render_page(page)
        self.console.print(table)
        
        # Show pagination info
        if self.total_pages > 1:
            start = page * self.page_size + 1
            end = min((page + 1) * self.page_size, len(self.data))
            footer = f"\n[dim]Showing {start}-{end} of {len(self.data)} | Page {page + 1}/{self.total_pages}[/dim]"
            self.console.print(footer)


class AlbumDetailPanel:
    """
    Detailed view panel for a single album.
    """
    
    def __init__(self, console: Console, album: Dict[str, Any]):
        """
        Initialize album detail panel.
        
        Args:
            console: Rich Console instance
            album: Album data dict
        """
        self.console = console
        self.album = album
    
    def render(self) -> Panel:
        """
        Render album details as a Rich Panel.
        
        Returns:
            Rich Panel instance
        """
        # Build content
        lines = []
        
        # Title and Artist
        title = self.album.get('Titre', 'Unknown')
        artist = self.album.get('Artiste', ['Unknown'])
        if isinstance(artist, list):
            artist_str = ", ".join(artist)
        else:
            artist_str = str(artist)
        
        lines.append(f"[bold cyan]{title}[/bold cyan]")
        lines.append(f"[magenta]{artist_str}[/magenta]")
        lines.append("")
        
        # Metadata
        year = self.album.get('Annee')
        if year:
            lines.append(f"[white]Year:[/white] {year}")
        
        support = self.album.get('Support')
        if support:
            lines.append(f"[white]Support:[/white] {support}")
        
        label = self.album.get('Label')
        if label:
            lines.append(f"[white]Label:[/white] {label}")
        
        release_id = self.album.get('Release_ID')
        if release_id:
            lines.append(f"[white]Discogs ID:[/white] {release_id}")
        
        # Soundtrack info
        film = self.album.get('Film')
        if film:
            lines.append("")
            lines.append(f"[yellow]🎬 Soundtrack:[/yellow] {film}")
            director = self.album.get('Realisateur')
            if director:
                lines.append(f"[dim]Director:[/dim] {director}")
        
        # Summary/Resume
        resume = self.album.get('Resume')
        if resume and resume != "Aucune information disponible":
            lines.append("")
            lines.append("[white]Description:[/white]")
            # Truncate long descriptions
            if len(resume) > 300:
                resume = resume[:297] + "..."
            lines.append(f"[dim]{resume}[/dim]")
        
        # URLs
        lines.append("")
        spotify_url = self.album.get('Spotify_Cover_URL')
        if spotify_url:
            lines.append(f"[blue]🎵 Spotify:[/blue] {spotify_url[:50]}...")
        
        discogs_url = self.album.get('Pochette')
        if discogs_url:
            lines.append(f"[green]💿 Discogs:[/green] {discogs_url[:50]}...")
        
        content = "\n".join(lines)
        
        return Panel(
            content,
            title="Album Details",
            border_style="cyan",
            padding=(1, 2)
        )
    
    def show(self):
        """Display the panel."""
        panel = self.render()
        self.console.print(panel)


class TrackListTable:
    """
    Table for displaying listening history tracks.
    """
    
    def __init__(
        self,
        console: Console,
        tracks: List[Dict[str, Any]],
        page_size: int = 25
    ):
        """
        Initialize track list table.
        
        Args:
            console: Rich Console instance
            tracks: List of track dicts
            page_size: Items per page
        """
        self.console = console
        self.tracks = tracks
        self.page_size = page_size
    
    def render_page(self, page: int = 0) -> RichTable:
        """
        Render tracks for specific page.
        
        Args:
            page: Page number (0-indexed)
            
        Returns:
            Rich Table instance
        """
        # Create table
        table = RichTable(
            title=f"Listening History ({len(self.tracks)} tracks)",
            show_header=True,
            header_style="bold cyan",
            show_lines=False
        )
        
        # Add columns
        table.add_column("Date", style="dim", width=16)
        table.add_column("Artist", style="magenta")
        table.add_column("Track", style="white")
        table.add_column("Album", style="cyan italic")
        table.add_column("Source", width=8)
        table.add_column("♥", width=3)
        
        # Get page data
        start = page * self.page_size
        end = start + self.page_size
        page_tracks = self.tracks[start:end]
        
        # Add rows
        for track in page_tracks:
            date = track.get('date', '')
            artist = track.get('artist', 'Unknown')
            title = track.get('title', 'Unknown')
            album = track.get('album', 'Unknown')
            source = track.get('source', '')
            loved = track.get('loved', False)
            
            # Format source with icon
            if source == 'roon':
                source_display = "🎵 Roon"
            elif source == 'lastfm':
                source_display = "📻 Last"
            else:
                source_display = source
            
            # Loved indicator
            loved_display = "❤️" if loved else ""
            
            table.add_row(
                date,
                artist,
                title,
                album,
                source_display,
                loved_display
            )
        
        return table
    
    def show_page(self, page: int = 0):
        """
        Display specific page.
        
        Args:
            page: Page number (0-indexed)
        """
        total_pages = (len(self.tracks) + self.page_size - 1) // self.page_size
        
        if page < 0 or page >= total_pages:
            return
        
        table = self.render_page(page)
        self.console.print(table)
        
        # Show pagination info
        if total_pages > 1:
            start = page * self.page_size + 1
            end = min((page + 1) * self.page_size, len(self.tracks))
            footer = f"\n[dim]Showing {start}-{end} of {len(self.tracks)} | Page {page + 1}/{total_pages}[/dim]"
            self.console.print(footer)


class StatsPanel:
    """
    Statistics display panel.
    """
    
    def __init__(self, console: Console, title: str, stats: Dict[str, Any]):
        """
        Initialize stats panel.
        
        Args:
            console: Rich Console instance
            title: Panel title
            stats: Statistics dict
        """
        self.console = console
        self.title = title
        self.stats = stats
    
    def render(self) -> Panel:
        """
        Render statistics as a Rich Panel.
        
        Returns:
            Rich Panel instance
        """
        lines = []
        
        for key, value in self.stats.items():
            # Format key (convert snake_case to Title Case)
            key_formatted = key.replace('_', ' ').title()
            
            # Format value
            if isinstance(value, dict):
                lines.append(f"[white]{key_formatted}:[/white]")
                for sub_key, sub_value in value.items():
                    lines.append(f"  [dim]{sub_key}:[/dim] {sub_value}")
            elif isinstance(value, tuple):
                lines.append(f"[white]{key_formatted}:[/white] {value[0]}-{value[1]}")
            else:
                lines.append(f"[white]{key_formatted}:[/white] [cyan]{value}[/cyan]")
        
        content = "\n".join(lines)
        
        return Panel(
            content,
            title=self.title,
            border_style="cyan",
            padding=(1, 2)
        )
    
    def show(self):
        """Display the panel."""
        panel = self.render()
        self.console.print(panel)


def format_album_line(album: Dict[str, Any]) -> str:
    """
    Format album as a single line with semantic colors.
    
    Args:
        album: Album data dict
        
    Returns:
        Formatted string with Rich markup
    """
    title = album.get('Titre', 'Unknown')
    artist = album.get('Artiste', ['Unknown'])
    year = album.get('Annee', '')
    
    if isinstance(artist, list):
        artist_str = ", ".join(artist)
    else:
        artist_str = str(artist)
    
    # Apply semantic colors
    title_colored = apply_color(title, SemanticColor.ALBUM)
    artist_colored = apply_color(artist_str, SemanticColor.ARTIST)
    year_colored = apply_color(f"({year})", SemanticColor.YEAR) if year else ""
    
    return f"{title_colored} - {artist_colored} {year_colored}".strip()


def format_track_line(track: Dict[str, Any]) -> str:
    """
    Format track as a single line with semantic colors.
    
    Args:
        track: Track data dict
        
    Returns:
        Formatted string with Rich markup
    """
    artist = track.get('artist', 'Unknown')
    title = track.get('title', 'Unknown')
    album = track.get('album', 'Unknown')
    source = track.get('source', '')
    loved = track.get('loved', False)
    
    # Apply semantic colors
    artist_colored = apply_color(artist, SemanticColor.ARTIST)
    title_colored = apply_color(title, SemanticColor.TRACK)
    album_colored = apply_color(album, SemanticColor.ALBUM)
    
    # Source icon
    if source == 'roon':
        source_role = SemanticColor.SOURCE_ROON
        source_icon = "🎵"
    elif source == 'lastfm':
        source_role = SemanticColor.SOURCE_LASTFM
        source_icon = "📻"
    else:
        source_role = SemanticColor.MUTED
        source_icon = "?"
    
    source_colored = apply_color(f"{source_icon} {source}", source_role)
    
    # Loved indicator
    loved_indicator = ""
    if loved:
        loved_indicator = " " + apply_color("❤️", SemanticColor.LOVED)
    
    return f"{artist_colored} - {title_colored} [{album_colored}] | {source_colored}{loved_indicator}"
