# Prototypes - Interface CLI ASCII/ANSI

Ce répertoire contient les prototypes et démonstrations pour l'interface CLI proposée dans l'issue #59.

## Contenu

### cli_demo.py

**Description**: Prototype fonctionnel démontrant les concepts clés de l'interface CLI.

**Fonctionnalités:**
- Menu principal interactif
- Vue Collection Discogs (liste paginée + détails)
- Vue Journal Roon (exemple avec tracks)
- Vue Timeline (visualisation ASCII)
- Système de couleurs sémantiques
- Navigation au clavier

**Usage:**

```bash
# Installation des dépendances
pip install rich prompt_toolkit

# Lancement du prototype
python3 prototypes/cli_demo.py
```

**Navigation:**
- Menu principal: Choisir l'action avec le prompt texte
- Collection: `n` (next), `p` (previous), `v` (view), `b` (back), `q` (quit)
- Journal/Timeline: Navigation simplifiée avec prompt

**Limitations:**
- Données d'exemple fictives (si `data/collection/discogs-collection.json` absent)
- Navigation simplifiée (prompt texte au lieu de menus interactifs complets)
- Fonctionnalités limitées pour démonstration

**Technologies démontrées:**
- `rich`: Tables, panels, couleurs, formatage élégant
- `prompt_toolkit`: Prompts interactifs (version simplifiée)
- Système de couleurs sémantiques
- Pagination et navigation

## Documentation Associée

- [ISSUE-59-DESIGN-REPORT.md](../issues/ISSUE-59-DESIGN-REPORT.md): Rapport de design complet
- [ISSUE-59-IMPLEMENTATION-PROPOSAL.md](../issues/ISSUE-59-IMPLEMENTATION-PROPOSAL.md): Propositions d'implémentation détaillées

## Prochaines Étapes

1. Valider le design avec le stakeholder
2. Créer branch `feature/cli-interface`
3. Implémenter la version complète dans `src/cli/`
4. Intégrer toutes les fonctionnalités de Streamlit
5. Tests et documentation

---

**Note**: Ce prototype est une **démonstration de concept** et ne remplace pas l'interface Streamlit actuelle. Il sert à valider l'approche et les technologies avant une implémentation complète.
