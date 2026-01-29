#!/bin/bash
################################################################################
# Script d'installation et de configuration pour Roon Music Tracker
#
# Ce script automatise la mise en place complète de l'environnement pour
# le suivi des lectures Roon avec enrichissement des métadonnées.
#
# Fonctionnalités:
#   - Vérification des prérequis système
#   - Création de l'environnement virtuel Python
#   - Installation des dépendances
#   - Configuration interactive des clés API
#   - Création des fichiers de configuration
#   - Tests de connectivité
#   - Lancement du tracker
#
# Auteur: Patrick Ostertag
# Version: 1.0.0
# Date: 17 janvier 2026
################################################################################

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
ENV_FILE="${PROJECT_ROOT}/data/config/.env"
REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements-roon.txt"
CONFIG_FILE="${PROJECT_ROOT}/data/config/roon-config.json"
TRACKER_SCRIPT="${PROJECT_ROOT}/src/trackers/chk-roon.py"

################################################################################
# Fonctions utilitaires
################################################################################

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

################################################################################
# Vérifications des prérequis
################################################################################

check_prerequisites() {
    print_header "Vérification des prérequis"
    
    # Vérifier Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé"
        echo "Installez Python 3 depuis https://www.python.org/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION trouvé"
    
    # Vérifier pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 n'est pas installé"
        exit 1
    fi
    print_success "pip3 trouvé"
    
    # Vérifier la connexion réseau
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        print_warning "Pas de connexion Internet détectée"
        print_info "Une connexion est nécessaire pour installer les dépendances"
    else
        print_success "Connexion Internet OK"
    fi
    
    echo ""
}

################################################################################
# Création de l'environnement virtuel
################################################################################

setup_virtual_environment() {
    print_header "Configuration de l'environnement virtuel Python"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "L'environnement virtuel existe déjà"
        read -p "Voulez-vous le recréer ? (o/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Oo]$ ]]; then
            rm -rf "$VENV_DIR"
            print_info "Environnement virtuel supprimé"
        else
            print_info "Réutilisation de l'environnement existant"
            return
        fi
    fi
    
    print_info "Création de l'environnement virtuel..."
    python3 -m venv "$VENV_DIR"
    print_success "Environnement virtuel créé dans $VENV_DIR"
    
    # Activer l'environnement virtuel
    source "$VENV_DIR/bin/activate"
    print_success "Environnement virtuel activé"
    
    # Mettre à jour pip
    print_info "Mise à jour de pip..."
    pip install --upgrade pip --quiet
    print_success "pip mis à jour"
    
    echo ""
}

################################################################################
# Installation des dépendances
################################################################################

install_dependencies() {
    print_header "Installation des dépendances Python"
    
    # Créer le fichier requirements s'il n'existe pas
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_info "Création du fichier requirements..."
        cat > "$REQUIREMENTS_FILE" << 'EOF'
# =============================================================================
# Requirements pour Roon Music Tracker (minimal)
# =============================================================================
# Installation: pip install -r requirements-roon.txt
# =============================================================================

# ---- API Roon ----
roonapi>=0.1.0                # Connexion et contrôle Roon Core

# ---- API Last.fm ----
pylast>=5.0.0                 # Vérification lectures Last.fm (utilisé par chk-roon.py)

# ---- Gestion configuration ----
python-dotenv>=1.0.0          # Chargement variables d'environnement (.env)

# ---- Gestion certificats SSL ----
certifi>=2023.0.0             # Certificats SSL pour connexions HTTPS

# ---- Requêtes HTTP ----
requests>=2.31.0              # Requêtes API (Spotify, Last.fm, EurIA)
EOF
        print_success "Fichier requirements-roon.txt créé"
    fi
    
    print_info "Installation des packages Python..."
    pip install -r "$REQUIREMENTS_FILE" --quiet
    print_success "Toutes les dépendances sont installées"
    
    # Afficher les packages installés
    print_info "Packages installés:"
    pip list | grep -E "roonapi|pylast|python-dotenv|certifi|requests"
    
    echo ""
}

################################################################################
# Configuration des clés API
################################################################################

configure_api_keys() {
    print_header "Configuration des clés API"
    
    if [ -f "$ENV_FILE" ]; then
        print_warning "Le fichier .env existe déjà"
        read -p "Voulez-vous le reconfigurer ? (o/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Oo]$ ]]; then
            print_info "Configuration existante conservée"
            return
        fi
    fi
    
    echo ""
    print_info "Configuration des identifiants Spotify"
    echo "Obtenez vos clés sur: https://developer.spotify.com/dashboard"
    read -p "Spotify Client ID: " SPOTIFY_CLIENT_ID
    read -p "Spotify Client Secret: " SPOTIFY_CLIENT_SECRET
    
    echo ""
    print_info "Configuration de la clé Last.fm"
    echo "Obtenez votre clé sur: https://www.last.fm/api/account/create"
    read -p "Last.fm API Key: " LASTFM_API_KEY
    
    # Créer le fichier .env
    cat > "$ENV_FILE" << EOF
# Configuration Spotify
SPOTIFY_CLIENT_ID=$SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET=$SPOTIFY_CLIENT_SECRET

# Configuration Last.fm
API_KEY=$LASTFM_API_KEY

# Configuration Last.fm (optionnel - pour chk-last-fm.py)
API_SECRET=
LASTFM_USERNAME=
LASTFM_LIMIT=200
EOF
    
    print_success "Fichier .env créé avec succès"
    echo ""
}

################################################################################
# Configuration Roon
################################################################################

configure_roon() {
    print_header "Configuration Roon"
    
    if [ -f "$CONFIG_FILE" ]; then
        print_warning "Le fichier roon-config.json existe déjà"
        print_info "Il sera mis à jour automatiquement lors de la première connexion"
        return
    fi
    
    print_info "Configuration des heures d'écoute"
    read -p "Heure de début d'enregistrement (0-23) [6]: " START_HOUR
    START_HOUR=${START_HOUR:-6}
    
    read -p "Heure de fin d'enregistrement (0-23) [23]: " END_HOUR
    END_HOUR=${END_HOUR:-23}
    
    # Créer le fichier de configuration initial
    cat > "$CONFIG_FILE" << EOF
{
  "listen_start_hour": $START_HOUR,
  "listen_end_hour": $END_HOUR
}
EOF
    
    print_success "Configuration Roon créée"
    print_info "Le token et les informations de connexion seront ajoutés automatiquement"
    echo ""
}

################################################################################
# Test de connectivité
################################################################################

test_connectivity() {
    print_header "Test de connectivité"
    
    print_info "Test de l'environnement Python..."
    source "$VENV_DIR/bin/activate"
    
    # Test des imports
    python3 << 'EOF'
import sys
try:
    from roonapi import RoonApi, RoonDiscovery
    from dotenv import load_dotenv
    import certifi
    print("✅ Tous les modules Python sont importables")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Environnement Python configuré correctement"
    else
        print_error "Problème avec l'environnement Python"
        exit 1
    fi
    
    echo ""
}

################################################################################
# Création du script de lancement
################################################################################

create_launch_script() {
    print_header "Création du script de lancement"
    
    LAUNCH_SCRIPT="${SCRIPT_DIR}/start-roon-tracker.sh"
    
    cat > "$LAUNCH_SCRIPT" << 'EOF'
#!/bin/bash
# Script de lancement du Roon Music Tracker

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo "🎵 Démarrage du Roon Music Tracker..."

# Activer l'environnement virtuel
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ Environnement virtuel non trouvé. Exécutez setup-roon-tracker.sh d'abord."
    exit 1
fi

# Lancer le tracker
python3 "${TRACKER_SCRIPT}"
EOF
    
    chmod +x "$LAUNCH_SCRIPT"
    print_success "Script de lancement créé: start-roon-tracker.sh"
    echo ""
}

################################################################################
# Affichage du résumé
################################################################################

display_summary() {
    print_header "Installation terminée !"
    
    echo ""
    print_success "Configuration réussie"
    echo ""
    
    print_info "Fichiers créés:"
    echo "  • $VENV_DIR (environnement virtuel)"
    echo "  • $ENV_FILE (clés API)"
    echo "  • $CONFIG_FILE (configuration Roon)"
    echo "  • $REQUIREMENTS_FILE (dépendances)"
    echo "  • ${SCRIPT_DIR}/start-roon-tracker.sh (script de lancement)"
    echo ""
    
    print_info "Prochaines étapes:"
    echo ""
    echo "1. Assurez-vous que Roon Core est en cours d'exécution"
    echo ""
    echo "2. Lancez le tracker avec:"
    echo "   ${GREEN}./start-roon-tracker.sh${NC}"
    echo "   ou"
    echo "   ${GREEN}source .venv/bin/activate && python3 src/trackers/chk-roon.py${NC}"
    echo ""
    echo "3. Lors du premier lancement:"
    echo "   - Le script recherchera automatiquement Roon Core"
    echo "   - Une demande d'autorisation apparaîtra dans Roon"
    echo "   - Allez dans Roon > Paramètres > Extensions"
    echo "   - Autorisez 'Python Roon Tracker'"
    echo ""
    echo "4. Les lectures seront enregistrées dans:"
    echo "   ${GREEN}${SCRIPT_DIR}/chk-roon.json${NC}"
    echo ""
    
    print_info "Configuration des heures d'écoute:"
    echo "   Lectures enregistrées entre ${GREEN}$(grep listen_start_hour "$CONFIG_FILE" | grep -o '[0-9]*')h00${NC} et ${GREEN}$(grep listen_end_hour "$CONFIG_FILE" | grep -o '[0-9]*')h59${NC}"
    echo "   (modifiable dans $CONFIG_FILE)"
    echo ""
    
    print_warning "Note importante:"
    echo "   Le script vérifie les lectures toutes les 45 secondes."
    echo "   Appuyez sur Ctrl+C pour arrêter la surveillance."
    echo ""
}

################################################################################
# Fonction principale
################################################################################

main() {
    clear
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}║         🎵  Installation Roon Music Tracker  🎵               ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}║  Suivi automatique des lectures Roon avec enrichissement      ║${NC}"
    echo -e "${BLUE}║  des métadonnées via Spotify et Last.fm                       ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Exécution des étapes
    check_prerequisites
    setup_virtual_environment
    install_dependencies
    configure_api_keys
    configure_roon
    test_connectivity
    create_launch_script
    display_summary
    
    # Proposer de lancer immédiatement
    echo ""
    read -p "Voulez-vous lancer le tracker maintenant ? (o/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        echo ""
        print_info "Lancement du tracker..."
        echo ""
        source "$VENV_DIR/bin/activate"
        python3 "${TRACKER_SCRIPT}"
    fi
}

# Exécution
main "$@"
