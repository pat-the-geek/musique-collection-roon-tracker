#!/usr/bin/env python3
"""
Prototype de démonstration - Interface CLI ASCII/ANSI

Ce prototype démontre les concepts clés de l'interface CLI proposée:
- Utilisation de Rich pour l'affichage élégant
- Système de couleurs sémantiques
- Navigation interactive avec prompt_toolkit
- Tables paginées
- Menus interactifs

Usage:
    python3 prototypes/cli_demo.py

Dependencies:
    pip install rich prompt_toolkit

Author: GitHub Copilot AI Agent
Date: 28 janvier 2026
Version: 1.0.0 (Prototype)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from prompt_toolkit import prompt
    from prompt_toolkit.shortcuts import radiolist_dialog
except ImportError:
    print("❌ Missing dependencies. Please install:")
    print("   pip install rich prompt_toolkit")
    sys.exit(1)

# Global console
console = Console()

# ASCII Art logo
LOGO = """
        🎵 Musique Collection & Roon Tracker
        
               Version 3.4.0-cli (Prototype)
"""


class SemanticColors:
    """Système de couleurs sémantiques."""
    
    # Primaires
    PRIMARY = "cyan bold"
    SECONDARY = "blue"
    ACCENT = "magenta"
    
    # États
    SUCCESS = "green bold"
    WARNING = "yellow"
    ERROR = "red bold"
    
    # Métadonnées
    MUTED = "bright_black"
    EMPHASIS = "white bold"
    
    # Musique
    ARTIST = "magenta"
    ALBUM = "cyan italic"
    TRACK = "white"
    YEAR = "bright_black"
    LOVED = "red"
    SOURCE_ROON = "blue"
    SOURCE_LASTFM = "green"


def load_sample_data() -> List[Dict]:
    """
    Charge des données d'exemple.
    
    Tente de charger depuis data/collection/discogs-collection.json,
    sinon utilise des données fictives.
    """
    data_path = Path("data/collection/discogs-collection.json")
    
    if data_path.exists():
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data[:50]  # Limit to 50 for demo
        except Exception as e:
            console.print(f"[yellow]⚠️  Cannot load real data: {e}[/yellow]")
    
    # Fallback: Sample data
    return [
        {
            "release_id": 1,
            "Titre": "Kind of Blue",
            "Artiste": ["Miles Davis"],
            "Année": 1959,
            "Support": "Vinyle",
            "Labels": ["Columbia"],
            "Resume": "Album de jazz modal révolutionnaire enregistré en 1959."
        },
        {
            "release_id": 2,
            "Titre": "The Dark Side of the Moon",
            "Artiste": ["Pink Floyd"],
            "Année": 1973,
            "Support": "Vinyle",
            "Labels": ["Harvest"],
            "Resume": "Chef-d'œuvre du rock progressif avec effets sonores innovants."
        },
        {
            "release_id": 3,
            "Titre": "Abbey Road",
            "Artiste": ["The Beatles"],
            "Année": 1969,
            "Support": "Vinyle",
            "Labels": ["Apple"],
            "Resume": "Dernier album enregistré par les Beatles, iconique."
        },
        {
            "release_id": 4,
            "Titre": "Thriller",
            "Artiste": ["Michael Jackson"],
            "Année": 1982,
            "Support": "CD",
            "Labels": ["Epic"],
            "Resume": "Album le plus vendu de tous les temps."
        },
        {
            "release_id": 5,
            "Titre": "Nevermind",
            "Artiste": ["Nirvana"],
            "Année": 1991,
            "Support": "CD",
            "Labels": ["DGC"],
            "Resume": "Album grunge définissant une génération."
        },
    ]


def show_main_menu() -> Optional[str]:
    """Affiche le menu principal et retourne la sélection."""
    console.clear()
    console.print(Panel(LOGO, border_style="cyan", expand=False))
    
    options = [
        ('collection', '📂 Collection Discogs'),
        ('journal', '📔 Journal Roon'),
        ('timeline', '📈 Timeline Roon'),
        ('ai_logs', '🤖 Journal IA'),
        ('about', '❓ À propos'),
        ('quit', '❌ Quitter'),
    ]
    
    console.print("\n? Choisissez une action:\n")
    for key, label in options:
        if key == 'collection':
            console.print(f"  [cyan]❯[/cyan] {label}")
        else:
            console.print(f"    {label}")
    
    console.print("\n[dim]Utilisez ↑↓ pour naviguer, Entrée pour sélectionner[/dim]\n")
    
    # Simplified menu (without prompt_toolkit interactive selection)
    # In real implementation, use radiolist_dialog
    choice = prompt("Votre choix [collection/journal/timeline/ai_logs/about/quit]: ")
    
    return choice if choice in dict(options) else None


def show_collection_list(albums: List[Dict], page: int = 1, per_page: int = 10):
    """Affiche la liste de la collection (paginated)."""
    console.clear()
    
    # Header
    console.print(Panel(
        "📂 Collection Discogs",
        border_style="cyan",
        expand=False
    ))
    console.print()
    
    # Create table
    table = Table(
        title=f"Collection Discogs ({len(albums)} albums)",
        show_header=True,
        header_style="bold cyan",
        border_style="cyan"
    )
    
    table.add_column("Titre", style=SemanticColors.ALBUM)
    table.add_column("Artiste", style=SemanticColors.ARTIST)
    table.add_column("Année", justify="right", style=SemanticColors.YEAR)
    table.add_column("Support", style="white")
    
    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    page_albums = albums[start:end]
    
    # Add rows
    for album in page_albums:
        artist = album['Artiste']
        if isinstance(artist, list):
            artist = ", ".join(artist)
        
        table.add_row(
            album['Titre'],
            artist,
            str(album.get('Année', '')),
            album.get('Support', '')
        )
    
    console.print(table)
    
    # Footer
    total_pages = (len(albums) + per_page - 1) // per_page
    footer = (
        f"[{start + 1}-{min(end, len(albums))} sur {len(albums)}] | "
        f"Page {page}/{total_pages}"
    )
    console.print(f"\n{footer}")
    console.print("\n? Commandes: [n]ext [p]revious [v]iew [s]earch [b]ack [q]uit\n")


def show_album_detail(album: Dict):
    """Affiche les détails d'un album."""
    console.clear()
    
    # Create content
    content = Text()
    content.append("🎵 ", style="cyan")
    content.append(album['Titre'], style="cyan italic bold")
    content.append("\n\n")
    
    content.append("🎤 Artiste: ", style="white")
    artist = album['Artiste']
    if isinstance(artist, list):
        artist = ", ".join(artist)
    content.append(artist, style="magenta")
    content.append("\n")
    
    content.append("📅 Année: ", style="white")
    content.append(str(album.get('Année', '')), style="bright_black")
    content.append("\n")
    
    content.append("💿 Support: ", style="white")
    content.append(album.get('Support', ''), style="white")
    content.append("\n")
    
    if album.get('Labels'):
        content.append("🏷️  Labels: ", style="white")
        labels = album['Labels'] if isinstance(album['Labels'], list) else [album['Labels']]
        content.append(", ".join(labels), style="bright_black")
        content.append("\n")
    
    # Links
    content.append("\n🔗 Discogs: ", style="white")
    content.append(
        f"https://www.discogs.com/release/{album.get('release_id', 0)}",
        style="blue underline"
    )
    content.append("\n")
    
    # Resume
    if album.get('Resume'):
        content.append("\n📝 Résumé:\n", style="white bold")
        content.append(album['Resume'], style="white")
    
    # Create panel
    panel = Panel(
        content,
        border_style="cyan",
        expand=False,
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print("\n? Commandes: [e]dit [b]ack [q]uit\n")


def show_journal_example():
    """Affiche un exemple de journal Roon."""
    console.clear()
    
    console.print(Panel(
        "📔 Journal Roon",
        border_style="cyan",
        expand=False
    ))
    console.print()
    
    # Sample tracks
    tracks = [
        {
            "time": "18:21",
            "artist": "Serge Gainsbourg",
            "title": "Couleur Cafe",
            "album": "Le Zenith De Gainsbourg",
            "source": "roon",
            "loved": False,
            "ai_info": True
        },
        {
            "time": "18:17",
            "artist": "Nina Simone",
            "title": "Feeling Good",
            "album": "I Put a Spell on You",
            "source": "roon",
            "loved": True,
            "ai_info": True
        },
        {
            "time": "18:12",
            "artist": "Miles Davis",
            "title": "So What",
            "album": "Kind of Blue",
            "source": "roon",
            "loved": False,
            "ai_info": True
        },
        {
            "time": "17:58",
            "artist": "The Beatles",
            "title": "Here Comes the Sun",
            "album": "Abbey Road",
            "source": "lastfm",
            "loved": False,
            "ai_info": False
        },
    ]
    
    # Create table
    table = Table(
        title="Historique d'écoute (2700 tracks)",
        show_header=True,
        header_style="bold cyan",
        border_style="cyan"
    )
    
    table.add_column("Heure", style=SemanticColors.MUTED)
    table.add_column("Artiste", style=SemanticColors.ARTIST)
    table.add_column("Titre", style=SemanticColors.TRACK)
    table.add_column("Album", style=SemanticColors.ALBUM)
    table.add_column("Info", style="white")
    
    for track in tracks:
        # Source icon
        source_icon = "🎵" if track['source'] == 'roon' else "📻"
        source_color = "blue" if track['source'] == 'roon' else "green"
        
        # Info column
        info_parts = [f"[{source_color}]{source_icon} {track['source']}[/]"]
        if track['loved']:
            info_parts.append("[red]❤️[/red]")
        if track['ai_info']:
            info_parts.append("🤖")
        info = " ".join(info_parts)
        
        table.add_row(
            track['time'],
            track['artist'],
            track['title'],
            track['album'],
            info
        )
    
    console.print(table)
    console.print("\n[1-4 sur 2700] | Page 1/675")
    console.print("\n? Commandes: [n]ext [p]revious [f]ilter [v]iew [b]ack [q]uit\n")


def show_timeline_example():
    """Affiche un exemple de timeline."""
    console.clear()
    
    console.print(Panel(
        "📈 Timeline - Mardi 28 Janvier 2026",
        border_style="cyan",
        expand=False
    ))
    console.print()
    
    # Stats
    console.print("📊 Statistiques: 42 tracks | 23 artistes | 31 albums | 🔥 18h\n")
    
    # Timeline ASCII art
    console.print("[white]  6h   8h   10h  12h  14h  16h  18h  20h  22h[/white]")
    console.print("  ─────────────────────────────────────────────")
    console.print()
    console.print("                      🎵   🎵🎵 🎵🎵🎵 🎵🎵  🎵")
    console.print()
    console.print("  ─────────────────────────────────────────────")
    console.print("                           Peak ↑\n")
    
    # Zoom on peak hour
    console.print("[cyan bold]Zoom sur 18h (5 tracks):[/cyan bold]")
    
    table = Table(
        show_header=False,
        border_style="dim",
        padding=(0, 1)
    )
    
    table.add_column("Time", style=SemanticColors.MUTED)
    table.add_column("Track", style="white")
    
    tracks_18h = [
        ("18:21", "🎵 Serge Gainsbourg - Couleur Cafe"),
        ("18:17", "🎵 Nina Simone - Feeling Good"),
        ("18:12", "🎵 Miles Davis - So What"),
        ("18:08", "🎵 The Beatles - Here Comes the Sun"),
        ("18:03", "🎵 Pink Floyd - Wish You Were Here"),
    ]
    
    for time, track in tracks_18h:
        table.add_row(time, track)
    
    console.print(table)
    
    console.print("\n? Commandes: [←] previous hour [→] next hour [d]ay [v]iew track [b]ack [q]uit\n")


def show_about():
    """Affiche les informations à propos."""
    console.clear()
    
    about_text = Text()
    about_text.append("🎵 Musique Collection & Roon Tracker\n", style="cyan bold")
    about_text.append("Version 3.4.0-cli (Prototype)\n\n", style="white")
    about_text.append("Interface CLI moderne pour gérer votre collection musicale\n", style="white")
    about_text.append("et visualiser votre historique d'écoute.\n\n", style="white")
    about_text.append("Fonctionnalités:\n", style="cyan")
    about_text.append("  • Collection Discogs (~400 albums)\n", style="white")
    about_text.append("  • Journal Roon (~2700 tracks)\n", style="white")
    about_text.append("  • Timeline horaire\n", style="white")
    about_text.append("  • Journal IA\n", style="white")
    about_text.append("  • Navigation interactive\n\n", style="white")
    about_text.append("Technologies:\n", style="cyan")
    about_text.append("  • Rich (tables, panels, couleurs)\n", style="white")
    about_text.append("  • Prompt Toolkit (menus interactifs)\n", style="white")
    about_text.append("  • Click (CLI arguments)\n\n", style="white")
    about_text.append("Auteur: GitHub Copilot AI Agent\n", style="bright_black")
    about_text.append("Date: 28 janvier 2026\n", style="bright_black")
    
    panel = Panel(
        about_text,
        border_style="cyan",
        expand=False,
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print("\n? Appuyez sur Entrée pour continuer...")


def main():
    """Point d'entrée du prototype."""
    albums = load_sample_data()
    current_page = 1
    
    while True:
        try:
            choice = show_main_menu()
            
            if choice == 'quit' or choice is None:
                console.print("[yellow]Au revoir![/yellow]")
                break
            
            elif choice == 'collection':
                while True:
                    show_collection_list(albums, page=current_page, per_page=10)
                    cmd = prompt(">> ")
                    
                    if cmd == 'n':
                        total_pages = (len(albums) + 9) // 10
                        if current_page < total_pages:
                            current_page += 1
                    elif cmd == 'p':
                        if current_page > 1:
                            current_page -= 1
                    elif cmd == 'v':
                        idx = int(prompt("Index (1-10): ")) - 1
                        start = (current_page - 1) * 10
                        if 0 <= idx < 10 and start + idx < len(albums):
                            show_album_detail(albums[start + idx])
                            prompt("\nAppuyez sur Entrée pour continuer...")
                    elif cmd in ['b', 'q']:
                        break
            
            elif choice == 'journal':
                show_journal_example()
                prompt("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == 'timeline':
                show_timeline_example()
                prompt("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == 'ai_logs':
                console.clear()
                console.print("[yellow]🤖 Journal IA - Fonctionnalité en cours de développement[/yellow]")
                prompt("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == 'about':
                show_about()
                prompt()
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red bold]Error:[/red bold] {str(e)}")
            prompt("\nAppuyez sur Entrée pour continuer...")


if __name__ == '__main__':
    main()
