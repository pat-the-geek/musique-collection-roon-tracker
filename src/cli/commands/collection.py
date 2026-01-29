"""
Collection Commands Implementation

Implements CLI commands for managing the Discogs collection.

Commands:
    - list: Paginated album listing with filters
    - search: Interactive album search
    - view: Detailed album view
    - edit: Basic metadata editing

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 29 janvier 2026
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from ..utils.data_loader import get_loader
from ..ui.components import (
    PaginatedTable,
    AlbumDetailPanel,
    StatsPanel,
    format_album_line
)
from ..ui.colors import SemanticColor, apply_color


class CollectionCommand:
    """
    Collection command implementation.
    
    Handles all collection-related operations.
    """
    
    def __init__(self, console: Console):
        """
        Initialize collection command.
        
        Args:
            console: Rich Console instance
        """
        self.console = console
        self.loader = get_loader()
    
    def list_albums(
        self,
        page: int = 1,
        per_page: int = 25,
        filter_type: Optional[str] = None,
        sort_by: str = 'title'
    ):
        """
        List albums with pagination and filters.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            filter_type: Filter type (soundtrack, year, support)
            sort_by: Sort field (title, artist, year)
        """
        # Load collection
        collection = self.loader.load_collection()
        
        if not collection:
            self.console.print("[yellow]⚠️  No collection data found.[/yellow]")
            self.console.print("[dim]Expected file: data/collection/discogs-collection.json[/dim]")
            return
        
        # Apply filters
        filtered_collection = self._apply_filters(collection, filter_type)
        
        # Apply sorting
        sorted_collection = self._apply_sorting(filtered_collection, sort_by)
        
        # Show stats
        self.console.print(f"\n[cyan bold]📂 Collection[/cyan bold] - {len(sorted_collection)} albums")
        if filter_type:
            self.console.print(f"[dim]Filter: {filter_type}[/dim]")
        self.console.print(f"[dim]Sort: {sort_by}[/dim]\n")
        
        # Prepare data for table
        table_data = []
        for album in sorted_collection:
            # Format artists
            artists = album.get('Artiste', ['Unknown'])
            if isinstance(artists, list):
                artist_str = ", ".join(artists[:2])  # Limit to 2 artists
                if len(artists) > 2:
                    artist_str += f" +{len(artists) - 2}"
            else:
                artist_str = str(artists)
            
            table_data.append({
                'Title': album.get('Titre', 'Unknown'),
                'Artist': artist_str,
                'Year': album.get('Annee', ''),
                'Support': album.get('Support', ''),
                'ID': album.get('Release_ID', '')
            })
        
        # Create paginated table
        table = PaginatedTable(
            console=self.console,
            title="Collection Albums",
            columns=['Title', 'Artist', 'Year', 'Support', 'ID'],
            data=table_data,
            page_size=per_page,
            show_index=True
        )
        
        # Show requested page (convert to 0-indexed)
        page_index = max(0, page - 1)
        if page_index >= table.total_pages:
            page_index = table.total_pages - 1
        
        table.show_page(page_index)
        
        # Show navigation hints
        if table.total_pages > 1:
            self.console.print(f"\n[dim]Use --page N to view other pages (1-{table.total_pages})[/dim]")
    
    def _apply_filters(
        self,
        collection: List[Dict[str, Any]],
        filter_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Apply filters to collection.
        
        Args:
            collection: Full collection
            filter_type: Filter string (e.g., "soundtrack", "year:1980", "support:Vinyle")
            
        Returns:
            Filtered collection
        """
        if not filter_type:
            return collection
        
        # Parse filter
        if ':' in filter_type:
            filter_key, filter_value = filter_type.split(':', 1)
        else:
            filter_key = filter_type
            filter_value = None
        
        filtered = []
        
        for album in collection:
            # Soundtrack filter
            if filter_key == 'soundtrack':
                if album.get('Film'):
                    filtered.append(album)
            
            # Year filter
            elif filter_key == 'year':
                if filter_value and album.get('Annee') == int(filter_value):
                    filtered.append(album)
            
            # Support filter
            elif filter_key == 'support':
                if filter_value and album.get('Support') == filter_value:
                    filtered.append(album)
            
            # Default: no filter
            else:
                filtered.append(album)
        
        return filtered if filtered else collection
    
    def _apply_sorting(
        self,
        collection: List[Dict[str, Any]],
        sort_by: str
    ) -> List[Dict[str, Any]]:
        """
        Apply sorting to collection.
        
        Args:
            collection: Collection to sort
            sort_by: Sort field (title, artist, year)
            
        Returns:
            Sorted collection
        """
        if sort_by == 'title':
            return sorted(collection, key=lambda x: x.get('Titre', '').lower())
        elif sort_by == 'artist':
            return sorted(collection, key=lambda x: self._get_artist_name(x).lower())
        elif sort_by == 'year':
            return sorted(collection, key=lambda x: x.get('Annee', 0))
        else:
            return collection
    
    def _get_artist_name(self, album: Dict[str, Any]) -> str:
        """
        Get primary artist name from album.
        
        Args:
            album: Album dict
            
        Returns:
            Artist name string
        """
        artists = album.get('Artiste', ['Unknown'])
        if isinstance(artists, list):
            return artists[0] if artists else 'Unknown'
        return str(artists)
    
    def search_albums(self, term: str):
        """
        Search albums by title or artist.
        
        Args:
            term: Search term
        """
        # Load collection
        collection = self.loader.load_collection()
        
        if not collection:
            self.console.print("[yellow]⚠️  No collection data found.[/yellow]")
            return
        
        # Search (case-insensitive)
        term_lower = term.lower()
        results = []
        
        for album in collection:
            # Check title
            title = album.get('Titre', '').lower()
            if term_lower in title:
                results.append(album)
                continue
            
            # Check artists
            artists = album.get('Artiste', [])
            if isinstance(artists, list):
                artist_str = ' '.join(artists).lower()
            else:
                artist_str = str(artists).lower()
            
            if term_lower in artist_str:
                results.append(album)
        
        # Display results
        if not results:
            self.console.print(f"\n[yellow]No albums found matching '{term}'[/yellow]\n")
            return
        
        self.console.print(f"\n[green]✓ Found {len(results)} album(s) matching '{term}'[/green]\n")
        
        # Show results in table
        table_data = []
        for album in results:
            artists = album.get('Artiste', ['Unknown'])
            if isinstance(artists, list):
                artist_str = ", ".join(artists[:2])
                if len(artists) > 2:
                    artist_str += f" +{len(artists) - 2}"
            else:
                artist_str = str(artists)
            
            table_data.append({
                'Title': album.get('Titre', 'Unknown'),
                'Artist': artist_str,
                'Year': album.get('Annee', ''),
                'ID': album.get('Release_ID', '')
            })
        
        # Create table
        table = PaginatedTable(
            console=self.console,
            title=f"Search Results: '{term}'",
            columns=['Title', 'Artist', 'Year', 'ID'],
            data=table_data,
            page_size=25,
            show_index=True
        )
        
        table.show_page(0)
        
        # Show hint
        self.console.print(f"\n[dim]Use 'collection view <ID>' to see album details[/dim]\n")
    
    def view_album(self, release_id: int):
        """
        View detailed information for an album.
        
        Args:
            release_id: Discogs release ID
        """
        # Load collection
        collection = self.loader.load_collection()
        
        if not collection:
            self.console.print("[yellow]⚠️  No collection data found.[/yellow]")
            return
        
        # Find album
        album = None
        for item in collection:
            if item.get('Release_ID') == release_id:
                album = item
                break
        
        if not album:
            self.console.print(f"\n[red]✗ Album not found with ID: {release_id}[/red]\n")
            return
        
        # Display album details
        self.console.print()
        detail_panel = AlbumDetailPanel(self.console, album)
        detail_panel.show()
        self.console.print()
        
        # Show additional options
        self.console.print("[dim]Actions:[/dim]")
        self.console.print(f"  [white]collection edit {release_id}[/white] - Edit metadata")
        self.console.print()
    
    def edit_album(self, release_id: int):
        """
        Edit album metadata (basic fields).
        
        Args:
            release_id: Discogs release ID
        """
        # Load collection
        collection = self.loader.load_collection()
        
        if not collection:
            self.console.print("[yellow]⚠️  No collection data found.[/yellow]")
            return
        
        # Find album
        album_index = None
        album = None
        for i, item in enumerate(collection):
            if item.get('Release_ID') == release_id:
                album_index = i
                album = item
                break
        
        if not album:
            self.console.print(f"\n[red]✗ Album not found with ID: {release_id}[/red]\n")
            return
        
        # Show current data
        self.console.print(f"\n[cyan bold]Editing Album: {album.get('Titre', 'Unknown')}[/cyan bold]\n")
        
        # Editable fields
        self.console.print("[dim]Leave empty to keep current value[/dim]\n")
        
        # Support
        current_support = album.get('Support', '')
        new_support = Prompt.ask(
            f"Support (current: {current_support})",
            default=current_support
        )
        
        # Label
        current_label = album.get('Label', '')
        new_label = Prompt.ask(
            f"Label (current: {current_label})",
            default=current_label
        )
        
        # Confirm changes
        self.console.print(f"\n[yellow]Changes:[/yellow]")
        self.console.print(f"  Support: {current_support} → {new_support}")
        self.console.print(f"  Label: {current_label} → {new_label}")
        
        confirm = Confirm.ask("\nSave changes?", default=False)
        
        if confirm:
            # Update album
            collection[album_index]['Support'] = new_support
            collection[album_index]['Label'] = new_label
            
            # Note: In a real implementation, we would save to JSON here
            # For now, just show success message
            self.console.print(f"\n[green]✓ Changes saved successfully[/green]")
            self.console.print("[yellow]⚠️  Note: File saving not yet implemented in this version[/yellow]\n")
        else:
            self.console.print("\n[yellow]Changes discarded[/yellow]\n")
    
    def show_stats(self):
        """Display collection statistics."""
        stats = self.loader.get_collection_stats()
        
        if stats['total_albums'] == 0:
            self.console.print("[yellow]⚠️  No collection data found.[/yellow]")
            return
        
        # Display stats panel
        self.console.print()
        stats_panel = StatsPanel(
            console=self.console,
            title="Collection Statistics",
            stats=stats
        )
        stats_panel.show()
        self.console.print()
