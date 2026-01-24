#!/usr/bin/env python3
"""
Script pour nettoyer les écoutes de radio invalides dans chk-roon.json
Supprime les écoutes où l'artiste, l'album ou le titre n'ont pas pu être détectés.

Auteur: Patrick Ostertag
Date: 21 janvier 2026
"""

import json
import os
from datetime import datetime

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def load_radio_stations() -> list:
    """Charge la liste des stations de radio depuis roon-config.json.
    
    Returns:
        Liste des noms de stations de radio configurées dans Roon.
        Liste par défaut si le fichier est absent ou invalide.
    """
    default_stations = [
        "RTS La Première",
        "RTS Couleur 3",
        "RTS Espace 2",
        "RTS Option Musique",
        "Radio Meuh",
        "Radio Nova"
    ]
    
    config_file = os.path.join(PROJECT_ROOT, "data", "config", "roon-config.json")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            stations = config.get('radio_stations', default_stations)
            print(f"📻 {len(stations)} station(s) de radio chargée(s) depuis roon-config.json")
            return stations
    except FileNotFoundError:
        print(f"⚠️ Fichier {config_file} non trouvé, utilisation des stations par défaut")
        return default_stations
    except json.JSONDecodeError:
        print(f"⚠️ Erreur de lecture du fichier de configuration, utilisation des stations par défaut")
        return default_stations

def is_radio_track(track: dict, radio_stations: list) -> bool:
    """Vérifie si une piste est une station de radio.
    
    Args:
        track: Dictionnaire de la piste à vérifier
        radio_stations: Liste des noms de stations de radio
    """
    title = track.get('title', '')
    return any(station in title for station in radio_stations)

def is_invalid_radio_track(track: dict, radio_stations: list) -> bool:
    """
    Vérifie si une piste radio est invalide (artiste, album ou titre non détecté).
    
    Args:
        track: Dictionnaire de la piste à vérifier
        radio_stations: Liste des noms de stations de radio
    
    Critères d'invalidité :
    - Titre est le nom d'une station de radio
    - Album est vide ou "Inconnu"
    - Artiste est en majuscules (format non parsé)
    - Artiste contient le nom de la station
    """
    if not is_radio_track(track, radio_stations):
        return False
    
    artist = track.get('artist', '')
    album = track.get('album', '')
    title = track.get('title', '')
    
    # Si le titre est encore le nom de la station, c'est invalide
    if any(station in title for station in radio_stations):
        return True
    
    # Si l'album est vide ou Inconnu, c'est invalide
    if not album or album == 'Inconnu':
        return True
    
    # Si l'artiste contient le nom d'une station, c'est invalide
    if any(station in artist for station in radio_stations):
        return True
    
    return False

def clean_radio_tracks(json_file: str = None, backup: bool = True) -> None:
    """
    Nettoie le fichier JSON en supprimant les écoutes radio invalides.
    
    Args:
        json_file: Chemin vers le fichier JSON
        backup: Si True, crée une sauvegarde avant modification
    """
    # Charger les stations de radio depuis la configuration
    radio_stations = load_radio_stations()
    
    if json_file is None:
        json_file = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")
    
    # Charger le fichier
    print(f"📂 Chargement de {json_file}...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {json_file} n'existe pas.")
        return
    except json.JSONDecodeError:
        print(f"❌ Erreur : Le fichier {json_file} n'est pas un JSON valide.")
        return
    
    tracks = data.get('tracks', [])
    initial_count = len(tracks)
    print(f"✅ {initial_count} pistes chargées\n")
    
    # Identifier les pistes invalides
    invalid_tracks = []
    for track in tracks:
        if is_invalid_radio_track(track, radio_stations):
            invalid_tracks.append(track)
    
    if not invalid_tracks:
        print("✅ Aucune écoute radio invalide détectée !")
        return
    
    print(f"🔍 {len(invalid_tracks)} écoute(s) radio invalide(s) détectée(s):\n")
    
    # Afficher les pistes à supprimer
    for i, track in enumerate(invalid_tracks[:10], 1):
        date = track.get('date', 'N/A')
        artist = track.get('artist', 'N/A')
        title = track.get('title', 'N/A')
        album = track.get('album', 'N/A')
        print(f"  {i}. {date} - {artist} - {title} ({album})")
    
    if len(invalid_tracks) > 10:
        print(f"  ... et {len(invalid_tracks) - 10} autres\n")
    else:
        print()
    
    # Demander confirmation
    response = input(f"⚠️  Supprimer ces {len(invalid_tracks)} écoute(s) ? (o/n) : ").strip().lower()
    
    if response != 'o':
        print("❌ Opération annulée.")
        return
    
    # Créer une sauvegarde si demandé
    if backup:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_file = f"Anciennes versions/chk-roon-{timestamp}.json"
        
        # S'assurer que le dossier existe
        os.makedirs('Anciennes versions', exist_ok=True)
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"💾 Sauvegarde créée : {backup_file}")
        except Exception as e:
            print(f"⚠️ Impossible de créer la sauvegarde : {e}")
            response = input("Continuer sans sauvegarde ? (o/n) : ").strip().lower()
            if response != 'o':
                print("❌ Opération annulée.")
                return
    
    # Filtrer les pistes invalides
    print("\n🔄 Suppression en cours...")
    
    # Créer une liste des timestamps invalides pour un filtrage rapide
    invalid_timestamps = {track['timestamp'] for track in invalid_tracks}
    
    # Filtrer
    cleaned_tracks = [
        track for track in tracks 
        if track.get('timestamp') not in invalid_timestamps
    ]
    
    data['tracks'] = cleaned_tracks
    
    # Sauvegarder
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        final_count = len(cleaned_tracks)
        removed_count = initial_count - final_count
        
        print(f"✅ Nettoyage terminé !")
        print(f"\n📊 Résultats :")
        print(f"  - Pistes initiales : {initial_count}")
        print(f"  - Pistes supprimées : {removed_count}")
        print(f"  - Pistes restantes : {final_count}")
        
        # Nettoyer les anciennes sauvegardes (garder seulement les 5 plus récentes)
        try:
            backup_dir = 'Anciennes versions'
            backup_files = sorted([
                f for f in os.listdir(backup_dir) 
                if f.startswith('chk-roon-') and f.endswith('.json')
            ], reverse=True)
            
            if len(backup_files) > 5:
                for old_backup in backup_files[5:]:
                    os.remove(os.path.join(backup_dir, old_backup))
                print(f"\n🧹 {len(backup_files) - 5} ancienne(s) sauvegarde(s) supprimée(s)")
        except Exception as e:
            pass  # Ignorer les erreurs de nettoyage des sauvegardes
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")

def main():
    """Fonction principale."""
    print("=" * 80)
    print("🧹 NETTOYAGE DES ÉCOUTES RADIO INVALIDES")
    print("=" * 80)
    print()
    
    clean_radio_tracks()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
