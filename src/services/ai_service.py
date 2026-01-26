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

def generate_album_info(artist: str, album: str, max_words: int = 35) -> str:
    """Génère une description courte d'un album via l'API EurIA.
    
    Génère une description concise en français limitée au nombre de mots spécifié,
    focalisée sur le contexte et l'approche artistique de l'album.
    
    Args:
        artist: Nom de l'artiste ou compositeur.
        album: Titre de l'album.
        max_words: Nombre maximum de mots (défaut: 35).
        
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
    Présente l'album "{album}" de {artist} en maximum {max_words} mots en français.
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
        import json
        
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
