#!/usr/bin/env python3
"""Module d'optimisation IA pour adaptation automatique de la configuration.

Ce module analyse les patterns d'utilisation du système (écoutes, tâches planifiées)
et génère des recommandations pour optimiser automatiquement la configuration.

Fonctionnalités principales:
    - Analyse des patterns d'écoute temporels
    - Analyse de la performance des tâches planifiées
    - Détection d'anomalies système
    - Génération de recommandations basées sur l'IA
    - Application automatique ou manuelle des recommandations

Architecture:
    Le système s'appuie sur l'infrastructure existante (ai_service, scheduler)
    et analyse les fichiers de données (chk-roon.json, scheduler-state.json,
    roon-config.json) pour identifier les opportunités d'optimisation.

Classes principales:
    - AIOptimizer: Orchestrateur principal de l'optimisation
    - Recommendation: Modèle de données pour les recommandations
    - Anomaly: Modèle de données pour les anomalies détectées

Usage:
    from services.ai_optimizer import AIOptimizer
    
    optimizer = AIOptimizer(
        config_path="data/config/roon-config.json",
        state_path="data/config/scheduler-state.json",
        history_path="data/history/chk-roon.json"
    )
    
    # Analyser et générer recommandations
    recommendations = optimizer.generate_recommendations()
    
    # Appliquer automatiquement les recommandations avec haute confiance
    optimizer.apply_recommendations(recommendations, auto_apply=True)

Auteur: Patrick Ostertag
**Version**: 1.0.1  
**Date**: 27 janvier 2026  
**Module**: `src/services/ai_optimizer.py`

**Changelog v1.0.1**:
- Fix #47: Correction du calcul de daily_volume pour utiliser la période d'analyse
  complète au lieu du nombre de jours actifs uniquement
- Ajout du champ active_days aux retours anticipés pour la cohérence
"""

import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

# Import du service IA existant
from services.ai_service import ask_for_ia, ensure_env_loaded

# Confidence score calculation constants
CONFIDENCE_BASE = 0.5
CONFIDENCE_ACTIVITY_FACTOR = 0.3
CONFIDENCE_CHANGE_FACTOR = 0.15
CONFIDENCE_MAX = 0.95
CONFIDENCE_HOUR_REFERENCE = 6


# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Représente une recommandation d'optimisation.
    
    Attributes:
        type: Type de recommandation (listening_hours, task_frequency, resource_allocation)
        current_value: Valeur actuelle du paramètre
        recommended_value: Valeur recommandée
        justification: Explication IA de la recommandation
        confidence: Score de confiance (0.0-1.0)
        estimated_impact: Description de l'impact attendu
        category: Catégorie de la recommandation (performance, cost, quality)
    """
    type: str
    current_value: Any
    recommended_value: Any
    justification: str
    confidence: float
    estimated_impact: str
    category: str = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la recommandation en dictionnaire."""
        return asdict(self)


@dataclass
class Anomaly:
    """Représente une anomalie détectée dans le système.
    
    Attributes:
        type: Type d'anomalie (tracking_interruption, task_failure, data_quality)
        severity: Niveau de sévérité (info, warning, error, critical)
        description: Description de l'anomalie
        detected_at: Timestamp de détection
        affected_component: Composant affecté (tracker, scheduler, api)
        suggested_action: Action suggérée pour résoudre
    """
    type: str
    severity: str
    description: str
    detected_at: datetime
    affected_component: str
    suggested_action: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'anomalie en dictionnaire."""
        data = asdict(self)
        data['detected_at'] = self.detected_at.isoformat()
        return data


class AIOptimizer:
    """Système d'optimisation IA pour adaptation automatique de la configuration.
    
    Cette classe orchestre l'analyse des données système et génère des recommandations
    intelligentes pour optimiser les performances, réduire les coûts API et améliorer
    l'expérience utilisateur.
    """
    
    def __init__(self, config_path: str, state_path: str, history_path: str):
        """Initialise l'optimiseur IA.
        
        Args:
            config_path: Chemin vers roon-config.json
            state_path: Chemin vers scheduler-state.json
            history_path: Chemin vers chk-roon.json
        """
        self.config_path = Path(config_path)
        self.state_path = Path(state_path)
        self.history_path = Path(history_path)
        
        # Charger les données
        self.config = self._load_json(self.config_path)
        self.state = self._load_json(self.state_path) if self.state_path.exists() else {}
        self.history = self._load_json(self.history_path) if self.history_path.exists() else []
        
        # S'assurer que les variables d'environnement sont chargées
        ensure_env_loaded()
        
        logger.info(f"AIOptimizer initialized with {len(self.history)} history entries")
    
    def _load_json(self, path: Path) -> Any:
        """Charge un fichier JSON.
        
        Args:
            path: Chemin du fichier JSON
            
        Returns:
            Contenu du fichier JSON ou {} si erreur
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {path}")
            return {} if path.suffix == '.json' else []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {path}: {e}")
            return {} if path.suffix == '.json' else []
    
    def _save_json(self, path: Path, data: Any) -> bool:
        """Sauvegarde des données en JSON.
        
        Args:
            path: Chemin du fichier JSON
            data: Données à sauvegarder
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Créer le répertoire parent si nécessaire
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON to {path}: {e}")
            return False
    
    def analyze_listening_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyse les patterns d'écoute dans l'historique.
        
        Analyse les derniers jours d'historique pour détecter:
        - Les heures de forte activité (peak hours)
        - Les heures typiques de début et fin d'écoute
        - Le volume quotidien moyen
        - La distribution par jour de semaine
        - Le score d'activité global
        
        Args:
            days: Nombre de jours à analyser (défaut: 30)
            
        Returns:
            Dictionnaire avec les métriques de patterns:
            {
                'peak_hours': Liste des heures de forte activité,
                'typical_start': Heure typique de début (entier 0-23),
                'typical_end': Heure typique de fin (entier 0-23),
                'daily_volume': Moyenne de tracks par jour,
                'weekly_distribution': Distribution par jour de semaine,
                'activity_score': Score d'activité (0-1),
                'analysis_period_days': Nombre de jours analysés,
                'total_tracks': Nombre total de tracks dans la période
            }
        """
        if not self.history:
            logger.warning("No history data available for pattern analysis")
            return {
                'peak_hours': [],
                'typical_start': 6,
                'typical_end': 23,
                'daily_volume': 0,
                'weekly_distribution': {},
                'activity_score': 0.0,
                'analysis_period_days': days,
                'total_tracks': 0,
                'active_days': 0
            }
        
        # Filtrer les entrées des X derniers jours
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tracks = []
        
        for track in self.history:
            try:
                # Support pour timestamp ou date string
                if 'timestamp' in track:
                    track_date = datetime.fromtimestamp(track['timestamp'])
                elif 'date' in track:
                    # Format: "2026-01-17 18:21"
                    track_date = datetime.strptime(track['date'], '%Y-%m-%d %H:%M')
                else:
                    continue
                    
                if track_date >= cutoff_date:
                    recent_tracks.append({
                        'timestamp': track.get('timestamp'),
                        'datetime': track_date,
                        'hour': track_date.hour,
                        'weekday': track_date.weekday(),  # 0=Monday, 6=Sunday
                        'artist': track.get('artist', 'Unknown'),
                        'title': track.get('title', 'Unknown')
                    })
            except (ValueError, KeyError) as e:
                logger.debug(f"Skipping track due to date parsing error: {e}")
                continue
        
        if not recent_tracks:
            logger.warning("No recent tracks found in the specified period")
            return {
                'peak_hours': [],
                'typical_start': 6,
                'typical_end': 23,
                'daily_volume': 0,
                'weekly_distribution': {},
                'activity_score': 0.0,
                'analysis_period_days': days,
                'total_tracks': 0,
                'active_days': 0
            }
        
        # Analyser les heures d'activité
        hour_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        daily_tracks = defaultdict(int)
        
        for track in recent_tracks:
            hour_counts[track['hour']] += 1
            weekday_counts[track['weekday']] += 1
            # Grouper par date uniquement (YYYY-MM-DD)
            day_key = track['datetime'].strftime('%Y-%m-%d')
            daily_tracks[day_key] += 1
        
        # Calculer les peak hours (top 4 heures avec le plus d'activité)
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, count in sorted_hours[:4]]
        
        # Calculer typical start/end (percentiles)
        active_hours = []
        for track in recent_tracks:
            active_hours.append(track['hour'])
        
        if active_hours:
            active_hours.sort()
            # 5e percentile pour start, 95e percentile pour end
            start_idx = max(0, int(len(active_hours) * 0.05))
            end_idx = min(len(active_hours) - 1, int(len(active_hours) * 0.95))
            typical_start = active_hours[start_idx]
            typical_end = active_hours[end_idx]
        else:
            typical_start = 6
            typical_end = 23
        
        # Calculer volume quotidien moyen
        actual_days = len(daily_tracks)
        total_tracks = len(recent_tracks)
        daily_volume = total_tracks / days if days > 0 else 0
        
        # Distribution par jour de semaine (normaliser en pourcentages)
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_distribution = {}
        for weekday in range(7):
            count = weekday_counts.get(weekday, 0)
            percentage = (count / total_tracks * 100) if total_tracks > 0 else 0
            weekly_distribution[weekday_names[weekday]] = round(percentage, 1)
        
        # Score d'activité basé sur volume et régularité
        # Volume score: tracks/jour par rapport à une référence (50 tracks/jour = 1.0)
        volume_score = min(1.0, daily_volume / 50.0)
        
        # Régularité score: nombre de jours avec activité / jours totaux
        regularity_score = actual_days / days
        
        # Score global (moyenne pondérée: 60% volume, 40% régularité)
        activity_score = 0.6 * volume_score + 0.4 * regularity_score
        
        result = {
            'peak_hours': peak_hours,
            'typical_start': typical_start,
            'typical_end': typical_end,
            'daily_volume': round(daily_volume, 1),
            'weekly_distribution': weekly_distribution,
            'activity_score': round(activity_score, 2),
            'analysis_period_days': days,
            'total_tracks': total_tracks,
            'active_days': actual_days
        }
        
        logger.info(f"Listening patterns analyzed: {total_tracks} tracks over {actual_days} days")
        return result
    
    def analyze_task_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyse l'efficacité des tâches planifiées.
        
        Analyse l'état du scheduler pour chaque tâche configurée et calcule:
        - Durée moyenne d'exécution
        - Taux de succès
        - Ratio valeur/coût estimé
        - Fréquence recommandée
        
        Returns:
            Dictionnaire avec les métriques par tâche:
            {
                'task_name': {
                    'avg_duration': Durée moyenne en secondes,
                    'success_rate': Taux de succès (0.0-1.0),
                    'execution_count': Nombre d'exécutions,
                    'last_execution': Timestamp dernière exécution,
                    'last_status': Statut de la dernière exécution,
                    'current_frequency': Fréquence actuelle,
                    'value_ratio': Ratio valeur/coût estimé (0.0-1.0)
                }
            }
        """
        task_analysis = {}
        
        # Analyser chaque tâche configurée
        scheduled_tasks = self.config.get('scheduled_tasks', {})
        
        for task_name, task_config in scheduled_tasks.items():
            # Récupérer l'état de la tâche
            task_state = self.state.get(task_name, {})
            
            # Extraire les métriques de base
            execution_count = task_state.get('execution_count', 0)
            last_duration = task_state.get('last_duration_seconds', 0)
            last_status = task_state.get('last_status', 'unknown')
            last_execution = task_state.get('last_execution')
            
            # Calculer le taux de succès (simplifié, basé sur le dernier statut)
            # Dans une version avancée, on pourrait tracker l'historique des exécutions
            success_rate = 1.0 if last_status == 'success' else 0.5
            
            # Calculer le ratio valeur/coût (heuristique basé sur le type de tâche)
            value_ratio = self._estimate_value_ratio(
                task_name, 
                execution_count, 
                last_duration,
                task_config
            )
            
            # Fréquence actuelle
            freq_unit = task_config.get('frequency_unit', 'day')
            freq_count = task_config.get('frequency_count', 1)
            current_frequency = f"{freq_count} {freq_unit}(s)"
            
            task_analysis[task_name] = {
                'avg_duration': last_duration,  # Simplifié: utiliser la dernière durée
                'success_rate': success_rate,
                'execution_count': execution_count,
                'last_execution': last_execution,
                'last_status': last_status,
                'current_frequency': current_frequency,
                'value_ratio': value_ratio,
                'enabled': task_config.get('enabled', True)
            }
        
        logger.info(f"Task performance analyzed for {len(task_analysis)} tasks")
        return task_analysis
    
    def _estimate_value_ratio(self, task_name: str, exec_count: int, 
                             duration: float, config: Dict[str, Any]) -> float:
        """Estime le ratio valeur/coût pour une tâche.
        
        Args:
            task_name: Nom de la tâche
            exec_count: Nombre d'exécutions
            duration: Durée d'exécution
            config: Configuration de la tâche
            
        Returns:
            Ratio valeur/coût (0.0-1.0)
        """
        # Heuristiques par type de tâche
        # Plus d'exécutions réussies = ratio plus élevé
        # Durée courte = ratio plus élevé
        
        base_ratio = 0.5
        
        # Bonus pour nombre d'exécutions (indique utilité)
        if exec_count > 10:
            base_ratio += 0.2
        elif exec_count > 5:
            base_ratio += 0.1
        
        # Bonus pour durée raisonnable (< 60s = efficace)
        if duration < 30:
            base_ratio += 0.2
        elif duration < 60:
            base_ratio += 0.1
        
        # Ajustements spécifiques par tâche
        if task_name == 'generate_haiku':
            # Haiku a haute valeur créative mais coût API élevé
            base_ratio -= 0.1
        elif task_name == 'analyze_listening_patterns':
            # Analyse a haute valeur et faible coût
            base_ratio += 0.1
        
        return min(1.0, max(0.0, base_ratio))
    
    def detect_anomalies(self, days: int = 7) -> List[Anomaly]:
        """Détecte les anomalies dans le système.
        
        Vérifie plusieurs aspects du système:
        - Interruptions de tracking inattendues
        - Échecs répétés de tâches scheduler
        - Dégradation de qualité des métadonnées
        - Pics d'activité inhabituels
        
        Args:
            days: Nombre de jours à analyser pour la détection (défaut: 7)
            
        Returns:
            Liste d'objets Anomaly détectés
        """
        anomalies = []
        now = datetime.now()
        
        # 1. Détecter interruptions de tracking
        if self.history:
            # Vérifier la dernière écoute
            try:
                last_track = self.history[-1]
                if 'timestamp' in last_track:
                    last_listen = datetime.fromtimestamp(last_track['timestamp'])
                elif 'date' in last_track:
                    last_listen = datetime.strptime(last_track['date'], '%Y-%m-%d %H:%M')
                else:
                    last_listen = None
                
                if last_listen:
                    days_since_last = (now - last_listen).days
                    
                    # Analyser patterns pour détecter si c'est anormal
                    patterns = self.analyze_listening_patterns(days=30)
                    
                    # Si l'utilisateur écoute normalement mais pas depuis 3+ jours = anomalie
                    if patterns['activity_score'] > 0.3 and days_since_last > 3:
                        anomalies.append(Anomaly(
                            type='tracking_interruption',
                            severity='warning',
                            description=f"Aucune écoute détectée depuis {days_since_last} jours (dernière: {last_listen.strftime('%Y-%m-%d %H:%M')})",
                            detected_at=now,
                            affected_component='tracker',
                            suggested_action="Vérifier que le tracker Roon est actif et que Roon Core est accessible"
                        ))
            except (ValueError, KeyError, IndexError) as e:
                logger.debug(f"Could not check tracking interruption: {e}")
        
        # 2. Détecter échecs répétés de tâches
        for task_name, task_state in self.state.items():
            last_status = task_state.get('last_status')
            last_error = task_state.get('last_error')
            
            if last_status == 'error' and last_error:
                anomalies.append(Anomaly(
                    type='task_failure',
                    severity='error',
                    description=f"Tâche '{task_name}' en échec: {last_error}",
                    detected_at=now,
                    affected_component='scheduler',
                    suggested_action=f"Vérifier les logs et la configuration de la tâche '{task_name}'"
                ))
        
        # 3. Détecter qualité dégradée des métadonnées
        if len(self.history) > 10:
            # Vérifier les 10 dernières entrées pour images manquantes
            recent_tracks = self.history[-10:]
            missing_images = 0
            
            for track in recent_tracks:
                if not track.get('artist_spotify_image') and not track.get('album_spotify_image'):
                    missing_images += 1
            
            missing_ratio = missing_images / len(recent_tracks)
            if missing_ratio > 0.3:  # Plus de 30% sans images
                anomalies.append(Anomaly(
                    type='data_quality',
                    severity='warning',
                    description=f"Qualité des métadonnées dégradée: {int(missing_ratio*100)}% des tracks récentes sans images",
                    detected_at=now,
                    affected_component='api',
                    suggested_action="Vérifier les credentials Spotify API et les quotas"
                ))
        
        # 4. Détecter pics d'activité inhabituels
        patterns = self.analyze_listening_patterns(days=7)
        if patterns['daily_volume'] > 100:  # Plus de 100 tracks/jour = potentiel problème
            anomalies.append(Anomaly(
                type='unusual_activity',
                severity='info',
                description=f"Pic d'activité détecté: {patterns['daily_volume']} tracks/jour (peut indiquer des doublons)",
                detected_at=now,
                affected_component='tracker',
                suggested_action="Vérifier les doublons dans l'historique avec remove-consecutive-duplicates.py"
            ))
        
        logger.info(f"Anomaly detection completed: {len(anomalies)} anomalies found")
        return anomalies
    
    def generate_recommendations(self) -> List[Recommendation]:
        """Génère des recommandations d'optimisation basées sur l'analyse.
        
        Utilise l'IA pour analyser les patterns et générer des recommandations
        pour:
        - Ajustement des plages horaires d'écoute
        - Optimisation des fréquences de tâches
        - Allocation des ressources
        
        Returns:
            Liste d'objets Recommendation avec justifications IA
        """
        recommendations = []
        
        # Analyser les patterns et performances
        patterns = self.analyze_listening_patterns(days=30)
        task_perf = self.analyze_task_performance()
        
        # 1. Recommandation: Ajustement des plages horaires
        current_start = self.config.get('listen_start_hour', 6)
        current_end = self.config.get('listen_end_hour', 23)
        
        # Calculer les plages recommandées avec marges
        recommended_start = max(0, patterns['typical_start'] - 1)
        recommended_end = min(23, patterns['typical_end'] + 1)
        
        # Générer recommandation seulement si changement significatif (>= 2h)
        hour_diff_start = abs(current_start - recommended_start)
        hour_diff_end = abs(current_end - recommended_end)
        
        if hour_diff_start >= 2 or hour_diff_end >= 2:
            # Utiliser l'IA pour justifier la recommandation
            ai_prompt = f"""Analysez ces patterns d'écoute musicale et justifiez en 2 phrases pourquoi ajuster les plages horaires de surveillance:

Données:
- Plage actuelle: {current_start}h-{current_end}h
- Plage recommandée: {recommended_start}h-{recommended_end}h
- Heures de pic d'activité: {patterns['peak_hours']}
- Volume quotidien: {patterns['daily_volume']} tracks/jour
- Score d'activité: {patterns['activity_score']}

Répondez en français, en 2 phrases maximum, en expliquant l'impact sur la performance."""
            
            justification = ask_for_ia(ai_prompt, max_attempts=3, timeout=30)
            
            # Calculer confiance basée sur l'écart et le score d'activité
            confidence = min(
                CONFIDENCE_MAX,
                CONFIDENCE_BASE + 
                CONFIDENCE_ACTIVITY_FACTOR * patterns['activity_score'] + 
                CONFIDENCE_CHANGE_FACTOR * min(hour_diff_start, hour_diff_end) / CONFIDENCE_HOUR_REFERENCE
            )
            
            recommendations.append(Recommendation(
                type='listening_hours',
                current_value={'start': current_start, 'end': current_end},
                recommended_value={'start': recommended_start, 'end': recommended_end},
                justification=justification,
                confidence=round(confidence, 2),
                estimated_impact=f"⚡ Réduction charge CPU de {int(((current_end - current_start) - (recommended_end - recommended_start)) / (current_end - current_start) * 100)}%, 📊 Meilleure précision statistiques",
                category='performance'
            ))
        
        # 2. Recommandation: Fréquences des tâches
        for task_name, perf in task_perf.items():
            if not perf['enabled']:
                continue
            
            # Extraire fréquence actuelle
            task_config = self.config['scheduled_tasks'][task_name]
            current_freq = f"{task_config['frequency_count']} {task_config['frequency_unit']}"
            
            # Logique d'optimisation par tâche
            if task_name == 'generate_haiku':
                # Ajuster selon volume d'écoute
                if patterns['daily_volume'] < 10:
                    # Peu d'écoutes -> réduire fréquence
                    recommended_freq = {'unit': 'day', 'count': 3}
                    reason = "faible volume d'écoute quotidien"
                    impact = "💰 -65% API calls, contenu reste pertinent"
                    confidence = 0.85
                elif patterns['daily_volume'] > 50:
                    # Beaucoup d'écoutes -> maintenir ou augmenter
                    recommended_freq = {'unit': 'day', 'count': 1}
                    reason = "volume d'écoute élevé"
                    impact = "🎯 Contenu frais quotidien"
                    confidence = 0.80
                else:
                    continue  # Pas de recommandation
                
                # Comparer avec fréquence actuelle
                if task_config['frequency_unit'] != recommended_freq['unit'] or \
                   task_config['frequency_count'] != recommended_freq['count']:
                    
                    recommendations.append(Recommendation(
                        type='task_frequency',
                        current_value={'task': task_name, 'frequency': current_freq},
                        recommended_value={'task': task_name, 'frequency': f"{recommended_freq['count']} {recommended_freq['unit']}"},
                        justification=f"Adaptation recommandée basée sur {reason} ({patterns['daily_volume']} tracks/jour)",
                        confidence=confidence,
                        estimated_impact=impact,
                        category='cost'
                    ))
            
            elif task_name == 'read_discogs':
                # Vérifier si la tâche est trop fréquente pour une collection stable
                if task_config['frequency_count'] < 7 and task_config['frequency_unit'] == 'day':
                    # Collection stable -> réduire fréquence
                    recommendations.append(Recommendation(
                        type='task_frequency',
                        current_value={'task': task_name, 'frequency': current_freq},
                        recommended_value={'task': task_name, 'frequency': '7 day'},
                        justification="Les collections Discogs évoluent lentement, une synchronisation hebdomadaire est suffisante",
                        confidence=0.75,
                        estimated_impact="💰 -85% API calls Discogs",
                        category='cost'
                    ))
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def apply_recommendations(self, recommendations: List[Recommendation], 
                            auto_apply: bool = False) -> Dict[str, Any]:
        """Applique ou présente les recommandations à l'utilisateur.
        
        Args:
            recommendations: Liste des recommandations à appliquer
            auto_apply: Si True, applique automatiquement les recommandations
                       avec confiance > 0.8
                       
        Returns:
            Dictionnaire avec le résultat de l'application:
            {
                'applied': Nombre de recommandations appliquées,
                'skipped': Nombre de recommandations ignorées,
                'failed': Nombre d'échecs,
                'details': Liste des actions effectuées
            }
        """
        result = {
            'applied': 0,
            'skipped': 0,
            'failed': 0,
            'details': []
        }
        
        # Créer un backup de la configuration avant modifications
        backup_path = self.config_path.parent / f"roon-config.backup.{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        if not self._save_json(backup_path, self.config):
            logger.error(f"Failed to create backup, aborting apply_recommendations")
            result['failed'] = len(recommendations)
            return result
        
        logger.info(f"Configuration backup created: {backup_path}")
        
        for rec in recommendations:
            # Vérifier si on applique automatiquement
            if auto_apply and rec.confidence < 0.8:
                result['skipped'] += 1
                result['details'].append({
                    'recommendation': rec.type,
                    'action': 'skipped',
                    'reason': f"Confiance trop faible ({rec.confidence} < 0.8)"
                })
                continue
            
            # Appliquer selon le type
            try:
                if rec.type == 'listening_hours':
                    # Mettre à jour les plages horaires
                    self.config['listen_start_hour'] = rec.recommended_value['start']
                    self.config['listen_end_hour'] = rec.recommended_value['end']
                    
                    result['applied'] += 1
                    result['details'].append({
                        'recommendation': rec.type,
                        'action': 'applied',
                        'changes': f"{rec.current_value} -> {rec.recommended_value}"
                    })
                    
                elif rec.type == 'task_frequency':
                    # Mettre à jour la fréquence d'une tâche
                    task_name = rec.recommended_value['task']
                    frequency_parts = rec.recommended_value['frequency'].split()
                    
                    if len(frequency_parts) >= 2:
                        count = int(frequency_parts[0])
                        unit = frequency_parts[1]
                        
                        self.config['scheduled_tasks'][task_name]['frequency_count'] = count
                        self.config['scheduled_tasks'][task_name]['frequency_unit'] = unit
                        
                        result['applied'] += 1
                        result['details'].append({
                            'recommendation': rec.type,
                            'action': 'applied',
                            'task': task_name,
                            'changes': f"{rec.current_value['frequency']} -> {rec.recommended_value['frequency']}"
                        })
                    else:
                        raise ValueError(f"Invalid frequency format: {rec.recommended_value['frequency']}")
                
                else:
                    # Type de recommandation non supporté
                    result['skipped'] += 1
                    result['details'].append({
                        'recommendation': rec.type,
                        'action': 'skipped',
                        'reason': 'Type not supported'
                    })
                    
            except Exception as e:
                logger.error(f"Failed to apply recommendation {rec.type}: {e}")
                result['failed'] += 1
                result['details'].append({
                    'recommendation': rec.type,
                    'action': 'failed',
                    'error': str(e)
                })
        
        # Sauvegarder la configuration modifiée
        if result['applied'] > 0:
            if self._save_json(self.config_path, self.config):
                logger.info(f"Configuration updated successfully: {result['applied']} recommendations applied")
            else:
                logger.error("Failed to save updated configuration")
                # Restaurer le backup
                self.config = self._load_json(backup_path)
                self._save_json(self.config_path, self.config)
                result['failed'] += result['applied']
                result['applied'] = 0
        
        return result
    
    def generate_optimization_report(self, output_dir: Path = None) -> str:
        """Génère un rapport complet d'optimisation.
        
        Args:
            output_dir: Répertoire de sortie (défaut: output/reports/)
            
        Returns:
            Chemin du rapport généré
        """
        if output_dir is None:
            # Déterminer le répertoire de sortie
            project_root = self.config_path.parent.parent.parent
            output_dir = project_root / "output" / "reports"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Générer le rapport
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        report_path = output_dir / f"ai-optimization-{timestamp}.txt"
        
        # Collecter toutes les analyses
        patterns = self.analyze_listening_patterns(days=30)
        task_perf = self.analyze_task_performance()
        anomalies = self.detect_anomalies(days=7)
        recommendations = self.generate_recommendations()
        
        # Construire le rapport
        lines = [
            "=" * 80,
            "RAPPORT D'OPTIMISATION IA",
            "=" * 80,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Période d'analyse: {patterns['analysis_period_days']} jours",
            "",
            "1. ANALYSE DES PATTERNS D'ÉCOUTE",
            "-" * 80,
            f"Total tracks analysés: {patterns['total_tracks']}",
            f"Volume quotidien moyen: {patterns['daily_volume']} tracks/jour",
            f"Score d'activité: {patterns['activity_score']}/1.0",
            f"Plages typiques: {patterns['typical_start']}h - {patterns['typical_end']}h",
            f"Heures de pic: {', '.join(map(str, patterns['peak_hours']))}h",
            "",
            "Distribution hebdomadaire:",
            *[f"  {day}: {percentage}%" for day, percentage in patterns['weekly_distribution'].items()],
            "",
            "2. PERFORMANCE DES TÂCHES PLANIFIÉES",
            "-" * 80,
        ]
        
        for task_name, perf in task_perf.items():
            lines.extend([
                f"\nTâche: {task_name}",
                f"  État: {'Activé' if perf['enabled'] else 'Désactivé'}",
                f"  Fréquence: {perf['current_frequency']}",
                f"  Exécutions: {perf['execution_count']}",
                f"  Dernier statut: {perf['last_status']}",
                f"  Durée: {perf['avg_duration']:.1f}s",
                f"  Ratio valeur/coût: {perf['value_ratio']:.2f}",
            ])
        
        lines.extend([
            "",
            "3. ANOMALIES DÉTECTÉES",
            "-" * 80,
        ])
        
        if anomalies:
            for anomaly in anomalies:
                lines.extend([
                    f"\n[{anomaly.severity.upper()}] {anomaly.type}",
                    f"  {anomaly.description}",
                    f"  Composant: {anomaly.affected_component}",
                    f"  Action suggérée: {anomaly.suggested_action}",
                ])
        else:
            lines.append("Aucune anomalie détectée ✅")
        
        lines.extend([
            "",
            "4. RECOMMANDATIONS D'OPTIMISATION",
            "-" * 80,
        ])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                lines.extend([
                    f"\nRecommandation #{i}: {rec.type}",
                    f"  Confiance: {rec.confidence:.2%}",
                    f"  Catégorie: {rec.category}",
                    f"  Valeur actuelle: {rec.current_value}",
                    f"  Valeur recommandée: {rec.recommended_value}",
                    f"  Justification: {rec.justification}",
                    f"  Impact estimé: {rec.estimated_impact}",
                ])
        else:
            lines.append("Aucune recommandation générée - configuration optimale ✅")
        
        lines.extend([
            "",
            "=" * 80,
            "FIN DU RAPPORT",
            "=" * 80,
        ])
        
        # Écrire le rapport
        report_content = "\n".join(lines)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Optimization report generated: {report_path}")
        return str(report_path)


# Fonction utilitaire pour exécution en ligne de commande
def main():
    """Point d'entrée principal pour tests et utilisation CLI."""
    import sys
    from pathlib import Path
    
    # Déterminer les chemins des fichiers
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    config_path = project_root / "data" / "config" / "roon-config.json"
    state_path = project_root / "data" / "config" / "scheduler-state.json"
    history_path = project_root / "data" / "history" / "chk-roon.json"
    
    # Créer l'optimiseur
    optimizer = AIOptimizer(
        config_path=str(config_path),
        state_path=str(state_path),
        history_path=str(history_path)
    )
    
    # Générer et afficher le rapport
    report_path = optimizer.generate_optimization_report()
    print(f"\n✅ Rapport d'optimisation généré: {report_path}")
    
    # Afficher les recommandations
    recommendations = optimizer.generate_recommendations()
    if recommendations:
        print(f"\n💡 {len(recommendations)} recommandations générées:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec.type} (confiance: {rec.confidence:.0%})")
            print(f"     {rec.justification}")
    else:
        print("\n✅ Aucune recommandation - système déjà optimisé!")


if __name__ == "__main__":
    main()
