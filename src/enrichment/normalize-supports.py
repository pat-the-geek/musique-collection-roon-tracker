#!/usr/bin/env python3
"""
Script pour normaliser les supports dans discogs-collection.json
Convertit tous les supports vers "Vinyle" ou "CD" uniquement.

Auteur: Patrick Ostertag
Date: 20 janvier 2026
"""

import json
import os

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def normalize_support(album: dict) -> str:
    """
    Détermine le support normalisé (Vinyle ou CD) basé sur les indices disponibles.
    
    Args:
        album: Dictionnaire contenant les données de l'album
        
    Returns:
        "Vinyle" ou "CD"
    """
    current_support = album.get('Support', 'Inconnu')
    titre = album.get('Titre', '')
    annee = album.get('Année', 0)
    spotify_date = album.get('Spotify_Date', 0)
    
    # Règles de normalisation
    if current_support == 'CDr':
        # CDr est un CD enregistrable
        return 'CD'
    
    elif current_support == 'Blu-ray':
        # Pink Floyd At Pompeii est probablement un concert filmé
        # Mais vu que l'utilisateur n'a que vinyle ou CD, on considère le support audio
        # Les concerts de cette époque étaient souvent sur vinyle, mais Blu-ray suggère une réédition récente -> CD
        return 'CD'
    
    elif current_support == 'Box Set':
        # Les box sets peuvent être vinyle ou CD
        # Gorillaz Cracker Island (2023) - album récent, probablement CD ou vinyle
        # On regarde l'année : si récent (>2015), plus probable en vinyle (revival du vinyle)
        year = spotify_date if spotify_date > 0 else annee
        if year >= 2015:
            return 'Vinyle'
        else:
            return 'CD'
    
    elif current_support == 'All Media':
        # AIR - 10 000 Hz Legend (2001)
        # Début des années 2000, l'ère CD dominante
        return 'CD'
    
    elif current_support == 'Inconnu':
        # Pour les inconnus, on se base sur l'année
        year = spotify_date if spotify_date > 0 else annee
        
        # The Young Gods - Only Heaven Reissue (2025) -> réédition récente = vinyle probable
        if 'Reissue' in titre or 'Redux' in titre or 'Remaster' in titre:
            return 'Vinyle'
        
        # La Môme (Original Soundtrack) (2007) -> BO, probablement CD
        if 'Soundtrack' in titre or 'Original' in titre:
            return 'CD'
        
        # Règle générale par année
        if year > 0:
            if year >= 2015:
                return 'Vinyle'  # Revival du vinyle
            elif year >= 1985:
                return 'CD'  # Ère du CD
            else:
                return 'Vinyle'  # Avant l'ère CD
        
        # Par défaut
        return 'CD'
    
    # Si déjà normalisé, retourner tel quel
    return current_support

def main():
    """
    Fonction principale qui charge les albums, normalise les supports
    et sauvegarde le fichier mis à jour.
    """
    json_file = os.path.join(PROJECT_ROOT, "data", "collection", "discogs-collection.json")
    
    # Charger les données
    print("📂 Chargement de discogs-collection.json...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {json_file} n'existe pas.")
        return
    except json.JSONDecodeError:
        print(f"❌ Erreur : Le fichier {json_file} n'est pas un JSON valide.")
        return
    
    # Identifier les albums à normaliser
    albums_a_normaliser = [
        album for album in data 
        if album.get('Support') not in ['Vinyle', 'CD']
    ]
    
    if not albums_a_normaliser:
        print("✅ Tous les albums ont déjà des supports normalisés (Vinyle ou CD) !")
        return
    
    print(f"\n🔍 {len(albums_a_normaliser)} album(s) avec support non standard détecté(s):\n")
    
    # Normaliser et afficher les changements
    modifications = []
    for album in albums_a_normaliser:
        artist = album['Artiste'][0] if isinstance(album['Artiste'], list) else album['Artiste']
        old_support = album.get('Support', 'Inconnu')
        new_support = normalize_support(album)
        
        print(f"  📀 {artist} - {album['Titre']}")
        print(f"     {old_support} → {new_support}")
        
        modifications.append({
            'album': album,
            'old': old_support,
            'new': new_support
        })
    
    # Demander confirmation
    print(f"\n⚠️  {len(modifications)} modification(s) à appliquer.")
    reponse = input("Confirmer ? (o/n) : ").strip().lower()
    
    if reponse != 'o':
        print("❌ Opération annulée.")
        return
    
    # Appliquer les modifications
    print("\n🔄 Application des modifications...")
    for modif in modifications:
        modif['album']['Support'] = modif['new']
    
    # Sauvegarder
    print("💾 Sauvegarde...")
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ {len(modifications)} support(s) normalisé(s) avec succès !")
        
        # Statistiques finales
        vinyles = sum(1 for d in data if d.get('Support') == 'Vinyle')
        cds = sum(1 for d in data if d.get('Support') == 'CD')
        print(f"\n📊 Distribution finale :")
        print(f"   🎵 Vinyle : {vinyles} albums ({round(vinyles/len(data)*100, 1)}%)")
        print(f"   💿 CD     : {cds} albums ({round(cds/len(data)*100, 1)}%)")
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")

if __name__ == "__main__":
    main()
