# CLI Module - Interface en ligne de commande

Interface CLI moderne et élégante pour Musique Collection & Roon Tracker.

**Version:** 1.0.0  
**Date:** 28 janvier 2026  
**Status:** Phase 1 - Fondations ✅

---

## 📋 Vue d'ensemble

Cette interface CLI fournit une alternative légère et rapide à l'interface web Streamlit, optimisée pour:
- Sessions SSH distantes
- Terminaux de faible capacité
- Scripts d'automatisation
- Utilisateurs préférant la ligne de commande

### Caractéristiques principales

✅ **Implémenté (Phase 1 - Fondations)**
- Architecture modulaire avec séparation des responsabilités
- Système de couleurs sémantiques adaptatif
- Détection automatique des capacités du terminal
- Support multi-modes: auto, truecolor, couleurs basiques, sans couleur
- Framework CLI complet avec Click
- Tests unitaires complets (48 tests, 100% pass)

🚧 **En développement (Phases suivantes)**
- Collection Discogs (liste, recherche, détails, édition)
- Journal d'écoute Roon/Last.fm
- Visualisation timeline horaire
- Logs d'enrichissement IA
- Mode interactif avec menus

---

## 🚀 Installation et Utilisation

### ⚠️ Prérequis

**IMPORTANT**: Avant d'utiliser le CLI, vous devez installer les dépendances Python requises.

### Installation des dépendances

**Méthode 1 - Installation complète (recommandée):**
```bash
# Installe toutes les dépendances du projet
pip install -r requirements.txt
```

**Méthode 2 - Installation minimale (CLI uniquement):**
```bash
# Installe uniquement les dépendances CLI
pip install rich click prompt-toolkit
```

**Méthode 3 - Utiliser le script de lancement:**
```bash
# Le script vérifie et installe automatiquement les dépendances
./start-cli.sh
```

### Lancement rapide

```bash
# Avec le script de lancement (recommandé)
./start-cli.sh

# Ou directement avec Python
python3 -m src.cli.main

# Mode interactif
python3 -m src.cli.main interactive

# Aide
python3 -m src.cli.main --help
```

---

## 📚 Commandes disponibles

### Commandes globales

```bash
# Afficher la version et les capacités du terminal
python3 -m src.cli.main version

# Mode interactif
python3 -m src.cli.main interactive

# Options de couleur
python3 -m src.cli.main --color auto      # Détection automatique (défaut)
python3 -m src.cli.main --color truecolor # Forcer 24-bit
python3 -m src.cli.main --color never     # Désactiver les couleurs
```

### Collection Discogs

```bash
# Lister les albums (à venir Phase 2)
python3 -m src.cli.main collection list --page 1 --per-page 25

# Rechercher un album
python3 -m src.cli.main collection search "Kind of Blue"

# Voir les détails d'un album
python3 -m src.cli.main collection view 123456
```

### Journal d'écoute

```bash
# Afficher le journal (à venir Phase 3)
python3 -m src.cli.main journal show --source all --page 1

# Filtrer par date
python3 -m src.cli.main journal show --date 2026-01-28

# Statistiques
python3 -m src.cli.main journal stats
```

### Timeline

```bash
# Afficher la timeline (à venir Phase 3)
python3 -m src.cli.main timeline display --day 2026-01-28

# Mode compact ou détaillé
python3 -m src.cli.main timeline display --mode detailed
```

### Logs IA

```bash
# Lister les logs disponibles (à venir Phase 3)
python3 -m src.cli.main ai logs

# Voir un log spécifique
python3 -m src.cli.main ai view 2026-01-28
```

---

## 🏗️ Architecture

### Structure des modules

```
src/cli/
├── __init__.py              # Package CLI
├── main.py                  # Point d'entrée et CLI Click
│
├── commands/                # Implémentations des commandes
│   ├── __init__.py
│   ├── collection.py       # (À venir Phase 2)
│   ├── journal.py          # (À venir Phase 3)
│   ├── timeline.py         # (À venir Phase 3)
│   └── ai_logs.py          # (À venir Phase 3)
│
├── ui/                      # Composants d'interface
│   ├── __init__.py
│   ├── colors.py           # Système de couleurs sémantiques ✅
│   ├── components.py       # (À venir)
│   └── layouts.py          # (À venir)
│
├── models/                  # Modèles de données
│   └── __init__.py
│
└── utils/                   # Utilitaires
    ├── __init__.py
    ├── terminal.py         # Détection capacités terminal ✅
    ├── data_loader.py      # (À venir)
    └── pager.py            # (À venir)
```

### Technologies utilisées

- **Click**: Framework CLI moderne et ergonomique
- **Rich**: Rendu terminal élégant avec couleurs et formatage
- **Prompt Toolkit**: Prompts interactifs et autocomplétion

---

## 🎨 Système de couleurs

Le CLI utilise un système de **couleurs sémantiques** qui s'adapte automatiquement aux capacités du terminal:

### Rôles sémantiques

```python
from src.cli.ui.colors import primary, success, error, artist, album

# Utilisation des couleurs
print(primary("Titre principal"))      # Cyan bold
print(success("Opération réussie"))    # Vert bold
print(error("Erreur détectée"))        # Rouge bold
print(artist("Nina Simone"))           # Magenta
print(album("Kind of Blue"))           # Cyan italic
```

### Modes de couleur supportés

1. **Auto** (défaut): Détection automatique
2. **Truecolor**: Couleurs 24-bit pour terminaux modernes
3. **Color**: Palette 4-bit/8-bit standard
4. **Never**: Désactivation complète (accessible)

---

## 🧪 Tests

### Tests unitaires

```bash
# Tous les tests CLI
python3 -m pytest src/tests/test_cli_*.py -v

# Tests couleurs
python3 -m pytest src/tests/test_cli_colors.py -v

# Tests terminal
python3 -m pytest src/tests/test_cli_terminal.py -v

# Avec couverture
python3 -m pytest src/tests/test_cli_*.py --cov=src.cli --cov-report=term-missing
```

### Résultats actuels

- **48 tests unitaires** (100% pass)
- Terminal utilities: 19 tests ✅
- Color system: 29 tests ✅
- Couverture: ~95% (fondations)

---

## 📖 Documentation

### Pour les développeurs

- [ISSUE-59-IMPLEMENTATION-PROPOSAL.md](../../issues/ISSUE-59-IMPLEMENTATION-PROPOSAL.md): Proposition complète
- [ISSUE-59-DESIGN-REPORT.md](../../issues/ISSUE-59-DESIGN-REPORT.md): Rapport de design
- Architecture complète détaillée dans la proposition

### Roadmap

**Phase 1 - Fondations** (Semaine 1) ✅ TERMINÉE
- Structure de base du module CLI
- Système de couleurs sémantiques
- Utilitaires terminal
- Tests unitaires

**Phase 2 - Collection** (Semaine 2) 🚧 EN COURS
- Liste paginée des albums
- Recherche interactive
- Vue détail album
- Édition basique

**Phase 3 - Journal & Timeline** (Semaines 3-4)
- Journal d'écoute
- Timeline ASCII art
- Logs IA

**Phase 4 - Polish** (Semaines 5-6)
- Optimisations performance
- Documentation complète
- Release v3.5.0-cli

---

## 🤝 Contribution

### Standards de code

- PEP 8 pour le style Python
- Docstrings complètes (Google style)
- Tests unitaires pour toute nouvelle fonctionnalité
- Type hints pour les signatures de fonctions

### Ajout de nouvelles commandes

1. Créer le module dans `src/cli/commands/`
2. Implémenter les fonctions de commande
3. Enregistrer dans `src/cli/main.py`
4. Ajouter les tests dans `src/tests/`

---

## 📝 Licence

Projet interne - Tous droits réservés

---

**Auteur:** GitHub Copilot AI Agent  
**Date:** 28 janvier 2026  
**Version:** 1.0.0
