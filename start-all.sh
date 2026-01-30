#!/bin/bash
# Script de lancement de l'interface Streamlit
# Usage: ./start-all.sh [--no-browser]

cd "$(dirname "$0")"

# Activer l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "Créez d'abord l'environnement: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source .venv/bin/activate

# Vérifier l'option --no-browser
NO_BROWSER=""
if [ "$1" = "--no-browser" ]; then
    NO_BROWSER="--server.headless=true"
    echo "🌐 Mode sans navigateur activé"
fi

# Fonction de nettoyage pour arrêter Streamlit
cleanup() {
    echo ""
    echo "🛑 Arrêt de l'interface..."
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null
        echo "✅ Streamlit arrêté"
    fi
    exit 0
}

# Capturer les signaux d'interruption (Ctrl+C)
trap cleanup SIGINT SIGTERM

echo "🚀 Démarrage de l'interface..."
echo ""

# Lancer Streamlit
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
echo "✨ Interface démarrée avec succès!"
echo ""
echo "🌐 Interface Web: http://localhost:8501"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter l'interface"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Attendre que le processus se termine
wait
