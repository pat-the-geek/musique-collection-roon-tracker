# Changelog - Architecture v3.0.0

## 🎯 Version 3.0.0 - Réorganisation Complète (23 janvier 2026)

### ✨ Changements Majeurs

#### Nouvelle Structure de Répertoires

**Organisation modulaire par fonction :**
- `src/` - Code source organisé en 7 modules fonctionnels
- `data/` - Données séparées (config, collection, history, exports)
- `output/` - Fichiers générés temporaires (haikus, reports)
- `backups/` - Sauvegardes organisées par type
- `docs/` - Documentation centralisée
- `resources/` - Ressources statiques (prompts, images)
- `scripts/` - Scripts shell d'administration

#### Modules Sources (`src/`)

1. **`trackers/`** - Surveillance temps réel
   - chk-roon.py (v2.2.0)
   - chk-last-fm.py

2. **`collection/`** - Gestion collection musicale
   - Read-discogs-ia.py
   - generate-soundtrack.py

3. **`enrichment/`** - Enrichissement métadonnées
   - complete-resumes.py
   - complete-images-roon.py
   - normalize-supports.py

4. **`analysis/`** - Analyse et rapports
   - analyze-listening-patterns.py
   - generate-haiku.py (v2.1.0)

5. **`maintenance/`** - Nettoyage et corrections
   - remove-consecutive-duplicates.py
   - fix-radio-tracks.py
   - clean-radio-tracks.py

6. **`utils/`** - Utilitaires
   - List_all_music_on_drive.py
   - test-spotify-search-v2.2.py

7. **`gui/`** - Interface utilisateur
   - musique-gui.py (v2.1)

#### Organisation des Données (`data/`)

**Séparation stricte par type :**
- `config/` - Configuration et credentials (.env, roon-config.json)
- `collection/` - Collection musicale (discogs-collection.json, soundtrack.json)
- `history/` - Historique lectures (chk-roon.json, chk-last-fm.json, chk-roon.lock)
- `exports/` - Exports formatés (MD, PDF, CSV)

### 🔧 Modifications Techniques

#### Chemins Relatifs

**Avant (v2.x) :**
```python
load_dotenv()
'discogs-collection.json'
'chk-roon.json'
```

**Après (v3.0) :**
```python
load_dotenv('../../data/config/.env')
'../../data/collection/discogs-collection.json'
'../../data/history/chk-roon.json'
'../../output/haikus/generate-haiku-*.txt'
```

**100+ chemins mis à jour** dans tous les scripts Python.

#### Scripts Shell

**Mis à jour :**
- `scripts/setup-roon-tracker.sh` - Variables PROJECT_ROOT, TRACKER_SCRIPT
- `scripts/start-streamlit.sh` - Chemin `src/gui/musique-gui.py`

**Nouveau :**
- `start-roon-tracker.sh` - Wrapper de lancement depuis la racine

#### Backups

**Avant :**
```
Backups/JSON/chk-roon-*.json
backup-python/
```

**Après :**
```
backups/
├── json/
│   ├── chk-roon/chk-roon-YYYYMMDD-HHMMSS.json
│   ├── discogs-collection/discogs-collection-YYYYMMDD-HHMMSS.json
│   └── soundtrack/soundtrack-YYYYMMDD-HHMMSS.json
├── python/backup-YYYYMMDD-HHMMSS/
└── legacy/  # Ancienne structure préservée
```

### 📚 Documentation

**Nouveaux fichiers :**
- `README.md` - Documentation principale complète
- `MIGRATION-GUIDE.md` - Guide de migration détaillé
- `REORGANISATION-COMPLETE.txt` - Synthèse de la réorganisation
- `docs/README-ROON-CONFIG.md` - Documentation roon-config.json
- `.gitignore` - Patterns mis à jour pour nouvelle structure

**Mis à jour :**
- `docs/ARCHITECTURE-OVERVIEW.md` - Version 3.0.0 complète
  - Nouveaux diagrammes Mermaid avec chemins
  - Organisation modulaire détaillée
  - Workflows mis à jour
  - Structure des données
  - Chemins relatifs documentés

### 🚀 Nouveaux Workflows

**Lancement simplifié depuis la racine :**
```bash
# Tracker Roon
./start-roon-tracker.sh

# Interface Streamlit
./scripts/start-streamlit.sh
```

**Exécution depuis modules :**
```bash
# Génération haïkus
cd src/analysis && python3 generate-haiku.py

# Maintenance
cd src/enrichment && python3 complete-images-roon.py
```

### 🔐 Sécurité

**Améliorations :**
- `.env` protégé dans `data/config/`
- `.gitignore` mis à jour pour nouvelle structure
- Backups JSON organisés et horodatés
- Lock file isolé : `data/history/chk-roon.lock`

### 📊 Statistiques Migration

- ✅ 15 scripts Python déplacés
- ✅ 8 fichiers JSON réorganisés
- ✅ 6 fichiers de documentation déplacés
- ✅ 3 scripts shell mis à jour
- ✅ 100+ chemins de fichiers corrigés
- ✅ 7 modules fonctionnels créés
- ✅ 4 catégories de données structurées

### ⚠️ Breaking Changes

**Chemins modifiés :**
- ❌ Les anciens chemins relatifs à la racine ne fonctionnent plus
- ✅ Tous les scripts utilisent désormais des chemins relatifs depuis `src/`
- ✅ Wrapper `start-roon-tracker.sh` fourni pour compatibilité

**Migration :**
- Ancienne structure préservée dans `backups/legacy/`
- Rollback possible en copiant le contenu de `legacy/`
- Tous les scripts mis à jour automatiquement

### 🎯 Avantages

1. **Séparation claire** - Code, données, docs séparés
2. **Modularité** - Scripts organisés par fonction
3. **Maintenabilité** - Structure intuitive et scalable
4. **Sécurité** - Credentials protégés, backups organisés
5. **Documentation** - Centralisée et complète
6. **Git-friendly** - Structure adaptée au versioning
7. **Performance** - Chemins explicites, pas d'ambiguïté

### 📖 Documentation Associée

- [README.md](../README.md) - Vue d'ensemble complète
- [MIGRATION-GUIDE.md](../MIGRATION-GUIDE.md) - Détails migration
- [docs/ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md) - Architecture v3.0.0

### 🔄 Compatibilité

**Rétrocompatibilité :**
- ❌ Scripts v2.x ne fonctionnent pas sans modification
- ✅ Données JSON compatibles (format inchangé)
- ✅ Configuration `.env` compatible
- ✅ Environnement virtuel `.venv` compatible

**Migration requise :**
- Scripts personnels utilisant les anciens chemins
- Scripts d'automatisation externes
- Références hardcodées aux fichiers

### 🐛 Corrections

- ✅ Chemins absolus remplacés par relatifs
- ✅ Configuration `.env` centralisée
- ✅ Backups mieux organisés
- ✅ Lock file déplacé avec les données

### 🚧 Limitations Connues

Aucune. Tous les systèmes testés et opérationnels.

---

**Migration effectuée le:** 23 janvier 2026  
**Auteur:** Patrick Ostertag  
**Assistant:** GitHub Copilot (Claude Sonnet 4.5)

## Versions Précédentes

### Version 2.0 (21 janvier 2026)
- Interface Streamlit v2.1
- Tracker Roon v2.2.0
- Haiku generator v2.1.0
- Structure plate (scripts à la racine)

Voir [CHANGELOG-v2.2.0.md](CHANGELOG-v2.2.0.md) et [CHANGELOG-generate-haiku-v2.1.0.md](CHANGELOG-generate-haiku-v2.1.0.md) pour détails.
