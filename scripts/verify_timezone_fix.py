#!/usr/bin/env python3
"""
Script de vérification et migration optionnelle pour le fix timezone (Issue #32).

Ce script permet de :
1. Vérifier que les nouvelles entrées utilisent le fuseau horaire local correct
2. Optionnellement migrer les anciennes entrées en recalculant le champ "date"
   à partir du timestamp Unix stocké

Usage:
    python3 scripts/verify_timezone_fix.py --check    # Vérifier uniquement
    python3 scripts/verify_timezone_fix.py --migrate  # Migrer les anciennes entrées

Auteur: GitHub Copilot
Date: 27 janvier 2026
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_timezone_consistency(json_file: str) -> dict:
    """
    Vérifie si les timestamps correspondent aux dates affichées.
    
    Args:
        json_file: Chemin vers le fichier JSON (chk-roon.json ou chk-last-fm.json)
        
    Returns:
        Dict avec les statistiques de vérification
    """
    if not os.path.exists(json_file):
        print(f"❌ Fichier non trouvé : {json_file}")
        return {"error": "File not found"}
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tracks = data if isinstance(data, list) else data.get("tracks", [])
    
    total = len(tracks)
    utc_format = 0
    local_format = 0
    
    print(f"\n📊 Analyse de {json_file}:")
    print(f"   Total d'entrées : {total}")
    
    for track in tracks[:10]:  # Vérifier les 10 premières entrées
        timestamp = track.get("timestamp")
        date_str = track.get("date", "")
        
        if not timestamp or not date_str:
            continue
        
        # Recalculer la date en local
        local_date = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
        # Recalculer la date en UTC
        utc_date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M')
        
        if date_str == utc_date and date_str != local_date:
            utc_format += 1
        elif date_str == local_date:
            local_format += 1
    
    print(f"   Entrées en format UTC : {utc_format}/10 (anciennes)")
    print(f"   Entrées en format local : {local_format}/10 (nouvelles)")
    
    if utc_format > 0:
        print(f"\n⚠️  Ce fichier contient des entrées au format UTC (ancien)")
        print(f"   Utilisez --migrate pour les corriger")
    else:
        print(f"\n✅ Toutes les entrées vérifiées utilisent le format local correct")
    
    return {
        "total": total,
        "utc_format": utc_format,
        "local_format": local_format
    }


def migrate_timestamps(json_file: str, backup: bool = True) -> None:
    """
    Migre les timestamps UTC vers le format local.
    
    Args:
        json_file: Chemin vers le fichier JSON
        backup: Créer une sauvegarde avant modification
    """
    if not os.path.exists(json_file):
        print(f"❌ Fichier non trouvé : {json_file}")
        return
    
    # Créer une sauvegarde
    if backup:
        backup_file = f"{json_file}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print(f"\n💾 Création d'une sauvegarde : {backup_file}")
        with open(json_file, 'r') as src, open(backup_file, 'w') as dst:
            dst.write(src.read())
    
    # Charger le fichier
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tracks = data if isinstance(data, list) else data.get("tracks", [])
    modified_count = 0
    
    print(f"\n🔄 Migration en cours...")
    
    for track in tracks:
        timestamp = track.get("timestamp")
        if not timestamp:
            continue
        
        # Recalculer la date en format local
        new_date = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
        
        if track.get("date") != new_date:
            track["date"] = new_date
            modified_count += 1
    
    # Sauvegarder les modifications
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Migration terminée : {modified_count} entrées modifiées")
    print(f"   Fichier mis à jour : {json_file}")


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/verify_timezone_fix.py --check    # Vérifier")
        print("  python3 scripts/verify_timezone_fix.py --migrate  # Migrer")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    # Déterminer le chemin du projet
    project_root = Path(__file__).parent.parent
    chk_roon_file = project_root / "data" / "history" / "chk-roon.json"
    chk_lastfm_file = project_root / "data" / "history" / "chk-last-fm.json"
    
    if mode == "--check":
        print("🔍 Vérification des fichiers de données...")
        check_timezone_consistency(str(chk_roon_file))
        check_timezone_consistency(str(chk_lastfm_file))
        
    elif mode == "--migrate":
        print("⚠️  ATTENTION : Cette opération va modifier vos fichiers de données")
        response = input("   Continuer ? (o/n) : ")
        if response.lower() != 'o':
            print("❌ Migration annulée")
            sys.exit(0)
        
        print("\n🔄 Migration des timestamps...")
        migrate_timestamps(str(chk_roon_file))
        migrate_timestamps(str(chk_lastfm_file))
        print("\n✅ Migration terminée avec succès")
        
    else:
        print(f"❌ Mode inconnu : {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
