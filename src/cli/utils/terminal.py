"""
Terminal Utilities - Détection et gestion des capacités du terminal.

Ce module fournit des utilitaires pour:
- Détecter les capacités du terminal (couleurs, dimensions, etc.)
- Obtenir la taille du terminal dynamiquement
- Vérifier le support des couleurs
- Détecter le type de terminal

Author: GitHub Copilot AI Agent
Version: 1.0.0
Date: 28 janvier 2026
"""

import os
import sys
import shutil
from typing import Tuple, Dict, Any


def get_terminal_size() -> Tuple[int, int]:
    """
    Obtient la taille actuelle du terminal.
    
    Returns:
        Tuple[int, int]: (colonnes, lignes)
    """
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines


def supports_color() -> bool:
    """
    Vérifie si le terminal supporte les couleurs.
    
    Returns:
        bool: True si le terminal supporte les couleurs
    """
    # Check NO_COLOR environment variable (https://no-color.org/)
    if os.environ.get('NO_COLOR'):
        return False
    
    # Check FORCE_COLOR
    if os.environ.get('FORCE_COLOR'):
        return True
    
    # Check if stdout is a TTY
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check TERM variable
    term = os.environ.get('TERM', '').lower()
    if term in ('dumb', 'unknown'):
        return False
    
    # Common color-supporting terminals
    if any(name in term for name in ['color', 'ansi', 'xterm', 'screen', 'linux']):
        return True
    
    return True


def supports_truecolor() -> bool:
    """
    Vérifie si le terminal supporte les couleurs truecolor (24-bit).
    
    Returns:
        bool: True si le terminal supporte truecolor
    """
    if not supports_color():
        return False
    
    # Check COLORTERM for truecolor support
    colorterm = os.environ.get('COLORTERM', '').lower()
    if colorterm in ('truecolor', '24bit'):
        return True
    
    # Some terminal emulators
    term_program = os.environ.get('TERM_PROGRAM', '').lower()
    if term_program in ('iterm.app', 'hyper', 'vscode'):
        return True
    
    return False


def detect_terminal_capabilities() -> Dict[str, Any]:
    """
    Détecte les capacités du terminal.
    
    Returns:
        Dict[str, Any]: Dictionnaire contenant les capacités détectées:
            - color: Support des couleurs (bool)
            - truecolor: Support truecolor 24-bit (bool)
            - unicode: Support Unicode (bool)
            - width: Largeur du terminal (int)
            - height: Hauteur du terminal (int)
            - term: Type de terminal (str)
            - is_tty: Est un TTY (bool)
    """
    width, height = get_terminal_size()
    
    capabilities = {
        'color': supports_color(),
        'truecolor': supports_truecolor(),
        'unicode': _supports_unicode(),
        'width': width,
        'height': height,
        'term': os.environ.get('TERM', 'unknown'),
        'is_tty': sys.stdout.isatty() if hasattr(sys.stdout, 'isatty') else False,
    }
    
    return capabilities


def _supports_unicode() -> bool:
    """
    Vérifie si le terminal supporte Unicode.
    
    Returns:
        bool: True si Unicode est supporté
    """
    try:
        encoding = sys.stdout.encoding or 'utf-8'
        return encoding.lower() in ('utf-8', 'utf8', 'utf_8')
    except:
        return False


def clear_screen():
    """Efface l'écran du terminal."""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/Mac
        os.system('clear')


def move_cursor(x: int, y: int):
    """
    Déplace le curseur à la position (x, y).
    
    Args:
        x: Colonne (0-indexed)
        y: Ligne (0-indexed)
    """
    print(f'\033[{y+1};{x+1}H', end='', flush=True)


def hide_cursor():
    """Cache le curseur."""
    print('\033[?25l', end='', flush=True)


def show_cursor():
    """Affiche le curseur."""
    print('\033[?25h', end='', flush=True)


def get_terminal_name() -> str:
    """
    Obtient le nom du terminal.
    
    Returns:
        str: Nom du terminal ou 'unknown'
    """
    # Try TERM_PROGRAM first (modern terminals)
    term_program = os.environ.get('TERM_PROGRAM')
    if term_program:
        return term_program
    
    # Fallback to TERM
    return os.environ.get('TERM', 'unknown')


def is_ssh_session() -> bool:
    """
    Détecte si on est dans une session SSH.
    
    Returns:
        bool: True si c'est une session SSH
    """
    return bool(os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'))
