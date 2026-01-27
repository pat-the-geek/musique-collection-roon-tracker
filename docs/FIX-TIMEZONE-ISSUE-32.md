# Fix pour le problème d'heure (Issue #32)

## Problème identifié

Les événements du journal Roon affichaient une heure en décalage par rapport à la réalité. Par exemple :
- Affichage dans le journal : 10:19
- Heure réelle : 11:19

Ce problème affectait :
- Le fichier `chk-roon.json` (historique des lectures Roon)
- Le fichier `chk-last-fm.json` (historique des lectures Last.fm)
- Les logs IA quotidiens (`output/ai-logs/ai-log-YYYY-MM-DD.txt`)

## Cause racine

Les timestamps Unix étaient convertis en affichage UTC au lieu du fuseau horaire local :

```python
# ❌ AVANT (incorrect)
date_str = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M')
# Résultat : affiche l'heure en UTC

# ✅ APRÈS (correct)
date_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
# Résultat : affiche l'heure en fuseau horaire local
```

## Corrections appliquées

### 1. `src/trackers/chk-roon.py` (3 emplacements)

**Ligne 1810** - Création d'entrées de lecture Roon :
```python
date_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
```

**Ligne 1373** - Nom de fichier des logs IA :
```python
date_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d')
```

**Ligne 1378** - Horodatage dans les logs IA :
```python
datetime_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
```

### 2. `src/trackers/chk-last-fm.py` (1 emplacement)

**Ligne 236** - Conversion des timestamps Last.fm :
```python
date_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
```

## Tests ajoutés

Un nouveau fichier de tests a été créé : `src/tests/test_timestamp_fix.py`

Ce fichier contient 5 tests unitaires qui vérifient :
1. La conversion correcte UTC → local
2. Le format de date pour `chk-roon.json` (YYYY-MM-DD HH:MM)
3. Le format de date avec secondes pour les logs IA (YYYY-MM-DD HH:MM:SS)
4. La préservation des informations de fuseau horaire
5. Un test de non-régression avec un timestamp spécifique

## Vérification recommandée

Pour vérifier que le fix fonctionne correctement dans votre environnement :

1. **Arrêter le tracker actuel** (si en cours d'exécution)

2. **Relancer le tracker Roon** :
   ```bash
   ./start-roon-tracker.sh
   ```

3. **Vérifier les nouvelles entrées** dans `data/history/chk-roon.json` :
   - Le champ `"date"` devrait maintenant afficher l'heure locale correcte
   - Comparer avec l'heure système actuelle

4. **Vérifier les logs IA** dans `output/ai-logs/ai-log-YYYY-MM-DD.txt` :
   - Les horodatages `=== YYYY-MM-DD HH:MM:SS ===` devraient être en heure locale
   - Le nom du fichier devrait correspondre à la date locale

5. **Vérifier l'interface GUI** :
   - Ouvrir `http://localhost:8501`
   - Les heures affichées dans le "Journal Roon" et "Journal IA" devraient être correctes

## Impact sur les données existantes

**Important** : Ce fix n'affecte que les **nouvelles entrées**. Les entrées existantes dans `chk-roon.json` et `chk-last-fm.json` conserveront leurs horodatages incorrects (en UTC).

Les timestamps Unix (champ `"timestamp"`) ne sont pas modifiés - ils restent corrects. Seul l'affichage de la date formatée (champ `"date"`) est corrigé pour les nouvelles entrées.

Si vous souhaitez corriger les anciennes entrées, il faudrait un script de migration pour recalculer les champs `"date"` à partir des timestamps Unix existants.

## Références

- Issue GitHub : #32
- Commit : a979162 et 7617d77
- Branche : copilot/fix-time-issue
- Date du fix : 27 janvier 2026
