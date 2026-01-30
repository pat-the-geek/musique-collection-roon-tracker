# 🧹 Quick Start: Nettoyer les Branches Mergées

## Exécution Rapide

**Méthode recommandée** (la plus simple):

```bash
./scripts/delete-merged-branches.sh
```

Ce script va supprimer les **42 branches** qui ont déjà été mergées dans `main`.

## Alternative: GitHub Actions

Si vous préférez utiliser l'interface GitHub:

1. Allez sur https://github.com/pat-the-geek/musique-collection-roon-tracker/actions
2. Sélectionnez "Delete Merged Branches" dans la liste
3. Cliquez sur "Run workflow"
4. Confirmez en cliquant sur le bouton vert "Run workflow"

## Vérification

Après exécution, vérifier le nettoyage:

```bash
# Mettre à jour les références locales
git fetch --prune origin

# Compter les branches restantes
git branch -r | wc -l
```

## Documentation Complète

Pour plus de détails, consultez:
- **Guide complet**: [docs/CLEANUP-MERGED-BRANCHES.md](CLEANUP-MERGED-BRANCHES.md)
- **Implémentation**: [docs/BRANCH-CLEANUP-IMPLEMENTATION.md](BRANCH-CLEANUP-IMPLEMENTATION.md)

## Branches qui Seront Supprimées

42 branches au total, incluant:
- copilot/implement-second-step-programming
- copilot/fix-click-module-error
- copilot/list-merged-branches
- ... et 39 autres branches mergées

Toutes ces branches correspondent à des Pull Requests qui ont été **mergées avec succès**. Le code est **préservé** dans l'historique de `main`.

## Sécurité

✅ **Opération sûre**: Le code de ces branches est déjà dans `main`  
⚠️ **Attention**: L'opération est irréversible (mais les branches peuvent être récupérées via GitHub pendant 90 jours si nécessaire)

---

**Dernière mise à jour**: 2026-01-30  
**Statut**: Prêt à exécuter
