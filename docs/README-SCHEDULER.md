# Task Scheduler - Guide d'Utilisation

## Vue d'ensemble

Le système de planification automatique (`scheduler.py`) permet d'exécuter périodiquement des tâches de traitement sans intervention manuelle. Le scheduler est intégré au tracker Roon et peut également être utilisé en ligne de commande.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    chk-roon.py (Main Loop)                  │
│  - Surveille lectures Roon/Last.fm                          │
│  - Vérifie tâches planifiées toutes les ~45 minutes         │
│  - Exécute tâches dues automatiquement                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TaskScheduler                            │
│  - Charge configuration depuis roon-config.json             │
│  - Persiste état dans scheduler-state.json                  │
│  - Calcule prochaines exécutions                            │
│  - Lance scripts Python via subprocess                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ analyze-     │    │ generate-    │    │ Read-        │
│ listening-   │    │ haiku.py     │    │ discogs-     │
│ patterns.py  │    │              │    │ ia.py        │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Tâches Gérées

### 1. `analyze_listening_patterns`
- **Description**: Analyse les patterns d'écoute et génère des rapports
- **Script**: `src/analysis/analyze-listening-patterns.py`
- **Fréquence par défaut**: Toutes les 6 heures
- **Sortie**: `output/reports/listening-patterns-YYYYMMDD-HHMMSS.txt`

### 2. `generate_haiku`
- **Description**: Génère des présentations poétiques pour albums
- **Script**: `src/analysis/generate-haiku.py`
- **Fréquence par défaut**: 1 fois par jour
- **Sortie**: `output/haikus/generate-haiku-YYYYMMDD-HHMMSS.txt`

### 3. `read_discogs`
- **Description**: Synchronise la collection Discogs
- **Script**: `src/collection/Read-discogs-ia.py`
- **Fréquence par défaut**: Tous les 7 jours
- **Sortie**: `data/collection/discogs-collection.json`

### 4. `generate_soundtrack`
- **Description**: Cross-référence films/soundtracks
- **Script**: `src/collection/generate-soundtrack.py`
- **Fréquence par défaut**: Tous les 7 jours
- **Sortie**: `data/collection/soundtrack.json`

## Configuration

### Fichier: `data/config/roon-config.json`

```json
{
  "scheduled_tasks": {
    "analyze_listening_patterns": {
      "enabled": true,
      "frequency_unit": "hour",
      "frequency_count": 6,
      "last_execution": null,
      "description": "Analyze listening patterns and generate insights"
    },
    "generate_haiku": {
      "enabled": true,
      "frequency_unit": "day",
      "frequency_count": 1,
      "last_execution": null,
      "description": "Generate haiku presentations for albums"
    }
  }
}
```

### Unités de Fréquence

- `hour`: Heures (1-8760)
- `day`: Jours (1-365)
- `month`: Mois (1-12, approximatif: 30 jours)
- `year`: Années (1+, approximatif: 365 jours)

## État des Tâches

### Fichier: `data/config/scheduler-state.json`

Ce fichier est créé automatiquement et contient:

```json
{
  "analyze_listening_patterns": {
    "last_execution": "2026-01-25T12:30:45.123456",
    "last_status": "success",
    "last_error": null,
    "execution_count": 42,
    "last_duration_seconds": 3.5
  }
}
```

## Utilisation

### Via le Tracker Roon (Automatique)

Le scheduler s'exécute automatiquement lorsque `chk-roon.py` tourne:

```bash
cd src/trackers
python3 chk-roon.py
```

Le tracker vérifie les tâches planifiées toutes les 60 itérations (~45 minutes).

### Via l'Interface GUI

Lancez l'interface Streamlit:

```bash
./scripts/start-streamlit.sh
# ou
streamlit run src/gui/musique-gui.py
```

Accédez à la page **⚙️ Configuration** pour:
- Activer/désactiver des tâches
- Modifier les fréquences d'exécution
- Voir le statut et l'historique
- Exécuter manuellement une tâche
- Télécharger les résultats (haïkus, rapports)

### Via la Ligne de Commande

```bash
cd src/utils

# Afficher le statut de toutes les tâches
python3 scheduler.py --status

# Vérifier et exécuter les tâches dues
python3 scheduler.py --check

# Exécuter une tâche manuellement
python3 scheduler.py --execute analyze_listening_patterns
```

## Workflow Typique

### 1. Première Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer .env avec les API keys
cp data/config/.env.example data/config/.env
# Éditer .env avec vos credentials

# 3. Lancer le tracker Roon
./start-roon-tracker.sh
```

Le scheduler se configure automatiquement avec les valeurs par défaut.

### 2. Personnalisation

Via la GUI (recommandé):
1. Ouvrir `streamlit run src/gui/musique-gui.py`
2. Aller sur **⚙️ Configuration**
3. Modifier les paramètres de chaque tâche
4. Cliquer sur **💾 Sauvegarder**

Via JSON (avancé):
1. Éditer `data/config/roon-config.json`
2. Modifier `scheduled_tasks`
3. Redémarrer `chk-roon.py` (le scheduler recharge la config)

### 3. Monitoring

#### Dans les Logs du Tracker

```
[SCHEDULER] Checking scheduled tasks...
[SCHEDULER] Task analyze_listening_patterns is due: Scheduled time reached
✅ analyze_listening_patterns: Task completed successfully in 3.5s
```

#### Dans la GUI

Page **⚙️ Configuration** affiche pour chaque tâche:
- ✅ Badge succès/erreur
- 📅 Dernière exécution
- ⏰ Prochaine exécution prévue
- 🔢 Nombre d'exécutions
- ⏱️ Durée dernière exécution
- ⚠️ Détails d'erreur (si échec)

## Résolution de Problèmes

### Tâche ne s'exécute pas

1. **Vérifier que la tâche est activée:**
   ```json
   "enabled": true
   ```

2. **Vérifier la dernière exécution:**
   - Si `last_execution` est récente, la tâche n'est pas encore due
   - Calculer: `next_execution = last_execution + frequency`

3. **Forcer l'exécution manuelle:**
   ```bash
   python3 src/utils/scheduler.py --execute task_name
   ```

### Erreurs d'Exécution

1. **Consulter `scheduler-state.json`:**
   ```json
   "last_error": "FileNotFoundError: catalogue.json not found"
   ```

2. **Vérifier les dépendances:**
   - `generate_soundtrack` nécessite le projet Cinéma
   - `generate_haiku` nécessite les credentials EurIA
   - `read_discogs` nécessite les credentials Discogs

3. **Consulter les logs du tracker:**
   ```
   [SCHEDULER] Error checking tasks: <details>
   ```

### État Corrompu

Si `scheduler-state.json` est corrompu:

```bash
# Supprimer le fichier (sera recréé automatiquement)
rm data/config/scheduler-state.json

# Relancer le tracker
./start-roon-tracker.sh
```

## Bonnes Pratiques

### 1. Fréquences Recommandées

- **Analyse patterns**: 3-6 heures (assez fréquent pour voir évolution)
- **Génération haïkus**: 1 jour (évite répétition)
- **Sync Discogs**: 7 jours (collection change rarement)
- **Sync soundtracks**: 7 jours (catalogue films stable)

### 2. Monitoring

- Consulter régulièrement la page **⚙️ Configuration**
- Vérifier que `last_status` = "success"
- Surveiller `execution_count` pour détecter blocages

### 3. Backup

Avant de modifier la configuration:

```bash
# Backup de la configuration
cp data/config/roon-config.json data/config/roon-config.json.backup

# Backup de l'état
cp data/config/scheduler-state.json data/config/scheduler-state.json.backup
```

### 4. Tests

Avant de déployer une nouvelle tâche:

```bash
# Tester l'exécution manuelle
python3 src/utils/scheduler.py --execute new_task

# Vérifier la sortie
ls -la output/
```

## Intégration avec l'Écosystème

Le scheduler s'intègre avec:

1. **Tracker Roon** (`chk-roon.py`):
   - Exécution automatique en arrière-plan
   - Aucune intervention manuelle requise

2. **Interface GUI** (`musique-gui.py`):
   - Configuration visuelle
   - Monitoring temps réel
   - Exécution manuelle

3. **Scripts d'Analyse**:
   - Génération automatique de rapports
   - Création de haïkus
   - Synchronisation Discogs

4. **Fichiers de Données**:
   - Lecture: `chk-roon.json`, `discogs-collection.json`
   - Écriture: `output/haikus/`, `output/reports/`

## Évolutions Futures

- [ ] Notifications par email/Slack en cas d'erreur
- [ ] Webhooks pour intégrations externes
- [ ] Dashboard de monitoring dédié
- [ ] Retry automatique en cas d'échec
- [ ] Parallélisation des tâches indépendantes
- [ ] Logs structurés (JSON) pour analyse

## Support

Pour toute question ou problème:
1. Consulter les logs du tracker Roon
2. Vérifier `scheduler-state.json` pour les erreurs
3. Tester l'exécution manuelle avec `--execute`
4. Consulter le code source dans `src/utils/scheduler.py`

## Auteur

Patrick Ostertag  
Version: 1.0.0  
Date: 25 janvier 2026
