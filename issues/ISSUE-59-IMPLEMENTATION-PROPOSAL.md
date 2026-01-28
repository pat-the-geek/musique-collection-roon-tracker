# Issue #59: Propositions de Réalisation - Interface ASCII/ANSI CLI

**Date**: 28 janvier 2026  
**Version**: 1.0.0  
**Auteur**: GitHub Copilot AI Agent  
**Statut**: 📝 Proposition concrète

---

## 📋 Table des Matières

1. [Architecture Détaillée](#architecture-détaillée)
2. [Exemples de Code](#exemples-de-code)
3. [Prototypes Fonctionnels](#prototypes-fonctionnels)
4. [Configuration et Déploiement](#configuration-et-déploiement)
5. [Plan de Migration](#plan-de-migration)
6. [Roadmap Détaillée](#roadmap-détaillée)

---

## 🏗️ Architecture Détaillée

### Structure des Fichiers

```
src/cli/
├── __init__.py                    # Package initialization
├── main.py                        # Entry point CLI (300 lignes)
│
├── commands/                      # Commandes CLI
│   ├── __init__.py
│   ├── collection.py             # Collection Discogs (400 lignes)
│   ├── journal.py                # Journal Roon (350 lignes)
│   ├── timeline.py               # Timeline Roon (300 lignes)
│   ├── ai_logs.py                # Journal IA (150 lignes)
│   ├── haikus.py                 # Haïkus & Rapports (150 lignes)
│   └── config.py                 # Configuration (200 lignes)
│
├── ui/                           # Composants UI
│   ├── __init__.py
│   ├── colors.py                 # Couleurs sémantiques (150 lignes)
│   ├── components.py             # Composants réutilisables (500 lignes)
│   │   ├── Table                 # Table paginée
│   │   ├── Panel                 # Panneau d'information
│   │   ├── Menu                  # Menu interactif
│   │   ├── Form                  # Formulaire d'édition
│   │   └── Timeline              # Timeline ASCII art
│   ├── layouts.py                # Layouts (300 lignes)
│   │   ├── ListLayout            # Layout liste
│   │   ├── DetailLayout          # Layout détail
│   │   └── TimelineLayout        # Layout timeline
│   └── renderer.py               # Rendering engine (400 lignes)
│       ├── DiffRenderer          # Diff-based rendering
│       ├── BufferedRenderer      # Buffered rendering
│       └── TerminalRenderer      # Terminal primitives
│
├── models/                       # Modèles de données
│   ├── __init__.py
│   ├── album.py                  # Album model (150 lignes)
│   ├── track.py                  # Track model (150 lignes)
│   ├── session.py                # Session model (100 lignes)
│   └── config.py                 # Configuration model (100 lignes)
│
└── utils/                        # Utilitaires
    ├── __init__.py
    ├── terminal.py               # Terminal utilities (200 lignes)
    │   ├── detect_capabilities() # Détection capacités
    │   ├── get_terminal_size()   # Taille terminal
    │   └── supports_color()      # Support couleurs
    ├── pager.py                  # Pager intégré (300 lignes)
    │   ├── Pager                 # Less-like pager
    │   └── SyntaxHighlighter     # Syntax highlighting
    ├── search.py                 # Recherche (200 lignes)
    │   ├── FuzzySearch           # Recherche floue
    │   └── InteractiveSearch     # Recherche interactive
    └── data_loader.py            # Data loading (250 lignes)
        ├── LazyLoader            # Lazy loading
        └── CachedLoader          # Cache layer

Total estimé: ~4500 lignes de code
```

---

## 💻 Exemples de Code

### 1. Point d'Entrée Principal

```python
# src/cli/main.py

"""
Musique Collection & Roon Tracker - CLI Interface

Interface en ligne de commande moderne pour gérer une collection musicale
et visualiser l'historique d'écoute Roon/Last.fm.

Usage:
    # Mode interactif (default)
    $ python3 -m src.cli.main
    
    # Mode CLI (arguments)
    $ python3 -m src.cli.main collection list --page 1
    $ python3 -m src.cli.main journal show --date 2026-01-28
    $ python3 -m src.cli.main timeline display --day 2026-01-28
    
    # Export et scripting
    $ python3 -m src.cli.main collection export --format json
    $ python3 -m src.cli.main journal stats --json

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 28 janvier 2026
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .ui.colors import SemanticColor, apply_color
from .ui.components import MainMenu
from .commands import (
    CollectionCommand,
    JournalCommand,
    TimelineCommand,
    AILogsCommand,
    HaikusCommand,
    ConfigCommand,
)
from .utils.terminal import detect_terminal_capabilities

# Global console instance
console = Console()

# ASCII Art logo
LOGO = """
    🎵 Musique Collection & Roon Tracker
    
           Version 3.4.0-cli
"""


@click.group()
@click.option(
    '--color',
    type=click.Choice(['auto', 'always', 'never', 'truecolor']),
    default='auto',
    help='Color mode'
)
@click.option(
    '--no-interactive',
    is_flag=True,
    help='Disable interactive mode'
)
@click.pass_context
def cli(ctx, color, no_interactive):
    """Musique Collection & Roon Tracker CLI.
    
    Manage your music collection, view listening history,
    and explore patterns with an elegant terminal interface.
    """
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['color_mode'] = color
    ctx.obj['interactive'] = not no_interactive
    
    # Detect terminal capabilities
    capabilities = detect_terminal_capabilities()
    ctx.obj['capabilities'] = capabilities
    
    # Configure console
    if color == 'never':
        console.color_system = None
    elif color == 'truecolor':
        console.color_system = 'truecolor'
    else:
        console.color_system = 'auto'


@cli.command()
@click.pass_context
def interactive(ctx):
    """Launch interactive mode (default)."""
    console.clear()
    console.print(Panel(LOGO, border_style="cyan", expand=False))
    
    # Create main menu
    menu = MainMenu(console)
    menu.show()


@cli.group()
def collection():
    """Manage music collection."""
    pass


@collection.command('list')
@click.option('--page', default=1, help='Page number')
@click.option('--per-page', default=25, help='Items per page')
@click.option('--filter', help='Filter (soundtrack, year, support)')
@click.option('--sort', default='title', help='Sort by (title, artist, year)')
def collection_list(page, per_page, filter, sort):
    """List albums (paginated)."""
    cmd = CollectionCommand(console)
    cmd.list_albums(page=page, per_page=per_page, filter=filter, sort=sort)


@collection.command('search')
@click.argument('term')
def collection_search(term):
    """Search albums by title or artist."""
    cmd = CollectionCommand(console)
    cmd.search_albums(term)


@collection.command('view')
@click.argument('release_id', type=int)
def collection_view(release_id):
    """View album details."""
    cmd = CollectionCommand(console)
    cmd.view_album(release_id)


@collection.command('edit')
@click.argument('release_id', type=int)
def collection_edit(release_id):
    """Edit album metadata."""
    cmd = CollectionCommand(console)
    cmd.edit_album(release_id)


@cli.group()
def journal():
    """View listening journal."""
    pass


@journal.command('show')
@click.option('--source', type=click.Choice(['all', 'roon', 'lastfm']), default='all')
@click.option('--loved', is_flag=True, help='Show only loved tracks')
@click.option('--date', help='Filter by date (YYYY-MM-DD)')
@click.option('--page', default=1, help='Page number')
def journal_show(source, loved, date, page):
    """Show listening journal."""
    cmd = JournalCommand(console)
    cmd.show_journal(source=source, loved=loved, date=date, page=page)


@journal.command('stats')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def journal_stats(json_output):
    """Show journal statistics."""
    cmd = JournalCommand(console)
    cmd.show_stats(json_output=json_output)


@cli.group()
def timeline():
    """View timeline visualization."""
    pass


@timeline.command('display')
@click.option('--day', help='Date (YYYY-MM-DD, default: today)')
@click.option('--mode', type=click.Choice(['compact', 'detailed']), default='compact')
def timeline_display(day, mode):
    """Display timeline for a specific day."""
    cmd = TimelineCommand(console)
    cmd.display_timeline(day=day, mode=mode)


@cli.group()
def ai_logs():
    """View AI enrichment logs."""
    pass


@ai_logs.command('list')
def ai_logs_list():
    """List available AI log files."""
    cmd = AILogsCommand(console)
    cmd.list_logs()


@ai_logs.command('view')
@click.argument('date', required=False)
def ai_logs_view(date):
    """View AI log for specific date (default: today)."""
    cmd = AILogsCommand(console)
    cmd.view_log(date)


def main():
    """Entry point."""
    try:
        # If no arguments, launch interactive mode
        if len(sys.argv) == 1:
            sys.argv.append('interactive')
        
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### 2. Système de Couleurs Sémantiques

```python
# src/cli/ui/colors.py

"""
Système de couleurs sémantiques pour l'interface CLI.

Utilise des rôles sémantiques plutôt que des couleurs fixes,
permettant une adaptation gracieuse selon les capacités du terminal.

Inspiré par GitHub CLI.
"""

from enum import Enum
from typing import Dict
from rich.style import Style


class SemanticColor(Enum):
    """Rôles sémantiques pour les couleurs."""
    
    # Primaires
    PRIMARY = "primary"           # Titres, headers
    SECONDARY = "secondary"       # Sous-titres, labels
    ACCENT = "accent"             # Highlights, emphasis
    
    # États
    SUCCESS = "success"           # Opérations réussies
    WARNING = "warning"           # Avertissements
    ERROR = "error"               # Erreurs
    INFO = "info"                 # Informations
    
    # Métadonnées
    MUTED = "muted"               # Texte secondaire
    EMPHASIS = "emphasis"         # Texte important
    
    # Spécifiques musique
    ARTIST = "artist"             # Noms d'artistes
    ALBUM = "album"               # Titres d'albums
    TRACK = "track"               # Titres de pistes
    YEAR = "year"                 # Années
    LOVED = "loved"               # Tracks aimés
    SOURCE_ROON = "source_roon"   # Source Roon
    SOURCE_LASTFM = "source_lastfm"  # Source Last.fm
    SOUNDTRACK = "soundtrack"     # Soundtracks


# Mapping vers couleurs Rich (4-bit palette)
COLOR_STYLES: Dict[SemanticColor, Style] = {
    SemanticColor.PRIMARY: Style(color="cyan", bold=True),
    SemanticColor.SECONDARY: Style(color="blue"),
    SemanticColor.ACCENT: Style(color="magenta"),
    
    SemanticColor.SUCCESS: Style(color="green", bold=True),
    SemanticColor.WARNING: Style(color="yellow"),
    SemanticColor.ERROR: Style(color="red", bold=True),
    SemanticColor.INFO: Style(color="blue"),
    
    SemanticColor.MUTED: Style(color="bright_black"),  # Dim gray
    SemanticColor.EMPHASIS: Style(color="white", bold=True),
    
    SemanticColor.ARTIST: Style(color="magenta"),
    SemanticColor.ALBUM: Style(color="cyan", italic=True),
    SemanticColor.TRACK: Style(color="white"),
    SemanticColor.YEAR: Style(color="bright_black"),  # Dim
    SemanticColor.LOVED: Style(color="red"),
    SemanticColor.SOURCE_ROON: Style(color="blue"),
    SemanticColor.SOURCE_LASTFM: Style(color="green"),
    SemanticColor.SOUNDTRACK: Style(color="yellow"),
}

# Mapping vers couleurs Truecolor (24-bit) pour terminaux modernes
TRUECOLOR_STYLES: Dict[SemanticColor, Style] = {
    SemanticColor.PRIMARY: Style(color="#00D9FF", bold=True),      # Cyan vif
    SemanticColor.SECONDARY: Style(color="#5CACEE"),              # Blue sky
    SemanticColor.ACCENT: Style(color="#FF00FF"),                 # Magenta
    
    SemanticColor.SUCCESS: Style(color="#00FF00", bold=True),     # Green
    SemanticColor.WARNING: Style(color="#FFD700"),                # Gold
    SemanticColor.ERROR: Style(color="#FF0000", bold=True),       # Red
    SemanticColor.INFO: Style(color="#1E90FF"),                   # Dodger blue
    
    SemanticColor.MUTED: Style(color="#808080"),                  # Gray
    SemanticColor.EMPHASIS: Style(color="#FFFFFF", bold=True),    # White
    
    SemanticColor.ARTIST: Style(color="#DA70D6"),                 # Orchid
    SemanticColor.ALBUM: Style(color="#48D1CC", italic=True),     # Turquoise
    SemanticColor.TRACK: Style(color="#F0F0F0"),                  # Off-white
    SemanticColor.YEAR: Style(color="#A9A9A9"),                   # Dark gray
    SemanticColor.LOVED: Style(color="#FF1493"),                  # Deep pink
    SemanticColor.SOURCE_ROON: Style(color="#4169E1"),            # Royal blue
    SemanticColor.SOURCE_LASTFM: Style(color="#32CD32"),          # Lime green
    SemanticColor.SOUNDTRACK: Style(color="#FFD700"),             # Gold
}


def apply_color(text: str, role: SemanticColor, truecolor: bool = False) -> str:
    """
    Applique une couleur sémantique à un texte.
    
    Args:
        text: Texte à colorer
        role: Rôle sémantique
        truecolor: Utiliser palette truecolor (si supportée)
    
    Returns:
        Texte avec markup Rich
    """
    styles = TRUECOLOR_STYLES if truecolor else COLOR_STYLES
    style = styles.get(role, Style())
    
    # Convert Rich style to markup string
    markup_parts = []
    if style.bold:
        markup_parts.append("bold")
    if style.italic:
        markup_parts.append("italic")
    if style.color:
        markup_parts.append(str(style.color))
    
    markup = " ".join(markup_parts)
    return f"[{markup}]{text}[/]" if markup else text


def format_album_line(title: str, artist: str, year: int, truecolor: bool = False) -> str:
    """
    Formate une ligne d'album avec couleurs sémantiques.
    
    Returns:
        Ligne formatée avec markup Rich
    """
    title_colored = apply_color(title, SemanticColor.ALBUM, truecolor)
    artist_colored = apply_color(artist, SemanticColor.ARTIST, truecolor)
    year_colored = apply_color(f"({year})", SemanticColor.YEAR, truecolor)
    
    return f"{title_colored} - {artist_colored} {year_colored}"


def format_track_line(
    artist: str,
    title: str,
    album: str,
    source: str,
    loved: bool = False,
    truecolor: bool = False
) -> str:
    """
    Formate une ligne de track avec couleurs sémantiques.
    
    Args:
        artist: Nom de l'artiste
        title: Titre du track
        album: Titre de l'album
        source: Source (roon ou lastfm)
        loved: Track aimé?
        truecolor: Utiliser palette truecolor
    
    Returns:
        Ligne formatée avec markup Rich
    """
    artist_colored = apply_color(artist, SemanticColor.ARTIST, truecolor)
    title_colored = apply_color(title, SemanticColor.TRACK, truecolor)
    album_colored = apply_color(album, SemanticColor.ALBUM, truecolor)
    
    # Source icon
    source_role = SemanticColor.SOURCE_ROON if source == 'roon' else SemanticColor.SOURCE_LASTFM
    source_icon = "🎵" if source == 'roon' else "📻"
    source_colored = apply_color(f"{source_icon} {source}", source_role, truecolor)
    
    # Loved indicator
    loved_indicator = ""
    if loved:
        loved_indicator = " " + apply_color("❤️", SemanticColor.LOVED, truecolor)
    
    return f"{artist_colored} - {title_colored} [{album_colored}] | {source_colored}{loved_indicator}"
```

### 3. Composant Table Réutilisable

```python
# src/cli/ui/components.py (extrait)

"""
Composants UI réutilisables pour l'interface CLI.
"""

from typing import List, Optional, Callable
from rich.console import Console
from rich.table import Table as RichTable
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog

from .colors import SemanticColor, apply_color


class PaginatedTable:
    """
    Table paginée avec navigation interactive.
    
    Features:
        - Pagination automatique
        - Navigation [n]ext/[p]revious
        - Actions personnalisables par ligne
        - Tri dynamique
    """
    
    def __init__(
        self,
        console: Console,
        title: str,
        columns: List[str],
        data: List[dict],
        page_size: int = 25,
        sortable: bool = True
    ):
        self.console = console
        self.title = title
        self.columns = columns
        self.data = data
        self.page_size = page_size
        self.current_page = 0
        self.sortable = sortable
        self.sort_by = None
        self.sort_reverse = False
    
    @property
    def total_pages(self) -> int:
        """Nombre total de pages."""
        return (len(self.data) + self.page_size - 1) // self.page_size
    
    def get_page_data(self, page: int) -> List[dict]:
        """Récupère les données pour une page."""
        start = page * self.page_size
        end = start + self.page_size
        return self.data[start:end]
    
    def render(self):
        """Rend la table pour la page courante."""
        self.console.clear()
        
        # Create Rich table
        table = RichTable(
            title=f"{self.title} ({len(self.data)} items)",
            show_header=True,
            header_style="bold cyan"
        )
        
        # Add columns
        for col in self.columns:
            table.add_column(col)
        
        # Add rows for current page
        page_data = self.get_page_data(self.current_page)
        for row in page_data:
            table.add_row(*[str(row.get(col, "")) for col in self.columns])
        
        self.console.print(table)
        
        # Footer with pagination info
        footer = (
            f"[{self.current_page * self.page_size + 1}-"
            f"{min((self.current_page + 1) * self.page_size, len(self.data))} "
            f"sur {len(self.data)}] | "
            f"Page {self.current_page + 1}/{self.total_pages}"
        )
        self.console.print(f"\n{footer}\n")
    
    def show_interactive(self) -> Optional[dict]:
        """
        Affiche la table en mode interactif.
        
        Returns:
            Item sélectionné par l'utilisateur (ou None)
        """
        while True:
            self.render()
            
            # Show commands
            self.console.print(
                "? Commandes: "
                "[n]ext [p]revious [s]earch [v]iew [q]uit"
            )
            
            command = prompt(">> ")
            
            if command == 'n' and self.current_page < self.total_pages - 1:
                self.current_page += 1
            elif command == 'p' and self.current_page > 0:
                self.current_page -= 1
            elif command == 's':
                # Search functionality
                term = prompt("Search: ")
                # ... implement search
            elif command == 'v':
                # View item
                idx = int(prompt("Item index: "))
                page_data = self.get_page_data(self.current_page)
                if 0 <= idx < len(page_data):
                    return page_data[idx]
            elif command == 'q':
                return None


class MainMenu:
    """
    Menu principal interactif.
    
    Utilise prompt_toolkit pour une navigation au clavier élégante.
    """
    
    def __init__(self, console: Console):
        self.console = console
        self.options = [
            ('collection', '📂 Collection Discogs'),
            ('journal', '📔 Journal Roon'),
            ('timeline', '📈 Timeline Roon'),
            ('ai_logs', '🤖 Journal IA'),
            ('haikus', '🎵 Haïkus & Rapports'),
            ('config', '⚙️  Configuration'),
            ('quit', '❌ Quitter'),
        ]
    
    def show(self):
        """Affiche le menu et gère la navigation."""
        while True:
            # Show logo
            self.console.print(Panel(
                "[bold cyan]🎵 Musique Collection & Roon Tracker[/]\n\n"
                "Version 3.4.0-cli",
                border_style="cyan"
            ))
            
            # Show menu with radiolist_dialog
            result = radiolist_dialog(
                title="Menu Principal",
                text="Choisissez une action:",
                values=self.options
            ).run()
            
            if result == 'quit' or result is None:
                self.console.print("[yellow]Au revoir![/yellow]")
                break
            
            # Handle selection
            self._handle_selection(result)
    
    def _handle_selection(self, selection: str):
        """Gère la sélection utilisateur."""
        from ..commands import (
            CollectionCommand,
            JournalCommand,
            TimelineCommand,
            AILogsCommand,
            HaikusCommand,
            ConfigCommand,
        )
        
        commands = {
            'collection': CollectionCommand(self.console),
            'journal': JournalCommand(self.console),
            'timeline': TimelineCommand(self.console),
            'ai_logs': AILogsCommand(self.console),
            'haikus': HaikusCommand(self.console),
            'config': ConfigCommand(self.console),
        }
        
        cmd = commands.get(selection)
        if cmd:
            cmd.run_interactive()
```

### 4. Commande Collection (Exemple Complet)

```python
# src/cli/commands/collection.py

"""
Commande Collection - Gestion de la collection Discogs.

Features:
    - List: Afficher liste paginée des albums
    - Search: Recherche interactive par titre/artiste
    - View: Afficher détails d'un album
    - Edit: Éditer métadonnées d'un album
    - Export: Exporter collection en JSON/CSV
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from ..ui.colors import format_album_line, SemanticColor, apply_color
from ..ui.components import PaginatedTable
from ..models.album import Album
from ..utils.data_loader import LazyLoader


class CollectionCommand:
    """Commande de gestion de la collection Discogs."""
    
    def __init__(self, console: Console):
        self.console = console
        self.data_path = Path("data/collection/discogs-collection.json")
        self.loader = LazyLoader(self.data_path)
    
    def list_albums(
        self,
        page: int = 1,
        per_page: int = 25,
        filter: Optional[str] = None,
        sort: str = 'title'
    ):
        """
        Affiche la liste des albums (paginated).
        
        Args:
            page: Numéro de page
            per_page: Items par page
            filter: Filtre (soundtrack, year:1980, support:vinyle)
            sort: Tri (title, artist, year)
        """
        # Load data
        albums = self.loader.load_all()
        
        # Apply filters
        if filter:
            albums = self._apply_filter(albums, filter)
        
        # Sort
        albums = self._sort_albums(albums, sort)
        
        # Create table
        table = Table(
            title=f"Collection Discogs ({len(albums)} albums)",
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Titre", style="cyan italic")
        table.add_column("Artiste", style="magenta")
        table.add_column("Année", justify="right", style="dim")
        table.add_column("Support", style="white")
        
        # Paginate
        start = (page - 1) * per_page
        end = start + per_page
        page_albums = albums[start:end]
        
        # Add rows
        for album in page_albums:
            # Add soundtrack indicator
            title = album['Titre']
            if self._is_soundtrack(album):
                title = f"🎬 {title}"
            
            table.add_row(
                title,
                self._format_artist(album['Artiste']),
                str(album.get('Année', '')),
                album.get('Support', '')
            )
        
        self.console.print(table)
        
        # Footer
        total_pages = (len(albums) + per_page - 1) // per_page
        footer = (
            f"[{start + 1}-{min(end, len(albums))} sur {len(albums)}] | "
            f"Page {page}/{total_pages}"
        )
        self.console.print(f"\n{footer}\n")
    
    def search_albums(self, term: str):
        """
        Recherche interactive d'albums.
        
        Args:
            term: Terme de recherche
        """
        albums = self.loader.load_all()
        
        # Search in title and artist
        results = [
            album for album in albums
            if term.lower() in album['Titre'].lower()
            or term.lower() in self._format_artist(album['Artiste']).lower()
        ]
        
        self.console.print(
            f"\n{apply_color(f'{len(results)} résultats trouvés', SemanticColor.INFO)}\n"
        )
        
        if not results:
            return
        
        # Display results
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Titre", style="cyan italic")
        table.add_column("Artiste", style="magenta")
        table.add_column("Année", justify="right", style="dim")
        table.add_column("Support", style="white")
        
        for album in results[:25]:  # Limit to 25 results
            title = album['Titre']
            if self._is_soundtrack(album):
                title = f"🎬 {title}"
            
            table.add_row(
                title,
                self._format_artist(album['Artiste']),
                str(album.get('Année', '')),
                album.get('Support', '')
            )
        
        self.console.print(table)
    
    def view_album(self, release_id: int):
        """
        Affiche les détails d'un album.
        
        Args:
            release_id: ID Discogs de l'album
        """
        albums = self.loader.load_all()
        album = next((a for a in albums if a.get('release_id') == release_id), None)
        
        if not album:
            self.console.print(f"[red]Album {release_id} introuvable[/red]")
            return
        
        # Create panel with album details
        title_line = format_album_line(
            album['Titre'],
            self._format_artist(album['Artiste']),
            album.get('Année', 0)
        )
        
        content = Text()
        content.append("🎵 ", style="cyan")
        content.append(album['Titre'], style="cyan italic bold")
        content.append("\n\n")
        
        content.append("🎤 Artiste: ", style="white")
        content.append(self._format_artist(album['Artiste']), style="magenta")
        content.append("\n")
        
        content.append("📅 Année: ", style="white")
        content.append(str(album.get('Année', '')), style="dim")
        content.append("\n")
        
        content.append("💿 Support: ", style="white")
        content.append(album.get('Support', ''), style="white")
        content.append("\n")
        
        if album.get('Labels'):
            content.append("🏷️  Labels: ", style="white")
            content.append(", ".join(album['Labels']), style="dim")
            content.append("\n")
        
        # Links
        if album.get('Spotify_URL'):
            content.append("\n🔗 Spotify: ", style="white")
            content.append(album['Spotify_URL'], style="blue underline")
            content.append("\n")
        
        content.append("🔗 Discogs: ", style="white")
        content.append(
            f"https://www.discogs.com/release/{release_id}",
            style="blue underline"
        )
        content.append("\n")
        
        # Resume
        if album.get('Resume') and album['Resume'] != "Aucune information disponible":
            content.append("\n📝 Résumé:\n", style="white bold")
            content.append(album['Resume'], style="white")
        
        panel = Panel(content, border_style="cyan", expand=False)
        self.console.print(panel)
    
    def edit_album(self, release_id: int):
        """
        Édite les métadonnées d'un album.
        
        Args:
            release_id: ID Discogs de l'album
        """
        albums = self.loader.load_all()
        album = next((a for a in albums if a.get('release_id') == release_id), None)
        
        if not album:
            self.console.print(f"[red]Album {release_id} introuvable[/red]")
            return
        
        self.console.print(Panel(
            f"✏️  Édition: {album['Titre']}",
            border_style="yellow"
        ))
        
        # Edit fields with prompts
        new_title = prompt("Titre: ", default=album['Titre'])
        new_artist = prompt(
            "Artiste: ",
            default=self._format_artist(album['Artiste'])
        )
        new_year = prompt("Année: ", default=str(album.get('Année', '')))
        
        # Support selection
        supports = ['Vinyle', 'CD']
        support_completer = WordCompleter(supports)
        new_support = prompt(
            "Support: ",
            default=album.get('Support', ''),
            completer=support_completer
        )
        
        # Confirmation
        confirm = prompt("Sauvegarder? [y/N]: ")
        if confirm.lower() == 'y':
            # Update album
            album['Titre'] = new_title
            album['Artiste'] = [new_artist]  # Convert to list
            album['Année'] = int(new_year) if new_year else None
            album['Support'] = new_support
            
            # Save
            self._save_collection(albums)
            self.console.print("[green]✓ Album mis à jour[/green]")
        else:
            self.console.print("[yellow]Édition annulée[/yellow]")
    
    def run_interactive(self):
        """Lance le mode interactif pour la collection."""
        while True:
            self.console.clear()
            self.console.print(Panel(
                "📂 Collection Discogs",
                border_style="cyan"
            ))
            
            # Show menu
            self.console.print(
                "? Actions:\n"
                "  [l]ist - Liste des albums\n"
                "  [s]earch - Rechercher\n"
                "  [v]iew - Voir détails\n"
                "  [e]dit - Éditer\n"
                "  [b]ack - Retour\n"
            )
            
            command = prompt(">> ")
            
            if command == 'l':
                self.list_albums()
                prompt("\nAppuyez sur Entrée pour continuer...")
            elif command == 's':
                term = prompt("Recherche: ")
                self.search_albums(term)
                prompt("\nAppuyez sur Entrée pour continuer...")
            elif command == 'v':
                release_id = int(prompt("Release ID: "))
                self.view_album(release_id)
                prompt("\nAppuyez sur Entrée pour continuer...")
            elif command == 'e':
                release_id = int(prompt("Release ID: "))
                self.edit_album(release_id)
            elif command == 'b':
                break
    
    # Helper methods
    
    def _format_artist(self, artist) -> str:
        """Formate le nom d'artiste (peut être une liste)."""
        if isinstance(artist, list):
            return ", ".join(artist)
        return str(artist)
    
    def _is_soundtrack(self, album: dict) -> bool:
        """Vérifie si l'album est une BOF."""
        # Check in soundtrack.json
        soundtrack_path = Path("data/collection/soundtrack.json")
        if soundtrack_path.exists():
            with open(soundtrack_path) as f:
                soundtracks = json.load(f)
            return any(
                s['album_title'].lower() == album['Titre'].lower()
                for s in soundtracks
            )
        return False
    
    def _apply_filter(self, albums: List[dict], filter: str) -> List[dict]:
        """Applique un filtre à la liste d'albums."""
        if filter == 'soundtrack':
            return [a for a in albums if self._is_soundtrack(a)]
        elif filter.startswith('year:'):
            year = int(filter.split(':')[1])
            return [a for a in albums if a.get('Année') == year]
        elif filter.startswith('support:'):
            support = filter.split(':')[1]
            return [a for a in albums if a.get('Support', '').lower() == support.lower()]
        return albums
    
    def _sort_albums(self, albums: List[dict], sort_by: str) -> List[dict]:
        """Trie la liste d'albums."""
        if sort_by == 'title':
            return sorted(albums, key=lambda a: a['Titre'].lower())
        elif sort_by == 'artist':
            return sorted(albums, key=lambda a: self._format_artist(a['Artiste']).lower())
        elif sort_by == 'year':
            return sorted(albums, key=lambda a: a.get('Année', 0), reverse=True)
        return albums
    
    def _save_collection(self, albums: List[dict]):
        """Sauvegarde la collection (avec backup)."""
        # Create backup
        import shutil
        from datetime import datetime
        
        backup_dir = Path("backups/json/discogs-collection")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"discogs-collection-{timestamp}.json"
        
        shutil.copy(self.data_path, backup_path)
        
        # Save new data
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(albums, f, ensure_ascii=False, indent=2)
```

---

## 🚀 Configuration et Déploiement

### 1. Installation

```bash
# requirements-cli.txt
rich>=13.0.0
prompt_toolkit>=3.0.0
click>=8.0.0
python-dotenv>=1.0.0
```

```bash
# Installation
pip install -r requirements-cli.txt

# Ou ajout au requirements.txt existant
echo "# CLI dependencies" >> requirements.txt
cat requirements-cli.txt >> requirements.txt
```

### 2. Script de Lancement

```bash
#!/bin/bash
# scripts/start-cli.sh

# Musique Collection & Roon Tracker - CLI Interface
# Lancement de l'interface en ligne de commande

set -e

# Couleurs pour output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎵 Musique Collection & Roon Tracker CLI${NC}"
echo ""

# Vérifier environnement virtuel
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
fi

# Activer environnement
source .venv/bin/activate

# Vérifier dépendances
if ! python3 -c "import rich" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing CLI dependencies...${NC}"
    pip install -r requirements-cli.txt
fi

# Lancer CLI
python3 -m src.cli.main "$@"
```

```bash
chmod +x scripts/start-cli.sh
```

### 3. Configuration

```python
# data/config/cli-config.json

{
    "color_mode": "auto",         # auto, always, never, truecolor
    "page_size": 25,              # Items per page
    "editor": "nano",             # Editor for text editing
    "pager": "less",              # Pager for long content
    "date_format": "%Y-%m-%d",    # Date format
    "time_format": "%H:%M",       # Time format
    "terminal_width": null,       # null = auto-detect
    "terminal_height": null,      # null = auto-detect
    "shortcuts": {
        "quit": ["q", "quit"],
        "help": ["?", "help"],
        "back": ["b", "back"]
    }
}
```

---

## 🔄 Plan de Migration

### Phase 1: Développement Parallèle (Semaines 1-3)

```bash
src/
├── gui/
│   └── musique-gui.py        # Existing Streamlit (untouched)
└── cli/                       # New CLI (in development)
    └── ...
```

**Avantages:**
- Pas de rupture pour utilisateurs existants
- Développement et tests indépendants
- Comparaison A/B possible

**Utilisation:**
```bash
# Streamlit (existing)
./start-streamlit.sh

# CLI (new)
./scripts/start-cli.sh
```

### Phase 2: Période de Transition (Semaine 4-6)

**Documentation:**
- Guide de migration Streamlit → CLI
- Comparaison fonctionnalités
- FAQ et troubleshooting

**Communication:**
```markdown
# 📢 Nouvelle Interface CLI Disponible!

À partir de la version 3.5.0, une interface CLI moderne est disponible
en alternative à Streamlit.

## Avantages CLI
- ⚡ Démarrage instantané (<1s)
- 🖥️ Utilisable en SSH
- 📦 Plus léger (~97% moins de dépendances)
- 🎨 Interface élégante avec couleurs

## Utilisation
```bash
# Interface CLI (nouveau)
./scripts/start-cli.sh

# Interface Web Streamlit (actuel)
./start-streamlit.sh
```

## Feedback
Testez la nouvelle interface et partagez votre feedback!
Les deux interfaces seront maintenues pendant 2 mois.
```

### Phase 3: Décision et Maintenance (Semaine 7+)

**Options:**

#### Option A: Maintenir les Deux
```bash
# Configuration par défaut
DEFAULT_INTERFACE=cli  # ou streamlit

# start-all.sh détecte et lance l'interface par défaut
```

**Avantages:**
- Flexibilité maximale
- Adaptation aux besoins utilisateur

**Inconvénients:**
- Maintenance double
- Code dupliqué

#### Option B: Déprécier Streamlit (Recommandé si CLI succès)
```bash
# Deprecation warning
echo "⚠️  Streamlit interface is deprecated and will be removed in v4.0.0"
echo "   Please migrate to CLI: ./scripts/start-cli.sh"
```

**Timeline:**
- v3.5.0: CLI disponible, Streamlit maintained
- v3.6.0-3.9.0: Les deux interfaces (2-3 mois)
- v4.0.0: CLI uniquement (si adoption réussie)

---

## 📅 Roadmap Détaillée

### Semaine 1: Fondations

**Objectifs:**
- ✅ Structure de base du module CLI
- ✅ Système de couleurs sémantiques
- ✅ Menu principal interactif

**Livrables:**
- `src/cli/main.py` (300 lignes)
- `src/cli/ui/colors.py` (150 lignes)
- `src/cli/ui/components.py` (200 lignes)
- Tests unitaires de base

**Timeline:**
- Jour 1-2: Architecture et structure
- Jour 3-4: Couleurs et composants de base
- Jour 5: Menu principal et navigation
- Jour 6-7: Tests et polish

### Semaine 2: Collection Discogs

**Objectifs:**
- ✅ Liste paginée des albums
- ✅ Recherche interactive
- ✅ Vue détail album
- ✅ Édition basique

**Livrables:**
- `src/cli/commands/collection.py` (400 lignes)
- Tests d'intégration

**Timeline:**
- Jour 1-2: Liste et pagination
- Jour 3: Recherche
- Jour 4: Vue détail
- Jour 5: Édition
- Jour 6-7: Tests et raffinements

### Semaine 3: Journal Roon

**Objectifs:**
- ✅ Historique chronologique
- ✅ Filtres (source, favoris, date)
- ✅ Vue détail track
- ✅ Toggle loved status

**Livrables:**
- `src/cli/commands/journal.py` (350 lignes)

**Timeline:**
- Jour 1-2: Liste chronologique
- Jour 3: Filtres
- Jour 4: Vue détail
- Jour 5: Actions (love/unlove)
- Jour 6-7: Tests

### Semaine 4: Timeline et Vues Secondaires

**Objectifs:**
- ✅ Timeline ASCII art
- ✅ Journal IA
- ✅ Haïkus & Rapports

**Livrables:**
- `src/cli/commands/timeline.py` (300 lignes)
- `src/cli/commands/ai_logs.py` (150 lignes)
- `src/cli/commands/haikus.py` (150 lignes)

**Timeline:**
- Jour 1-3: Timeline
- Jour 4-5: Vues secondaires
- Jour 6-7: Intégration et tests

### Semaine 5: Optimisation et Polish

**Objectifs:**
- ✅ Performance (lazy loading, cache)
- ✅ Tests multi-terminaux
- ✅ Documentation

**Livrables:**
- Optimisations performance
- Tests de compatibilité
- Documentation complète

### Semaine 6: Release et Migration

**Objectifs:**
- ✅ Release v3.5.0-cli
- ✅ Guide de migration
- ✅ Communication utilisateurs

**Livrables:**
- Release notes
- Guide migration
- Exemples et tutoriels

---

## 📊 Métriques de Succès

### Critères Techniques

- ✅ Temps de démarrage < 1s
- ✅ Consommation mémoire < 50 MB
- ✅ Temps de réponse < 100ms
- ✅ Compatible 5+ terminaux majeurs
- ✅ 90%+ couverture tests

### Critères Fonctionnels

- ✅ Parité fonctionnelle avec Streamlit (95%+)
- ✅ 100% utilisable au clavier
- ✅ SSH-friendly
- ✅ Scriptable/automatisable

### Critères Utilisateurs

- ✅ Satisfaction utilisateurs ≥ 8/10
- ✅ Adoption par ≥ 50% utilisateurs actifs
- ✅ Feedback positif sur performance et UX

---

## 🎯 Conclusion

Cette proposition détaille une implémentation complète et réaliste d'une interface CLI moderne pour le projet Musique Collection & Roon Tracker.

**Points Clés:**

1. **Architecture solide**: Modulaire, extensible, testable
2. **Stack éprouvée**: Rich + Prompt Toolkit + Click
3. **Migration douce**: Développement parallèle, période de transition
4. **Performance garantie**: Démarrage instantané, faible empreinte mémoire
5. **UX moderne**: Couleurs sémantiques, navigation élégante, accessible

**Prochaines Étapes:**

1. Validation de cette proposition par le stakeholder
2. Création de la branch `feature/cli-interface`
3. Implémentation Phase 1 (Semaine 1)
4. Revues itératives et ajustements
5. Release progressive selon roadmap

---

**Auteur:** GitHub Copilot AI Agent  
**Date:** 28 janvier 2026  
**Version:** 1.0.0  
**Statut:** 📝 Proposition concrète - Prête pour implémentation
