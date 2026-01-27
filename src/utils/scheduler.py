#!/usr/bin/env python3
"""Gestionnaire de tâches planifiées pour le projet Musique Tracker.

Ce module gère la planification et l'exécution automatique de tâches périodiques
telles que l'analyse des patterns d'écoute, la génération de haïkus, et la
synchronisation avec Discogs.

Fonctionnalités principales:
    - Configuration centralisée dans roon-config.json
    - État persistant dans scheduler-state.json
    - Fréquences configurables (heure, jour, mois, année)
    - Logging des succès/erreurs avec détails
    - Exécution manuelle de tâches
    - Statut en temps réel de toutes les tâches

Architecture:
    Le scheduler est conçu pour être intégré dans le tracker Roon qui tourne
    en continu. Il vérifie périodiquement si des tâches doivent être exécutées
    et les lance en fonction de leur configuration.

Tâches gérées:
    - analyze_listening_patterns: Analyse des patterns d'écoute
    - generate_haiku: Génération de haïkus pour albums
    - read_discogs: Synchronisation collection Discogs
    - generate_soundtrack: Cross-référence bandes originales

Configuration (dans roon-config.json):
    {
        "scheduled_tasks": {
            "task_name": {
                "enabled": bool,
                "frequency_unit": "hour"|"day"|"month"|"year",
                "frequency_count": int,
                "last_execution": ISO8601 timestamp|null,
                "description": str
            }
        }
    }

État (dans scheduler-state.json):
    {
        "task_name": {
            "last_execution": ISO8601 timestamp,
            "last_status": "success"|"error",
            "last_error": str|null,
            "execution_count": int,
            "last_duration_seconds": float
        }
    }

Usage:
    # Initialisation
    scheduler = TaskScheduler(config_path, state_path)
    
    # Vérification et exécution des tâches dues
    scheduler.check_and_execute_tasks()
    
    # Exécution manuelle
    scheduler.execute_task("generate_haiku")
    
    # Obtenir le statut
    status = scheduler.get_task_status("generate_haiku")

Auteur: Patrick Ostertag
Version: 1.0.0
Date: 25 janvier 2026
"""

import json
import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration des tâches disponibles
TASKS_CONFIG = {
    "analyze_listening_patterns": {
        "script": "src/analysis/analyze-listening-patterns.py",
        "description": "Analyze listening patterns and generate insights"
    },
    "generate_haiku": {
        "script": "src/analysis/generate-haiku.py",
        "description": "Generate haiku presentations for albums"
    },
    "generate_playlist": {
        "script": "src/analysis/generate-playlist.py",
        "description": "Generate playlists based on listening patterns"
    },
    "read_discogs": {
        "script": "src/collection/Read-discogs-ia.py",
        "description": "Fetch Discogs collection"
    },
    "generate_soundtrack": {
        "script": "src/collection/generate-soundtrack.py",
        "description": "Cross-reference soundtracks"
    },
    "ai_optimize_system": {
        "script": "src/services/ai_optimizer.py",
        "description": "AI-powered system optimization with recommendations"
    }
}

# Configuration par défaut pour les tâches
DEFAULT_TASK_CONFIG = {
    "analyze_listening_patterns": {
        "enabled": True,
        "frequency_unit": "hour",
        "frequency_count": 6,
        "last_execution": None,
        "description": "Analyze listening patterns and generate insights"
    },
    "generate_haiku": {
        "enabled": True,
        "frequency_unit": "day",
        "frequency_count": 1,
        "last_execution": None,
        "description": "Generate haiku presentations for albums"
    },
    "generate_playlist": {
        "enabled": True,
        "frequency_unit": "day",
        "frequency_count": 7,
        "last_execution": None,
        "description": "Generate playlists based on listening patterns",
        "playlist_type": "top_sessions",
        "max_tracks": 25,
        "output_formats": ["json", "m3u", "csv", "roon-txt"]
    },
    "read_discogs": {
        "enabled": True,
        "frequency_unit": "day",
        "frequency_count": 7,
        "last_execution": None,
        "description": "Fetch Discogs collection"
    },
    "generate_soundtrack": {
        "enabled": True,
        "frequency_unit": "day",
        "frequency_count": 7,
        "last_execution": None,
        "description": "Cross-reference soundtracks"
    },
    "ai_optimize_system": {
        "enabled": True,
        "frequency_unit": "day",
        "frequency_count": 7,
        "last_execution": None,
        "description": "AI-powered system optimization with recommendations",
        "auto_apply": False
    }
}


class TaskScheduler:
    """Gestionnaire de tâches planifiées."""
    
    def __init__(self, config_path: Path, state_path: Path):
        """Initialise le scheduler.
        
        Args:
            config_path: Chemin vers roon-config.json
            state_path: Chemin vers scheduler-state.json
        """
        self.config_path = Path(config_path)
        self.state_path = Path(state_path)
        self.project_root = self.config_path.parent.parent.parent
        
        # Créer les répertoires de sortie s'ils n'existent pas
        self._ensure_output_directories()
        
        # Charger ou initialiser la configuration
        self._load_or_create_config()
        
        # Charger ou initialiser l'état
        self._load_or_create_state()
        
        logger.info("TaskScheduler initialized successfully")
    
    def _ensure_output_directories(self):
        """Crée les répertoires de sortie s'ils n'existent pas."""
        output_dirs = [
            self.project_root / "output" / "haikus",
            self.project_root / "output" / "reports"
        ]
        for directory in output_dirs:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_or_create_config(self):
        """Charge ou crée la configuration des tâches."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Vérifier si la section scheduled_tasks existe
            if "scheduled_tasks" not in self.config:
                logger.info("Adding scheduled_tasks section to config")
                self.config["scheduled_tasks"] = DEFAULT_TASK_CONFIG
                self._save_config()
            else:
                # Vérifier que toutes les tâches par défaut sont présentes
                updated = False
                for task_name, task_config in DEFAULT_TASK_CONFIG.items():
                    if task_name not in self.config["scheduled_tasks"]:
                        logger.info(f"Adding missing task config: {task_name}")
                        self.config["scheduled_tasks"][task_name] = task_config
                        updated = True
                
                if updated:
                    self._save_config()
                    
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}, creating default")
            self.config = {
                "token": "auto-detected-token",
                "host": "auto-detected-host",
                "port": "9330",
                "listen_start_hour": 6,
                "listen_end_hour": 23,
                "scheduled_tasks": DEFAULT_TASK_CONFIG
            }
            self._save_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def _load_or_create_state(self):
        """Charge ou crée l'état des tâches."""
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            logger.info("Creating new state file")
            self.state = {}
            for task_name in TASKS_CONFIG.keys():
                self.state[task_name] = {
                    "last_execution": None,
                    "last_status": None,
                    "last_error": None,
                    "execution_count": 0,
                    "last_duration_seconds": None
                }
            self._save_state()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in state file: {e}")
            raise
    
    def _save_config(self):
        """Sauvegarde la configuration."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _save_state(self):
        """Sauvegarde l'état."""
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _get_next_execution_time(self, task_name: str) -> Optional[datetime]:
        """Calcule la prochaine exécution prévue pour une tâche.
        
        Args:
            task_name: Nom de la tâche
            
        Returns:
            Datetime de la prochaine exécution ou None si jamais exécutée
        """
        task_config = self.config["scheduled_tasks"].get(task_name, {})
        last_execution_str = task_config.get("last_execution")
        
        if not last_execution_str:
            return None
        
        try:
            last_execution = datetime.fromisoformat(last_execution_str)
        except (ValueError, TypeError):
            return None
        
        frequency_count = task_config.get("frequency_count", 1)
        frequency_unit = task_config.get("frequency_unit", "day")
        
        if frequency_unit == "hour":
            delta = timedelta(hours=frequency_count)
        elif frequency_unit == "day":
            delta = timedelta(days=frequency_count)
        elif frequency_unit == "month":
            delta = timedelta(days=frequency_count * 30)
        elif frequency_unit == "year":
            delta = timedelta(days=frequency_count * 365)
        else:
            delta = timedelta(days=1)
        
        return last_execution + delta
    
    def should_execute(self, task_name: str) -> Tuple[bool, str]:
        """Vérifie si une tâche doit être exécutée.
        
        Args:
            task_name: Nom de la tâche
            
        Returns:
            Tuple (should_execute: bool, reason: str)
        """
        if task_name not in TASKS_CONFIG:
            return False, f"Task {task_name} not found in configuration"
        
        task_config = self.config["scheduled_tasks"].get(task_name, {})
        
        if not task_config.get("enabled", False):
            return False, "Task is disabled"
        
        last_execution_str = task_config.get("last_execution")
        
        if not last_execution_str:
            return True, "Task has never been executed"
        
        try:
            last_execution = datetime.fromisoformat(last_execution_str)
        except (ValueError, TypeError):
            logger.warning(f"Invalid last_execution timestamp for {task_name}")
            return True, "Invalid timestamp, executing anyway"
        
        frequency_count = task_config.get("frequency_count", 1)
        frequency_unit = task_config.get("frequency_unit", "day")
        
        now = datetime.now()
        
        if frequency_unit == "hour":
            delta = timedelta(hours=frequency_count)
        elif frequency_unit == "day":
            delta = timedelta(days=frequency_count)
        elif frequency_unit == "month":
            delta = timedelta(days=frequency_count * 30)
        elif frequency_unit == "year":
            delta = timedelta(days=frequency_count * 365)
        else:
            logger.warning(f"Unknown frequency_unit '{frequency_unit}' for {task_name}")
            delta = timedelta(days=1)
        
        next_execution = last_execution + delta
        
        if now >= next_execution:
            return True, f"Scheduled time reached (last: {last_execution_str})"
        
        return False, f"Not yet due (next: {next_execution.isoformat()})"
    
    def execute_task(self, task_name: str, manual: bool = False) -> Tuple[bool, str]:
        """Exécute une tâche.
        
        Args:
            task_name: Nom de la tâche à exécuter
            manual: Si True, ignore la vérification de planification
            
        Returns:
            Tuple (success: bool, message: str)
        """
        if task_name not in TASKS_CONFIG:
            return False, f"Task {task_name} not found"
        
        if not manual:
            should_run, reason = self.should_execute(task_name)
            if not should_run:
                return False, f"Task not ready to execute: {reason}"
        
        task_info = TASKS_CONFIG[task_name]
        script_path = self.project_root / task_info["script"]
        
        if not script_path.exists():
            error_msg = f"Script not found: {script_path}"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"Executing task: {task_name} ({'manual' if manual else 'scheduled'})")
        
        start_time = datetime.now()
        
        try:
            # Construire la commande avec les arguments spécifiques à la tâche
            cmd = [sys.executable, str(script_path)]
            
            # Traitement spécial pour ai_optimize_system (exécution directe via import)
            if task_name == "ai_optimize_system":
                try:
                    # Import direct pour éviter subprocess
                    sys.path.insert(0, str(self.project_root / "src"))
                    from services.ai_optimizer import AIOptimizer
                    
                    # Déterminer les chemins
                    config_path = self.config_path
                    state_path = self.state_path
                    history_path = self.project_root / "data" / "history" / "chk-roon.json"
                    
                    # Créer l'optimiseur
                    optimizer = AIOptimizer(
                        config_path=str(config_path),
                        state_path=str(state_path),
                        history_path=str(history_path)
                    )
                    
                    # Générer le rapport
                    report_path = optimizer.generate_optimization_report()
                    logger.info(f"AI optimization report generated: {report_path}")
                    
                    # Générer et appliquer les recommandations si configuré
                    task_config = self.config["scheduled_tasks"].get(task_name, {})
                    auto_apply = task_config.get("auto_apply", False)
                    
                    recommendations = optimizer.generate_recommendations()
                    if recommendations:
                        logger.info(f"Generated {len(recommendations)} recommendations")
                        
                        # Sauvegarder les recommandations en JSON
                        output_dir = self.project_root / "output" / "reports"
                        rec_path = output_dir / f"ai-recommendations-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                        with open(rec_path, 'w', encoding='utf-8') as f:
                            json.dump([r.to_dict() for r in recommendations], f, indent=2, ensure_ascii=False)
                        logger.info(f"Recommendations saved to: {rec_path}")
                        
                        if auto_apply:
                            result_apply = optimizer.apply_recommendations(recommendations, auto_apply=True)
                            logger.info(f"Applied {result_apply['applied']} recommendations automatically")
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    # Succès - mettre à jour la configuration et l'état
                    self.config["scheduled_tasks"][task_name]["last_execution"] = start_time.isoformat()
                    self._save_config()
                    
                    if task_name not in self.state:
                        self.state[task_name] = {
                            "last_execution": None,
                            "last_status": None,
                            "last_error": None,
                            "execution_count": 0,
                            "last_duration_seconds": None
                        }
                    
                    self.state[task_name]["last_execution"] = start_time.isoformat()
                    self.state[task_name]["last_status"] = "success"
                    self.state[task_name]["last_error"] = None
                    self.state[task_name]["execution_count"] += 1
                    self.state[task_name]["last_duration_seconds"] = duration
                    self._save_state()
                    
                    return True, f"AI optimization completed in {duration:.1f}s - {len(recommendations)} recommendations generated"
                    
                except Exception as e:
                    error_msg = f"AI optimizer failed: {str(e)}"
                    logger.error(error_msg)
                    
                    if task_name not in self.state:
                        self.state[task_name] = {
                            "last_execution": None,
                            "last_status": None,
                            "last_error": None,
                            "execution_count": 0,
                            "last_duration_seconds": None
                        }
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    self.state[task_name]["last_execution"] = start_time.isoformat()
                    self.state[task_name]["last_status"] = "error"
                    self.state[task_name]["last_error"] = error_msg
                    self.state[task_name]["execution_count"] += 1
                    self.state[task_name]["last_duration_seconds"] = duration
                    self._save_state()
                    
                    return False, error_msg
            
            # Ajouter des arguments spécifiques pour generate_playlist
            if task_name == "generate_playlist":
                task_config = self.config["scheduled_tasks"].get(task_name, {})
                playlist_type = task_config.get("playlist_type", "top_sessions")
                max_tracks = task_config.get("max_tracks", 25)
                output_formats = task_config.get("output_formats", ["json", "m3u", "csv", "roon-txt"])
                ai_prompt = task_config.get("ai_prompt", "")
                
                cmd.extend([
                    "--algorithm", playlist_type,
                    "--max-tracks", str(max_tracks),
                    "--formats"
                ])
                cmd.extend(output_formats)
                
                # Ajouter le prompt IA si l'algorithme est ai_generated
                if playlist_type == "ai_generated" and ai_prompt:
                    cmd.extend(["--ai-prompt", ai_prompt])
            
            # Exécuter le script Python
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                # Succès
                logger.info(f"Task {task_name} completed successfully in {duration:.1f}s")
                
                # Mettre à jour la configuration
                self.config["scheduled_tasks"][task_name]["last_execution"] = start_time.isoformat()
                self._save_config()
                
                # Mettre à jour l'état
                if task_name not in self.state:
                    self.state[task_name] = {
                        "last_execution": None,
                        "last_status": None,
                        "last_error": None,
                        "execution_count": 0,
                        "last_duration_seconds": None
                    }
                
                self.state[task_name]["last_execution"] = start_time.isoformat()
                self.state[task_name]["last_status"] = "success"
                self.state[task_name]["last_error"] = None
                self.state[task_name]["execution_count"] += 1
                self.state[task_name]["last_duration_seconds"] = duration
                self._save_state()
                
                return True, f"Task completed successfully in {duration:.1f}s"
            else:
                # Erreur
                error_msg = f"Task failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f"\nError output: {result.stderr[:500]}"
                
                logger.error(f"Task {task_name} failed: {error_msg}")
                
                # Mettre à jour l'état
                if task_name not in self.state:
                    self.state[task_name] = {
                        "last_execution": None,
                        "last_status": None,
                        "last_error": None,
                        "execution_count": 0,
                        "last_duration_seconds": None
                    }
                
                self.state[task_name]["last_execution"] = start_time.isoformat()
                self.state[task_name]["last_status"] = "error"
                self.state[task_name]["last_error"] = error_msg
                self.state[task_name]["execution_count"] += 1
                self.state[task_name]["last_duration_seconds"] = duration
                self._save_state()
                
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Task execution timeout (10 minutes)"
            logger.error(f"Task {task_name} timed out")
            
            if task_name not in self.state:
                self.state[task_name] = {
                    "last_execution": None,
                    "last_status": None,
                    "last_error": None,
                    "execution_count": 0,
                    "last_duration_seconds": None
                }
            
            self.state[task_name]["last_execution"] = start_time.isoformat()
            self.state[task_name]["last_status"] = "error"
            self.state[task_name]["last_error"] = error_msg
            self.state[task_name]["execution_count"] += 1
            self._save_state()
            
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Task {task_name} failed with exception: {error_msg}")
            
            if task_name not in self.state:
                self.state[task_name] = {
                    "last_execution": None,
                    "last_status": None,
                    "last_error": None,
                    "execution_count": 0,
                    "last_duration_seconds": None
                }
            
            self.state[task_name]["last_execution"] = start_time.isoformat()
            self.state[task_name]["last_status"] = "error"
            self.state[task_name]["last_error"] = error_msg
            self.state[task_name]["execution_count"] += 1
            self._save_state()
            
            return False, error_msg
    
    def check_and_execute_tasks(self):
        """Vérifie toutes les tâches et exécute celles qui sont dues."""
        logger.info("Checking scheduled tasks...")
        
        executed_count = 0
        for task_name in TASKS_CONFIG.keys():
            should_run, reason = self.should_execute(task_name)
            
            if should_run:
                logger.info(f"Task {task_name} is due: {reason}")
                success, message = self.execute_task(task_name, manual=False)
                
                if success:
                    executed_count += 1
                    logger.info(f"✅ {task_name}: {message}")
                else:
                    logger.error(f"❌ {task_name}: {message}")
            else:
                logger.debug(f"Task {task_name} not due: {reason}")
        
        if executed_count > 0:
            logger.info(f"Executed {executed_count} task(s)")
        else:
            logger.debug("No tasks were due for execution")
    
    def get_task_status(self, task_name: str) -> Dict[str, Any]:
        """Retourne le statut complet d'une tâche.
        
        Args:
            task_name: Nom de la tâche
            
        Returns:
            Dictionnaire avec le statut complet
        """
        if task_name not in TASKS_CONFIG:
            return {"error": "Task not found"}
        
        config = self.config["scheduled_tasks"].get(task_name, {})
        state = self.state.get(task_name, {})
        
        next_execution = self._get_next_execution_time(task_name)
        
        status = {
            "name": task_name,
            "description": config.get("description", ""),
            "enabled": config.get("enabled", False),
            "frequency_count": config.get("frequency_count", 1),
            "frequency_unit": config.get("frequency_unit", "day"),
            "last_execution": config.get("last_execution"),
            "next_execution": next_execution.isoformat() if next_execution else None,
            "last_status": state.get("last_status"),
            "last_error": state.get("last_error"),
            "execution_count": state.get("execution_count", 0),
            "last_duration_seconds": state.get("last_duration_seconds")
        }
        
        # Ajouter les paramètres spécifiques à generate_playlist
        if task_name == "generate_playlist":
            status["playlist_type"] = config.get("playlist_type", "top_sessions")
            status["max_tracks"] = config.get("max_tracks", 25)
            status["output_formats"] = config.get("output_formats", ["json", "m3u", "csv", "roon-txt"])
        
        return status
    
    def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Retourne le statut de toutes les tâches.
        
        Returns:
            Dictionnaire avec le statut de toutes les tâches
        """
        return {
            task_name: self.get_task_status(task_name)
            for task_name in TASKS_CONFIG.keys()
        }
    
    def update_task_config(self, task_name: str, enabled: bool, 
                          frequency_count: int, frequency_unit: str, **extra_params) -> Tuple[bool, str]:
        """Met à jour la configuration d'une tâche.
        
        Args:
            task_name: Nom de la tâche
            enabled: Activer/désactiver la tâche
            frequency_count: Nombre d'unités
            frequency_unit: Unité de fréquence (hour, day, month, year)
            **extra_params: Paramètres supplémentaires spécifiques à la tâche
                           (ex: playlist_type, max_tracks, output_formats pour generate_playlist)
            
        Returns:
            Tuple (success: bool, message: str)
        """
        if task_name not in TASKS_CONFIG:
            return False, "Task not found"
        
        if frequency_unit not in ["hour", "day", "month", "year"]:
            return False, "Invalid frequency_unit"
        
        if frequency_count < 1:
            return False, "frequency_count must be >= 1"
        
        self.config["scheduled_tasks"][task_name]["enabled"] = enabled
        self.config["scheduled_tasks"][task_name]["frequency_count"] = frequency_count
        self.config["scheduled_tasks"][task_name]["frequency_unit"] = frequency_unit
        
        # Ajouter les paramètres supplémentaires s'ils existent
        for key, value in extra_params.items():
            self.config["scheduled_tasks"][task_name][key] = value
        
        self._save_config()
        
        logger.info(f"Task {task_name} configuration updated")
        return True, "Configuration updated successfully"


if __name__ == "__main__":
    # Test simple du scheduler
    import argparse
    
    parser = argparse.ArgumentParser(description='Task Scheduler CLI')
    parser.add_argument('--check', action='store_true', help='Check and execute due tasks')
    parser.add_argument('--status', action='store_true', help='Show status of all tasks')
    parser.add_argument('--execute', type=str, help='Execute a specific task manually')
    
    args = parser.parse_args()
    
    # Déterminer les chemins
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    config_path = project_root / "data" / "config" / "roon-config.json"
    state_path = project_root / "data" / "config" / "scheduler-state.json"
    
    # Initialiser le scheduler
    scheduler = TaskScheduler(config_path, state_path)
    
    if args.check:
        scheduler.check_and_execute_tasks()
    elif args.status:
        statuses = scheduler.get_all_tasks_status()
        for task_name, status in statuses.items():
            print(f"\n{task_name}:")
            for key, value in status.items():
                print(f"  {key}: {value}")
    elif args.execute:
        success, message = scheduler.execute_task(args.execute, manual=True)
        print(f"{'✅' if success else '❌'} {message}")
    else:
        parser.print_help()
