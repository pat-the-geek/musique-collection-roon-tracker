#!/bin/bash
# =============================================================================
# Script d'installation des dépendances du projet Musique
# =============================================================================
# Ce script installe automatiquement toutes les dépendances Python nécessaires
# pour le projet dans un environnement virtuel.
#
# Usage:
#   chmod +x scripts/install-dependencies.sh
#   ./scripts/install-dependencies.sh
#
# Auteur: Patrick Ostertag
# Date: 24 janvier 2026
# Version: 3.0.0
# =============================================================================

set -e  # Arrêter le script en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Déterminer le répertoire du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Installation des dépendances - Projet Musique v3.0.0            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Vérifier Python
echo -e "${YELLOW}📌 Vérification de Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    echo "   Installez Python 3.8 ou supérieur depuis https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION détecté${NC}"
echo ""

# Se déplacer vers le répertoire du projet
cd "$PROJECT_ROOT"

# Vérifier ou créer l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
else
    echo -e "${GREEN}✅ Environnement virtuel existant détecté${NC}"
fi
echo ""

# Activer l'environnement virtuel
echo -e "${YELLOW}🔧 Activation de l'environnement virtuel...${NC}"
source .venv/bin/activate

# Mettre à jour pip
echo -e "${YELLOW}⬆️  Mise à jour de pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✅ pip mis à jour${NC}"
echo ""

# Installer les dépendances
echo -e "${YELLOW}📥 Installation des dépendances depuis requirements.txt...${NC}"
echo ""

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo ""
    echo -e "${GREEN}✅ Toutes les dépendances ont été installées avec succès !${NC}"
else
    echo -e "${RED}❌ Fichier requirements.txt introuvable${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      Installation terminée !                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📋 Dépendances installées :${NC}"
echo ""
pip list | grep -E "(roonapi|pylast|mutagen|streamlit|pillow|requests|python-dotenv|certifi)"
echo ""
echo -e "${YELLOW}💡 Pour activer l'environnement virtuel :${NC}"
echo "   source .venv/bin/activate"
echo ""
echo -e "${YELLOW}📚 Documentation disponible dans :${NC}"
echo "   - docs/README-ROON-TRACKER.md"
echo "   - docs/README-MUSIQUE-GUI.md"
echo "   - docs/ARCHITECTURE-OVERVIEW.md"
echo ""
