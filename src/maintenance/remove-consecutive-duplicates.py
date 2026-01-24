#!/usr/bin/env python3
"""
Script pour supprimer les doublons consécutifs dans chk-roon.json
Un doublon est défini comme une piste identique (artiste, titre, album) 
qui apparaît immédiatement après la même piste sans autre piste entre les deux.

Auteur: Patrick Ostertag
Date: 23 janvier 2026
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def load_tracks() -> Tuple[Dict, List[Dict]]:
    """
    Charge les pistes depuis chk-roon.json.
    
    Returns:
        Tuple contenant les données complètes et la liste des tracks
    """
    json_file = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")
    
    if not os.path.exists(json_file):
        print(f"❌ Erreur : Le fichier {json_file} n'existe pas.")
        return None, []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        tracks = data.get('tracks', [])
        return data, tracks
    except json.JSONDecodeError:
        print(f"❌ Erreur : Le fichier {json_file} n'est pas un JSON valide.")
        return None, []
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return None, []

def are_tracks_identical(track1: Dict, track2: Dict) -> bool:
    """
    Vérifie si deux pistes sont identiques (même artiste, titre et album).
    
    Args:
        track1: Première piste
        track2: Deuxième piste
        
    Returns:
        True si les pistes sont identiques, False sinon
    """
    return (
        track1.get('artist') == track2.get('artist') and
        track1.get('title') == track2.get('title') and
        track1.get('album') == track2.get('album')
    )

def remove_consecutive_duplicates(tracks: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Supprime les doublons consécutifs de la liste de pistes.
    
    Args:
        tracks: Liste des pistes
        
    Returns:
        Tuple contenant la liste nettoyée et le nombre de doublons supprimés
    """
    if not tracks:
        return [], 0
    
    cleaned_tracks = [tracks[0]]  # Garder la première piste
    duplicates_count = 0
    duplicates_details = []
    
    for i in range(1, len(tracks)):
        current_track = tracks[i]
        previous_track = tracks[i-1]
        
        # Vérifier si la piste actuelle est identique à la précédente
        if are_tracks_identical(current_track, previous_track):
            # C'est un doublon consécutif - on le saute
            duplicates_count += 1
            duplicates_details.append({
                'index': i,
                'artist': current_track.get('artist'),
                'title': current_track.get('title'),
                'album': current_track.get('album'),
                'date': current_track.get('date'),
                'timestamp': current_track.get('timestamp')
            })
        else:
            # Piste différente - on la garde
            cleaned_tracks.append(current_track)
    
    return cleaned_tracks, duplicates_count, duplicates_details

def backup_file(filename: str) -> str:
    """
    Crée une sauvegarde du fichier avec timestamp.
    
    Args:
        filename: Nom du fichier à sauvegarder
        
    Returns:
        Nom du fichier de sauvegarde créé
    """
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_dir = os.path.join(PROJECT_ROOT, "backups", "json", "chk-roon")
    
    # Créer le répertoire de backup s'il n'existe pas
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_filename = f"{backup_dir}/chk-roon-{timestamp}.json"
    
    # Copier le fichier
    with open(filename, 'r', encoding='utf-8') as source:
        content = source.read()
    
    with open(backup_filename, 'w', encoding='utf-8') as backup:
        backup.write(content)
    
    return backup_filename

def save_tracks(data: Dict, tracks: List[Dict], filename: str = None) -> bool:
    """
    Sauvegarde les pistes dans le fichier JSON.
    
    Args:
        data: Données complètes du fichier
        tracks: Liste des pistes nettoyées
        filename: Nom du fichier de sortie
        
    Returns:
        True si la sauvegarde a réussi, False sinon
    """    
    if filename is None:
        filename = os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json")    
    try:
        # Mettre à jour les tracks dans data
        data['tracks'] = tracks
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        return False

def main():
    """Fonction principale."""
    print("=" * 80)
    print("🧹 SUPPRESSION DES DOUBLONS CONSÉCUTIFS")
    print("=" * 80)
    print()
    
    # Charger les données
    print("📂 Chargement de chk-roon.json...")
    data, tracks = load_tracks()
    
    if not data or not tracks:
        return
    
    print(f"✅ {len(tracks)} piste(s) chargée(s)")
    print()
    
    # Identifier et supprimer les doublons
    print("🔍 Recherche des doublons consécutifs...")
    cleaned_tracks, duplicates_count, duplicates_details = remove_consecutive_duplicates(tracks)
    
    if duplicates_count == 0:
        print("✅ Aucun doublon consécutif détecté !")
        print()
        return
    
    print(f"⚠️  {duplicates_count} doublon(s) consécutif(s) détecté(s) :")
    print()
    
    # Afficher les détails des doublons
    for i, dup in enumerate(duplicates_details[:10], 1):  # Afficher max 10 premiers
        print(f"  {i}. [{dup['date']}] {dup['artist']} - {dup['title']}")
        print(f"     Album: {dup['album']}")
    
    if len(duplicates_details) > 10:
        print(f"  ... et {len(duplicates_details) - 10} autre(s) doublon(s)")
    
    print()
    print(f"📊 Résultat:")
    print(f"  - Pistes avant  : {len(tracks)}")
    print(f"  - Pistes après  : {len(cleaned_tracks)}")
    print(f"  - Doublons      : {duplicates_count}")
    print()
    
    # Demander confirmation
    response = input("Voulez-vous supprimer ces doublons ? (o/n) : ").strip().lower()
    
    if response != 'o':
        print("❌ Opération annulée.")
        return
    
    # Créer une sauvegarde
    print()
    print("💾 Création d'une sauvegarde...")
    backup_filename = backup_file('../../data/history/chk-roon.json')
    print(f"✅ Sauvegarde créée : {backup_filename}")
    
    # Sauvegarder les données nettoyées
    print()
    print("💾 Sauvegarde des données nettoyées...")
    if save_tracks(data, cleaned_tracks):
        print("✅ Doublons supprimés avec succès !")
        print()
        print(f"📄 Fichier mis à jour : chk-roon.json")
        print(f"📄 Sauvegarde disponible : {backup_filename}")
    else:
        print("❌ Erreur lors de la sauvegarde des données nettoyées.")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
