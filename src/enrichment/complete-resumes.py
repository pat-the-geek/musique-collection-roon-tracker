#!/usr/bin/env python3
"""
Script pour compléter les résumés manquants dans discogs-collection.json
Utilise l'API EurIA pour générer des résumés détaillés des albums.

Auteur: Patrick Ostertag
Date: 20 janvier 2026
"""

import json
import os
import requests
import time
from dotenv import load_dotenv

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Charger les variables d'environnement
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Configuration EurIA API
URL = os.getenv("URL")
BEARER = os.getenv("bearer")
MAX_ATTEMPTS = int(os.getenv("max_attempts", "5"))

def ask_for_ia(prompt: str, max_attempts: int = 3, timeout: int = 60) -> str:
    """
    Envoie un prompt à l'API EurIA (basée sur Qwen3) et retourne la réponse textuelle.
    Utilise la recherche web si nécessaire (enable_web_search=True).
    Gère les erreurs et les tentatives automatiques.
    """
    data = {
        "messages": [{"content": prompt, "role": "user"}],
        "model": "qwen3",
        "enable_web_search": True
    }
    headers = {
        'Authorization': f'Bearer {BEARER}',
        'Content-Type': 'application/json',
    }

    for attempt in range(max_attempts):
        try:
            response = requests.post(URL, json=data, headers=headers, timeout=timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'choices' in json_data and len(json_data['choices']) > 0:
                content = json_data['choices'][0]['message']['content']
                return content.strip()

            raise ValueError("Réponse API invalide : champ 'choices' manquant ou vide.")

        except requests.exceptions.Timeout:
            print(f"  ⏱️ Timeout (tentative {attempt + 1}/{max_attempts})")
            continue
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Erreur réseau (tentative {attempt + 1}/{max_attempts}): {e}")
            continue
        except (ValueError, KeyError, TypeError) as e:
            print(f"  ⚠️ Erreur de format (tentative {attempt + 1}/{max_attempts}): {e}")
            continue

    return "Désolé, je n'ai pas pu obtenir de réponse. Veuillez réessayer plus tard."

def generate_resume(artist: str, album: str, year: int) -> str:
    """
    Génère un résumé détaillé d'un album via l'API EurIA.
    
    Args:
        artist: Nom de l'artiste
        album: Titre de l'album
        year: Année de sortie
        
    Returns:
        Résumé détaillé de l'album
    """
    year_str = str(year) if year > 0 else ""
    
    prompt = f"""
    Résume en 30 lignes maximum l'album {album} de {artist} {f'({year_str})' if year_str else ''}, en mettant l'accent sur :
    - Le contexte de création (collaboration, événement spécial, anniversaire de l'album original).
    - La démarche artistique de {artist} (déconstruction, réinterprétation, atmosphère, touches modernes).
    - Les réactions critiques (accueil, comparaison avec l'original, points forts).
    - Les éléments sonores marquants (beats, textures, voix, ambiance).
    Utilise un ton objectif et synthétique, sans commentaire personnel.
    Présente le texte avec des paragraphes avec sous-titre.
    Si l'album est un remix ou une réinterprétation, précise-le clairement.
    Ne réponds que par le résumé, sans ajout ni commentaire.
    Si tu ne trouves pas d'informations suffisantes, résume l'album {album} {f'({year_str})' if year_str else ''} en 30 lignes maximum.
    """
    
    return ask_for_ia(prompt)

def main():
    """
    Fonction principale qui charge les albums, identifie ceux sans résumé,
    génère les résumés manquants et sauvegarde le fichier mis à jour.
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
    
    # Identifier les albums sans résumé
    albums_sans_resume = [
        album for album in data 
        if not album.get('Resume') or album.get('Resume') == 'Aucune information disponible'
    ]
    
    if not albums_sans_resume:
        print("✅ Tous les albums ont déjà un résumé !")
        return
    
    print(f"\n🔍 {len(albums_sans_resume)} album(s) sans résumé détecté(s):\n")
    for album in albums_sans_resume:
        artist = album['Artiste'][0] if isinstance(album['Artiste'], list) else album['Artiste']
        print(f"  - {artist} - {album['Titre']} ({album.get('Année', 'N/A')})")
    
    print(f"\n🚀 Génération des résumés en cours...\n")
    
    # Générer les résumés
    completed = 0
    for i, album in enumerate(albums_sans_resume, 1):
        artist = album['Artiste'][0] if isinstance(album['Artiste'], list) else album['Artiste']
        titre = album['Titre']
        
        # Utiliser Spotify_Date si Année est 0
        annee = album.get('Spotify_Date', 0) if album.get('Année', 0) == 0 else album.get('Année', 0)
        
        print(f"[{i}/{len(albums_sans_resume)}] 🎵 {artist} - {titre} ({annee if annee > 0 else 'N/A'})...")
        
        try:
            resume = generate_resume(artist, titre, annee)
            
            # Mettre à jour l'album dans la liste originale
            for original_album in data:
                if (original_album['release_id'] == album['release_id']):
                    original_album['Resume'] = resume
                    completed += 1
                    print(f"  ✅ Résumé généré ({len(resume)} caractères)")
                    break
            
            # Pause pour éviter de surcharger l'API
            if i < len(albums_sans_resume):
                time.sleep(2)
                
        except Exception as e:
            print(f"  ❌ Erreur lors de la génération: {e}")
            continue
    
    # Sauvegarder les modifications
    if completed > 0:
        print(f"\n💾 Sauvegarde des modifications...")
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ {completed} résumé(s) ajouté(s) avec succès !")
            print(f"📄 Fichier mis à jour : {json_file}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
    else:
        print("\n⚠️ Aucun résumé n'a pu être généré.")

if __name__ == "__main__":
    main()
