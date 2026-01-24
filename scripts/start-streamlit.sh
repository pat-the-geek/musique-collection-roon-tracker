#!/bin/bash
# Script de lancement de l'interface Streamlit Musique - GUI

# Remonter au répertoire racine du projet
cd "$(dirname "$0")/.."

# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer Streamlit
streamlit run src/gui/musique-gui.py
