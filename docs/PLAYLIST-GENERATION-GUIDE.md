# Guide de Génération de Playlists

**Version**: 1.2.0  
**Date**: 27 janvier 2026  
**Issue**: #19 - Création de playlists basées sur les patterns d'écoute  
**Fix**: #38 - Suppression des doublons dans les playlists

## 📋 Vue d'ensemble

Le générateur de playlists analyse votre historique d'écoute Roon/Last.fm pour créer automatiquement des playlists intelligentes basées sur vos habitudes d'écoute. **10 algorithmes** sont disponibles, dont un algorithme **alimenté par l'IA EurIA** qui permet de créer des playlists sur mesure via des prompts en langage naturel.

**✨ Nouveau dans v1.2.0**: Détection et suppression automatique des doublons avec normalisation intelligente (ignore les variations de casse et espaces).

###  ⚠️ Limitation Importante: API Roon

**L'API Roon ne permet PAS la création automatique de playlists programmatiquement.**

Cette limitation est documentée dans la communauté Roon Labs et affecte tous les wrappers Python (roonapi, pyroon). Les playlists générées sont donc exportées dans plusieurs formats standard pour:
- Import manuel dans Roon (via instructions détaillées)
- Utilisation directe dans d'autres lecteurs (VLC, iTunes, Foobar2000)
- Archivage et partage (JSON, CSV)

## 🎯 Algorithmes Disponibles

### 1. Top Sessions (`top_sessions`)
**Analyse les sessions d'écoute continues** (gap < 30 minutes entre pistes) et sélectionne les pistes les plus fréquentes dans les sessions les plus longues.

**Idéal pour:** Recréer l'ambiance de vos meilleures sessions d'écoute.

### 2. Corrélations d'Artistes (`artist_correlations`)
**Identifie les artistes souvent écoutés ensemble** dans les mêmes sessions et crée des playlists thématiques.

**Idéal pour:** Découvrir des connexions entre vos artistes favoris.

### 3. Flow Naturel (`artist_flow`)
**Analyse les transitions fréquentes** entre artistes et crée un "flow" musical naturel basé sur vos habitudes.

**Idéal pour:** Une écoute fluide qui respecte votre style de navigation musicale.

### 4. Heures de Pic (`time_based_peak`)
**Sélectionne les pistes les plus écoutées entre 18h et 22h.**

**Idéal pour:** Musique de soirée, fin de journée.

### 5. Weekend (`time_based_weekend`)
**Pistes typiquement écoutées le samedi et dimanche.**

**Idéal pour:** Ambiance décontractée du weekend.

### 6. Soirée (`time_based_evening`)
**Pistes écoutées entre 18h et 23h.**

**Idéal pour:** Détente en soirée, dîner.

### 7. Matin (`time_based_morning`)
**Pistes écoutées entre 6h et 12h.**

**Idéal pour:** Réveil en douceur, petit-déjeuner.

### 8. Albums Complets (`complete_albums`)
**Sélectionne les albums écoutés en entier** (≥5 pistes) et trie par fréquence.

**Idéal pour:** Albums concepts, œuvres complètes.

### 9. Redécouverte (`rediscovery`)
**Pistes aimées mais non écoutées depuis plus de 30 jours.**

**Idéal pour:** Redécouvrir des trésors oubliés de votre bibliothèque.

### 10. 🤖 Génération par IA (`ai_generated`) - NOUVEAU!

**Utilise l'API EurIA (Qwen3)** pour créer des playlists sur mesure basées sur un prompt en langage naturel.

**Comment ça marche:**
1. Vous décrivez la playlist souhaitée en français (ex: "jazz cool pour le soir")
2. L'IA analyse jusqu'à 200 pistes de votre historique
3. L'IA sélectionne intelligemment les pistes correspondantes
4. L'IA propose un nom créatif et justifie ses choix

**Exemples de prompts:**
- "playlist calme pour méditer le soir"
- "musique énergique des années 80 pour faire du sport"
- "jazz sophistiqué pour un dîner romantique"
- "découverte de nouveaux artistes variés"
- "ambiance chaleureuse pour lire un livre"

**Avantages:**
- ✅ Créativité et flexibilité maximales
- ✅ Comprend le contexte et l'ambiance
- ✅ Justifie ses choix (transparence)
- ✅ Propose des noms de playlists créatifs
- ✅ Utilise les métadonnées d'albums existantes

**Idéal pour:** Toute situation spécifique, besoin d'ambiance particulière, ou exploration créative.

## 🧹 Détection et Suppression des Doublons

Tous les algorithmes de génération de playlists incluent **automatiquement** une étape de détection et suppression des doublons.

### Comment ça marche

Le système crée une **clé normalisée** pour chaque piste en combinant:
- Nom de l'artiste (normalisé)
- Titre de la piste (normalisé)
- Nom de l'album (normalisé)

La normalisation:
- ✅ Ignore la casse (majuscules/minuscules)
- ✅ Supprime les espaces multiples
- ✅ Détecte les variations mineures

### Exemples de Doublons Détectés

Les pistes suivantes seraient considérées comme des **doublons** et seule la première occurrence serait conservée:

```
❌ DOUBLON:
   - "London Calling (remastered)" 
   - "London Calling (Remastered)"
   → Normalisé: "london calling (remastered)"

❌ DOUBLON:
   - "Love Is the Drug"
   - "Love Is The Drug"
   → Normalisé: "love is the drug"

❌ DOUBLON:
   - "Let's Dance (2018 Remaster)"
   - "Let's Dance (2018 remaster)"
   → Normalisé: "let's dance (2018 remaster)"
```

### Comportement

- 🔍 La détection s'exécute **après** la génération de la playlist
- 📊 Le nombre de doublons supprimés est affiché dans la console
- 📁 Seule la **première occurrence** est conservée
- 🎵 L'ordre original des pistes est préservé
- ✅ Fonctionne avec **tous les algorithmes** (y compris IA)

### Sortie Console

```bash
🎵 Génération avec l'algorithme 'top_sessions'...
   ✅ 30 pistes sélectionnées
   🔍 5 doublon(s) supprimé(s)
```

## 📦 Formats d'Export

### JSON (Métadonnées Complètes)
```json
{
  "name": "Soirée Jazz Cool",
  "description": "Playlist générée par IA pour une ambiance jazz sophistiquée",
  "created_at": "2026-01-27T14:30:00",
  "algorithm": "ai_generated",
  "total_tracks": 25,
  "total_duration_minutes": 100,
  "ai_reasoning": "J'ai sélectionné des classiques du jazz modal...",
  "tracks": [
    {
      "artist": "Miles Davis",
      "title": "So What",
      "album": "Kind of Blue",
      "timestamp": 1738000000,
      "source": "roon",
      "artist_spotify_image": "https://...",
      "album_spotify_image": "https://...",
      "ai_info": "Kind of Blue est un album emblématique..."
    }
  ]
}
```

**Utilisation:** Archivage, intégration avec d'autres outils, analyse.

### M3U (Standard Universel)
```
#EXTM3U
#PLAYLIST:Soirée Jazz Cool
#EXTIMG:https://...
#EXTINF:240,Miles Davis - So What
# Miles Davis - So What (Kind of Blue)

#EXTINF:210,John Coltrane - Blue Train
# John Coltrane - Blue Train (Blue Train)
```

**Compatible avec:**
- VLC Media Player
- iTunes / Apple Music
- Winamp
- Foobar2000
- Et tout lecteur supportant M3U

### CSV (Excel / Google Sheets)
```csv
Artist,Title,Album,Date,Source,Spotify Image,Last.fm Image
Miles Davis,So What,Kind of Blue,2026-01-15 20:30,roon,https://...,https://...
John Coltrane,Blue Train,Blue Train,2026-01-15 21:00,roon,https://...,https://...
```

**Utilisation:** Analyse Excel, import bases de données, partage.

### TXT (Import Manuel Roon)
```
================================================================================
PLAYLIST POUR ROON
================================================================================

Nom: Soirée Jazz Cool
Description: Playlist générée par IA pour une ambiance jazz sophistiquée
Créée le: 2026-01-27 à 14:30
Nombre de pistes: 25
Durée estimée: 100 minutes

🤖 RAISONNEMENT IA:
J'ai sélectionné des classiques du jazz modal et cool jazz qui créent une
ambiance sophistiquée parfaite pour une soirée. Miles Davis, John Coltrane,
et Bill Evans apportent cette atmosphère contemplative que vous recherchez.

⚠️ LIMITATION ROON API:
L'API Roon ne permet PAS la création automatique de playlists.
Vous devez importer cette playlist MANUELLEMENT.

INSTRUCTIONS D'IMPORT DANS ROON:
1. Ouvrir Roon
2. Aller dans la section 'Browse' > 'Tracks'
3. Pour chaque piste ci-dessous:
   a. Utiliser la fonction 'Focus' ou 'Search' pour trouver la piste
   b. Ajouter la piste à la queue de lecture
4. Une fois la queue complète, faire clic-droit > 'Save as Playlist'
5. Nommer la playlist: 'Soirée Jazz Cool'

================================================================================
PISTES (25)
================================================================================

  1. Miles Davis - So What
      Album: Kind of Blue
      Image: https://...

  2. John Coltrane - Blue Train
      Album: Blue Train
      Image: https://...
```

## 🚀 Utilisation

### Via Ligne de Commande

#### Algorithmes Standards
```bash
cd src/analysis

# Sessions fréquentes (25 pistes)
python3 generate-playlist.py --algorithm top_sessions

# Flow naturel (30 pistes, formats JSON + M3U)
python3 generate-playlist.py --algorithm artist_flow --max-tracks 30 --formats json m3u

# Redécouverte (50 pistes, tous formats)
python3 generate-playlist.py --algorithm rediscovery --max-tracks 50
```

#### 🤖 Génération par IA
```bash
# Prompt simple
python3 generate-playlist.py --algorithm ai_generated \
  --ai-prompt "playlist calme pour méditer le soir"

# Prompt détaillé avec personnalisation
python3 generate-playlist.py --algorithm ai_generated \
  --ai-prompt "musique énergique des années 80 pour faire du sport" \
  --max-tracks 30 \
  --formats json m3u

# Ambiance spécifique
python3 generate-playlist.py --algorithm ai_generated \
  --ai-prompt "jazz cool et sophistiqué pour un dîner romantique" \
  --max-tracks 20
```

### Via Interface GUI

1. **Ouvrir l'interface Streamlit:**
   ```bash
   ./scripts/start-streamlit.sh
   # ou
   streamlit run src/gui/musique-gui.py
   ```

2. **Accéder à la page Configuration (⚙️)**

3. **Configurer la tâche `generate_playlist`:**
   - ✅ Activer la tâche
   - 📅 Définir la fréquence (ex: tous les 7 jours)
   - 🎵 Choisir le type de playlist
   - 🤖 **Pour IA:** Saisir le prompt dans le champ "Prompt pour l'IA"
   - 🔢 Définir le nombre de pistes (10-100)
   - 📦 Sélectionner les formats d'export
   - 💾 Sauvegarder

4. **Exécuter immédiatement (optionnel):**
   - Cliquer sur "▶️ Exécuter maintenant"

5. **Visualiser les playlists:**
   - Aller sur la page "🎵 Playlists"
   - Parcourir les playlists générées
   - Voir les détails (nom IA, description, justification)
   - Télécharger dans le format souhaité

### Via Scheduler (Automatique)

**Configuration dans `data/config/roon-config.json`:**

```json
{
  "scheduled_tasks": {
    "generate_playlist": {
      "enabled": true,
      "frequency_unit": "day",
      "frequency_count": 7,
      "description": "Generate playlists based on listening patterns",
      "playlist_type": "ai_generated",
      "max_tracks": 25,
      "ai_prompt": "playlist variée pour découvrir de nouveaux artistes",
      "output_formats": ["json", "m3u", "csv", "roon-txt"]
    }
  }
}
```

Le scheduler s'exécute automatiquement toutes les ~45 minutes via `chk-roon.py`.

## 💡 Conseils d'Utilisation IA

### Rédiger un Bon Prompt

**Structure recommandée:**
```
[Ambiance/Genre] + [Contexte d'utilisation] + [Préférences optionnelles]
```

**Exemples:**

✅ **Bon prompt:**
- "jazz modal relaxant pour lire le soir"
- "rock énergique des années 70-80 pour courir"
- "musique classique contemplative pour travailler"
- "découverte électronique expérimentale et variée"

❌ **Prompt trop vague:**
- "musique"
- "quelque chose de bien"
- "surprise-moi"

### Optimiser les Résultats

1. **Soyez spécifique sur l'ambiance:** "calme", "énergique", "mélancolique", "joyeux"
2. **Mentionnez le contexte:** "pour dormir", "pour faire du sport", "pour étudier"
3. **Précisez un genre si important:** "jazz", "rock", "classique", "électronique"
4. **Indiquez une époque si pertinent:** "années 80", "contemporain", "classique baroque"
5. **Suggérez une diversité:** "variée", "découverte", "différents styles"

### Exemples de Prompts Créatifs

```
"voyage sonore à travers le jazz modal et le cool jazz"
"énergie positive avec du funk et de la soul des années 70"
"ambiance feutrée pour soirée romantique avec jazz et bossa nova"
"exploration de musiques du monde apaisantes et méditatives"
"réveil en douceur avec musique acoustique folk et indie"
"concentration maximale avec post-rock instrumental et ambient"
```

## 📊 Workflow Typique

### 1. Exploration Initiale
```bash
# Découvrir vos sessions favorites
python3 generate-playlist.py --algorithm top_sessions --max-tracks 30

# Analyser vos habitudes temporelles
python3 generate-playlist.py --algorithm time_based_evening --max-tracks 25
```

### 2. Création Thématique
```bash
# Utiliser l'IA pour un besoin spécifique
python3 generate-playlist.py --algorithm ai_generated \
  --ai-prompt "musique pour concentration profonde au travail"
```

### 3. Redécouverte
```bash
# Retrouver des pépites oubliées
python3 generate-playlist.py --algorithm rediscovery --max-tracks 40
```

### 4. Automatisation
- Configurer le scheduler pour générer hebdomadairement
- Utiliser l'IA avec différents prompts selon les semaines
- Consulter régulièrement la page Playlists du GUI

## 🔧 Dépannage

### "Module roonapi not found"
```bash
pip install -r requirements-roon.txt
```

### "API EurIA configuration manquante"
Vérifier que `data/config/.env` contient:
```env
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=votre_token_euria
```

### "Aucune piste disponible"
Vérifier que `data/history/chk-roon.json` contient des pistes enregistrées.

### L'IA sélectionne trop peu de pistes
- Augmenter `--max-tracks`
- Raffiner le prompt pour être moins restrictif
- Vérifier que l'historique contient suffisamment de pistes correspondantes

### Playlist IA ne correspond pas au prompt
- Rendre le prompt plus spécifique
- Vérifier que votre historique contient des pistes du genre souhaité
- Essayer un prompt différent avec plus de contexte

### Des doublons apparaissent dans mes playlists
✅ **Résolu dans v1.2.0** - La détection automatique des doublons est maintenant activée.

Si vous utilisez une version antérieure:
```bash
# Mettre à jour vers v1.2.0+
git pull origin main
```

Si le problème persiste:
- Vérifier que la console affiche "🔍 X doublon(s) supprimé(s)"
- Les doublons détectés sont basés sur la normalisation (artiste + titre + album)
- Seules les pistes avec les **3 champs identiques** (après normalisation) sont considérées comme doublons

## 📚 Références

- [ROON-API-PLAYLIST-LIMITATIONS.md](./ROON-API-PLAYLIST-LIMITATIONS.md) - Documentation détaillée des limitations
- [README-SCHEDULER.md](./README-SCHEDULER.md) - Guide du scheduler
- [AI-INTEGRATION.md](./AI-INTEGRATION.md) - Intégration EurIA
- [Issue #19](https://github.com/pat-the-geek/musique-collection-roon-tracker/issues/19) - Demande initiale

## 🎬 Vidéo Tutoriel

_(À venir)_ - Démonstration complète de la génération de playlists par IA.

## 📝 Changelog

### Version 1.2.0 (27 janvier 2026)
- 🔍 Détection et suppression automatique des doublons
- 🧹 Normalisation intelligente (ignore casse et espaces)
- ✅ Affichage du nombre de doublons supprimés
- 📝 Correction du problème GitHub Issue #38
- ✅ 13 tests unitaires ajoutés

### Version 1.1.0 (27 janvier 2026)
- ✨ Ajout algorithme `ai_generated` avec EurIA
- ✨ Support des prompts en langage naturel
- ✨ Justification IA dans les exports
- ✨ Configuration GUI pour prompt IA
- ✨ Documentation complète

### Version 1.0.0 (27 janvier 2026)
- 🎉 Release initiale
- 9 algorithmes de génération
- 4 formats d'export
- Intégration scheduler
- Interface GUI complète
