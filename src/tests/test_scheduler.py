"""Tests pour le module scheduler.

Ce fichier teste les fonctionnalités du TaskScheduler incluant:
- Initialisation et configuration
- Vérification des tâches planifiées
- Exécution des tâches
- Gestion de l'état et de la configuration

Version: 1.0.0
Date: 25 janvier 2026
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

from utils.scheduler import TaskScheduler, TASKS_CONFIG, DEFAULT_TASK_CONFIG


@pytest.fixture
def temp_dir():
    """Crée un répertoire temporaire pour les tests."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def test_config_path(temp_dir):
    """Crée un fichier de configuration de test."""
    config_dir = temp_dir / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "roon-config.json"
    
    config = {
        "token": "test-token",
        "host": "test-host",
        "port": "9330",
        "scheduled_tasks": {
            "analyze_listening_patterns": {
                "enabled": True,
                "frequency_unit": "hour",
                "frequency_count": 1,
                "last_execution": None,
                "description": "Test task"
            }
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f)
    
    return config_path


@pytest.fixture
def test_state_path(temp_dir):
    """Crée un chemin pour le fichier d'état de test."""
    config_dir = temp_dir / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "scheduler-state.json"


@pytest.fixture
def scheduler(test_config_path, test_state_path, temp_dir):
    """Crée une instance de TaskScheduler pour les tests."""
    # Créer les répertoires de sortie
    (temp_dir / "output" / "haikus").mkdir(parents=True, exist_ok=True)
    (temp_dir / "output" / "reports").mkdir(parents=True, exist_ok=True)
    
    return TaskScheduler(test_config_path, test_state_path)


class TestTaskSchedulerInit:
    """Tests d'initialisation du scheduler."""
    
    def test_init_creates_config(self, temp_dir):
        """Teste que l'initialisation crée la configuration si elle n'existe pas."""
        config_dir = temp_dir / "data" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "roon-config.json"
        state_path = config_dir / "scheduler-state.json"
        
        # Créer les répertoires de sortie
        (temp_dir / "output" / "haikus").mkdir(parents=True, exist_ok=True)
        (temp_dir / "output" / "reports").mkdir(parents=True, exist_ok=True)
        
        scheduler = TaskScheduler(config_path, state_path)
        
        assert config_path.exists()
        assert state_path.exists()
    
    def test_init_creates_output_directories(self, scheduler, temp_dir):
        """Teste que l'initialisation crée les répertoires de sortie."""
        assert (temp_dir / "output" / "haikus").exists()
        assert (temp_dir / "output" / "reports").exists()
    
    def test_init_loads_existing_config(self, scheduler, test_config_path):
        """Teste que l'initialisation charge une configuration existante."""
        assert "scheduled_tasks" in scheduler.config
        assert "analyze_listening_patterns" in scheduler.config["scheduled_tasks"]


class TestTaskSchedulerMethods:
    """Tests des méthodes du scheduler."""
    
    def test_should_execute_never_executed(self, scheduler):
        """Teste qu'une tâche jamais exécutée doit être lancée."""
        should_run, reason = scheduler.should_execute("analyze_listening_patterns")
        assert should_run
        assert "never been executed" in reason.lower()
    
    def test_should_execute_disabled_task(self, scheduler):
        """Teste qu'une tâche désactivée ne doit pas être lancée."""
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["enabled"] = False
        should_run, reason = scheduler.should_execute("analyze_listening_patterns")
        assert not should_run
        assert "disabled" in reason.lower()
    
    def test_should_execute_recently_executed(self, scheduler):
        """Teste qu'une tâche récemment exécutée ne doit pas être relancée."""
        # Mettre à jour avec une exécution récente
        now = datetime.now()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["last_execution"] = now.isoformat()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 1
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] = "hour"
        
        should_run, reason = scheduler.should_execute("analyze_listening_patterns")
        assert not should_run
        assert "not yet due" in reason.lower()
    
    def test_should_execute_due_task(self, scheduler):
        """Teste qu'une tâche due doit être lancée."""
        # Mettre à jour avec une exécution ancienne
        past = datetime.now() - timedelta(hours=2)
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["last_execution"] = past.isoformat()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 1
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] = "hour"
        
        should_run, reason = scheduler.should_execute("analyze_listening_patterns")
        assert should_run
        assert "scheduled time reached" in reason.lower()
    
    def test_get_task_status(self, scheduler):
        """Teste la récupération du statut d'une tâche."""
        status = scheduler.get_task_status("analyze_listening_patterns")
        
        assert "name" in status
        assert status["name"] == "analyze_listening_patterns"
        assert "enabled" in status
        assert "frequency_count" in status
        assert "frequency_unit" in status
    
    def test_get_all_tasks_status(self, scheduler):
        """Teste la récupération du statut de toutes les tâches."""
        statuses = scheduler.get_all_tasks_status()
        
        assert isinstance(statuses, dict)
        assert len(statuses) == len(TASKS_CONFIG)
        
        for task_name in TASKS_CONFIG.keys():
            assert task_name in statuses
    
    def test_update_task_config(self, scheduler):
        """Teste la mise à jour de la configuration d'une tâche."""
        success, message = scheduler.update_task_config(
            "analyze_listening_patterns",
            enabled=False,
            frequency_count=12,
            frequency_unit="hour"
        )
        
        assert success
        assert scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["enabled"] == False
        assert scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] == 12
        assert scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] == "hour"
    
    def test_update_task_config_invalid_unit(self, scheduler):
        """Teste la mise à jour avec une unité invalide."""
        success, message = scheduler.update_task_config(
            "analyze_listening_patterns",
            enabled=True,
            frequency_count=1,
            frequency_unit="invalid"
        )
        
        assert not success
        assert "invalid" in message.lower()
    
    def test_update_task_config_invalid_count(self, scheduler):
        """Teste la mise à jour avec un count invalide."""
        success, message = scheduler.update_task_config(
            "analyze_listening_patterns",
            enabled=True,
            frequency_count=0,
            frequency_unit="hour"
        )
        
        assert not success
        assert "must be >= 1" in message.lower()
    
    def test_get_next_execution_time_never_executed(self, scheduler):
        """Teste le calcul du prochain temps d'exécution pour une tâche jamais exécutée."""
        next_time = scheduler._get_next_execution_time("analyze_listening_patterns")
        assert next_time is None
    
    def test_get_next_execution_time_with_last_execution(self, scheduler):
        """Teste le calcul du prochain temps d'exécution."""
        # Définir une dernière exécution
        last_exec = datetime.now()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["last_execution"] = last_exec.isoformat()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 1
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] = "hour"
        
        next_time = scheduler._get_next_execution_time("analyze_listening_patterns")
        
        assert next_time is not None
        expected = last_exec + timedelta(hours=1)
        # Tolérance de 1 seconde pour les arrondis
        assert abs((next_time - expected).total_seconds()) < 1


class TestTaskSchedulerFrequencyUnits:
    """Tests des différentes unités de fréquence."""
    
    def test_frequency_unit_hour(self, scheduler):
        """Teste la fréquence en heures."""
        past = datetime.now() - timedelta(hours=2)
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["last_execution"] = past.isoformat()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 1
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] = "hour"
        
        should_run, _ = scheduler.should_execute("analyze_listening_patterns")
        assert should_run
    
    def test_frequency_unit_day(self, scheduler):
        """Teste la fréquence en jours."""
        past = datetime.now() - timedelta(days=2)
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["last_execution"] = past.isoformat()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 1
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] = "day"
        
        should_run, _ = scheduler.should_execute("analyze_listening_patterns")
        assert should_run
    
    def test_frequency_unit_month(self, scheduler):
        """Teste la fréquence en mois."""
        past = datetime.now() - timedelta(days=60)
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["last_execution"] = past.isoformat()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 1
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] = "month"
        
        should_run, _ = scheduler.should_execute("analyze_listening_patterns")
        assert should_run
    
    def test_frequency_unit_year(self, scheduler):
        """Teste la fréquence en années."""
        past = datetime.now() - timedelta(days=400)
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["last_execution"] = past.isoformat()
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 1
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_unit"] = "year"
        
        should_run, _ = scheduler.should_execute("analyze_listening_patterns")
        assert should_run


class TestTaskSchedulerPersistence:
    """Tests de la persistance de la configuration et de l'état."""
    
    def test_config_persists_after_save(self, scheduler, test_config_path):
        """Teste que la configuration est persistée après sauvegarde."""
        scheduler.config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] = 42
        scheduler._save_config()
        
        # Recharger le fichier
        with open(test_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert config["scheduled_tasks"]["analyze_listening_patterns"]["frequency_count"] == 42
    
    def test_state_persists_after_save(self, scheduler, test_state_path):
        """Teste que l'état est persisté après sauvegarde."""
        scheduler.state["analyze_listening_patterns"]["execution_count"] = 99
        scheduler._save_state()
        
        # Recharger le fichier
        with open(test_state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        assert state["analyze_listening_patterns"]["execution_count"] == 99


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
