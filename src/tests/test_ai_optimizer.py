"""Tests pour le module ai_optimizer.

Ce fichier teste les fonctionnalités de l'optimiseur IA incluant:
- Analyse des patterns d'écoute
- Analyse de la performance des tâches
- Détection d'anomalies
- Génération de recommandations
- Application des recommandations

Version: 1.0.0
Date: 27 janvier 2026
"""

import pytest
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_optimizer import AIOptimizer, Recommendation, Anomaly


@pytest.fixture
def temp_dir():
    """Crée un répertoire temporaire pour les tests."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def sample_config(temp_dir):
    """Crée un fichier de configuration de test."""
    config_dir = temp_dir / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "roon-config.json"
    
    config = {
        "token": "test-token",
        "host": "test-host",
        "port": "9330",
        "listen_start_hour": 6,
        "listen_end_hour": 23,
        "scheduled_tasks": {
            "analyze_listening_patterns": {
                "enabled": True,
                "frequency_unit": "hour",
                "frequency_count": 6,
                "last_execution": None,
                "description": "Analyze listening patterns"
            },
            "generate_haiku": {
                "enabled": True,
                "frequency_unit": "day",
                "frequency_count": 1,
                "last_execution": None,
                "description": "Generate haiku"
            },
            "read_discogs": {
                "enabled": True,
                "frequency_unit": "day",
                "frequency_count": 3,
                "last_execution": None,
                "description": "Sync Discogs"
            }
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    return config_path


@pytest.fixture
def sample_state(temp_dir):
    """Crée un fichier d'état de test."""
    config_dir = temp_dir / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    state_path = config_dir / "scheduler-state.json"
    
    state = {
        "analyze_listening_patterns": {
            "last_execution": datetime.now().isoformat(),
            "last_status": "success",
            "last_error": None,
            "execution_count": 15,
            "last_duration_seconds": 12.5
        },
        "generate_haiku": {
            "last_execution": datetime.now().isoformat(),
            "last_status": "success",
            "last_error": None,
            "execution_count": 30,
            "last_duration_seconds": 45.2
        },
        "read_discogs": {
            "last_execution": (datetime.now() - timedelta(days=1)).isoformat(),
            "last_status": "error",
            "last_error": "Connection timeout",
            "execution_count": 5,
            "last_duration_seconds": 120.0
        }
    }
    
    with open(state_path, 'w') as f:
        json.dump(state, f)
    
    return state_path


@pytest.fixture
def sample_history(temp_dir):
    """Crée un fichier d'historique de test avec 30 jours de données."""
    history_dir = temp_dir / "data" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_path = history_dir / "chk-roon.json"
    
    history = []
    now = datetime.now()
    
    # Générer 30 jours d'historique avec patterns réalistes
    # Pattern: écoutes principalement entre 19h-23h, ~40 tracks/jour
    for day in range(30):
        date = now - timedelta(days=day)
        
        # Skip certains jours (weekends moins actifs)
        if date.weekday() == 6:  # Dimanche
            tracks_count = 20
        else:
            tracks_count = 40
        
        for i in range(tracks_count):
            # Concentration des écoutes entre 19h-23h
            if i < tracks_count * 0.8:
                hour = 19 + (i % 5)  # 19h-23h
            else:
                hour = 8 + (i % 10)  # Quelques tracks le matin
            
            track_time = date.replace(hour=hour, minute=i % 60, second=0)
            
            history.append({
                "timestamp": int(track_time.timestamp()),
                "date": track_time.strftime('%Y-%m-%d %H:%M'),
                "artist": f"Artist {i % 10}",
                "title": f"Track {i}",
                "album": f"Album {i % 5}",
                "artist_spotify_image": "https://example.com/artist.jpg" if i % 3 != 0 else None,
                "album_spotify_image": "https://example.com/album.jpg" if i % 4 != 0 else None,
                "source": "roon"
            })
    
    # Inverser pour avoir l'ordre chronologique
    history.reverse()
    
    with open(history_path, 'w') as f:
        json.dump(history, f)
    
    return history_path


@pytest.fixture
def optimizer(sample_config, sample_state, sample_history):
    """Crée une instance d'AIOptimizer pour les tests."""
    return AIOptimizer(
        config_path=str(sample_config),
        state_path=str(sample_state),
        history_path=str(sample_history)
    )


class TestAIOptimizerInit:
    """Tests d'initialisation de l'AIOptimizer."""
    
    def test_init_with_valid_files(self, optimizer):
        """Test d'initialisation avec des fichiers valides."""
        assert optimizer.config is not None
        assert optimizer.state is not None
        assert optimizer.history is not None
        assert len(optimizer.history) > 0
    
    def test_init_with_missing_state(self, sample_config, sample_history, temp_dir):
        """Test d'initialisation avec état manquant."""
        state_path = temp_dir / "data" / "config" / "nonexistent.json"
        opt = AIOptimizer(
            config_path=str(sample_config),
            state_path=str(state_path),
            history_path=str(sample_history)
        )
        assert opt.state == {}
    
    def test_init_with_missing_history(self, sample_config, sample_state, temp_dir):
        """Test d'initialisation avec historique manquant."""
        history_path = temp_dir / "data" / "history" / "nonexistent.json"
        opt = AIOptimizer(
            config_path=str(sample_config),
            state_path=str(sample_state),
            history_path=str(history_path)
        )
        assert opt.history == []


class TestAnalyzeListeningPatterns:
    """Tests d'analyse des patterns d'écoute."""
    
    def test_analyze_patterns_basic(self, optimizer):
        """Test d'analyse basique des patterns."""
        patterns = optimizer.analyze_listening_patterns(days=30)
        
        assert 'peak_hours' in patterns
        assert 'typical_start' in patterns
        assert 'typical_end' in patterns
        assert 'daily_volume' in patterns
        assert 'weekly_distribution' in patterns
        assert 'activity_score' in patterns
        assert 'total_tracks' in patterns
    
    def test_analyze_patterns_peak_hours(self, optimizer):
        """Test de détection des heures de pic."""
        patterns = optimizer.analyze_listening_patterns(days=30)
        
        # Avec nos données de test, les pics devraient être entre 19h-23h
        peak_hours = patterns['peak_hours']
        assert len(peak_hours) <= 4
        # Au moins une heure de pic devrait être dans la plage 19h-23h
        assert any(19 <= hour <= 23 for hour in peak_hours)
    
    def test_analyze_patterns_typical_hours(self, optimizer):
        """Test de calcul des heures typiques."""
        patterns = optimizer.analyze_listening_patterns(days=30)
        
        typical_start = patterns['typical_start']
        typical_end = patterns['typical_end']
        
        assert 0 <= typical_start <= 23
        assert 0 <= typical_end <= 23
        assert typical_start < typical_end
    
    def test_analyze_patterns_daily_volume(self, optimizer):
        """Test de calcul du volume quotidien."""
        patterns = optimizer.analyze_listening_patterns(days=30)
        
        daily_volume = patterns['daily_volume']
        assert daily_volume > 0
        # Avec nos données de test (~40 tracks/jour)
        assert 20 <= daily_volume <= 50
    
    def test_analyze_patterns_activity_score(self, optimizer):
        """Test de calcul du score d'activité."""
        patterns = optimizer.analyze_listening_patterns(days=30)
        
        activity_score = patterns['activity_score']
        assert 0.0 <= activity_score <= 1.0
    
    def test_analyze_patterns_empty_history(self, sample_config, sample_state, temp_dir):
        """Test avec historique vide."""
        history_path = temp_dir / "data" / "history" / "empty.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, 'w') as f:
            json.dump([], f)
        
        opt = AIOptimizer(
            config_path=str(sample_config),
            state_path=str(sample_state),
            history_path=str(history_path)
        )
        
        patterns = opt.analyze_listening_patterns(days=30)
        
        assert patterns['daily_volume'] == 0
        assert patterns['activity_score'] == 0.0
        assert patterns['total_tracks'] == 0
    
    def test_analyze_patterns_weekly_distribution(self, optimizer):
        """Test de la distribution hebdomadaire."""
        patterns = optimizer.analyze_listening_patterns(days=30)
        
        weekly_dist = patterns['weekly_distribution']
        assert len(weekly_dist) == 7
        
        # Vérifier que toutes les jours sont présents
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in weekdays:
            assert day in weekly_dist
            assert 0 <= weekly_dist[day] <= 100


class TestAnalyzeTaskPerformance:
    """Tests d'analyse de la performance des tâches."""
    
    def test_analyze_task_performance_basic(self, optimizer):
        """Test d'analyse basique des tâches."""
        task_perf = optimizer.analyze_task_performance()
        
        assert len(task_perf) > 0
        assert 'analyze_listening_patterns' in task_perf
        assert 'generate_haiku' in task_perf
        assert 'read_discogs' in task_perf
    
    def test_analyze_task_performance_metrics(self, optimizer):
        """Test des métriques de performance."""
        task_perf = optimizer.analyze_task_performance()
        
        for task_name, metrics in task_perf.items():
            assert 'avg_duration' in metrics
            assert 'success_rate' in metrics
            assert 'execution_count' in metrics
            assert 'last_status' in metrics
            assert 'current_frequency' in metrics
            assert 'value_ratio' in metrics
            assert 'enabled' in metrics
    
    def test_analyze_task_performance_success_rate(self, optimizer):
        """Test du calcul du taux de succès."""
        task_perf = optimizer.analyze_task_performance()
        
        # Tâche en succès
        assert task_perf['generate_haiku']['success_rate'] == 1.0
        
        # Tâche en erreur
        assert task_perf['read_discogs']['success_rate'] == 0.5
    
    def test_analyze_task_performance_value_ratio(self, optimizer):
        """Test du calcul du ratio valeur/coût."""
        task_perf = optimizer.analyze_task_performance()
        
        for task_name, metrics in task_perf.items():
            value_ratio = metrics['value_ratio']
            assert 0.0 <= value_ratio <= 1.0


class TestDetectAnomalies:
    """Tests de détection d'anomalies."""
    
    def test_detect_anomalies_basic(self, optimizer):
        """Test de détection basique d'anomalies."""
        anomalies = optimizer.detect_anomalies(days=7)
        
        assert isinstance(anomalies, list)
    
    def test_detect_anomalies_task_failure(self, optimizer):
        """Test de détection d'échec de tâche."""
        anomalies = optimizer.detect_anomalies(days=7)
        
        # On devrait détecter l'échec de read_discogs
        task_failures = [a for a in anomalies if a.type == 'task_failure']
        assert len(task_failures) > 0
        
        # Vérifier les détails
        failure = task_failures[0]
        assert failure.severity == 'error'
        assert 'read_discogs' in failure.description
    
    def test_detect_anomalies_tracking_interruption(self, sample_config, sample_state, temp_dir):
        """Test de détection d'interruption de tracking."""
        # Créer un historique avec bonne activité récente, puis interruption de 5 jours
        history_path = temp_dir / "data" / "history" / "old.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        history = []
        now = datetime.now()
        old_date = now - timedelta(days=5)
        
        # Ajouter beaucoup d'historique récent (jours -30 à -5) pour avoir un bon activity_score
        for day in range(30, 5, -1):
            date = now - timedelta(days=day)
            # ~30 tracks par jour pour avoir un bon activity_score
            for i in range(30):
                track_date = date.replace(hour=19 + (i % 5), minute=i % 60)
                history.append({
                    "timestamp": int(track_date.timestamp()),
                    "date": track_date.strftime('%Y-%m-%d %H:%M'),
                    "artist": f"Artist {i % 10}",
                    "title": f"Track {i}",
                    "album": f"Album {i % 5}",
                    "source": "roon"
                })
        
        # Dernière écoute il y a 5 jours (interruption)
        history.append({
            "timestamp": int(old_date.timestamp()),
            "date": old_date.strftime('%Y-%m-%d %H:%M'),
            "artist": "Test Artist",
            "title": "Test Track",
            "album": "Test Album",
            "source": "roon"
        })
        
        with open(history_path, 'w') as f:
            json.dump(history, f)
        
        opt = AIOptimizer(
            config_path=str(sample_config),
            state_path=str(sample_state),
            history_path=str(history_path)
        )
        
        anomalies = opt.detect_anomalies(days=7)
        
        # On devrait détecter l'interruption
        interruptions = [a for a in anomalies if a.type == 'tracking_interruption']
        assert len(interruptions) > 0
    
    def test_detect_anomalies_data_quality(self, sample_config, sample_state, temp_dir):
        """Test de détection de dégradation de qualité."""
        # Créer un historique avec beaucoup d'images manquantes
        history_path = temp_dir / "data" / "history" / "poor_quality.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        history = []
        now = datetime.now()
        
        for i in range(20):
            date = now - timedelta(minutes=i*5)
            history.append({
                "timestamp": int(date.timestamp()),
                "date": date.strftime('%Y-%m-%d %H:%M'),
                "artist": f"Artist {i}",
                "title": f"Track {i}",
                "album": f"Album {i}",
                # Pas d'images pour la plupart des tracks
                "artist_spotify_image": None,
                "album_spotify_image": None,
                "source": "roon"
            })
        
        with open(history_path, 'w') as f:
            json.dump(history, f)
        
        opt = AIOptimizer(
            config_path=str(sample_config),
            state_path=str(sample_state),
            history_path=str(history_path)
        )
        
        anomalies = opt.detect_anomalies(days=7)
        
        # On devrait détecter la dégradation de qualité
        quality_issues = [a for a in anomalies if a.type == 'data_quality']
        assert len(quality_issues) > 0


class TestGenerateRecommendations:
    """Tests de génération de recommandations."""
    
    def test_generate_recommendations_basic(self, optimizer, monkeypatch):
        """Test de génération basique de recommandations."""
        # Mock de l'API IA pour éviter les appels réels
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Recommandation justifiée par l'analyse des patterns d'écoute."
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        recommendations = optimizer.generate_recommendations()
        
        assert isinstance(recommendations, list)
    
    def test_generate_recommendations_listening_hours(self, optimizer, monkeypatch):
        """Test de recommandation pour les plages horaires."""
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Ajustement recommandé pour optimiser la charge CPU."
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        recommendations = optimizer.generate_recommendations()
        
        # Filtrer les recommandations de type listening_hours
        hour_recs = [r for r in recommendations if r.type == 'listening_hours']
        
        if hour_recs:
            rec = hour_recs[0]
            assert 'start' in rec.current_value
            assert 'end' in rec.current_value
            assert 'start' in rec.recommended_value
            assert 'end' in rec.recommended_value
            assert 0.0 <= rec.confidence <= 1.0
    
    def test_generate_recommendations_task_frequency(self, optimizer, monkeypatch):
        """Test de recommandation pour les fréquences de tâches."""
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Fréquence ajustée selon le volume d'activité."
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        recommendations = optimizer.generate_recommendations()
        
        # Filtrer les recommandations de type task_frequency
        freq_recs = [r for r in recommendations if r.type == 'task_frequency']
        
        for rec in freq_recs:
            assert 'task' in rec.current_value
            assert 'frequency' in rec.current_value
            assert 'task' in rec.recommended_value
            assert 'frequency' in rec.recommended_value
            assert 0.0 <= rec.confidence <= 1.0


class TestApplyRecommendations:
    """Tests d'application des recommandations."""
    
    def test_apply_recommendations_listening_hours(self, optimizer, monkeypatch):
        """Test d'application de recommandation pour plages horaires."""
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Justification test"
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        # Créer une recommandation manuelle
        rec = Recommendation(
            type='listening_hours',
            current_value={'start': 6, 'end': 23},
            recommended_value={'start': 19, 'end': 23},
            justification="Test justification",
            confidence=0.9,
            estimated_impact="Test impact",
            category='performance'
        )
        
        result = optimizer.apply_recommendations([rec], auto_apply=True)
        
        assert result['applied'] == 1
        assert result['failed'] == 0
        
        # Vérifier que la config a été mise à jour
        assert optimizer.config['listen_start_hour'] == 19
        assert optimizer.config['listen_end_hour'] == 23
    
    def test_apply_recommendations_task_frequency(self, optimizer, monkeypatch):
        """Test d'application de recommandation pour fréquence de tâche."""
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Justification test"
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        rec = Recommendation(
            type='task_frequency',
            current_value={'task': 'generate_haiku', 'frequency': '1 day'},
            recommended_value={'task': 'generate_haiku', 'frequency': '3 day'},
            justification="Test justification",
            confidence=0.85,
            estimated_impact="Test impact",
            category='cost'
        )
        
        result = optimizer.apply_recommendations([rec], auto_apply=True)
        
        assert result['applied'] == 1
        assert result['failed'] == 0
        
        # Vérifier que la config a été mise à jour
        assert optimizer.config['scheduled_tasks']['generate_haiku']['frequency_count'] == 3
        assert optimizer.config['scheduled_tasks']['generate_haiku']['frequency_unit'] == 'day'
    
    def test_apply_recommendations_low_confidence_skip(self, optimizer):
        """Test que les recommandations avec faible confiance sont ignorées."""
        rec = Recommendation(
            type='listening_hours',
            current_value={'start': 6, 'end': 23},
            recommended_value={'start': 8, 'end': 22},
            justification="Low confidence",
            confidence=0.5,  # Trop faible pour auto_apply
            estimated_impact="Minimal",
            category='performance'
        )
        
        result = optimizer.apply_recommendations([rec], auto_apply=True)
        
        assert result['applied'] == 0
        assert result['skipped'] == 1
    
    def test_apply_recommendations_backup_created(self, optimizer, monkeypatch):
        """Test que le backup est créé avant modification."""
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Justification test"
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        rec = Recommendation(
            type='listening_hours',
            current_value={'start': 6, 'end': 23},
            recommended_value={'start': 19, 'end': 23},
            justification="Test",
            confidence=0.9,
            estimated_impact="Test",
            category='performance'
        )
        
        # Compter les fichiers backup avant
        backup_dir = optimizer.config_path.parent
        backup_files_before = list(backup_dir.glob('roon-config.backup.*.json'))
        
        optimizer.apply_recommendations([rec], auto_apply=True)
        
        # Vérifier qu'un nouveau backup a été créé
        backup_files_after = list(backup_dir.glob('roon-config.backup.*.json'))
        assert len(backup_files_after) == len(backup_files_before) + 1


class TestRecommendationModel:
    """Tests du modèle Recommendation."""
    
    def test_recommendation_creation(self):
        """Test de création d'une recommandation."""
        rec = Recommendation(
            type='listening_hours',
            current_value={'start': 6, 'end': 23},
            recommended_value={'start': 8, 'end': 22},
            justification="Test justification",
            confidence=0.85,
            estimated_impact="Test impact",
            category='performance'
        )
        
        assert rec.type == 'listening_hours'
        assert rec.confidence == 0.85
        assert rec.category == 'performance'
    
    def test_recommendation_to_dict(self):
        """Test de conversion en dictionnaire."""
        rec = Recommendation(
            type='task_frequency',
            current_value={'task': 'test', 'frequency': '1 day'},
            recommended_value={'task': 'test', 'frequency': '2 day'},
            justification="Test",
            confidence=0.9,
            estimated_impact="Impact",
            category='cost'
        )
        
        rec_dict = rec.to_dict()
        
        assert isinstance(rec_dict, dict)
        assert rec_dict['type'] == 'task_frequency'
        assert rec_dict['confidence'] == 0.9


class TestAnomalyModel:
    """Tests du modèle Anomaly."""
    
    def test_anomaly_creation(self):
        """Test de création d'une anomalie."""
        now = datetime.now()
        anomaly = Anomaly(
            type='task_failure',
            severity='error',
            description="Test failure",
            detected_at=now,
            affected_component='scheduler',
            suggested_action="Check logs"
        )
        
        assert anomaly.type == 'task_failure'
        assert anomaly.severity == 'error'
        assert anomaly.detected_at == now
    
    def test_anomaly_to_dict(self):
        """Test de conversion en dictionnaire."""
        now = datetime.now()
        anomaly = Anomaly(
            type='tracking_interruption',
            severity='warning',
            description="No activity",
            detected_at=now,
            affected_component='tracker',
            suggested_action="Verify tracker"
        )
        
        anomaly_dict = anomaly.to_dict()
        
        assert isinstance(anomaly_dict, dict)
        assert anomaly_dict['type'] == 'tracking_interruption'
        assert anomaly_dict['severity'] == 'warning'
        assert 'detected_at' in anomaly_dict


class TestGenerateOptimizationReport:
    """Tests de génération de rapport d'optimisation."""
    
    def test_generate_report_basic(self, optimizer, monkeypatch, temp_dir):
        """Test de génération basique de rapport."""
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Recommandation justifiée"
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        output_dir = temp_dir / "output" / "reports"
        report_path = optimizer.generate_optimization_report(output_dir=output_dir)
        
        assert os.path.exists(report_path)
        assert report_path.endswith('.txt')
    
    def test_generate_report_content(self, optimizer, monkeypatch, temp_dir):
        """Test du contenu du rapport."""
        def mock_ask_for_ia(prompt, max_attempts=5, timeout=60):
            return "Recommandation justifiée"
        
        monkeypatch.setattr('services.ai_optimizer.ask_for_ia', mock_ask_for_ia)
        
        output_dir = temp_dir / "output" / "reports"
        report_path = optimizer.generate_optimization_report(output_dir=output_dir)
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier que les sections principales sont présentes
        assert "RAPPORT D'OPTIMISATION IA" in content
        assert "ANALYSE DES PATTERNS D'ÉCOUTE" in content
        assert "PERFORMANCE DES TÂCHES PLANIFIÉES" in content
        assert "ANOMALIES DÉTECTÉES" in content
        assert "RECOMMANDATIONS D'OPTIMISATION" in content
