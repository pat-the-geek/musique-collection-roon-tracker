#!/usr/bin/env python3
"""Service d'intégration avec l'API EurIA pour génération de contenu IA.

Ce module fournit une interface unifiée pour l'utilisation de l'API EurIA
(basée sur Qwen3) dans tout le projet. Il gère l'authentification, les appels API,
les retry automatiques et la génération de résumés d'albums.

Fonctionnalités principales:
    - Appel API EurIA avec recherche web activée
    - Génération de résumés d'albums courts (30-35 mots)
    - Gestion des erreurs et retry automatiques
    - Cache des résultats pour optimisation

Configuration requise dans .env:
    URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
    bearer=votre_token_euria
    max_attempts=5
    default_error_message=Aucune information disponible

Auteur: Patrick Ostertag
Version: 1.0.0
Date: 26 janvier 2026
"""

import os
import json
import requests
import time
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement si nécessaire
def ensure_env_loaded():
    """S'assure que les variables d'environnement sont chargées."""
    if not os.getenv("URL"):
        # Déterminer le répertoire racine du projet
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        env_path = os.path.join(project_root, "data", "config", ".env")
        load_dotenv(env_path)

# Configuration EurIA API
def get_euria_config():
    """Récupère la configuration de l'API EurIA depuis les variables d'environnement.
    
    Returns:
        Tuple[str, str, int, str]: URL, bearer token, max_attempts, default_error_message
    """
    ensure_env_loaded()
    url = os.getenv("URL")
    bearer = os.getenv("bearer")
    max_attempts = int(os.getenv("max_attempts", "5"))
    default_error = os.getenv("default_error_message", "Aucune information disponible")
    
    return url, bearer, max_attempts, default_error

def ask_for_ia(prompt: str, max_attempts: int = None, timeout: int = 60) -> str:
    """Envoie un prompt à l'API EurIA et retourne la réponse textuelle.
    
    Interroge l'API EurIA (basée sur Qwen3) avec recherche web activée pour
    obtenir des informations contextuelles. Gère automatiquement les erreurs
    et réessaye en cas d'échec.
    
    Args:
        prompt: Question ou instruction à envoyer à l'IA.
        max_attempts: Nombre maximum de tentatives. Si None, utilise la valeur
            de la variable d'environnement max_attempts (défaut: 5).
        timeout: Délai d'attente maximum en secondes (défaut: 60).
        
    Returns:
        Réponse textuelle de l'IA, nettoyée des espaces superflus.
        Message d'erreur générique si toutes les tentatives échouent.
        
    Examples:
        >>> response = ask_for_ia("Présente l'album Kind of Blue de Miles Davis")
        >>> print(response)
        'Kind of Blue est un album emblématique du jazz modal...'
        
    Note:
        - Nécessite les variables d'environnement URL et bearer
        - Active automatiquement la recherche web (enable_web_search=True)
        - Gère les timeouts et erreurs réseau avec réessais automatiques
    """
    url, bearer, default_max_attempts, default_error = get_euria_config()
    
    # Use configured max_attempts if not explicitly provided
    if max_attempts is None:
        max_attempts = default_max_attempts
    
    if not url or not bearer:
        print("⚠️ Configuration EurIA manquante (URL ou bearer)")
        return default_error
    
    data = {
        "messages": [{"content": prompt, "role": "user"}],
        "model": "qwen3",
        "enable_web_search": True
    }
    headers = {
        'Authorization': f'Bearer {bearer}',
        'Content-Type': 'application/json',
    }

    for attempt in range(max_attempts):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'choices' in json_data and len(json_data['choices']) > 0:
                content = json_data['choices'][0]['message']['content']
                return content.strip()  # Nettoyage des espaces superflus

            raise ValueError("Réponse API invalide : champ 'choices' manquant ou vide.")

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout EurIA API (tentative {attempt + 1}/{max_attempts})")
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur réseau EurIA (tentative {attempt + 1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue
        except (ValueError, KeyError, TypeError) as e:
            print(f"⚠️ Erreur format EurIA (tentative {attempt + 1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue

    return default_error

def generate_album_info(artist: str, album: str, max_characters: int = 2000) -> str:
    """Génère une description courte d'un album via l'API EurIA.
    
    Génère une description concise en français limitée au nombre de caractères spécifié,
    focalisée sur le contexte et l'approche artistique de l'album.
    
    Args:
        artist: Nom de l'artiste ou compositeur.
        album: Titre de l'album.
        max_characters: Nombre maximum de caractères (défaut: 2000).
        
    Returns:
        Description courte de l'album en français.
        Message d'erreur si génération échoue.
        
    Examples:
        >>> info = generate_album_info("Miles Davis", "Kind of Blue")
        >>> print(info)
        'Kind of Blue, sorti en 1959, est un album majeur du jazz modal...'
        
    Note:
        - Utilise la recherche web pour obtenir des informations actualisées
        - Fonctionne avec tous types d'albums (studio, live, BO, radio)
        - Gère les artistes inconnus et les stations de radio
    """
    prompt = f"""
    Présente l'album "{album}" de {artist} en maximum {max_characters} caractères en français.
    Concentre-toi sur le contexte de création et l'approche artistique.
    Ne réponds que par la description, sans ajout ni commentaire.
    Si c'est une station de radio ou un artiste inconnu, décris le contenu musical général.
    """
    
    return ask_for_ia(prompt.strip(), max_attempts=3, timeout=45)

def get_album_info_from_discogs(album_title: str, discogs_collection_path: str) -> Optional[str]:
    """Recherche le résumé d'un album dans la collection Discogs.
    
    Vérifie si l'album existe dans discogs-collection.json et retourne
    son résumé s'il est disponible et non vide.
    
    Args:
        album_title: Titre de l'album à rechercher (case-insensitive).
        discogs_collection_path: Chemin vers discogs-collection.json.
        
    Returns:
        Résumé de l'album si trouvé et non vide, None sinon.
        
    Examples:
        >>> resume = get_album_info_from_discogs("Kind of Blue", "data/collection/discogs-collection.json")
        >>> if resume:
        ...     print(resume)
        'Kind of Blue est un album emblématique...'
        
    Note:
        - Recherche insensible à la casse
        - Ignore les résumés vides ou "Aucune information disponible"
        - Ne lève pas d'exception si le fichier est absent
    """
    try:
        if not os.path.exists(discogs_collection_path):
            return None
        
        with open(discogs_collection_path, 'r', encoding='utf-8') as f:
            collection = json.load(f)
        
        # Normaliser le titre pour la recherche
        album_title_lower = album_title.lower().strip()
        
        # Rechercher l'album dans la collection
        for album in collection:
            album_titre = album.get('Titre', '').lower().strip()
            if album_titre == album_title_lower:
                resume = album.get('Resume', '').strip()
                # Vérifier que le résumé n'est pas vide ou générique
                if resume and resume != "Aucune information disponible":
                    return resume
        
        return None
        
    except Exception as e:
        print(f"⚠️ Erreur lecture Discogs collection: {e}")
        return None


def generate_ai_playlist(user_prompt: str, available_tracks: list, max_tracks: int = 25) -> dict:
    """Génère une playlist intelligente basée sur un prompt utilisateur via l'IA EurIA.
    
    Utilise l'API EurIA pour analyser le prompt de l'utilisateur et sélectionner
    les pistes les plus appropriées parmi l'historique d'écoute. L'IA prend en compte
    le contexte, l'ambiance, le genre, et les préférences exprimées dans le prompt.
    
    Args:
        user_prompt: Description en langage naturel du type de playlist souhaité.
            Exemples:
            - "une playlist calme pour méditer le soir"
            - "musique énergique des années 80 pour faire du sport"
            - "jazz cool et sophistiqué pour un dîner"
        available_tracks: Liste des pistes disponibles avec leurs métadonnées.
            Chaque piste doit contenir: artist, title, album, (optionnel) ai_info.
        max_tracks: Nombre maximum de pistes à inclure (défaut: 25).
        
    Returns:
        Dictionnaire contenant:
        - 'tracks': Liste des pistes sélectionnées
        - 'ai_reasoning': Explication de l'IA sur ses choix
        - 'playlist_name': Nom suggéré par l'IA
        - 'playlist_description': Description de la playlist
        
    Examples:
        >>> tracks = [
        ...     {"artist": "Miles Davis", "title": "So What", "album": "Kind of Blue"},
        ...     {"artist": "The Beatles", "title": "Yesterday", "album": "Help!"}
        ... ]
        >>> result = generate_ai_playlist("jazz cool pour le soir", tracks, max_tracks=10)
        >>> print(result['playlist_name'])
        'Soirée Jazz Cool'
        >>> print(len(result['tracks']))
        10
        
    Note:
        - L'IA analyse le prompt et les métadonnées des pistes
        - Fonctionne mieux si les pistes ont des ai_info descriptives
        - Nécessite une connexion à l'API EurIA
        - Peut prendre jusqu'à 60 secondes selon le nombre de pistes
    """
    ensure_env_loaded()
    
    # Limiter le nombre de pistes envoyées à l'IA (pour éviter un prompt trop long)
    max_tracks_to_analyze = min(len(available_tracks), 200)
    tracks_sample = available_tracks[:max_tracks_to_analyze]
    
    # Construire une représentation compacte des pistes pour l'IA
    tracks_summary = []
    for i, track in enumerate(tracks_sample, 1):
        artist = track.get('artist', 'Unknown')
        title = track.get('title', 'Unknown')
        album = track.get('album', 'Unknown')
        ai_info = track.get('ai_info', '')
        
        # Format compact: index|artiste|titre|album|info
        track_line = f"{i}. {artist} - {title} ({album})"
        if ai_info:
            track_line += f" | {ai_info[:100]}"  # Limiter l'info à 100 caractères
        tracks_summary.append(track_line)
    
    # Construire le prompt pour l'IA
    prompt = f"""
Tu es un expert en curation musicale. Un utilisateur te demande de créer une playlist avec cette description:

"{user_prompt}"

Voici les pistes disponibles dans son historique d'écoute (format: index|artiste|titre|album|description):

{chr(10).join(tracks_summary)}

TÂCHE:
1. Sélectionne exactement {min(max_tracks, len(tracks_sample))} pistes qui correspondent le mieux à la demande
2. Propose un nom créatif pour cette playlist (maximum 60 caractères)
3. Écris une description de 2-3 phrases expliquant ta sélection
4. Liste UNIQUEMENT les numéros des pistes sélectionnées, séparés par des virgules

FORMAT DE RÉPONSE STRICT (respecte EXACTEMENT ce format):
NOM: [nom de la playlist]
DESCRIPTION: [description]
SELECTION: [liste des numéros séparés par des virgules, ex: 1,5,12,23,45]
JUSTIFICATION: [1-2 phrases expliquant tes choix]

IMPORTANT: Réponds UNIQUEMENT dans ce format, sans texte supplémentaire avant ou après.
""".strip()
    
    print("🤖 Consultation de l'IA EurIA pour composition de playlist...")
    print(f"   Prompt utilisateur: {user_prompt}")
    print(f"   Pistes à analyser: {len(tracks_sample)}")
    
    # Appeler l'IA avec un timeout plus long
    ai_response = ask_for_ia(prompt, max_attempts=3, timeout=90)
    
    # Parser la réponse de l'IA
    try:
        lines = ai_response.strip().split('\n')
        playlist_name = None
        playlist_description = None
        selection_indices = []
        ai_reasoning = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('NOM:'):
                playlist_name = line.replace('NOM:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                playlist_description = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('SELECTION:'):
                selection_str = line.replace('SELECTION:', '').strip()
                # Extraire les numéros
                try:
                    selection_indices = [int(x.strip()) for x in selection_str.split(',') if x.strip().isdigit()]
                except ValueError:
                    print(f"⚠️ Erreur parsing sélection IA: {selection_str}")
            elif line.startswith('JUSTIFICATION:'):
                ai_reasoning = line.replace('JUSTIFICATION:', '').strip()
        
        # Valider la réponse
        if not playlist_name:
            playlist_name = f"Playlist {user_prompt[:30]}"
        if not playlist_description:
            playlist_description = f"Playlist créée selon vos préférences: {user_prompt}"
        if not ai_reasoning:
            ai_reasoning = "Sélection basée sur votre demande."
        
        # Sélectionner les pistes correspondant aux indices
        selected_tracks = []
        for idx in selection_indices:
            if 1 <= idx <= len(tracks_sample):
                selected_tracks.append(tracks_sample[idx - 1])
        
        # Si pas assez de pistes sélectionnées, en ajouter
        if len(selected_tracks) < max_tracks // 2:
            print(f"⚠️ L'IA a sélectionné seulement {len(selected_tracks)} pistes, ajout de pistes supplémentaires...")
            # Ajouter les premières pistes non encore sélectionnées
            for track in tracks_sample:
                if track not in selected_tracks and len(selected_tracks) < max_tracks:
                    selected_tracks.append(track)
        
        print(f"✅ Playlist générée: {len(selected_tracks)} pistes sélectionnées")
        
        return {
            'tracks': selected_tracks[:max_tracks],
            'ai_reasoning': ai_reasoning,
            'playlist_name': playlist_name,
            'playlist_description': playlist_description,
            'user_prompt': user_prompt
        }
        
    except Exception as e:
        print(f"❌ Erreur lors du parsing de la réponse IA: {e}")
        print(f"   Réponse brute: {ai_response[:500]}")
        
        # Fallback: retourner les premières pistes
        return {
            'tracks': tracks_sample[:max_tracks],
            'ai_reasoning': "Erreur de parsing, sélection automatique des premières pistes.",
            'playlist_name': f"Playlist {user_prompt[:30]}",
            'playlist_description': f"Playlist créée selon: {user_prompt}",
            'user_prompt': user_prompt
        }
