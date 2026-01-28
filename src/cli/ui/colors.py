"""
Semantic Color System - Système de couleurs sémantiques pour l'interface CLI.

Utilise des rôles sémantiques plutôt que des couleurs fixes,
permettant une adaptation gracieuse selon les capacités du terminal.

Inspiré par GitHub CLI et les guidelines de design moderne.

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 28 janvier 2026
"""

from enum import Enum
from typing import Dict, Optional
from rich.style import Style
from rich.text import Text


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


# Mapping vers couleurs Rich (4-bit palette) - Compatible tous terminaux
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
    
    SemanticColor.ARTIST: Style(color="#FF00FF"),                 # Magenta
    SemanticColor.ALBUM: Style(color="#00D9FF", italic=True),     # Cyan
    SemanticColor.TRACK: Style(color="#FFFFFF"),                  # White
    SemanticColor.YEAR: Style(color="#808080"),                   # Gray
    SemanticColor.LOVED: Style(color="#FF0000"),                  # Red
    SemanticColor.SOURCE_ROON: Style(color="#1E90FF"),           # Blue
    SemanticColor.SOURCE_LASTFM: Style(color="#00FF00"),         # Green
    SemanticColor.SOUNDTRACK: Style(color="#FFD700"),            # Gold
}

# Mapping sans couleurs pour terminaux basiques
NO_COLOR_STYLES: Dict[SemanticColor, Style] = {
    SemanticColor.PRIMARY: Style(bold=True),
    SemanticColor.SECONDARY: Style(),
    SemanticColor.ACCENT: Style(underline=True),
    
    SemanticColor.SUCCESS: Style(bold=True),
    SemanticColor.WARNING: Style(),
    SemanticColor.ERROR: Style(bold=True),
    SemanticColor.INFO: Style(),
    
    SemanticColor.MUTED: Style(dim=True),
    SemanticColor.EMPHASIS: Style(bold=True),
    
    SemanticColor.ARTIST: Style(),
    SemanticColor.ALBUM: Style(italic=True),
    SemanticColor.TRACK: Style(),
    SemanticColor.YEAR: Style(dim=True),
    SemanticColor.LOVED: Style(bold=True),
    SemanticColor.SOURCE_ROON: Style(),
    SemanticColor.SOURCE_LASTFM: Style(),
    SemanticColor.SOUNDTRACK: Style(underline=True),
}


# Variable globale pour le mode de couleur actuel
_color_mode = "auto"


def set_color_mode(mode: str):
    """
    Définit le mode de couleur global.
    
    Args:
        mode: Mode de couleur ('auto', 'truecolor', 'color', 'never')
    """
    global _color_mode
    _color_mode = mode


def get_color_mode() -> str:
    """
    Obtient le mode de couleur actuel.
    
    Returns:
        str: Mode de couleur actuel
    """
    return _color_mode


def apply_color(text: str, color: SemanticColor, truecolor: bool = False, 
                no_color: bool = False) -> Text:
    """
    Applique une couleur sémantique à un texte.
    
    Args:
        text: Texte à colorer
        color: Couleur sémantique
        truecolor: Force l'utilisation de truecolor
        no_color: Force l'absence de couleur
        
    Returns:
        Text: Objet Text Rich avec le style appliqué
    """
    if no_color:
        style = NO_COLOR_STYLES.get(color, Style())
    elif truecolor:
        style = TRUECOLOR_STYLES.get(color, COLOR_STYLES[color])
    else:
        style = COLOR_STYLES.get(color, Style())
    
    return Text(text, style=style)


def get_style(color: SemanticColor, truecolor: bool = False, 
              no_color: bool = False) -> Style:
    """
    Obtient le style Rich pour une couleur sémantique.
    
    Args:
        color: Couleur sémantique
        truecolor: Utiliser truecolor
        no_color: Désactiver les couleurs
        
    Returns:
        Style: Style Rich
    """
    if no_color:
        return NO_COLOR_STYLES.get(color, Style())
    elif truecolor:
        return TRUECOLOR_STYLES.get(color, COLOR_STYLES[color])
    else:
        return COLOR_STYLES.get(color, Style())


# Raccourcis pour les couleurs fréquemment utilisées
def primary(text: str, **kwargs) -> Text:
    """Applique le style PRIMARY."""
    return apply_color(text, SemanticColor.PRIMARY, **kwargs)


def secondary(text: str, **kwargs) -> Text:
    """Applique le style SECONDARY."""
    return apply_color(text, SemanticColor.SECONDARY, **kwargs)


def success(text: str, **kwargs) -> Text:
    """Applique le style SUCCESS."""
    return apply_color(text, SemanticColor.SUCCESS, **kwargs)


def warning(text: str, **kwargs) -> Text:
    """Applique le style WARNING."""
    return apply_color(text, SemanticColor.WARNING, **kwargs)


def error(text: str, **kwargs) -> Text:
    """Applique le style ERROR."""
    return apply_color(text, SemanticColor.ERROR, **kwargs)


def muted(text: str, **kwargs) -> Text:
    """Applique le style MUTED."""
    return apply_color(text, SemanticColor.MUTED, **kwargs)


def artist(text: str, **kwargs) -> Text:
    """Applique le style ARTIST."""
    return apply_color(text, SemanticColor.ARTIST, **kwargs)


def album(text: str, **kwargs) -> Text:
    """Applique le style ALBUM."""
    return apply_color(text, SemanticColor.ALBUM, **kwargs)
