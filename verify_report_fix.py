#!/usr/bin/env python3
"""Script de vérification manuelle pour Issue #47.

Ce script génère un rapport d'optimisation avec des données de test
pour vérifier visuellement le formatage des heures de pic et l'affichage
du nombre de jours actifs.
"""

import json
import sys
import re
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
            },
            "generate_haiku": {
                "enabled": True,
                "frequency_unit": "day",
                "frequency_count": 1,
                "last_execution": None,
                "description": "Generate haiku"
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
    
    return temp_dir, config_path, state_path, history_dir


def test_scenario_1_no_data():
    """Scénario 1: Aucune donnée d'historique."""
    print("=" * 80)
    print("SCÉNARIO 1: Aucune donnée d'historique")
    print("=" * 80)
    
    temp_dir, config_path, state_path, history_dir = create_test_data()
    
    # Créer un historique vide
    history_path = history_dir / "chk-roon.json"
    with open(history_path, 'w') as f:
        json.dump([], f)
    
    # Générer le rapport
    optimizer = AIOptimizer(
        config_path=str(config_path),
        state_path=str(state_path),
        history_path=str(history_path)
    )
    
    output_dir = temp_dir / "output" / "reports"
    report_path = optimizer.generate_optimization_report(output_dir=output_dir)
    
    # Afficher le rapport
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les lignes pertinentes
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "ANALYSE DES PATTERNS" in line:
            # Afficher les 10 lignes suivantes
            for j in range(i, min(i+10, len(lines))):
                print(lines[j])
            break
    
    # Vérifications
    print("\nVÉRIFICATIONS:")
    if "Heures de pic: Aucune" in content:
        print("✅ Heures de pic: Format correct (affiche 'Aucune')")
    else:
        print("❌ Heures de pic: Format incorrect")
    
    if "Jours actifs:" in content:
        print("✅ Jours actifs: Présent dans le rapport")
    else:
        print("❌ Jours actifs: Manquant dans le rapport")
    
    print()


def test_scenario_2_sparse_data():
    """Scénario 2: Données éparses (activité sur quelques jours)."""
    print("=" * 80)
    print("SCÉNARIO 2: Données éparses (100 tracks sur 5 jours)")
    print("=" * 80)
    
    temp_dir, config_path, state_path, history_dir = create_test_data()
    
    # Créer un historique avec des tracks sur 5 jours
    history = []
    now = datetime.now()
    
    # Distribuer 100 tracks sur 5 jours (20 tracks par jour)
    for day_offset in [2, 5, 10, 15, 25]:
        for hour in range(14, 18):  # 4 heures par jour
            for i in range(5):  # 5 tracks par heure
                track_date = now - timedelta(days=day_offset, hours=(23-hour), minutes=i*10)
                history.append({
                    "timestamp": int(track_date.timestamp()),
                    "date": track_date.strftime('%Y-%m-%d %H:%M'),
                    "artist": f"Artist {i}",
                    "title": f"Track {i}",
                    "album": f"Album {i}"
                })
    
    history_path = history_dir / "chk-roon.json"
    with open(history_path, 'w') as f:
        json.dump(history, f)
    
    # Générer le rapport
    optimizer = AIOptimizer(
        config_path=str(config_path),
        state_path=str(state_path),
        history_path=str(history_path)
    )
    
    output_dir = temp_dir / "output" / "reports"
    report_path = optimizer.generate_optimization_report(output_dir=output_dir)
    
    # Afficher le rapport
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les lignes pertinentes
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "ANALYSE DES PATTERNS" in line:
            # Afficher les 10 lignes suivantes
            for j in range(i, min(i+12, len(lines))):
                print(lines[j])
            break
    
    # Vérifications
    print("\nVÉRIFICATIONS:")
    
    # Vérifier le nombre de tracks
    total_tracks_match = re.search(r"Total tracks analysés: (\d+)", content)
    if total_tracks_match:
        total_tracks = int(total_tracks_match.group(1))
        print(f"✅ Total tracks: {total_tracks}")
    
    # Vérifier les jours actifs
    active_days_match = re.search(r"Jours actifs: (\d+)/(\d+)", content)
    if active_days_match:
        active_days = int(active_days_match.group(1))
        total_days = int(active_days_match.group(2))
        print(f"✅ Jours actifs: {active_days}/{total_days}")
    else:
        print("❌ Jours actifs: Non trouvé")
    
    # Vérifier le volume quotidien
    daily_volume_match = re.search(r"Volume quotidien moyen: ([\d.]+) tracks/jour", content)
    if daily_volume_match:
        daily_volume = float(daily_volume_match.group(1))
        print(f"✅ Volume quotidien moyen: {daily_volume} tracks/jour")
        
        # Vérifier que c'est correct (100 tracks / 30 jours = 3.3)
        if 3.0 <= daily_volume <= 3.5:
            print("   ✓ Calcul correct (basé sur période complète)")
        else:
            print("   ✗ Calcul incorrect (devrait être ~3.3)")
    
    # Vérifier les heures de pic
    peak_hours_match = re.search(r"Heures de pic: (.+)", content)
    if peak_hours_match:
        peak_hours_text = peak_hours_match.group(1)
        if peak_hours_text == "Aucune":
            print("✅ Heures de pic: Format correct (Aucune)")
        elif "h" in peak_hours_text and peak_hours_text != "h":
            print(f"✅ Heures de pic: Format correct ({peak_hours_text})")
        else:
            print(f"❌ Heures de pic: Format incorrect ({peak_hours_text})")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VÉRIFICATION MANUELLE POUR ISSUE #47")
    print("Formatage du rapport d'optimisation IA")
    print("=" * 80 + "\n")
    
    try:
        # Tester les deux scénarios
        test_scenario_1_no_data()
        test_scenario_2_sparse_data()
        
        print("=" * 80)
        print("VÉRIFICATION TERMINÉE")
        print("=" * 80)
        print("\nSi tous les tests montrent ✅, le fix est correct.")
        print("Sinon, vérifier les messages d'erreur ci-dessus.")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
