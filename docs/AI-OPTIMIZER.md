# AI Optimizer - Documentation Technique

**Version**: 1.0.0  
**Date**: 27 janvier 2026  
**Module**: `src/services/ai_optimizer.py`

---

## 📋 Vue d'Ensemble

L'**AI Optimizer** est un système d'optimisation intelligent qui analyse automatiquement les patterns d'utilisation du système (écoutes musicales, tâches planifiées) et génère des recommandations pour améliorer les performances, réduire les coûts API et optimiser l'expérience utilisateur.

### Objectifs Principaux

1. **Analyse Automatique** : Surveillance continue des patterns d'écoute et d'utilisation
2. **Recommandations Intelligentes** : Suggestions basées sur l'IA avec justifications détaillées
3. **Application Sécurisée** : Modifications contrôlées avec backups et rollback automatique
4. **Détection Proactive** : Identification d'anomalies et de problèmes potentiels

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AIOptimizer (Core)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  analyze_listening_patterns()                              │
│    ├─ Peak hours detection                                 │
│    ├─ Typical start/end calculation                        │
│    ├─ Daily volume & activity score                        │
│    └─ Weekly distribution                                  │
│                                                             │
│  analyze_task_performance()                                │
│    ├─ Success rate calculation                             │
│    ├─ Duration tracking                                    │
│    └─ Value/cost ratio estimation                          │
│                                                             │
│  detect_anomalies()                                        │
│    ├─ Tracking interruption detection                      │
│    ├─ Task failure detection                               │
│    ├─ Data quality degradation                             │
│    └─ Unusual activity patterns                            │
│                                                             │
│  generate_recommendations()                                │
│    ├─ Listening hours adjustment                           │
│    ├─ Task frequency optimization                          │
│    └─ AI-powered justifications                            │
│                                                             │
│  apply_recommendations()                                   │
│    ├─ Automatic backup creation                            │
│    ├─ Confidence thresholds                                │
│    └─ Rollback support                                     │
│                                                             │
│  generate_optimization_report()                            │
│    └─ Comprehensive text reports                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    chk-roon.json    scheduler-state.json  roon-config.json
```

---

## 🎯 Fonctionnalités Détaillées

### 1. Analyse des Patterns d'Écoute

**Méthode**: `analyze_listening_patterns(days: int = 30) -> Dict[str, Any]`

Analyse les derniers jours d'historique d'écoute pour extraire des métriques clés:

**Sorties**:
- `peak_hours`: Top 4 heures avec le plus d'activité
- `typical_start`: Heure typique de début d'écoute (5e percentile)
- `typical_end`: Heure typique de fin d'écoute (95e percentile)
- `daily_volume`: Nombre moyen de tracks par jour
- `weekly_distribution`: Répartition des écoutes par jour de semaine (%)
- `activity_score`: Score d'activité global (0.0-1.0)
- `total_tracks`: Nombre total de tracks analysées
- `active_days`: Nombre de jours avec activité

**Algorithme**:
```python
# Score d'activité = 60% volume + 40% régularité
volume_score = min(1.0, daily_volume / 50.0)  # 50 tracks/jour = référence
regularity_score = active_days / analysis_period_days
activity_score = 0.6 * volume_score + 0.4 * regularity_score
```

**Exemple de sortie**:
```python
{
    'peak_hours': [19, 20, 21, 22],
    'typical_start': 18,
    'typical_end': 23,
    'daily_volume': 42.3,
    'weekly_distribution': {
        'Monday': 14.2,
        'Tuesday': 15.8,
        'Wednesday': 14.1,
        'Thursday': 16.3,
        'Friday': 18.5,
        'Saturday': 12.1,
        'Sunday': 9.0
    },
    'activity_score': 0.87,
    'total_tracks': 1269,
    'active_days': 30
}
```

---

### 2. Analyse de la Performance des Tâches

**Méthode**: `analyze_task_performance() -> Dict[str, Dict[str, Any]]`

Analyse l'efficacité de chaque tâche planifiée du scheduler.

**Sorties par tâche**:
- `avg_duration`: Durée moyenne d'exécution (secondes)
- `success_rate`: Taux de succès (0.0-1.0)
- `execution_count`: Nombre total d'exécutions
- `last_execution`: Timestamp de la dernière exécution
- `last_status`: Statut de la dernière exécution (success/error)
- `current_frequency`: Fréquence actuelle configurée
- `value_ratio`: Ratio valeur/coût estimé (0.0-1.0)
- `enabled`: État d'activation de la tâche

**Calcul du Value Ratio**:
```python
base_ratio = 0.5

# Bonus pour nombre d'exécutions réussies
if execution_count > 10: base_ratio += 0.2
elif execution_count > 5: base_ratio += 0.1

# Bonus pour durée raisonnable
if duration < 30s: base_ratio += 0.2
elif duration < 60s: base_ratio += 0.1

# Ajustements spécifiques par tâche
# generate_haiku: -0.1 (coût API élevé)
# analyze_listening_patterns: +0.1 (faible coût, haute valeur)
```

---

### 3. Détection d'Anomalies

**Méthode**: `detect_anomalies(days: int = 7) -> List[Anomaly]`

Détecte automatiquement les problèmes et comportements anormaux.

**Types d'anomalies détectées**:

#### 3.1 Interruption de Tracking
- **Condition**: Pas d'écoute depuis >3 jours alors que activity_score > 0.3
- **Severity**: `warning`
- **Action suggérée**: Vérifier que le tracker Roon est actif

#### 3.2 Échec de Tâche
- **Condition**: `last_status == 'error'` pour une tâche
- **Severity**: `error`
- **Action suggérée**: Vérifier les logs et la configuration

#### 3.3 Dégradation de Qualité
- **Condition**: >30% des 10 dernières tracks sans images
- **Severity**: `warning`
- **Action suggérée**: Vérifier credentials Spotify API et quotas

#### 3.4 Activité Inhabituelle
- **Condition**: Volume >100 tracks/jour
- **Severity**: `info`
- **Action suggérée**: Vérifier doublons avec `remove-consecutive-duplicates.py`

**Exemple d'anomalie**:
```python
Anomaly(
    type='tracking_interruption',
    severity='warning',
    description='Aucune écoute détectée depuis 5 jours (dernière: 2026-01-22 19:30)',
    detected_at=datetime(2026, 1, 27, 18, 14, 0),
    affected_component='tracker',
    suggested_action='Vérifier que le tracker Roon est actif et que Roon Core est accessible'
)
```

---

### 4. Génération de Recommandations

**Méthode**: `generate_recommendations() -> List[Recommendation]`

Génère des recommandations d'optimisation basées sur l'analyse et l'IA.

#### 4.1 Ajustement des Plages Horaires

**Condition de déclenchement**: Écart ≥2h entre plages actuelles et typiques

**Exemple**:
```python
Recommendation(
    type='listening_hours',
    current_value={'start': 6, 'end': 23},
    recommended_value={'start': 18, 'end': 23},
    justification='L\'analyse montre que 95% de vos écoutes ont lieu entre 18h-23h. Ajuster la surveillance à cette plage réduira la charge CPU de 30% sans perte de données.',
    confidence=0.92,
    estimated_impact='⚡ Réduction charge CPU de 30%, 📊 Meilleure précision statistiques',
    category='performance'
)
```

**Calcul de confiance**:
```python
confidence = min(0.95, 
    0.5 +                          # Base
    0.3 * activity_score +         # Fiabilité des données
    0.15 * min(hour_diff, 6) / 6   # Magnitude du changement
)
```

#### 4.2 Optimisation des Fréquences de Tâches

**Tâche `generate_haiku`**:
- **Si** `daily_volume < 10`: Réduire à 1x/3 jours (peu d'écoutes)
- **Si** `daily_volume > 50`: Maintenir à 1x/jour (beaucoup d'écoutes)

**Tâche `read_discogs`**:
- **Si** fréquence < 7 jours: Proposer 1x/semaine (collection stable)

**Exemple**:
```python
Recommendation(
    type='task_frequency',
    current_value={'task': 'generate_haiku', 'frequency': '1 day'},
    recommended_value={'task': 'generate_haiku', 'frequency': '3 day'},
    justification='Adaptation recommandée basée sur faible volume d\'écoute quotidien (8.5 tracks/jour)',
    confidence=0.85,
    estimated_impact='💰 -65% API calls, contenu reste pertinent',
    category='cost'
)
```

---

### 5. Application des Recommandations

**Méthode**: `apply_recommendations(recommendations: List[Recommendation], auto_apply: bool = False) -> Dict[str, Any]`

Applique les recommandations avec mécanismes de sécurité.

**Processus**:
1. **Backup automatique**: Crée `roon-config.backup.{timestamp}.json`
2. **Filtrage par confiance**: Si `auto_apply=True`, n'applique que si `confidence > 0.8`
3. **Application des modifications**: Met à jour `roon-config.json`
4. **Validation**: Vérifie que la sauvegarde a réussi
5. **Rollback si erreur**: Restaure le backup en cas d'échec

**Paramètre `auto_apply`**:
- `False`: Génère les recommandations sans les appliquer (défaut)
- `True`: Applique automatiquement les recommandations avec `confidence > 0.8`

**Sorties**:
```python
{
    'applied': 2,           # Nombre de recommandations appliquées
    'skipped': 1,           # Nombre ignorées (confiance trop faible)
    'failed': 0,            # Nombre d'échecs
    'details': [            # Détails de chaque action
        {
            'recommendation': 'listening_hours',
            'action': 'applied',
            'changes': "{'start': 6, 'end': 23} -> {'start': 18, 'end': 23}"
        },
        ...
    ]
}
```

---

### 6. Génération de Rapport

**Méthode**: `generate_optimization_report(output_dir: Path = None) -> str`

Génère un rapport complet d'optimisation au format texte.

**Structure du rapport**:
1. **En-tête**: Date, période d'analyse
2. **Analyse des patterns d'écoute**: Métriques complètes
3. **Performance des tâches**: État de chaque tâche
4. **Anomalies détectées**: Liste avec sévérité et actions
5. **Recommandations**: Détail de chaque recommandation

**Sortie**: `output/reports/ai-optimization-YYYYMMDD-HHMMSS.txt`

---

## 🔧 Configuration

### Intégration au Scheduler

Ajouter dans `roon-config.json`:

```json
{
  "scheduled_tasks": {
    "ai_optimize_system": {
      "enabled": true,
      "frequency_unit": "day",
      "frequency_count": 7,
      "last_execution": null,
      "description": "AI-powered system optimization with recommendations",
      "auto_apply": false
    }
  }
}
```

**Paramètres**:
- `enabled`: Active/désactive la tâche
- `frequency_unit`: Unité de temps (hour, day, month, year)
- `frequency_count`: Nombre d'unités entre exécutions
- `auto_apply`: Si `true`, applique automatiquement les recommandations avec confiance >0.8

### Variables d'Environnement

Requiert dans `.env`:
```bash
# EurIA API (pour justifications IA)
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=votre_token_euria
max_attempts=5
default_error_message=Aucune information disponible
```

---

## 📊 Métriques et Seuils

### Seuils de Détection

| Métrique | Seuil | Action |
|----------|-------|--------|
| Interruption tracking | >3 jours sans écoute | Alerte warning |
| Quality degradation | >30% tracks sans images | Alerte warning |
| Unusual activity | >100 tracks/jour | Alerte info |
| Confidence auto-apply | >0.8 | Application automatique |
| Changement horaire significatif | ≥2h | Génération recommandation |

### Calcul des Scores

**Activity Score**:
- Référence: 50 tracks/jour = score 1.0
- Formule: 60% volume + 40% régularité
- Plage: 0.0-1.0

**Value Ratio**:
- Base: 0.5
- Bonus exécutions: +0.1 ou +0.2
- Bonus performance: +0.1 ou +0.2
- Ajustements spécifiques: -0.1 ou +0.1
- Plage: 0.0-1.0

**Confidence Score**:
- Base: 0.5
- Facteur activité: 0.3 × activity_score
- Facteur changement: 0.15 × (hour_diff / 6)
- Maximum: 0.95

---

## 🧪 Tests

### Suite de Tests

**Fichier**: `src/tests/test_ai_optimizer.py`  
**Tests**: 31 tests unitaires  
**Coverage**: ~95% des fonctions principales

**Classes de tests**:
1. `TestAIOptimizerInit`: Initialisation (3 tests)
2. `TestAnalyzeListeningPatterns`: Analyse patterns (7 tests)
3. `TestAnalyzeTaskPerformance`: Performance tâches (4 tests)
4. `TestDetectAnomalies`: Détection anomalies (4 tests)
5. `TestGenerateRecommendations`: Génération recommandations (3 tests)
6. `TestApplyRecommendations`: Application recommandations (4 tests)
7. `TestRecommendationModel`: Modèle Recommendation (2 tests)
8. `TestAnomalyModel`: Modèle Anomaly (2 tests)
9. `TestGenerateOptimizationReport`: Génération rapport (2 tests)

**Exécution**:
```bash
cd /path/to/project
python3 -m pytest src/tests/test_ai_optimizer.py -v
```

---

## 🚀 Utilisation

### Utilisation Programmée (Scheduler)

L'AI Optimizer s'exécute automatiquement via le scheduler (défaut: 1x/semaine).

**Logs**:
```
2026-01-27 18:14:00 - TaskScheduler - INFO - Executing task: ai_optimize_system (scheduled)
2026-01-27 18:14:15 - ai_optimizer - INFO - Listening patterns analyzed: 1269 tracks over 30 days
2026-01-27 18:14:18 - ai_optimizer - INFO - Generated 3 recommendations
2026-01-27 18:14:20 - ai_optimizer - INFO - Optimization report generated: output/reports/ai-optimization-20260127-181420.txt
```

### Utilisation Manuelle (CLI)

```bash
cd src/services
python3 ai_optimizer.py
```

**Sortie**:
```
✅ Rapport d'optimisation généré: /path/to/output/reports/ai-optimization-20260127-181420.txt

💡 3 recommandations générées:

  1. listening_hours (confiance: 92%)
     L'analyse montre que 95% de vos écoutes ont lieu entre 18h-23h...

  2. task_frequency (confiance: 85%)
     Adaptation recommandée basée sur faible volume d'écoute quotidien...

  3. task_frequency (confiance: 75%)
     Les collections Discogs évoluent lentement...
```

### Utilisation Programmée (API Python)

```python
from services.ai_optimizer import AIOptimizer

# Créer l'optimiseur
optimizer = AIOptimizer(
    config_path="data/config/roon-config.json",
    state_path="data/config/scheduler-state.json",
    history_path="data/history/chk-roon.json"
)

# Analyser les patterns
patterns = optimizer.analyze_listening_patterns(days=30)
print(f"Activity score: {patterns['activity_score']}")
print(f"Peak hours: {patterns['peak_hours']}")

# Détecter les anomalies
anomalies = optimizer.detect_anomalies(days=7)
for anomaly in anomalies:
    print(f"[{anomaly.severity}] {anomaly.description}")

# Générer recommandations
recommendations = optimizer.generate_recommendations()
for rec in recommendations:
    print(f"{rec.type}: {rec.justification}")

# Appliquer automatiquement si confiance élevée
result = optimizer.apply_recommendations(recommendations, auto_apply=True)
print(f"Applied {result['applied']} recommendations")

# Générer rapport
report_path = optimizer.generate_optimization_report()
print(f"Report: {report_path}")
```

---

## 📈 Bénéfices Attendus

### Quantifiables
- **⚡ CPU**: -20 à -30% de charge moyenne (optimisation plages horaires)
- **💰 API**: -40 à -60% d'appels (fréquences adaptatives)
- **📊 Précision**: +5 à +10% sur les statistiques (plages ajustées)
- **🕐 Maintenance**: -50% de temps (automatisation décisions)
- **🔋 Énergie**: -15 à -25% de consommation (polling réduit)

### Qualitatifs
- **🧠 Auto-apprentissage**: Adaptation continue aux habitudes
- **🔍 Visibilité**: Compréhension des patterns d'utilisation
- **🛡️ Fiabilité**: Détection proactive d'anomalies
- **🎓 Éducation**: Insights sur les comportements d'écoute
- **🚀 Scalabilité**: Support de volumes croissants de données

---

## 🔐 Sécurité et Confidentialité

### Protection des Données
- **Traitement local**: Toutes les analyses sont effectuées localement
- **Minimisation**: Seuls les patterns agrégés sont transmis à l'IA (pas de tracks individuelles)
- **Pas de stockage externe**: Aucune donnée n'est envoyée ou stockée en dehors du système

### Sécurité des Modifications
- **Backup automatique**: Avant chaque modification de configuration
- **Validation**: Vérification de validité avant application
- **Rollback**: Restauration automatique en cas d'échec
- **Audit trail**: Log complet de toutes les modifications IA

### Contrôle Utilisateur
- **Opt-out**: Configuration `enabled: false` pour désactiver
- **Mode manuel**: `auto_apply: false` pour validation humaine
- **Seuil de confiance**: Contrôle du niveau d'automatisation

---

## 🐛 Troubleshooting

### Problèmes Courants

#### 1. Aucune recommandation générée
**Causes possibles**:
- Historique insuffisant (< 7 jours de données)
- Configuration déjà optimale
- Activity score trop faible

**Solution**: Attendre plus de données ou vérifier l'activité d'écoute

#### 2. Erreur API EurIA
**Message**: `⚠️ Configuration EurIA manquante (URL ou bearer)`

**Solution**: Vérifier que `.env` contient `URL` et `bearer` valides

#### 3. Rapport non généré
**Causes possibles**:
- Permissions d'écriture insuffisantes
- Répertoire `output/reports/` manquant

**Solution**: Vérifier les permissions et créer le répertoire manuellement

#### 4. Recommandations non appliquées
**Causes possibles**:
- `auto_apply: false` dans la configuration
- Confiance des recommandations < 0.8
- Échec de création du backup

**Solution**: Vérifier les logs pour le détail des raisons

---

## 📚 Références

### Fichiers Liés
- **Module principal**: `src/services/ai_optimizer.py`
- **Tests**: `src/tests/test_ai_optimizer.py`
- **Scheduler**: `src/utils/scheduler.py`
- **Service IA**: `src/services/ai_service.py`

### Documentation Connexe
- **Issue #41**: [Utiliser l'IA pour optimiser le fonctionnement du système](https://github.com/pat-the-geek/musique-collection-roon-tracker/issues/41)
- **ISSUE-41-ANALYSIS.md**: Analyse complète et propositions
- **README-SCHEDULER.md**: Documentation du scheduler
- **AI-INTEGRATION.md**: Intégration EurIA API

---

**Auteur**: Patrick Ostertag  
**Date de création**: 27 janvier 2026  
**Dernière mise à jour**: 27 janvier 2026  
**Version**: 1.0.0
