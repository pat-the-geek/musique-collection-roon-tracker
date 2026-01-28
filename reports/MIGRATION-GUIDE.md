# 📋 Migration vers Nouvelle Structure - Guide de Référence

**Date**: 23 janvier 2026  
**Version**: 3.0.0

## ✅ Changements Effectués

### 1. Structure des Répertoires

```
Ancienne structure → Nouvelle structure

Scripts (racine) → src/{trackers,collection,enrichment,analysis,maintenance,utils,gui}/
JSON (racine) → data/{config,collection,history,exports}/
Outputs (racine) → output/{haikus,reports}/
Backups/ → backups/{json,python,legacy}/
README*.md → docs/
Prompt/ → resources/prompts/
Scripts shell (racine) → scripts/
```

### 2. Fichiers Déplacés

#### Scripts Python (vers src/)

| Ancien emplacement | Nouvel emplacement |
|--------------------|-------------------|
| `chk-roon.py` | `src/trackers/chk-roon.py` |
| `chk-last-fm.py` | `src/trackers/chk-last-fm.py` |
| `Read-discogs-ia.py` | `src/collection/Read-discogs-ia.py` |
| `generate-soundtrack.py` | `src/collection/generate-soundtrack.py` |
| `complete-resumes.py` | `src/enrichment/complete-resumes.py` |
| `complete-images-roon.py` | `src/enrichment/complete-images-roon.py` |
| `normalize-supports.py` | `src/enrichment/normalize-supports.py` |
| `analyze-listening-patterns.py` | `src/analysis/analyze-listening-patterns.py` |
| `generate-haiku.py` | `src/analysis/generate-haiku.py` |
| `remove-consecutive-duplicates.py` | `src/maintenance/remove-consecutive-duplicates.py` |
| `fix-radio-tracks.py` | `src/maintenance/fix-radio-tracks.py` |
| `clean-radio-tracks.py` | `src/maintenance/clean-radio-tracks.py` |
| `List_all_music_on_drive.py` | `src/utils/List_all_music_on_drive.py` |
| `test-spotify-search-v2.2.py` | `src/utils/test-spotify-search-v2.2.py` |
| `musique-gui.py` | `src/gui/musique-gui.py` |

#### Données JSON (vers data/)

| Ancien emplacement | Nouvel emplacement |
|--------------------|-------------------|
| `.env` | `data/config/.env` |
| `roon-config.json` | `data/config/roon-config.json` |
| `Liste_sites_musique-favoris.json` | `data/config/Liste_sites_musique-favoris.json` |
| `discogs-collection.json` | `data/collection/discogs-collection.json` |
| `soundtrack.json` | `data/collection/soundtrack.json` |
| `chk-roon.json` | `data/history/chk-roon.json` |
| `chk-last-fm.json` | `data/history/chk-last-fm.json` |
| `discogs-collection.md` | `data/exports/discogs-collection.md` |
| `Collection-discogs.csv` | `data/exports/Collection-discogs.csv` |
| `list_all_music.csv` | `data/exports/list_all_music.csv` |

#### Documentation (vers docs/)

| Ancien emplacement | Nouvel emplacement |
|--------------------|-------------------|
| `README-ROON-TRACKER.md` | `docs/README-ROON-TRACKER.md` |
| `README-MUSIQUE-GUI.md` | `docs/README-MUSIQUE-GUI.md` |
| `README-ROON-CONFIG.md` | `docs/README-ROON-CONFIG.md` |
| `README-GENERATE-HAIKU.md` | `docs/README-GENERATE-HAIKU.md` |
| `ARCHITECTURE-OVERVIEW.md` | `docs/ARCHITECTURE-OVERVIEW.md` |
| `CHANGELOG-*.md` | `docs/CHANGELOG-*.md` |

#### Scripts Shell (vers scripts/)

| Ancien emplacement | Nouvel emplacement |
|--------------------|-------------------|
| `setup-roon-tracker.sh` | `scripts/setup-roon-tracker.sh` |
| `start-streamlit.sh` | `scripts/start-streamlit.sh` |
| `update_python_certificates.sh` | `scripts/update_python_certificates.sh` |

### 3. Modifications des Chemins dans le Code

#### Tous les scripts Python ont été mis à jour:

**Configuration (.env):**
```python
# Avant
load_dotenv()

# Après
load_dotenv('../../data/config/.env')
```

**Fichiers JSON de données:**
```python
# Avant
'discogs-collection.json'
'chk-roon.json'
'roon-config.json'

# Après
'../../data/collection/discogs-collection.json'
'../../data/history/chk-roon.json'
'../../data/config/roon-config.json'
```

**Fichiers de sortie:**
```python
# Avant
f"generate-haiku-{timestamp}.txt"
f"listening-patterns-{timestamp}.txt"

# Après
f"../../output/haikus/generate-haiku-{timestamp}.txt"
f"../../output/reports/listening-patterns-{timestamp}.txt"
```

**Backups:**
```python
# Avant
'Backups/JSON'

# Après
'../../backups/json/chk-roon'
```

### 4. Scripts Shell Mis à Jour

**`scripts/setup-roon-tracker.sh`:**
- Variables mises à jour pour pointer vers `data/config/`
- Chemins d'exécution vers `src/trackers/chk-roon.py`

**`scripts/start-streamlit.sh`:**
- Chemin mis à jour: `streamlit run src/gui/musique-gui.py`

**Nouveau: `start-roon-tracker.sh`** (racine):
- Script de lancement simplifié depuis la racine
- Activation automatique venv
- Lance `src/trackers/chk-roon.py`

### 5. Fichiers Créés

- ✅ `README.md` (racine) - Documentation complète nouvelle structure
- ✅ `.gitignore` - Ignore patterns mis à jour
- ✅ `MIGRATION-GUIDE.md` - Ce fichier
- ✅ `start-roon-tracker.sh` - Wrapper de lancement

## 🔄 Migration Automatique

Toutes les modifications ont été effectuées automatiquement:
1. ✅ Création de la nouvelle structure de dossiers
2. ✅ Déplacement de tous les fichiers
3. ✅ Mise à jour de tous les chemins dans le code Python
4. ✅ Mise à jour des scripts shell
5. ✅ Création de la documentation

## 🧪 Vérification Post-Migration

### Tests à Effectuer

```bash
# 1. Vérifier la structure
ls -la src/ data/ output/ backups/ docs/ scripts/

# 2. Tester le tracker Roon
./start-roon-tracker.sh

# 3. Tester l'interface GUI
./scripts/start-streamlit.sh

# 4. Tester génération haïku
cd src/analysis && python3 generate-haiku.py

# 5. Tester analyse patterns
cd src/analysis && python3 analyze-listening-patterns.py
```

### Points de Vérification

- [ ] Le tracker Roon démarre et trouve la configuration
- [ ] Les fichiers JSON sont lus/écrits correctement
- [ ] L'interface Streamlit charge les données
- [ ] Les outputs sont générés dans `output/`
- [ ] Les backups sont créés dans `backups/json/`

## 🔙 Rollback (si nécessaire)

L'ancienne structure est préservée dans `backups/legacy/`:

```bash
# 1. Sauvegarder la nouvelle structure
mv src src.new
mv data data.new
mv output output.new

# 2. Restaurer l'ancienne structure
cp -R backups/legacy/* .

# 3. Nettoyer
rm -rf src.new data.new output.new
```

## 📝 Avantages de la Nouvelle Structure

1. **Séparation claire**: Code, données, documentation séparés
2. **Modularité**: Scripts organisés par fonction
3. **Chemins robustes**: Chemins relatifs explicites
4. **Facilité de navigation**: Arborescence intuitive
5. **Maintenance simplifiée**: Backups organisés
6. **Git-friendly**: Structure adaptée au versioning
7. **Scalabilité**: Facilite l'ajout de nouveaux modules

## 🚀 Prochaines Étapes

1. Tester tous les scripts dans la nouvelle structure
2. Mettre à jour `.github/copilot-instructions.md` avec les nouveaux chemins
3. Créer des alias/raccourcis pour les scripts fréquents
4. Documenter les patterns de développement pour nouveaux scripts
5. Configurer CI/CD si nécessaire

---

**Note**: Cette migration préserve l'intégralité des fonctionnalités existantes. Seuls les chemins ont été modifiés pour refléter la nouvelle organisation.
