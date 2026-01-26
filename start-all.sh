#!/bin/bash
# Script de lancement simultané du tracker Roon et de l'interface Streamlit
# Usage: ./start-all.sh [--no-browser]

cd "$(dirname "$0")"

# Activer l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "Exécutez d'abord: ./scripts/setup-roon-tracker.sh"
    exit 1
fi

source .venv/bin/activate

# Vérifier l'option --no-browser
NO_BROWSER=""
if [ "$1" = "--no-browser" ]; then
    NO_BROWSER="--server.headless=true"
    echo "🌐 Mode sans navigateur activé"
fi

# Fonction de nettoyage pour arrêter les processus en arrière-plan
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    if [ ! -z "$ROON_PID" ]; then
        kill $ROON_PID 2>/dev/null
        echo "✅ Tracker Roon arrêté"
    fi
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null
        echo "✅ Streamlit arrêté"
    fi
    exit 0
}

# Capturer les signaux d'interruption (Ctrl+C)
trap cleanup SIGINT SIGTERM

echo "🚀 Démarrage des services..."
echo ""

# Lancer le tracker Roon en arrière-plan
echo "📻 Démarrage du tracker Roon..."
python3 src/trackers/chk-roon.py &
ROON_PID=$!
echo "✅ Tracker Roon lancé (PID: $ROON_PID)"
echo ""

# Attendre 2 secondes pour laisser le tracker démarrer
sleep 2

# Lancer Streamlit en arrière-plan
echo "🌐 Démarrage de l'interface Streamlit..."
if [ -z "$NO_BROWSER" ]; then
    streamlit run src/gui/musique-gui.py &
else
    streamlit run src/gui/musique-gui.py $NO_BROWSER &
fi
STREAMLIT_PID=$!
echo "✅ Streamlit lancé (PID: $STREAMLIT_PID)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Services démarrés avec succès!"
echo ""
echo "📻 Tracker Roon: Surveillance des lectures en cours..."
echo "🌐 Interface Web: http://localhost:8501"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter les deux services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Attendre que l'un des processus se termine
wait
