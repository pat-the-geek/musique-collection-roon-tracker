#!/bin/bash
# Script pour exécuter les tests du projet Musique Collection & Tracker
# Version: 1.0.0
# Date: 26 janvier 2026

set -e

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Tests - Musique Collection & Tracker${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Vérifier que pytest est installé
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo -e "${RED}❌ pytest n'est pas installé${NC}"
    echo -e "${YELLOW}Installation avec: pip install pytest pytest-cov pytest-mock${NC}"
    exit 1
fi

# Parse arguments
COVERAGE=false
VERBOSE=false
MARKERS=""
TEST_PATH="src/tests/"

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --spotify)
            TEST_PATH="src/tests/test_spotify_service.py"
            shift
            ;;
        --constants)
            TEST_PATH="src/tests/test_constants.py"
            shift
            ;;
        --metadata)
            TEST_PATH="src/tests/test_metadata_cleaner.py"
            shift
            ;;
        --scheduler)
            TEST_PATH="src/tests/test_scheduler.py"
            shift
            ;;
        -m)
            MARKERS="-m $2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./run-tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage       Afficher la couverture de code"
            echo "  -v, --verbose        Mode verbose"
            echo "  --spotify            Exécuter uniquement les tests Spotify"
            echo "  --constants          Exécuter uniquement les tests Constants"
            echo "  --metadata           Exécuter uniquement les tests Metadata Cleaner"
            echo "  --scheduler          Exécuter uniquement les tests Scheduler"
            echo "  -m <marker>          Filtrer par marqueur (unit, integration, slow)"
            echo "  -h, --help           Afficher cette aide"
            echo ""
            echo "Exemples:"
            echo "  ./run-tests.sh                    # Tous les tests"
            echo "  ./run-tests.sh --coverage         # Avec couverture"
            echo "  ./run-tests.sh --spotify          # Tests Spotify uniquement"
            echo "  ./run-tests.sh -m unit            # Tests unitaires uniquement"
            exit 0
            ;;
        *)
            echo -e "${RED}Option inconnue: $1${NC}"
            echo "Utilisez --help pour voir les options disponibles"
            exit 1
            ;;
    esac
done

# Construire la commande pytest
CMD="python3 -m pytest ${TEST_PATH}"

if [ "$VERBOSE" = true ]; then
    CMD="${CMD} -vv"
else
    CMD="${CMD} -v"
fi

if [ "$COVERAGE" = true ]; then
    CMD="${CMD} --cov=services --cov=constants --cov-report=term-missing --cov-report=html"
fi

if [ -n "$MARKERS" ]; then
    CMD="${CMD} ${MARKERS}"
fi

# Exécuter les tests
echo -e "${YELLOW}Exécution des tests...${NC}"
echo -e "${BLUE}Commande: ${CMD}${NC}"
echo ""

if $CMD; then
    echo ""
    echo -e "${GREEN}✅ Tests réussis!${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo -e "${BLUE}📊 Rapport de couverture HTML généré dans: htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}❌ Certains tests ont échoué${NC}"
    exit 1
fi
