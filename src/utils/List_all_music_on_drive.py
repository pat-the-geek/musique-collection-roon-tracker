import os
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import csv
from dotenv import load_dotenv

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Charger les variables d'environnement
load_dotenv(os.path.join(PROJECT_ROOT, "data", "config", ".env"))

# Chemin vers la bibliothèque musicale (depuis .env)
music_dir = os.getenv("MUSIC_LIBRARY_PATH", "/Volumes/USB2/Biliotheque-Musicale-Sonos")

# Fichier de sortie
output_file = os.path.join(PROJECT_ROOT, "data", "exports", "list_all_music.csv")

def get_metadata(file_path):
    """Extrait les métadonnées d'un fichier audio."""
    if file_path.endswith('.flac'):
        audio = FLAC(file_path)
        title = audio.get('title', [""])[0]
        artist = audio.get('artist', [""])[0]
        album = audio.get('album', [""])[0]
        genre = audio.get('genre', [""])[0]
        return title, artist, album, genre
    elif file_path.endswith('.mp3'):
        audio = MP3(file_path, ID3=ID3)
        title = audio.get('TIT2', [""])[0]
        artist = audio.get('TPE1', [""])[0]
        album = audio.get('TALB', [""])[0]
        genre = audio.get('TCON', [""])[0]
        return title, artist, album, genre
    else:
        return "", "", "", ""

def list_music(directory, output_file):
    """Parcourt les dossiers et génère un CSV avec la liste des morceaux."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Chemin", "Titre", "Artiste", "Album", "Genre"])
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.flac', '.mp3')):
                    file_path = os.path.join(root, file)
                    title, artist, album, genre = get_metadata(file_path)
                    writer.writerow([file_path, title, artist, album, genre])

if __name__ == "__main__":
    list_music(music_dir, output_file)
    print(f"Liste générée dans {output_file}")
