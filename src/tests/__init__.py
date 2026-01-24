"""Module d'initialisation pour les tests.

Permet l'import du package tests et configure le path.

Version: 1.0.0
Date: 24 janvier 2026
"""

import sys
import os

# S'assurer que le répertoire src est dans le path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
