#!/bin/bash
# Script de lancement de l'interface Streamlit Musique - GUI

# Remonter au répertoire racine du projet
cd "$(dirname "$0")/.."

# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer Streamlit avec paramètres réseau explicites
streamlit run src/gui/musique-gui.py --server.address 0.0.0.0 --server.port 8501
