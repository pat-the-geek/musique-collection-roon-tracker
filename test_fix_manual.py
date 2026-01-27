#!/usr/bin/env python3
"""Test manuel pour vérifier la correction du bug de chargement de l'historique.

Ce script crée des données de test au format dict avec clé 'tracks'
et génère un rapport d'optimisation pour vérifier que les tracks sont bien comptés.
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.ai_optimizer import AIOptimizer


def create_test_data():
    """Crée des fichiers de test pour la vérification."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Créer la structure de répertoires
    config_dir = temp_dir / "data" / "config"
    history_dir = temp_dir / "data" / "history"
    config_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer roon-config.json
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
            }
        }
    }
    config_path = config_dir / "roon-config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    # Créer scheduler-state.json
    state = {
        "analyze_listening_patterns": {
            "last_execution": datetime.now().isoformat(),
            "last_status": "success",
            "last_error": None,
            "execution_count": 15,
            "last_duration_seconds": 12.5
        }
    }
    state_path = config_dir / "scheduler-state.json"
    with open(state_path, 'w') as f:
        json.dump(state, f)
    
    # Créer chk-roon.json au format DICT avec clé 'tracks' (nouveau format)
    now = datetime.now()
    tracks = []
    
    # Générer 100 tracks sur 5 jours (activité éparse)
    for day_offset in [2, 5, 10, 15, 25]:
        for hour in range(14, 18):  # 4 heures par jour
            for i in range(5):  # 5 tracks par heure
                track_date = now - timedelta(days=day_offset, hours=(23-hour), minutes=i*10)
                tracks.append({
                    "timestamp": int(track_date.timestamp()),
                    "date": track_date.strftime('%Y-%m-%d %H:%M'),
                    "artist": f"Artist {i % 10}",
                    "title": f"Track {i}",
                    "album": f"Album {i % 5}",
                    "source": "roon"
                })
    
    # Format dict avec clé 'tracks' (format réel du fichier chk-roon.json)
    history_data = {
        "username": "test_user",
        "month": "January 2026",
        "tracks": tracks
    }
    
    history_path = history_dir / "chk-roon.json"
    with open(history_path, 'w') as f:
        json.dump(history_data, f, indent=2)
    
    print(f"✅ Données de test créées dans: {temp_dir}")
    print(f"   - Config: {config_path}")
    print(f"   - State: {state_path}")
    print(f"   - History: {history_path}")
    print(f"   - Format history: dict avec clé 'tracks'")
    print(f"   - Nombre de tracks: {len(tracks)}")
    
    return temp_dir, config_path, state_path, history_path


def main():
    """Test principal."""
    print("=" * 80)
    print("TEST MANUEL: Correction du bug de chargement de l'historique")
    print("=" * 80)
    print()
    
    # Créer les données de test
    temp_dir, config_path, state_path, history_path = create_test_data()
    print()
    
    # Initialiser l'optimiseur
    print("🔧 Initialisation de l'AIOptimizer...")
    optimizer = AIOptimizer(
        config_path=str(config_path),
        state_path=str(state_path),
        history_path=str(history_path)
    )
    
    # Vérifier que les tracks ont été chargés
    print(f"✅ Historique chargé: {len(optimizer.history)} tracks")
    print()
    
    if len(optimizer.history) == 0:
        print("❌ ÉCHEC: Aucun track chargé (le bug est toujours présent)")
        return False
    
    if len(optimizer.history) != 100:
        print(f"⚠️  ATTENTION: {len(optimizer.history)} tracks chargés, attendu 100")
    
    # Analyser les patterns
    print("📊 Analyse des patterns d'écoute...")
    patterns = optimizer.analyze_listening_patterns(days=30)
    print()
    
    # Afficher les résultats
    print("=" * 80)
    print("RÉSULTATS DE L'ANALYSE")
    print("=" * 80)
    print(f"Total tracks analysés: {patterns['total_tracks']}")
    print(f"Jours actifs: {patterns['active_days']}/30")
    print(f"Volume quotidien moyen: {patterns['daily_volume']} tracks/jour")
    print(f"Score d'activité: {patterns['activity_score']}/1.0")
    print(f"Plages typiques: {patterns['typical_start']}h - {patterns['typical_end']}h")
    
    if patterns['peak_hours']:
        peak_hours_str = ", ".join([f"{h}h" for h in patterns['peak_hours']])
        print(f"Heures de pic: {peak_hours_str}")
    else:
        print("Heures de pic: Aucune")
    print()
    
    # Vérifications
    print("=" * 80)
    print("VÉRIFICATIONS")
    print("=" * 80)
    
    success = True
    
    # Vérification 1: Total tracks
    if patterns['total_tracks'] == 100:
        print("✅ Total tracks: Correct (100)")
    else:
        print(f"❌ Total tracks: Incorrect ({patterns['total_tracks']}, attendu 100)")
        success = False
    
    # Vérification 2: Jours actifs
    if patterns['active_days'] == 5:
        print("✅ Jours actifs: Correct (5)")
    else:
        print(f"⚠️  Jours actifs: {patterns['active_days']} (attendu 5)")
    
    # Vérification 3: Volume quotidien (100 tracks / 30 jours = 3.3)
    expected_volume = 100 / 30
    if 3.3 <= patterns['daily_volume'] <= 3.4:
        print(f"✅ Volume quotidien moyen: Correct ({patterns['daily_volume']} tracks/jour)")
    else:
        print(f"❌ Volume quotidien moyen: Incorrect ({patterns['daily_volume']}, attendu ~3.3)")
        success = False
    
    # Vérification 4: Score d'activité (devrait être > 0)
    if patterns['activity_score'] > 0:
        print(f"✅ Score d'activité: Correct ({patterns['activity_score']})")
    else:
        print(f"❌ Score d'activité: Incorrect ({patterns['activity_score']}, devrait être > 0)")
        success = False
    
    print()
    print("=" * 80)
    
    if success:
        print("✅ SUCCÈS: Tous les tests sont passés")
        print("   Le bug de chargement de l'historique est corrigé!")
    else:
        print("❌ ÉCHEC: Certains tests ont échoué")
    
    print("=" * 80)
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
