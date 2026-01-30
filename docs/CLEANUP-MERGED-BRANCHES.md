# Nettoyage des Branches Mergées

## Vue d'ensemble

Ce document explique comment supprimer toutes les branches qui ont déjà été mergées dans la branche `main`.

## Branches identifiées pour suppression

**Total: 42 branches**

Toutes ces branches correspondent à des Pull Requests qui ont été mergées avec succès dans `main`.

### Liste complète des branches

1. `copilot/implement-second-step-programming`
2. `copilot/fix-click-module-error`
3. `copilot/list-merged-branches`
4. `copilot/check-library-dependencies`
5. `copilot/implement-issue-59-solution`
6. `copilot/prepare-design-report`
7. `copilot/update-documents-for-timeline-roon`
8. `copilot/fix-timeline-roon-code`
9. `copilot/fix-display-issues`
10. `copilot/propose-roon-journal-interface`
11. `copilot/organize-main-directory-files`
12. `copilot/fix-zero-tracks-issue`
13. `copilot/fix-tracks-analysis-issue`
14. `copilot/verify-report-data-issue-47`
15. `copilot/fix-calculation-errors`
16. `copilot/modify-code-according-to-document`
17. `copilot/analyze-issue-41`
18. `copilot/prepare-data-model-for-sqlite-migration`
19. `copilot/update-docs-todo-roadmap`
20. `copilot/fix-playlist-duplicates`
21. `copilot/check-roon-api-playlist-functionality`
22. `copilot/update-roadmap-and-todo-list`
23. `copilot/improve-tests-based-on-issue-28`
24. `copilot/fix-time-issue`
25. `copilot/check-test-status`
26. `copilot/continue-test-implementation`
27. `copilot/fix-correct-collection-issue`
28. `copilot/update-coherence-check`
29. `copilot/update-roadmap-and-docs`
30. `copilot/fix-246838957-1141348123-1143eb3b-6dc7-42ae-9e2b-6ea93ddca748`
31. `copilot/fix-issue-21-tracker`
32. `copilot/analyse-revues-modifications`
33. `copilot/fix-issue-15-collection-errors`
34. `copilot/improve-user-interface-design`
35. `copilot/fix-haiku-markdown-display`
36. `copilot/fix-haiku-display-issues`
37. `copilot/create-task-scheduler-module`
38. `copilot/update-last-order-status`
39. `copilot/create-scheduler-module`
40. `copilot/improve-ui-layout-history`
41. `copilot/prioritize-tasks-for-project`
42. `copilot/analyse-code-architecture`

## Méthode automatisée: Script Bash

### Utilisation du script

Un script automatisé a été créé pour faciliter la suppression de toutes ces branches:

```bash
./scripts/delete-merged-branches.sh
```

### Ce que fait le script

1. Parcourt la liste complète des 42 branches mergées
2. Tente de supprimer chaque branche du remote GitHub
3. Affiche un résumé avec:
   - Nombre de branches supprimées avec succès
   - Nombre de branches qui n'ont pas pu être supprimées
   - Liste des branches en échec (le cas échéant)
4. Nettoie les références locales avec `git fetch --prune`

### Prérequis

- Accès en écriture au dépôt GitHub
- Authentification Git configurée correctement

## Méthode manuelle: Commande Git

Si vous préférez supprimer les branches manuellement ou en petits lots:

```bash
# Supprimer une seule branche
git push origin --delete nom-de-la-branche

# Exemple
git push origin --delete copilot/implement-second-step-programming
```

### Supprimer plusieurs branches à la fois

```bash
# Méthode 1: Ligne par ligne
git push origin --delete \
  copilot/implement-second-step-programming \
  copilot/fix-click-module-error \
  copilot/list-merged-branches

# Méthode 2: Depuis un fichier
cat liste-branches.txt | while read branch; do
  git push origin --delete "$branch"
done
```

## Méthode via l'interface GitHub

1. Aller sur https://github.com/pat-the-geek/musique-collection-roon-tracker/branches
2. Pour chaque branche dans la liste ci-dessus:
   - Cliquer sur l'icône de la corbeille (🗑️) à droite de la branche
   - Confirmer la suppression

## Nettoyage des références locales

Après la suppression des branches distantes, nettoyer les références locales:

```bash
# Mettre à jour les références et supprimer les branches distantes obsolètes
git fetch --prune origin

# Optionnel: Supprimer les branches locales trackées qui n'existent plus
git branch -vv | grep ': gone]' | awk '{print $1}' | xargs -r git branch -d
```

## Vérification

Pour vérifier que les branches ont bien été supprimées:

```bash
# Lister les branches distantes restantes
git branch -r

# Compter les branches distantes
git branch -r | wc -l
```

## Sécurité

⚠️ **Attention**: Cette opération est **irréversible**. Les branches supprimées ne pourront pas être récupérées facilement (sauf via les refs GitHub pendant 90 jours).

✅ **Sûr car**: Toutes ces branches correspondent à des Pull Requests déjà mergées. Le code est préservé dans l'historique de `main`.

## Support

En cas de problème:
1. Vérifier que vous avez les droits d'écriture sur le dépôt
2. Vérifier votre authentification Git
3. Consulter les logs d'erreur du script

---

**Date de création**: 2026-01-30  
**Branches identifiées**: 42  
**Statut**: Prêt pour exécution
