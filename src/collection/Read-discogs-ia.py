#!/usr/bin/env python3
"""Script de synchronisation et enrichissement de collection musicale Discogs.

Ce module récupère automatiquement la collection musicale d'un utilisateur Discogs,
l'enrichit avec des métadonnées Spotify (URLs, dates de réédition, pochettes) et
génère des résumés détaillés via l'API EurIA (Qwen3). Il produit également un fichier
Markdown formaté pour visualisation.

Fonctionnalités principales:
    - Récupération complète de la collection Discogs via API
    - Enrichissement avec données Spotify (URLs, images, dates)
    - Génération automatique de résumés d'albums via IA (EurIA/Qwen3)
    - Export Markdown avec images et liens
    - Détection de doublons pour éviter les réimports
    - Normalisation des formats de support (Vinyle/CD)

Dépendances:
    - requests: Client HTTP pour appels API
    - python-dotenv: Chargement variables d'environnement
    - typing: Annotations de types

Configuration requise (.env):
    DISCOGS_API_KEY: Clé API Discogs
    DISCOGS_USERNAME: Nom d'utilisateur Discogs
    SPOTIFY_CLIENT_ID: ID client Spotify
    SPOTIFY_CLIENT_SECRET: Secret client Spotify
    URL: URL API EurIA
    bearer: Token d'authentification EurIA
    max_attempts: Nombre de tentatives max (défaut: 5)
    default_error_message: Message d'erreur par défaut

Fichiers générés:
    - discogs-collection.json: Collection complète avec métadonnées
    - discogs-collection.md: Export Markdown formaté

Exemple d'utilisation:
    $ python3 Read-discogs-ia.py
    # Synchronise la collection et génère les fichiers

Auteur: Patrick Ostertag
Date: 21 janvier 2026
Version: 1.0
"""

# pip3 install requests
import os
import requests
import time
import json
import base64
import re
from typing import Tuple, Optional, List
from dotenv import load_dotenv

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
DISCOGS_API_KEY = os.getenv("DISCOGS_API_KEY")
DISCOGS_USERNAME = os.getenv("DISCOGS_USERNAME")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def nettoyer_nom_artiste(nom_artiste: str) -> str:
    """Nettoie un nom d'artiste en supprimant les suffixes numériques Discogs.
    
    Discogs ajoute parfois des suffixes numériques pour différencier les homonymes,
    par exemple "Miles Davis (2)". Cette fonction supprime ces suffixes.
    
    Args:
        nom_artiste: Nom de l'artiste brut, potentiellement avec suffixe.
        
    Returns:
        Nom de l'artiste nettoyé sans suffixe numérique.
        
    Examples:
        >>> nettoyer_nom_artiste("Miles Davis (2)")
        'Miles Davis'
        >>> nettoyer_nom_artiste("Nina Simone")
        'Nina Simone'
    """
    # Utilise une expression régulière pour supprimer le motif "(chiffre)" à la fin de la chaîne
    return re.sub(r'\s*\(\d+\)$', '', nom_artiste)

# Identifiants Spotify
def get_spotify_access_token() -> Optional[str]:
    """Récupère un token d'accès Spotify via OAuth 2.0 Client Credentials Flow.
    
    Utilise les credentials SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET
    pour obtenir un token d'accès via l'API Spotify. Le token est nécessaire
    pour effectuer des recherches d'albums et récupérer les métadonnées.
    
    Returns:
        Token d'accès Spotify (string) si succès, None en cas d'échec.
        
    Raises:
        Aucune - Les exceptions sont capturées et None est retourné.
        
    Note:
        - Nécessite SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET dans .env
        - Le token expire après 1 heure (géré par Spotify)
        - Affiche les erreurs sur stdout en cas de problème
        
    Examples:
        >>> token = get_spotify_access_token()
        >>> if token:
        ...     print("Token obtenu avec succès")
    """
    url = 'https://accounts.spotify.com/api/token'
    headers = {}
    data = {'grant_type': "client_credentials"}
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
    headers['Authorization'] = "Basic " + auth_base64
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        response_data = response.json()
        if 'access_token' not in response_data:
            print("Erreur : La réponse ne contient pas 'access_token'.")
            print("Réponse complète :", response_data)
            return None
        return response_data['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Réponse d'erreur :", e.response.text)
        return None

def spotify_search_album(
    artist: str,
    album: str,
    access_token: str,
    max_retries: int = 5,
    retry_delay: float = 1.0
) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Recherche un album sur Spotify et retourne ses métadonnées.
    
    Effectue une recherche d'album sur Spotify avec validation de l'artiste,
    gestion des retries et fallback. Retourne l'URL Spotify, l'année de sortie
    et l'URL de la pochette.
    
    Args:
        artist: Nom de l'artiste à rechercher.
        album: Titre de l'album à rechercher.
        access_token: Token d'accès Spotify valide.
        max_retries: Nombre maximum de tentatives en cas d'échec (défaut: 5).
        retry_delay: Délai en secondes entre les tentatives (défaut: 1.0).
        
    Returns:
        Tuple de 3 éléments:
            - URL Spotify de l'album (str ou None)
            - Année de sortie (int ou None)
            - URL de la pochette (str ou None)
        Retourne (None, None, None) si aucun résultat trouvé.
        
    Note:
        - Effectue d'abord une recherche avec artiste + album
        - Fallback sur recherche album seul si échec
        - Valide que l'artiste correspond (sauf "Various Artists")
        - Gère automatiquement les retries en cas d'erreur réseau
        
    Examples:
        >>> token = get_spotify_access_token()
        >>> url, year, cover = spotify_search_album("Miles Davis", "Kind of Blue", token)
        >>> print(f"Album trouvé: {url}, année {year}")
    """
    if not access_token:
        print("Erreur : Impossible de rechercher sans jeton d'accès.")
        return None, None, None
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}

    def _search(query: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        search_url = f"{url}?{query}"
        for attempt in range(max_retries):
            try:
                response = requests.get(search_url, headers=headers)
                response.raise_for_status()
                response_data = response.json()
                albums = response_data.get('albums', {}).get('items', [])
                if albums:
                    album_data = albums[0]
                    album_artists = album_data.get('artists', [])
                    
                    if not album_artists :
                        print(f"Erreur : L'artiste de l'album trouvé ({album_artists[0]['name']}) ne correspond pas à {artist}.")
                        return None, None, None
                    
                    if album_artists[0]['name'].lower() != artist.lower():
                         
                        if artist.lower().startswith("various"):
                            pass
                        else:
                            print(f"Erreur : L'artiste de l'album trouvé ({album_artists[0]['name']}) ne correspond pas à {artist}.")
                            return None, None, None

                    album_url = album_data['external_urls']['spotify']
                    album_date = album_data.get('release_date', '')
                    
                    if not album_date:
                        print("Erreur : Date de sortie non disponible.")
                        return None, None, None
                    try:
                        album_annee = int(album_date.split('-')[0])
                    except (ValueError, IndexError):
                        print(f"Erreur : Format de date invalide pour {album_date}.")
                        return None, None, None
                    images = album_data.get('images', [])
                    spotify_cover_url = images[0]['url'] if images else None
                    return album_url, album_annee, spotify_cover_url
                return None, None, None
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Tentative {attempt + 1}/{max_retries} échouée. Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"Erreur lors de la recherche (tentative {attempt + 1}/{max_retries}) : {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print("Réponse d'erreur :", e.response.text)
                    return None, None, None
            except (KeyError, IndexError, ValueError) as e:
                print(f"Erreur de traitement des données : {e}")
                return None, None, None

    query = f"q=artist:{artist}%20album:{album}&type=album&limit=1"
    result = _search(query)
    if result[0] is not None:
        return result
    print(f"Aucun résultat trouvé pour {artist} - {album}. Recherche uniquement sur le nom de l'album...")
    query = f"q=album:{album}&type=album&limit=1"
    return _search(query)

def generate_markdown_from_json(json_path: str = None, output_md_path: str = None) -> bool:
    """Génère un fichier Markdown formaté depuis la collection JSON.
    
    Lit le fichier JSON de la collection, trie les albums par artiste et année,
    puis génère un fichier Markdown structuré avec images, liens et métadonnées.
    
    Args:
        json_path: Chemin du fichier JSON source (défaut: 'discogs-collection.json').
        output_md_path: Chemin du fichier Markdown de sortie (défaut: 'discogs-collection.md').
        
    Returns:
        True si le fichier a été généré avec succès, False en cas d'erreur.
        
    Format de sortie:
        - Albums groupés par artiste (titres de niveau 1)
        - Chaque album en sous-section (niveau 2)
        - Métadonnées: année, labels, support, résumé
        - Images: priorité à Spotify, fallback sur Discogs
        - Liens Spotify si disponibles
        
    Raises:
        Aucune - Les erreurs sont capturées et affichées.
        
    Examples:
        >>> success = generate_markdown_from_json()
        >>> if success:
        ...     print("Fichier Markdown généré")
    """
    if json_path is None:
        json_path = os.path.join(PROJECT_ROOT, "data", "collection", "discogs-collection.json")
    if output_md_path is None:
        output_md_path = os.path.join(PROJECT_ROOT, "data", "exports", "discogs-collection.md")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {json_path} n'existe pas.")
        return False
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier {json_path} n'est pas un JSON valide.")
        return False
    except Exception as e:
        print(f"Erreur inattendue lors de la lecture du fichier JSON : {e}")
        return False

    try:
        albums_sorted = sorted(
            data,
            key=lambda x: (
                x['Artiste'][0] if isinstance(x['Artiste'], list) else x['Artiste'],
                x['Année']
            )
        )
    except KeyError as e:
        print(f"Erreur : Clé manquante dans le JSON : {e}")
        return False

    markdown_content = ""
    current_artist = None
    for album in albums_sorted:
        try:
            artist_name = album['Artiste'][0] if isinstance(album['Artiste'], list) else album['Artiste']
            if artist_name != current_artist:
                if current_artist is not None:
                    markdown_content += "\n---\n\n"
                markdown_content += f"# {artist_name}\n\n"
                current_artist = artist_name
            markdown_content += f"## {album['Titre']}\n\n"
            markdown_content += f"**Artiste:** {artist_name}\n"

            if album['Spotify_Date'] != None :
                markdown_content += f"- **Année:** {album['Spotify_Date']}\n"
            else :
                markdown_content += f"- **Année:** {album['Année']}\n"

            markdown_content += f"- **Labels:** {', '.join(album['Labels'])}\n"
            markdown_content += f"- **Support:** {album['Support']}\n"
            markdown_content += f"- **Résumé:** {album['Resume']}\n"

            if album['Spotify_URL'] != None :
                markdown_content += f"\n**Spotify:** [Lien]({album['Spotify_URL']})\n\n"

            ## ajoute le code pour choisir l'image spotify si not null Spotify_Cover_URL
            if album['Spotify_Cover_URL'] != None :
                markdown_content += f'<img src="{album["Spotify_Cover_URL"]}" style="display:block; margin:auto; max-width:100%;" />\n\n'
            else :
                markdown_content += f'<img src="{album["Pochette"]}" style="display:block; margin:auto; max-width:100%;" />\n\n'

            markdown_content += "===\n\n"
        except KeyError as e:
            print(f"Erreur : Clé manquante dans un album : {e}")
            continue

    try:
        with open(output_md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        print(f"Fichier Markdown généré avec succès : {os.path.abspath(output_md_path)}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier Markdown : {e}")
        return False

def lire_albums(fichier: str = None) -> List[dict]:
    """Charge la collection d'albums depuis un fichier JSON.
    
    Args:
        fichier: Chemin du fichier JSON à lire (défaut: 'discogs-collection.json').
        
    Returns:
        Liste de dictionnaires représentant les albums.
        Liste vide si le fichier n'existe pas ou est invalide.
        
    Raises:
        Aucune - Les erreurs sont capturées et affichées.
        
    Examples:
        >>> albums = lire_albums()
        >>> print(f"{len(albums)} albums chargés")
    """
    if fichier is None:
        fichier = os.path.join(PROJECT_ROOT, "data", "collection", "discogs-collection.json")
    if not os.path.exists(fichier):
        return []
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            albums = json.load(f)
            if not isinstance(albums, list):
                raise ValueError("Le fichier JSON doit contenir une liste d'albums.")
            return albums
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier {fichier} est malformé ou non valide.")
        return []
    except PermissionError:
        print(f"Erreur : Permission refusée pour lire le fichier {fichier}.")
        return []
    except Exception as e:
        print(f"Erreur inattendue lors de la lecture du fichier : {e}")
        return []

def album_existe(albums: List[dict], release_id: int) -> bool:
    """Vérifie si un album existe déjà dans la collection.
    
    Args:
        albums: Liste des albums existants.
        release_id: ID Discogs de l'album à vérifier.
        
    Returns:
        True si l'album existe déjà, False sinon.
        
    Examples:
        >>> albums = lire_albums()
        >>> if album_existe(albums, 123456):
        ...     print("Album déjà présent")
    """
    return any(str(album.get('release_id')) == str(release_id) for album in albums)

def ajouter_album(
    release_id: int,
    titre: str,
    artiste: List[str],
    annee: int,
    labels: List[str],
    support: str,
    pochette: str,
    resume: str,
    spotify_url: Optional[str] = None,
    spotify_date: Optional[int] = None,
    spotify_cover_url: Optional[str] = None,
    fichier: str = None
) -> bool:
    """Ajoute un nouvel album à la collection JSON.
    
    Vérifie d'abord si l'album existe déjà (via release_id), puis l'ajoute
    au fichier JSON avec toutes ses métadonnées.
    
    Args:
        release_id: ID unique Discogs de l'album.
        titre: Titre de l'album.
        artiste: Liste des noms d'artistes.
        annee: Année de sortie originale.
        labels: Liste des labels.
        support: Type de support ("Vinyle", "CD", etc.).
        pochette: URL de la pochette Discogs.
        resume: Résumé détaillé de l'album.
        spotify_url: URL Spotify (optionnel).
        spotify_date: Année de réédition Spotify (optionnel).
        spotify_cover_url: URL pochette Spotify (optionnel).
        fichier: Chemin du fichier JSON (défaut: 'discogs-collection.json').
        
    Returns:
        True si l'album a été ajouté avec succès, False sinon
        (déjà existant ou erreur d'écriture).
        
    Examples:
        >>> success = ajouter_album(
        ...     release_id=123456,
        ...     titre="Kind of Blue",
        ...     artiste=["Miles Davis"],
        ...     annee=1959,
        ...     labels=["Columbia"],
        ...     support="Vinyle",
        ...     pochette="https://...",
        ...     resume="Album emblématique..."
        ... )
    """
    if fichier is None:
        fichier = os.path.join(PROJECT_ROOT, "data", "collection", "discogs-collection.json")
    albums = lire_albums(fichier)
    if album_existe(albums, release_id):
        print(f"L'album avec l'ID {release_id} existe déjà. Aucun ajout effectué.")
        return False
    nouvel_album = {
        "release_id": release_id,
        "Titre": titre,
        "Artiste": artiste,
        "Année": annee,
        "Labels": labels,
        "Support": support,
        "Pochette": pochette,
        "Resume": resume,
        "Spotify_URL": spotify_url,
        "Spotify_Date": spotify_date,
        "Spotify_Cover_URL": spotify_cover_url
    }
    albums.append(nouvel_album)
    try:
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(albums, f, indent=4, ensure_ascii=False)
        print(f"L'album '{titre}' a été ajouté avec succès.")
        return True
    except PermissionError:
        print(f"Erreur : Permission refusée pour écrire dans le fichier {fichier}.")
        return False
    except Exception as e:
        print(f"Erreur inattendue lors de l'écriture du fichier : {e}")
        return False
    
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

def askForResume(artist: str, album: str, annee: int) -> str:
    """Génère un résumé détaillé d'un album via l'API EurIA.
    
    Construit un prompt structuré et interroge l'API EurIA (Qwen3) avec
    recherche web activée pour obtenir un résumé de 30 lignes maximum.
    
    Args:
        artist: Nom de l'artiste.
        album: Titre de l'album.
        annee: Année de sortie.
        
    Returns:
        Résumé détaillé de l'album (30 lignes max) ou message d'erreur
        si la génération échoue.
        
    Note:
        Le résumé couvre:
        - Contexte de création
        - Démarche artistique
        - Réactions critiques
        - Éléments sonores marquants
        
    Examples:
        >>> resume = askForResume("Miles Davis", "Kind of Blue", 1959)
        >>> print(resume[:50])
    """

    prompt_for_ia = f"""
        Résume en 30 lignes maximum l’album {album} de {artist} ({annee}), en mettant l’accent sur :
        - Le contexte de création (collaboration, événement spécial, anniversaire de l’album original).
        - La démarche artistique de {artist} (déconstruction, réinterprétation, atmosphère, touches modernes).
        - Les réactions critiques (accueil, comparaison avec l’original, points forts).
        - Les éléments sonores marquants (beats, textures, voix, ambiance).
        Utilise un ton objectif et synthétique, sans commentaire personnel.
        Présente le texte avec des paragraphes avec sous-titre.
        Si l’album est un remix ou une réinterprétation, précise-le clairement.
        Ne réponds que par le résumé, sans ajout ni commentaire.
        Si tu ne trouves pas d'informations, Résume l'album {album} ({annee}) en 30 lignes maximum.
        """
    return (ask_for_ia(prompt_for_ia))

def get_collection(username: str, api_key: str, page: int = 1) -> Optional[dict]:
    """Récupère une page de la collection Discogs d'un utilisateur.
    
    Args:
        username: Nom d'utilisateur Discogs.
        api_key: Clé API Discogs.
        page: Numéro de page à récupérer (défaut: 1).
        
    Returns:
        Dictionnaire contenant les données de la page, ou None si erreur.
        
    Note:
        - Récupère 100 albums par page maximum
        - Nécessite authentification via clé API
        
    Examples:
        >>> data = get_collection("username", "api_key", page=1)
        >>> if data:
        ...     print(f"{len(data['releases'])} albums sur cette page")
    """
    url = f"https://api.discogs.com/users/{username}/collection/folders/0/releases?page={page}&per_page=100"
    headers = {
        "Authorization": f"Discogs key={api_key}",
        "User-Agent": "YourAppName/1.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code} lors de la récupération de la collection.")
        return None

def get_release_details(release_id: int, api_key: str) -> Optional[dict]:
    """Récupère les détails complets d'une release Discogs.
    
    Args:
        release_id: ID Discogs de la release.
        api_key: Clé API Discogs.
        
    Returns:
        Dictionnaire contenant les détails complets, ou None si erreur.
        
    Note:
        - Gère automatiquement le rate limiting (HTTP 429)
        - Attend 10 secondes et réessaye si limite atteinte
        - Inclut les images, tracklist, crédits, etc.
        
    Examples:
        >>> details = get_release_details(123456, "api_key")
        >>> if details:
        ...     print(details.get('title'))
    """
    url = f"https://api.discogs.com/releases/{release_id}"
    headers = {
        "Authorization": f"Discogs key={api_key}",
        "User-Agent": "YourAppName/1.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Limite de taux atteinte. Attente avant nouvelle tentative...")
        time.sleep(10)
        return get_release_details(release_id, api_key)
    else:
        print(f"Erreur {response.status_code} pour l'ID {release_id}")
        return None

def get_all_releases(username: str, api_key: str) -> List[dict]:
    """Récupère l'intégralité de la collection Discogs d'un utilisateur.
    
    Parcourt toutes les pages de la collection jusqu'à épuisement.
    Ajoute un délai de 1 seconde entre chaque page pour respecter
    les limites de taux de l'API Discogs.
    
    Args:
        username: Nom d'utilisateur Discogs.
        api_key: Clé API Discogs.
        
    Returns:
        Liste complète de tous les albums de la collection.
        
    Note:
        - Peut prendre plusieurs minutes pour les grandes collections
        - Affiche la progression dans la fonction appelante
        - Respecte le rate limiting avec sleep(1) entre pages
        
    Examples:
        >>> releases = get_all_releases("username", "api_key")
        >>> print(f"Collection totale: {len(releases)} albums")
    """
    page = 1
    all_releases = []
    while True:
        collection = get_collection(username, api_key, page)
        if not collection:
            break
        releases = collection['releases']
        if not releases:
            break
        all_releases.extend(releases)
        page += 1
        time.sleep(1)
    return all_releases

def support_from_basic_info(basic_info: dict) -> str:
    """Extrait et normalise le type de support depuis les infos de base Discogs.
    
    Convertit les formats Discogs en formats normalisés (Vinyle/CD) et
    ajoute la quantité si multiple.
    
    Args:
        basic_info: Dictionnaire des informations de base d'une release Discogs.
        
    Returns:
        Type de support normalisé ("Vinyle", "CD", "Vinyle (x2)", etc.)
        ou "Inconnu" si format non disponible.
        
    Note:
        - "Vinyl" → "Vinyle"
        - "CD" → "CD"
        - Autres formats conservés tels quels
        - Ajoute "(xN)" si quantité > 1
        
    Examples:
        >>> info = {'formats': [{'name': 'Vinyl', 'qty': 2}]}
        >>> print(support_from_basic_info(info))
        'Vinyle (x2)'
    """
    formats = basic_info.get('formats', [])
    if not formats:
        return "Inconnu"
    fmt = formats[0]
    name = (fmt.get('name') or "").strip()
    mapping = {"Vinyl": "Vinyle", "CD": "CD"}
    support = mapping.get(name, name if name else "Inconnu")
    qty = fmt.get('qty')
    if isinstance(qty, int) and qty > 1:
        support = f"{support} (x{qty})"
    return support

def main():
    """Fonction principale de synchronisation de la collection Discogs.
    
    Orchestre le processus complet:
    1. Récupération de la collection Discogs complète
    2. Chargement de la collection locale existante
    3. Pour chaque album non présent localement:
       - Récupération des détails Discogs
       - Recherche des métadonnées Spotify
       - Génération du résumé via IA
       - Ajout à la collection locale
    4. Génération du fichier Markdown final
    
    Note:
        - Affiche la progression en temps réel
        - Saute les albums déjà présents
        - Peut prendre plusieurs heures pour les grandes collections
        - Respecte les limites de taux des APIs
        
    Raises:
        Aucune - Les erreurs sont capturées et affichées.
    """

    all_releases = get_all_releases(DISCOGS_USERNAME, DISCOGS_API_KEY)
    albums = lire_albums()
    if not all_releases:
        print("Aucun album trouvé.")
        return
    access_token = get_spotify_access_token()
    nombre_albums = len(all_releases)
    print(f"Nombre d'albums dans la collection : {nombre_albums}")
    nbre_item = 0
    for release in all_releases:
        basic_info = release['basic_information']
        release_id = basic_info['id']
        support = support_from_basic_info(basic_info)
        if album_existe(albums, release_id):
            print(f"L'album {release_id} existe déjà. Passage au suivant.")
            nbre_item += 1
            print(f"{nbre_item}/{nombre_albums} albums traités ({round(nbre_item/nombre_albums*100, 1)}%)")
            print("-" * 40)
            continue
        release_details = get_release_details(release_id, DISCOGS_API_KEY)
        cover_image = release_details.get('images', [{}])[0].get('uri', 'Aucune image disponible') if release_details else 'Aucune image disponible'
        album_resume = askForResume(
            ', '.join(artist['name'] for artist in basic_info['artists']),
            basic_info['title'],
            basic_info['year']
        )
        artist_name = [nettoyer_nom_artiste(artist['name']) for artist in basic_info['artists']]
        spotify_url, spotify_date, spotify_cover_url = spotify_search_album(artist_name[0], basic_info['title'], access_token)
        ajouter_album(
            release_id=release_id,
            titre=basic_info['title'],
            artiste=artist_name,
            annee=basic_info['year'],
            labels=[label['name'] for label in basic_info['labels']],
            support=support,
            pochette=cover_image,
            resume=album_resume,
            spotify_url=spotify_url,
            spotify_date=spotify_date,
            spotify_cover_url=spotify_cover_url
        )
        nbre_item += 1
        print(f"{nbre_item}/{nombre_albums} albums traités ({round(nbre_item/nombre_albums*100, 1)}%)")
        print("-" * 40)
    generate_markdown_from_json()

if __name__ == "__main__":
    main()
