#!/usr/bin/env python3
"""Générateur de haïkus pour albums musicaux.

Ce script génère automatiquement des présentations courtes (style haïku) pour des albums
musicaux sélectionnés aléatoirement depuis deux sources :
- Collection Discogs (10 albums)
- Historique d'écoutes Roon (10 albums)

Le script utilise l'API EurIA (Qwen3) pour générer des descriptions concises en français,
et produit un fichier texte formaté pour iA Presenter avec images et liens.

Fonctionnalités principales:
    - Sélection aléatoire sécurisée de 20 albums (10 Discogs + 10 Roon)
    - Détection et élimination automatique des doublons entre les deux sources
    - Génération de descriptions courtes via API EurIA
    - Formatage automatique pour iA Presenter
    - Support des images Spotify et Last.fm
    - Gestion des métadonnées (année, réédition, support)
    - Liens vers Spotify et Discogs

Fichiers utilisés:
    - discogs-collection.json: Collection Discogs complète
    - chk-roon.json: Historique des écoutes Roon
    - .env: Variables d'environnement (API EurIA)

Fichier généré:
    - generate-haiku-YYYYMMDD-HHMMSS.txt: Présentation formatée

Dépendances:
    - requests: Requêtes HTTP vers API EurIA
    - python-dotenv: Chargement des variables d'environnement
    - secrets: Sélection aléatoire sécurisée

Configuration requise dans .env:
    URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
    bearer=votre_token_euria
    max_attempts=5
    default_error_message=Aucune information disponible

Exemple d'utilisation:
    $ python generate-haiku.py
    # Génère un fichier generate-haiku-20260121-095530.txt

Auteur: Patrick Ostertag
Version: 2.1.0
Date: 21 janvier 2026
"""

import random
import os
import requests
import time
import json
import base64
import re
from datetime import datetime
from typing import Tuple, Optional
import secrets
from dotenv import load_dotenv

def decouper_en_lignes(texte: str) -> str:
    """Découpe un texte en lignes formatées avec indentation.
    
    Découpe le texte en lignes de maximum 45 caractères tout en préservant
    les mots entiers. Chaque ligne est indentée avec deux tabulations.
    
    Args:
        texte: Texte à découper en lignes.
        
    Returns:
        Texte formaté avec lignes indentées, séparées par des retours à la ligne.
        
    Examples:
        >>> decouper_en_lignes("Cet album présente une atmosphère unique et captivante")
        '\\t\\tCet album présente une atmosphère\\n\\t\\tunique et captivante\\n'
        
    Note:
        - Limite de 45 caractères par ligne
        - Préserve l'intégrité des mots
        - Ajoute deux tabulations au début de chaque ligne
    """
    lignes = []
    mots = texte.split()
    ligne_courante = ""

    for mot in mots:
        # Si ajouter ce mot dépasse 45 caractères, on termine la ligne
        if len(ligne_courante) + len(mot) + (1 if ligne_courante else 0) > 45:
            lignes.append(f"\t\t{ligne_courante}\n")
            ligne_courante = mot
        else:
            if ligne_courante:
                ligne_courante += " " + mot
            else:
                ligne_courante = mot

    # N’oubliez pas la dernière ligne
    if ligne_courante:
        lignes.append(f"\t\t{ligne_courante}\n")

    return "".join(lignes)

def ask_for_ia(prompt: str, max_attempts: int = 3, timeout: int = 60) -> str:
    """Envoie un prompt à l'API EurIA et retourne la réponse textuelle.
    
    Interroge l'API EurIA (basée sur Qwen3) avec recherche web activée pour
    obtenir des informations contextuelles. Gère automatiquement les erreurs
    et réessaye en cas d'échec.
    
    Args:
        prompt: Question ou instruction à envoyer à l'IA.
        max_attempts: Nombre maximum de tentatives (défaut: 3).
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
                return content.strip()  # Nettoyage des espaces superflus

            raise ValueError("Réponse API invalide : champ 'choices' manquant ou vide.")

        except requests.exceptions.Timeout:
            continue  # Réessayer
        except requests.exceptions.RequestException as e:
            # Log implicite (à adapter selon votre système)
            pass
        except (ValueError, KeyError, TypeError) as e:
            # Erreur de format de réponse
            pass

    return "Désolé, je n'ai pas pu obtenir de réponse. Veuillez réessayer plus tard."

def normalize_album_key(artist: str, album: str) -> str:
    """Crée une clé normalisée pour identifier un album de manière unique.
    
    Normalise l'artiste et l'album pour permettre la détection de doublons
    même si les formats diffèrent légèrement entre Discogs et Roon.
    
    Args:
        artist: Nom de l'artiste (peut être une liste ou une chaîne).
        album: Titre de l'album.
        
    Returns:
        Clé normalisée au format "artiste|||album" en minuscules.
        
    Examples:
        >>> normalize_album_key("Nina Simone", "Pastel Blues")
        'nina simone|||pastel blues'
        >>> normalize_album_key(["Miles Davis"], "Kind of Blue")
        'miles davis|||kind of blue'
        
    Note:
        - Gère les listes d'artistes (prend le premier)
        - Convertit en minuscules pour comparaison insensible à la casse
        - Supprime les espaces superflus
    """
    # Nettoyer l'artiste
    if isinstance(artist, list) and len(artist) > 0:
        artist = artist[0]
    elif not isinstance(artist, str):
        artist = 'Unknown'
    
    # Nettoyer et normaliser
    artist_clean = str(artist).lower().strip()
    album_clean = str(album).lower().strip()
    
    return f"{artist_clean}|||{album_clean}"

def nettoyer_nom_artiste(nom_artiste) -> str:
    """Nettoie et normalise un nom d'artiste.
    
    Traite les différents formats de noms d'artistes (liste, chaîne) et
    supprime les suffixes numériques ajoutés par Discogs.
    
    Args:
        nom_artiste: Nom d'artiste brut (peut être une liste, une chaîne ou autre).
        
    Returns:
        Nom d'artiste nettoyé et normalisé.
        
    Examples:
        >>> nettoyer_nom_artiste(['Nina Simone (5)', 'Other Artist'])
        'Nina Simone'
        >>> nettoyer_nom_artiste('Miles Davis (3)')
        'Miles Davis'
        >>> nettoyer_nom_artiste('Various')
        'Various'
        
    Note:
        - Si liste: prend le premier élément
        - Supprime les suffixes (nombre) de Discogs: "Artist (5)" → "Artist"
        - Gère les valeurs non-string en retournant 'Unknown'
    """
    if isinstance(nom_artiste, list) and len(nom_artiste) > 0:
        nom_artiste = nom_artiste[0]

        if nom_artiste == "Various" :
            nom_artiste == "Various artists"
            
    elif not isinstance(nom_artiste, str):
        nom_artiste = 'Unknown'
    return re.sub(r'\s*\(\d+\)$', '', nom_artiste)

def get_current_datetime_forFileName() -> str:
    """Génère un timestamp formaté pour noms de fichiers.
    
    Returns:
        Timestamp au format 'YYYYMMDD-HHMMSS' (ex: '20260121-095530').
        
    Examples:
        >>> timestamp = get_current_datetime_forFileName()
        >>> print(timestamp)
        '20260121-095530'
    """
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def poetic_date() -> str:
    """Génère une date au format poétique en anglais.
    
    Returns:
        Date formatée style "The 21 of January, 2026".
        
    Examples:
        >>> date = poetic_date()
        >>> print(date)
        'The 21 of January, 2026'
        
    Note:
        Utilisé pour l'en-tête des présentations iA Presenter.
    """
    today = datetime.now()
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month = month_names[today.month - 1]
    day = today.day
    year = today.year

    return f"The {day} of {month}, {year}"

def generate_haiku_from_artist_and_album(artist: str, album: str) -> str:
    """Génère une description courte d'un album via l'API EurIA.
    
    Utilise l'API EurIA pour générer une présentation concise (35 mots max)
    d'un album musical en français.
    
    Args:
        artist: Nom de l'artiste.
        album: Titre de l'album.
        
    Returns:
        Description courte de l'album en français (≤35 mots).
        
    Examples:
        >>> desc = generate_haiku_from_artist_and_album("Nina Simone", "Pastel Blues")
        >>> print(desc)
        'Pastel Blues capture Nina Simone dans toute sa puissance vocale...'
        
    Note:
        - Limite stricte de 35 mots
        - Réponse en français uniquement
        - Pas de questions ni commentaires ajoutés
    """
    artist_lower = artist.lower()
    album_lower = album.lower()

    prompt_for_euria = f"""
    Présente moi l'album {album_lower} de {artist_lower}. 
    N'ajoute pas de questions ou de commentaires. 
    Limite ta réponse à 35 mots maximum.
    Réponds uniquement en français.
    """    
    haiku_text = ask_for_ia(prompt_for_euria)
    return haiku_text.strip()

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Charger les variables d'environnement
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Vérifier les valeurs chargées
URL = os.getenv("URL")
BEARER = os.getenv("bearer")
MAX_ATTEMPTS = int(os.getenv("max_attempts", "5"))
DEFAULT_ERROR_MESSAGE = os.getenv("default_error_message", "Aucune information disponible")

# Charger le fichier JSON Discogs
with open(os.path.join(PROJECT_ROOT, "data", "collection", "discogs-collection.json"), 'r', encoding='utf-8') as f:
    data = json.load(f)

# Charger le fichier JSON Roon
with open(os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json"), 'r', encoding='utf-8') as f:
    roon_data = json.load(f)

# Sélectionner 10 albums aléatoires de Discogs
random_albums_discogs = secrets.SystemRandom().sample(data, 10)

# Créer un set des clés d'albums Discogs pour détecter les doublons
discogs_keys = set()
for album in random_albums_discogs:
    key = normalize_album_key(album.get('Artiste', ''), album.get('Titre', ''))
    discogs_keys.add(key)

print(f"[DEBUG] {len(random_albums_discogs)} albums sélectionnés depuis Discogs")
print(f"[DEBUG] Clés Discogs: {len(discogs_keys)} uniques")

# Extraire les albums uniques de Roon (artiste + album)
roon_albums_dict = {}
for track in roon_data['tracks']:
    artist = track.get('artist', 'Unknown')
    album = track.get('album', 'Unknown')
    key = f"{artist}|||{album}"  # Clé unique
    
    if key not in roon_albums_dict and artist != 'Inconnu' and album != 'Inconnu':
        roon_albums_dict[key] = {
            'Artiste': artist,
            'Titre': album,
            'Année': 0,  # Pas d'année dans chk-roon.json
            'Pochette': track.get('album_spotify_image') or track.get('album_lastfm_image', ''),
            'Support': 'Roon Play',
            'SpotifyURL': None,
            'release_id': '',
            'artist_image': track.get('artist_spotify_image', '')
        }

# Convertir en liste et filtrer les doublons avec Discogs
roon_albums_list = []
for album in roon_albums_dict.values():
    key = normalize_album_key(album.get('Artiste', ''), album.get('Titre', ''))
    if key not in discogs_keys:  # Exclure si déjà dans Discogs
        roon_albums_list.append(album)

print(f"[DEBUG] {len(roon_albums_list)} albums Roon uniques (après exclusion des doublons Discogs)")

# Sélectionner jusqu'à 10 albums de Roon (ou moins s'il n'y en a pas assez)
if len(roon_albums_list) >= 10:
    random_albums_roon = secrets.SystemRandom().sample(roon_albums_list, 10)
else:
    random_albums_roon = roon_albums_list
    print(f"[DEBUG] ⚠️  Seulement {len(roon_albums_list)} albums Roon disponibles (< 10)")

print(f"[DEBUG] {len(random_albums_roon)} albums sélectionnés depuis Roon")

# Combiner les deux listes (maintenant garanties sans doublons)
all_random_albums = random_albums_discogs + random_albums_roon
print(f"[DEBUG] ✅ Total: {len(all_random_albums)} albums uniques pour la génération")

# Générer les résultats
results = []
for album in all_random_albums:
    artist = nettoyer_nom_artiste(album.get('Artiste', 'Unknown'))
    
    title = album.get('Titre', 'Unknown')
    # On recalcule title en gardant seulement la partie avant la première parenthèse
    title = title.split('(')[0].strip()

    year = album.get('Année', 0)
    if isinstance(year, str) and year != '':
        year = int(year)
    elif not isinstance(year, int):
        year = 0
        
    cover = album.get('Pochette', '')
    support = album.get('Support', '')
    release_id = album.get('release_id', '')
    
    spotify_url = album.get('Spotify_URL', '')

    # Gérer Spotify_Date de manière sécurisée
    spotify_date_value = album.get('Spotify_Date', None)
    if spotify_date_value is not None and spotify_date_value != '':
        try:
            spotify_date = int(spotify_date_value)
        except (ValueError, TypeError):
            spotify_date = 0
    else:
        spotify_date = 0
        
    spotify_cover_url = album.get('Spotify_Cover_URL', '')

    # Générer le haïku
    haiku = decouper_en_lignes (generate_haiku_from_artist_and_album(artist, title))

    reissue_year = 0
    if spotify_url and spotify_date > 0 and year > 0:
        reissue_year = year

        if spotify_date < year:
            year = spotify_date

    if spotify_cover_url:
        cover = spotify_cover_url
    
    results.append({
        'Artiste': artist,
        'Titre': title,
        'Année': year,
        'Reissue': reissue_year,
        'Pochette': cover,
        'Support': support,
        'SpotifyURL': spotify_url,
        'release_id': release_id,
        'Haiku': haiku
    })

# Nom du fichier de sortie
fichier_sortie = os.path.join(PROJECT_ROOT, "output", "haikus", f"generate-haiku-{get_current_datetime_forFileName()}.txt")

# Ouvrir le fichier en mode écriture
with open(fichier_sortie, 'w', encoding='utf-8') as f:

    # Écrire la 1ère page
    f.write(f"# Album Haïku\n")
    f.write(f"#### {poetic_date()}\n")
    f.write(f"\t\t{len(random_albums_discogs)} albums from Discogs collection\n")
    f.write(f"\t\t{len(random_albums_roon)} albums from Roon listening history\n")
    f.write(f"\t\tRandom discs spin,\n")
    f.write(f"\t\twhispers of vinyl dreams rise\n")
    f.write(f"\t\teyes wide, heart adrift\n")
    f.write("---\n")
    
    # Écrire les résultats dans le fichier
  # Dans la boucle principale :
    for album in results:

        release_id = album.get('release_id', 0) 
        artist = nettoyer_nom_artiste(album.get('Artiste', 'Unknown'))
        title = album.get('Titre', '')
        year = album.get('Année', 0)
        reissue_year = album.get('Reissue', 0)
        spotify_url = album.get('SpotifyURL', None)
        cover = album.get('Pochette', '')
        support = album.get('Support', '')
        haiku = album.get('Haiku', '')

        if title:
            print(f"{artist}")
            print(f"{title} ({year})")
            
            if spotify_url:
                print(f"{spotify_url}")
                
            print(f"{haiku}")
            print("---\n")

            if len(artist) < 30:
                f.write(f"# {artist}\n")
            else:
                f.write(f"#### {artist}\n")

            if year > 0:
                f.write(f"#### {title} ({year})")
            else:
                f.write(f"#### {title}")

            if year < reissue_year:
                f.write(f" - Reissue {reissue_year}")

            f.write(f"\n")

            if spotify_url:
                f.write(f"\t###### 🎧 [Listen with Spotify]({spotify_url})  👥 [Read on Discogs](https://www.discogs.com/release/{release_id})\n")
            elif release_id:
                f.write(f"\t###### 👥 [Read on Discogs](https://www.discogs.com/release/{release_id})\n")
            else:
                f.write(f"\t###### 🎧 From Roon listening history\n")

            f.write(f"\t###### 💿 {support}\n")

            f.write(f"{haiku}\n\n")
            f.write(f"<img src='{cover}' />\n")
            f.write("---\n")
            
    # Écrire la dernière page
    f.write("\t\tPython generated with love, for iA Presenter using Euria AI from Infomaniak")
		
print(f"Les résultats ont été enregistrés dans {fichier_sortie}.")

