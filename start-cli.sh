#!/usr/bin/env bash
###############################################################################
# start-cli.sh - Lancement de l'interface CLI
#
# Ce script lance l'interface CLI moderne pour le projet
# Musique Collection & Roon Tracker.
#
# Usage:
#   ./start-cli.sh                    # Mode interactif
#   ./start-cli.sh collection list    # Commande CLI
#   ./start-cli.sh --help             # Aide
#
# Author: GitHub Copilot AI Agent
# Version: 1.0.0
# Date: 28 janvier 2026
###############################################################################

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Détection du répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

# Fonction d'affichage d'erreur
error() {
    echo -e "${RED}❌ Erreur:${NC} $1" >&2
    exit 1
}

# Fonction d'affichage d'information
info() {
    echo -e "${CYAN}ℹ️  Info:${NC} $1"
}

# Fonction d'affichage de succès
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Vérification de Python 3
if ! command -v python3 &> /dev/null; then
    error "Python 3 n'est pas installé. Veuillez l'installer."
fi

# Vérification de l'environnement virtuel
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    info "Création de l'environnement virtuel..."
    python3 -m venv "$PROJECT_ROOT/.venv" || error "Impossible de créer l'environnement virtuel"
    success "Environnement virtuel créé"
fi

# Activation de l'environnement virtuel
source "$PROJECT_ROOT/.venv/bin/activate" || error "Impossible d'activer l'environnement virtuel"

# Vérification et installation des dépendances
info "Vérification des dépendances..."
if ! python3 -c "import rich" 2>/dev/null; then
    info "Installation des dépendances CLI..."
    pip install -q rich click prompt-toolkit || error "Impossible d'installer les dépendances"
    success "Dépendances installées"
else
    success "Dépendances déjà installées"
fi

# Changement vers le répertoire du projet
cd "$PROJECT_ROOT" || error "Impossible d'accéder au répertoire du projet"

# Lancement du CLI
info "Lancement de l'interface CLI..."
echo ""

# Exécution avec les arguments fournis
python3 -m src.cli.main "$@"
