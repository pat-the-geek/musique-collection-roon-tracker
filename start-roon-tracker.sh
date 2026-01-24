#!/bin/bash
# Script de lancement du tracker Roon depuis la racine du projet

cd "$(dirname "$0")"

# Activer l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "Exécutez d'abord: ./scripts/setup-roon-tracker.sh"
    exit 1
fi

source .venv/bin/activate

# Lancer le tracker
python3 src/trackers/chk-roon.py
