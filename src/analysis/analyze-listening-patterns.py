#!/usr/bin/env python3
"""
Script d'analyse des patterns d'écoute dans chk-roon.json
Détecte les sessions, albums complets, corrélations et transitions.

Auteur: Patrick Ostertag
Date: 20 janvier 2026
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

# Déterminer le répertoire racine du projet (2 niveaux au-dessus de ce script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def load_tracks() -> List[Dict]:
    """Charge les pistes depuis chk-roon.json."""
    with open(os.path.join(PROJECT_ROOT, "data", "history", "chk-roon.json"), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['tracks']

def detect_listening_sessions(tracks: List[Dict], gap_minutes: int = 30) -> List[List[Dict]]:
    """
    Détecte les sessions d'écoute continues.
    Une session se termine si le gap entre deux pistes dépasse gap_minutes.
    """
    if not tracks:
        return []
    
    # Trier par timestamp (du plus ancien au plus récent)
    sorted_tracks = sorted(tracks, key=lambda t: t['timestamp'])
    
    sessions = []
    current_session = [sorted_tracks[0]]
    
    for i in range(1, len(sorted_tracks)):
        prev_time = sorted_tracks[i-1]['timestamp']
        curr_time = sorted_tracks[i]['timestamp']
        
        # Calculer le gap en minutes
        gap = (curr_time - prev_time) / 60
        
        if gap <= gap_minutes:
            # Même session
            current_session.append(sorted_tracks[i])
        else:
            # Nouvelle session
            sessions.append(current_session)
            current_session = [sorted_tracks[i]]
    
    # Ajouter la dernière session
    if current_session:
        sessions.append(current_session)
    
    return sessions

def estimate_session_duration(session: List[Dict], avg_track_duration: int = 4) -> int:
    """
    Estime la durée d'une session en minutes.
    avg_track_duration: durée moyenne d'une piste en minutes (défaut: 4 min)
    """
    if not session:
        return 0
    
    # Durée = nombre de pistes × durée moyenne
    return len(session) * avg_track_duration

def detect_complete_albums(tracks: List[Dict], min_tracks: int = 5) -> Dict[str, int]:
    """
    Détecte les albums potentiellement écoutés en entier.
    Un album est considéré "complet" s'il a au moins min_tracks écoutes.
    """
    album_plays = Counter()
    
    for track in tracks:
        album_key = f"{track['artist']} - {track['album']}"
        album_plays[album_key] += 1
    
    # Filtrer les albums avec au moins min_tracks
    complete_albums = {album: count for album, count in album_plays.items() 
                      if count >= min_tracks}
    
    return dict(sorted(complete_albums.items(), key=lambda x: x[1], reverse=True))

def analyze_artist_correlations(tracks: List[Dict]) -> Dict[str, List[Tuple[str, int]]]:
    """
    Analyse les corrélations entre artistes.
    Retourne pour chaque artiste, les artistes souvent écoutés dans la même session.
    """
    sessions = detect_listening_sessions(tracks)
    
    # Dictionnaire: artiste -> {autre_artiste: count}
    correlations = defaultdict(lambda: defaultdict(int))
    
    for session in sessions:
        # Récupérer tous les artistes uniques de cette session
        session_artists = list(set(t['artist'] for t in session))
        
        # Pour chaque paire d'artistes dans la session
        for i, artist1 in enumerate(session_artists):
            for artist2 in session_artists[i+1:]:
                correlations[artist1][artist2] += 1
                correlations[artist2][artist1] += 1
    
    # Convertir en liste triée par fréquence
    result = {}
    for artist, related in correlations.items():
        result[artist] = sorted(related.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return result

def analyze_transitions(tracks: List[Dict]) -> Dict[str, List[Tuple[str, int]]]:
    """
    Analyse les transitions fréquentes entre artistes.
    Retourne pour chaque artiste, les artistes écoutés juste après.
    """
    # Trier par timestamp
    sorted_tracks = sorted(tracks, key=lambda t: t['timestamp'])
    
    # Dictionnaire: artiste -> {artiste_suivant: count}
    transitions = defaultdict(lambda: defaultdict(int))
    
    for i in range(len(sorted_tracks) - 1):
        current_artist = sorted_tracks[i]['artist']
        next_artist = sorted_tracks[i+1]['artist']
        
        # Ne compter que si l'artiste change
        if current_artist != next_artist:
            transitions[current_artist][next_artist] += 1
    
    # Convertir en liste triée par fréquence
    result = {}
    for artist, nexts in transitions.items():
        result[artist] = sorted(nexts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return result

def analyze_time_patterns(tracks: List[Dict]) -> Dict[str, any]:
    """Analyse les patterns temporels d'écoute."""
    hours = []
    days = []
    
    for track in tracks:
        dt = datetime.fromtimestamp(track['timestamp'])
        hours.append(dt.hour)
        days.append(dt.strftime('%A'))
    
    hour_distribution = Counter(hours)
    day_distribution = Counter(days)
    
    return {
        'peak_hour': hour_distribution.most_common(1)[0] if hour_distribution else None,
        'hour_distribution': dict(sorted(hour_distribution.items())),
        'peak_day': day_distribution.most_common(1)[0] if day_distribution else None,
        'day_distribution': day_distribution
    }

def generate_report(tracks: List[Dict]) -> str:
    """Génère un rapport complet d'analyse des patterns."""
    report = []
    report.append("=" * 80)
    report.append("📊 ANALYSE DES PATTERNS D'ÉCOUTE")
    report.append("=" * 80)
    report.append("")
    
    # 1. Sessions d'écoute
    report.append("🎵 SESSIONS D'ÉCOUTE")
    report.append("-" * 80)
    sessions = detect_listening_sessions(tracks)
    report.append(f"Nombre total de sessions : {len(sessions)}")
    report.append(f"Sessions de plus de 10 pistes : {sum(1 for s in sessions if len(s) >= 10)}")
    
    # Top 5 plus longues sessions
    sorted_sessions = sorted(sessions, key=len, reverse=True)[:5]
    report.append("\nTop 5 sessions les plus longues :")
    for i, session in enumerate(sorted_sessions, 1):
        duration = estimate_session_duration(session)
        start_time = datetime.fromtimestamp(session[0]['timestamp']).strftime('%Y-%m-%d %H:%M')
        report.append(f"  {i}. {len(session)} pistes (~{duration} min) - Début: {start_time}")
        # Afficher les 3 premiers artistes de la session
        artists = [t['artist'] for t in session[:3]]
        report.append(f"     Artistes: {', '.join(set(artists))[:70]}...")
    
    report.append("")
    
    # 2. Albums complets
    report.append("💿 ALBUMS ÉCOUTÉS EN ENTIER (5+ pistes)")
    report.append("-" * 80)
    complete_albums = detect_complete_albums(tracks)
    if complete_albums:
        for i, (album, count) in enumerate(list(complete_albums.items())[:10], 1):
            report.append(f"  {i}. {album} - {count} pistes")
    else:
        report.append("  Aucun album complet détecté")
    
    report.append("")
    
    # 3. Patterns temporels
    report.append("⏰ PATTERNS TEMPORELS")
    report.append("-" * 80)
    time_patterns = analyze_time_patterns(tracks)
    
    if time_patterns['peak_hour']:
        peak_hour, count = time_patterns['peak_hour']
        report.append(f"Heure préférée : {peak_hour}h ({count} écoutes)")
    
    if time_patterns['peak_day']:
        peak_day, count = time_patterns['peak_day']
        report.append(f"Jour préféré : {peak_day} ({count} écoutes)")
    
    report.append("\nDistribution par tranche horaire :")
    hour_dist = time_patterns['hour_distribution']
    
    # Regrouper par tranches de 3 heures
    tranches = {
        '0h-3h': sum(hour_dist.get(h, 0) for h in range(0, 3)),
        '3h-6h': sum(hour_dist.get(h, 0) for h in range(3, 6)),
        '6h-9h': sum(hour_dist.get(h, 0) for h in range(6, 9)),
        '9h-12h': sum(hour_dist.get(h, 0) for h in range(9, 12)),
        '12h-15h': sum(hour_dist.get(h, 0) for h in range(12, 15)),
        '15h-18h': sum(hour_dist.get(h, 0) for h in range(15, 18)),
        '18h-21h': sum(hour_dist.get(h, 0) for h in range(18, 21)),
        '21h-0h': sum(hour_dist.get(h, 0) for h in range(21, 24))
    }
    
    max_count = max(tranches.values()) if tranches.values() else 1
    for tranche, count in tranches.items():
        bar_length = int((count / max_count) * 40) if max_count > 0 else 0
        bar = '█' * bar_length
        report.append(f"  {tranche:8} : {bar} {count}")
    
    report.append("")
    
    # 4. Corrélations entre artistes
    report.append("🔗 CORRÉLATIONS ENTRE ARTISTES")
    report.append("-" * 80)
    report.append("Artistes souvent écoutés dans les mêmes sessions :")
    correlations = analyze_artist_correlations(tracks)
    
    # Top 5 artistes avec le plus de corrélations
    top_correlated = sorted(correlations.items(), 
                           key=lambda x: sum(count for _, count in x[1]), 
                           reverse=True)[:5]
    
    for artist, related in top_correlated:
        if related:
            report.append(f"\n  • {artist[:60]}")
            for related_artist, count in related[:3]:
                report.append(f"    → {related_artist[:55]} ({count}× ensemble)")
    
    report.append("")
    
    # 5. Transitions fréquentes
    report.append("➡️  TRANSITIONS FRÉQUENTES")
    report.append("-" * 80)
    report.append("Après avoir écouté X, vous écoutez souvent Y :")
    transitions = analyze_transitions(tracks)
    
    # Top 5 artistes avec le plus de transitions
    top_transitions = sorted(transitions.items(), 
                            key=lambda x: sum(count for _, count in x[1]), 
                            reverse=True)[:5]
    
    for artist, nexts in top_transitions:
        if nexts:
            report.append(f"\n  • Après {artist[:55]}")
            for next_artist, count in nexts[:3]:
                report.append(f"    → {next_artist[:55]} ({count}×)")
    
    report.append("")
    
    # 6. Résumé statistique
    report.append("📈 RÉSUMÉ STATISTIQUE")
    report.append("-" * 80)
    total_duration = estimate_session_duration(tracks)
    avg_session_length = sum(len(s) for s in sessions) / len(sessions) if sessions else 0
    unique_artists = len(set(t['artist'] for t in tracks))
    unique_albums = len(set(f"{t['artist']} - {t['album']}" for t in tracks))
    
    report.append(f"Durée totale estimée : ~{total_duration} minutes (~{total_duration//60}h{total_duration%60}min)")
    report.append(f"Durée moyenne par session : ~{int(avg_session_length * 4)} minutes")
    report.append(f"Artistes différents écoutés : {unique_artists}")
    report.append(f"Albums différents écoutés : {unique_albums}")
    report.append(f"Diversité artistique : {round(unique_artists / len(tracks) * 100, 1)}%")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    """Fonction principale."""
    print("📂 Chargement de chk-roon.json...")
    try:
        tracks = load_tracks()
        print(f"✅ {len(tracks)} pistes chargées\n")
    except FileNotFoundError:
        print("❌ Erreur : Le fichier chk-roon.json n'existe pas.")
        return
    except json.JSONDecodeError:
        print("❌ Erreur : Le fichier chk-roon.json n'est pas un JSON valide.")
        return
    
    print("🔍 Analyse des patterns en cours...\n")
    
    # Générer le rapport
    report = generate_report(tracks)
    
    # Afficher le rapport
    print(report)
    
    # Sauvegarder le rapport
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = os.path.join(PROJECT_ROOT, "output", "reports", f"listening-patterns-{timestamp}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Rapport sauvegardé dans : {output_file}")

if __name__ == "__main__":
    main()
