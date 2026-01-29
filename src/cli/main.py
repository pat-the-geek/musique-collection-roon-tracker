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

# Check for required dependencies and provide helpful error message
try:
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError as e:
    missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
    print(f"\n❌ Erreur: Le module '{missing_module}' n'est pas installé.\n")
    print("📦 Pour installer les dépendances CLI, utilisez l'une de ces méthodes:\n")
    print("   Méthode 1 (Recommandée) - Utiliser le script de lancement:")
    print("   $ ./start-cli.sh\n")
    print("   Méthode 2 - Installer toutes les dépendances:")
    print("   $ pip install -r requirements.txt\n")
    print("   Méthode 3 - Installer uniquement les dépendances CLI:")
    print("   $ pip install rich click prompt-toolkit\n")
    print("📚 Voir la documentation: src/cli/README.md\n")
    sys.exit(1)

from .ui.colors import SemanticColor, apply_color, set_color_mode
from .utils.terminal import detect_terminal_capabilities

# ASCII Art logo
LOGO = """
    🎵 Musique Collection & Roon Tracker
    
           Version 3.5.0-cli
"""


def get_console(color_mode: str = 'auto') -> Console:
    """
    Crée une instance Console avec le mode de couleur approprié.
    
    Args:
        color_mode: Mode de couleur ('auto', 'always', 'never', 'truecolor')
        
    Returns:
        Console: Instance Console configurée
    """
    if color_mode == 'never':
        return Console(color_system=None, force_terminal=True)
    elif color_mode == 'truecolor':
        return Console(color_system='truecolor', force_terminal=True)
    elif color_mode == 'always':
        return Console(force_terminal=True)
    else:  # auto
        return Console()


# Global console instance (created with default settings)
console = Console()


@click.group(invoke_without_command=True)
@click.option(
    '--color',
    type=click.Choice(['auto', 'always', 'never', 'truecolor']),
    default='auto',
    help='Mode de couleur (auto, always, never, truecolor)'
)
@click.option(
    '--no-interactive',
    is_flag=True,
    help='Désactive le mode interactif'
)
@click.pass_context
def cli(ctx, color, no_interactive):
    """
    Musique Collection & Roon Tracker CLI.
    
    Gérez votre collection musicale, visualisez l'historique d'écoute,
    et explorez les patterns avec une interface terminal élégante.
    """
    # Update global console with correct color mode
    global console
    console = get_console(color)
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['color_mode'] = color
    ctx.obj['interactive'] = not no_interactive
    ctx.obj['console'] = console
    
    # Detect terminal capabilities
    capabilities = detect_terminal_capabilities()
    ctx.obj['capabilities'] = capabilities
    
    # Configure color mode
    set_color_mode(color)
    
    # If no subcommand provided, show interactive mode
    if ctx.invoked_subcommand is None:
        launch_interactive()


def launch_interactive():
    """Lance le mode interactif (menu principal)."""
    console.clear()
    console.print(Panel(LOGO, border_style="cyan", expand=False))
    
    console.print("\n[cyan]🎵 Bienvenue dans Musique Collection & Roon Tracker![/cyan]\n")
    console.print("Mode interactif complet sera disponible dans la prochaine version.")
    console.print("Pour l'instant, utilisez les commandes CLI:\n")
    
    console.print("  [white]python3 -m src.cli.main --help[/white]")
    console.print("  [white]python3 -m src.cli.main collection list[/white]")
    console.print("  [white]python3 -m src.cli.main journal show[/white]")
    console.print("  [white]python3 -m src.cli.main timeline display[/white]\n")


@cli.command()
@click.pass_context
def interactive(ctx):
    """Lance le mode interactif (menu principal)."""
    launch_interactive()


@cli.group()
def collection():
    """Gérer la collection musicale."""
    pass


@collection.command('list')
@click.option('--page', default=1, help='Numéro de page')
@click.option('--per-page', default=25, help='Éléments par page')
@click.option('--filter', help='Filtre (soundtrack, year, support)')
@click.option('--sort', default='title', help='Trier par (title, artist, year)')
def collection_list(page, per_page, filter, sort):
    """Liste les albums (paginée)."""
    console.print(f"[yellow]Collection list - Page {page}, {per_page} par page[/yellow]")
    console.print("[dim]Implémentation à venir dans Phase 2...[/dim]")


@collection.command('search')
@click.argument('term')
def collection_search(term):
    """Recherche des albums par titre ou artiste."""
    console.print(f"[yellow]Recherche: {term}[/yellow]")
    console.print("[dim]Implémentation à venir dans Phase 2...[/dim]")


@collection.command('view')
@click.argument('release_id', type=int)
def collection_view(release_id):
    """Affiche les détails d'un album."""
    console.print(f"[yellow]Vue album #{release_id}[/yellow]")
    console.print("[dim]Implémentation à venir dans Phase 2...[/dim]")


@cli.group()
def journal():
    """Voir le journal d'écoute."""
    pass


@journal.command('show')
@click.option('--source', type=click.Choice(['all', 'roon', 'lastfm']), default='all')
@click.option('--loved', is_flag=True, help='Afficher uniquement les tracks aimés')
@click.option('--date', help='Filtrer par date (YYYY-MM-DD)')
@click.option('--page', default=1, help='Numéro de page')
def journal_show(source, loved, date, page):
    """Affiche le journal d'écoute."""
    console.print(f"[yellow]Journal - Source: {source}, Page: {page}[/yellow]")
    console.print("[dim]Implémentation à venir dans Phase 3...[/dim]")


@journal.command('stats')
@click.option('--json', 'json_output', is_flag=True, help='Sortie JSON')
def journal_stats(json_output):
    """Affiche les statistiques du journal."""
    console.print("[yellow]Statistiques du journal[/yellow]")
    console.print("[dim]Implémentation à venir dans Phase 3...[/dim]")


@cli.group()
def timeline():
    """Voir la visualisation timeline."""
    pass


@timeline.command('display')
@click.option('--day', help='Date (YYYY-MM-DD, défaut: aujourd\'hui)')
@click.option('--mode', type=click.Choice(['compact', 'detailed']), default='compact')
def timeline_display(day, mode):
    """Affiche la timeline pour un jour spécifique."""
    console.print(f"[yellow]Timeline - Mode: {mode}[/yellow]")
    if day:
        console.print(f"Date: {day}")
    console.print("[dim]Implémentation à venir dans Phase 3...[/dim]")


@cli.group()
def ai():
    """Voir les logs d'enrichissement IA."""
    pass


@ai.command('logs')
def ai_logs_list():
    """Liste les fichiers de logs IA disponibles."""
    console.print("[yellow]Liste des logs IA[/yellow]")
    console.print("[dim]Implémentation à venir dans Phase 3...[/dim]")


@ai.command('view')
@click.argument('date', required=False)
def ai_logs_view(date):
    """Voir le log IA pour une date spécifique (défaut: aujourd'hui)."""
    date_display = date or "aujourd'hui"
    console.print(f"[yellow]Log IA - Date: {date_display}[/yellow]")
    console.print("[dim]Implémentation à venir dans Phase 3...[/dim]")


@cli.command()
@click.pass_context
def version(ctx):
    """Affiche les informations de version."""
    from . import __version__, __date__, __author__
    
    console.print(Panel(
        f"[cyan bold]Musique Collection & Roon Tracker CLI[/cyan bold]\n\n"
        f"[white]Version:[/white] {__version__}\n"
        f"[white]Date:[/white] {__date__}\n"
        f"[white]Auteur:[/white] {__author__}\n\n"
        f"[dim]Interface CLI moderne pour la gestion de collection musicale[/dim]",
        border_style="cyan",
        expand=False
    ))
    
    # Afficher les capacités du terminal
    capabilities = ctx.obj.get('capabilities', {})
    console.print("\n[cyan bold]Capacités du terminal:[/cyan bold]")
    console.print(f"  [white]Couleurs:[/white] {'✓' if capabilities.get('color') else '✗'}")
    console.print(f"  [white]Truecolor:[/white] {'✓' if capabilities.get('truecolor') else '✗'}")
    console.print(f"  [white]Unicode:[/white] {'✓' if capabilities.get('unicode') else '✗'}")
    console.print(f"  [white]Dimensions:[/white] {capabilities.get('width')}x{capabilities.get('height')}")
    console.print(f"  [white]Terminal:[/white] {capabilities.get('term')}\n")


def main():
    """Point d'entrée principal."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrompu par l'utilisateur[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
