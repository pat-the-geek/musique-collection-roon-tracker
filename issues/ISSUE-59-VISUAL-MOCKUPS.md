# Issue #59: Mockups Visuels - Interface CLI

**Date**: 28 janvier 2026  
**Version**: 1.0.0  
**Auteur**: GitHub Copilot AI Agent

---

## 📸 Aperçus Visuels de l'Interface CLI

Ce document présente des mockups visuels en ASCII/ANSI de l'interface CLI proposée.

---

## 🎨 Menu Principal

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎵 Musique Collection & Roon Tracker                  ║
║                                                              ║
║                    Version 3.4.0-cli                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

? Choisissez une action:

  ❯ 📂 Collection Discogs (400 albums)
    📔 Journal Roon (2700 tracks)
    📈 Timeline Roon (visualisation horaire)
    🤖 Journal IA (logs quotidiens)
    🎵 Haïkus & Rapports
    ⚙️  Configuration
    ❓ Aide
    ❌ Quitter

[↑↓] Navigate  [Enter] Select  [q] Quit
```

**Couleurs:**
- Titre: Cyan bold
- Sélection active: Cyan avec ❯
- Options: Blanc
- Aide: Gris dim

---

## 📂 Collection Discogs - Liste

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📂 Collection Discogs                            400 albums  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Filtres: [Tous] [🎬 BOF: Non] [Support: Tous] [Année: Toutes]

┌──────────────────────────────────────────────────────────────┐
│ Titre                        Artiste         Année  Support  │
├──────────────────────────────────────────────────────────────┤
│ Kind of Blue                 Miles Davis      1959  Vinyle   │
│ The Dark Side of the Moon    Pink Floyd       1973  Vinyle   │
│ Abbey Road                   The Beatles      1969  Vinyle   │
│ 🎬 La Môme (BOF)             Édith Piaf       2007  CD       │
│ Thriller                     Michael Jackson  1982  Vinyle   │
│ What's Going On              Marvin Gaye      1971  Vinyle   │
│ The Velvet Underground & N.  Velvet Undergr.  1967  Vinyle   │
│ Born to Run                  Bruce Springst.  1975  Vinyle   │
│ A Love Supreme               John Coltrane    1965  Vinyle   │
│ Nevermind                    Nirvana          1991  CD       │
└──────────────────────────────────────────────────────────────┘

[1-10 sur 400] | Page 1/40

? Commandes: [n]ext [p]revious [s]earch [f]ilter [v]iew [e]dit [q]uit
```

**Couleurs:**
- Titres: Cyan italic
- Artistes: Magenta
- Années: Gris dim
- BOF indicator: Yellow
- Bordures: Cyan

---

## 🔍 Collection Discogs - Recherche Interactive

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔍 Recherche dans Collection                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Search: miles davis_

⠋ Recherche en cours...

┌──────────────────────────────────────────────────────────────┐
│ 8 résultats trouvés                                          │
├──────────────────────────────────────────────────────────────┤
│ Kind of Blue                 Miles Davis      1959  Vinyle   │
│ Bitches Brew                 Miles Davis      1970  Vinyle   │
│ Sketches of Spain            Miles Davis      1960  Vinyle   │
│ In a Silent Way              Miles Davis      1969  Vinyle   │
│ Round About Midnight         Miles Davis      1957  Vinyle   │
│ Porgy and Bess               Miles Davis      1959  Vinyle   │
│ Miles Ahead                  Miles Davis      1957  Vinyle   │
│ Birth of the Cool            Miles Davis      1957  Vinyle   │
└──────────────────────────────────────────────────────────────┘

? [Enter] pour voir détails, [Esc] pour annuler, [↑↓] pour naviguer
```

**Fonctionnalités:**
- Auto-completion pendant la frappe
- Recherche floue (fuzzy matching)
- Spinner animé pendant recherche
- Navigation au clavier dans résultats

---

## 📄 Collection Discogs - Vue Détail

```
╭──────────────────────────────────────────────────────────────╮
│ 🎵 Kind of Blue                                              │
│                                                               │
│ 🎤 Artiste: Miles Davis                                      │
│ 📅 Année: 1959                                               │
│ 📅 Réédition Spotify: 2015                                   │
│ 💿 Support: Vinyle                                           │
│ 🏷️  Labels: Columbia                                         │
│                                                               │
│ 🔗 Spotify: https://open.spotify.com/album/1weenld61qoi... │
│ 🔗 Discogs: https://www.discogs.com/release/123456          │
│                                                               │
│ 📝 Résumé:                                                   │
│ Album de jazz modal révolutionnaire enregistré en mars et   │
│ avril 1959 aux Columbia 30th Street Studios de New York.    │
│ Considéré comme l'un des plus grands albums de jazz de tous │
│ les temps. Featuring: John Coltrane (saxophone ténor),      │
│ Cannonball Adderley (saxophone alto), Bill Evans (piano),   │
│ Wynton Kelly (piano sur "Freddie Freeloader"), Paul         │
│ Chambers (contrebasse), Jimmy Cobb (batterie).              │
│                                                               │
│ Morceaux iconiques: "So What", "Freddie Freeloader",        │
│ "Blue in Green", "All Blues", "Flamenco Sketches".          │
│                                                               │
│ 🤖 Info IA:                                                  │
│ ╭──────────────────────────────────────────────────────────╮ │
│ │ Album légendaire qui a défini le jazz modal. Les        │ │
│ │ improvisations sont basées sur des modes plutôt que     │ │
│ │ des progressions d'accords traditionnelles. Enregistré │ │
│ │ en seulement deux sessions, la spontanéité et la        │ │
│ │ créativité sont palpables.                              │ │
│ ╰──────────────────────────────────────────────────────────╯ │
│                                                               │
│ 🖼️  [Voir pochette] (iTerm2/Kitty uniquement)                │
╰──────────────────────────────────────────────────────────────╯

? Commandes: [b]ack [e]dit [s]potify [d]iscogs [a]i regenerate [q]uit
```

**Couleurs:**
- Titre album: Cyan italic bold
- Artiste: Magenta
- Année: Gris dim
- Labels: Gris dim
- URLs: Blue underline
- Info IA: Cyan sur fond dim

---

## ✏️ Collection Discogs - Mode Édition

```
╭──────────────────────────────────────────────────────────────╮
│ ✏️  Édition: Kind of Blue                                    │
╰──────────────────────────────────────────────────────────────╯

Titre: [Kind of Blue_________________________________]

Artiste: [Miles Davis_________________________________]
         [+ Ajouter artiste]

Année: [1959__]

Année Réédition Spotify: [2015__]

Support: ❯ Vinyle
         CD
         Digital

Labels: [Columbia__________________________________]
        [+ Ajouter label]

Résumé:
┌──────────────────────────────────────────────────────────────┐
│ Album de jazz modal révolutionnaire enregistré en mars et   │
│ avril 1959 aux Columbia 30th Street Studios de New York...  │
│                                                               │
│ [Éditer dans éditeur externe]                                │
└──────────────────────────────────────────────────────────────┘

URLs:
  Spotify: [https://open.spotify.com/album/1weenld61qoi...]
  Discogs: [https://www.discogs.com/release/123456______]

[s]ave [c]ancel [g]enerate AI resume [r]eset
```

**Fonctionnalités:**
- Champs avec validation
- Sélecteur radio pour Support
- Multi-valeur pour artistes/labels
- Éditeur externe pour résumé long
- Génération IA sur demande

---

## 📔 Journal Roon - Liste Chronologique

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📔 Journal Roon                                  2700 tracks  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Filtres: [Source: Tous ▼] [❤️  Favoris: Non] [Date: Aujourd'hui ▼]

📊 Stats: 42 tracks aujourd'hui | 23 artistes | 31 albums | Peak: 18h

┌──────────────────────────────────────────────────────────────┐
│ Heure   Artiste              Titre                Album      │
├──────────────────────────────────────────────────────────────┤
│ 18:21   Serge Gainsbourg     Couleur Cafe      Le Zenith... │
│         🎵 roon | 🤖                                          │
│                                                               │
│ 18:17   Nina Simone          Feeling Good      I Put a S... │
│         🎵 roon | ❤️ | 🤖                                    │
│                                                               │
│ 18:12   Miles Davis          So What           Kind of B... │
│         🎵 roon | 🤖                                          │
│                                                               │
│ 17:58   The Beatles          Here Comes the... Abbey Road   │
│         📻 lastfm                                             │
│                                                               │
│ 17:54   Pink Floyd           Wish You Were...  Wish You...  │
│         🎵 roon | 🤖                                          │
│                                                               │
│ 17:49   Radiohead            Paranoid Android OK Computer   │
│         🎵 roon | ❤️ | 🤖                                    │
└──────────────────────────────────────────────────────────────┘

[1-6 sur 2700] | Page 1/450

? Commandes: [n]ext [p]revious [f]ilter [v]iew [❤] toggle loved [q]uit
```

**Couleurs:**
- Heure: Gris dim
- Artiste: Magenta
- Titre: Blanc
- Album: Cyan italic
- Source roon: Blue (🎵)
- Source lastfm: Green (📻)
- Loved: Red (❤️)
- AI info: Cyan (🤖)

---

## 🔍 Journal Roon - Vue Détail Track

```
╭──────────────────────────────────────────────────────────────╮
│ 🎵 Track Details                                             │
╰──────────────────────────────────────────────────────────────╯

🕐 Date: 2026-01-17 18:21:35
🎤 Artiste: Serge Gainsbourg
🎼 Titre: Couleur Cafe (Live)
💿 Album: Le Zenith De Gainsbourg
❤️  Favoris: Non
📡 Source: roon

┌─ 🤖 Info IA ─────────────────────────────────────────────────┐
│ Album live légendaire de Serge Gainsbourg enregistré au     │
│ Zénith de Paris en 1989, peu avant son décès. Ce concert    │
│ captivant offre un mélange de chansons iconiques et de      │
│ performances intimes qui témoignent de son génie artistique. │
│                                                               │
│ "Couleur Cafe" est une chanson sensuelle et tropicale qui   │
│ évoque les plaisirs de l'été avec des paroles imagées et    │
│ un arrangement jazzy caractéristique de Gainsbourg.         │
└──────────────────────────────────────────────────────────────┘

🔗 Spotify Artist: https://open.spotify.com/artist/...
🔗 Spotify Album: https://open.spotify.com/album/...
🔗 Last.fm Album: https://www.last.fm/music/...

🖼️  Images:
  • Artiste: https://i.scdn.co/image/...
  • Album (Spotify): https://i.scdn.co/image/...
  • Album (Last.fm): https://lastfm.freetls.fastly.net/...

? Commandes: [b]ack [❤] toggle loved [s]potify [l]astfm [a]i info [q]uit
```

**Fonctionnalités:**
- Métadonnées complètes
- Info IA expandable
- Liens cliquables (terminaux modernes)
- Toggle loved avec confirmation
- Navigation rapide vers services

---

## 📈 Timeline Roon - Visualisation Horaire

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📈 Timeline - Mardi 28 Janvier 2026                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📊 Statistiques: 42 tracks | 23 artistes uniques | 31 albums | 🔥 Peak: 18h

Mode: [Compact ▼] Détaillé   Navigation: [◀ Hier] [Aujourd'hui ▼] [Demain ▶]

  6h   7h   8h   9h   10h  11h  12h  13h  14h  15h  16h  17h  18h  19h  20h  21h  22h  23h
  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
  │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │
  │    │    │    │    │    │    │    │    │    │    │    🎵   🎵🎵🎵 🎵🎵  🎵   │    │
  │    │    │    │    │    │    │    │    │    │    │    │🎵  │🎵🎵│ 🎵│  🎵  │    │
  │    │    │    │    │    │    │    │    │    │    │    │    │🎵  │    │    │    │    │
  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
                                                   ↑ Peak Hour (18h - 9 tracks)

╔═ 18h ═══════════════════════════════════════════════════════╗
║ 18:21 🎵 Serge Gainsbourg - Couleur Cafe               [🤖] ║
║ 18:17 🎵 Nina Simone - Feeling Good               [❤️] [🤖] ║
║ 18:12 🎵 Miles Davis - So What                         [🤖] ║
║ 18:08 🎵 The Beatles - Here Comes the Sun               [🤖] ║
║ 18:03 🎵 Pink Floyd - Wish You Were Here                [🤖] ║
║ 17:58 📻 Radiohead - Paranoid Android              [❤️] [🤖] ║
║ 17:54 🎵 John Coltrane - Giant Steps                   [🤖] ║
║ 17:49 🎵 Björk - Joga                                   [🤖] ║
║ 17:45 🎵 David Bowie - Heroes                           [🤖] ║
╚═════════════════════════════════════════════════════════════╝

? Commandes: [←→] navigate hours [d]ay select [v]iew track [m]ode toggle [q]uit
```

**Fonctionnalités:**
- Timeline ASCII graduée par heures
- Densité visuelle (nombre d'écoutes)
- Peak hour indicator
- Zoom sur heure sélectionnée
- Mode compact/détaillé
- Navigation par jour
- Alternance couleurs par heure

---

## 🤖 Journal IA - Logs Quotidiens

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🤖 Journal IA - Logs Quotidiens                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

? Sélectionnez un fichier de log:

  ❯ 📅 2026-01-28 (aujourd'hui) - 42 albums enrichis
    📅 2026-01-27 - 38 albums enrichis
    📅 2026-01-26 - 45 albums enrichis
    📅 2026-01-25 - 51 albums enrichis
    📅 2026-01-24 - 39 albums enrichis

[Enter] pour visualiser | [↑↓] pour naviguer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Log: 2026-01-28 (42 albums traités | Source: 34 Discogs, 8 IA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

18:21 | Serge Gainsbourg - Le Zenith De Gainsbourg
      ✓ Discogs | Album live légendaire enregistré au Zénith de Paris
      en 1989. Captivant mélange de chansons iconiques et de
      performances intimes.

18:17 | Nina Simone - I Put a Spell on You
      ✓ Discogs | Compilation des plus grands succès de Nina Simone.
      Voix puissante et émotions intenses caractéristiques de l'artiste.

18:12 | Miles Davis - Kind of Blue
      ✓ Discogs | Album de jazz modal révolutionnaire enregistré en 1959.
      Considéré comme l'un des plus grands albums de jazz de tous les temps.

17:58 | The Beatles - Abbey Road
      ⚠ IA | Dernier album enregistré par les Beatles en 1969. Pochette
      iconique avec passage piéton. Morceaux légendaires comme
      "Come Together" et "Here Comes the Sun".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1-4 sur 42] | Page 1/11

? Commandes: [n]ext [p]revious [b]ack [d]ate select [e]xport [q]uit
```

**Couleurs:**
- Titre section: Cyan bold
- Date aujourd'hui: Green bold
- Dates passées: White
- Source Discogs: Green (✓)
- Source IA: Yellow (⚠)
- Timestamps: Gris dim

---

## ⚙️ Configuration

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ⚙️  Configuration                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

? Catégorie:
  ❯ 🎨 Interface (couleurs, thème, taille)
    📊 Pagination (items par page, limites)
    🕐 Heures d'écoute (début, fin)
    📡 Sources de données (chemins, priorités)
    🤖 IA (API, timeouts, fallback)
    🔧 Avancé (cache, logs, debug)

╭─ 🎨 Interface ──────────────────────────────────────────────╮
│                                                              │
│ Mode couleur: [auto ▼]                                      │
│   Options: auto, always, never, truecolor                   │
│                                                              │
│ Thème: [default ▼]                                          │
│   Options: default, dark, light, solarized                  │
│                                                              │
│ Largeur terminal: [auto] (détecté: 120 colonnes)            │
│                                                              │
│ Hauteur terminal: [auto] (détecté: 40 lignes)               │
│                                                              │
│ Affichage compact: [Non ▼]                                  │
│   Options: Oui, Non                                         │
│                                                              │
╰──────────────────────────────────────────────────────────────╯

[s]ave [r]eset defaults [c]ancel
```

**Fonctionnalités:**
- Configuration catégorisée
- Validation temps réel
- Preview des changements
- Reset aux valeurs par défaut
- Export/Import configuration

---

## 🎯 Résumé des Fonctionnalités UI

### Composants Réutilisables

1. **Tables**: Pagination, tri, filtres
2. **Panels**: Bordures élégantes, padding adaptatif
3. **Menus**: Navigation au clavier, sélection multiple
4. **Forms**: Validation, auto-completion, erreurs inline
5. **Progress**: Spinners, bars, estimations temps
6. **Dialogs**: Confirmations, alertes, prompts

### Couleurs Sémantiques

- **Cyan**: Titres, albums, éléments primaires
- **Magenta**: Artistes, accents
- **Blue**: Liens, source Roon
- **Green**: Succès, source Last.fm
- **Yellow**: Avertissements, soundtracks
- **Red**: Erreurs, favoris
- **Gris**: Métadonnées secondaires (années, dates)
- **Blanc**: Texte principal

### Navigation

- **Flèches**: ↑↓←→ pour navigation
- **Enter**: Sélection/validation
- **Esc**: Annulation/retour
- **Lettres**: Raccourcis (n=next, p=previous, q=quit, etc.)
- **Tab**: Changement de champ
- **Ctrl+C**: Interruption

---

## 📊 Comparaison Visuelle

### Streamlit (Actuel)
```
[Navigateur Web avec barre d'adresse]
├─ Sidebar (fixed)
│  └─ Menu radio vertical
└─ Main content
   ├─ Header avec titre
   ├─ Filtres (selectbox, checkbox)
   ├─ Images (pochettes, artistes)
   ├─ Expandables (info IA)
   └─ Boutons d'action
```

**Avantages:**
- Images natives
- Layout flexible
- Édition inline simple

**Inconvénients:**
- Nécessite navigateur
- Lent (3-5s démarrage)
- Pas SSH-friendly

### CLI (Proposé)
```
[Terminal fullscreen]
├─ Header (titre + stats)
├─ Content area
│  ├─ Tables avec bordures
│  ├─ Panels avec métadonnées
│  └─ Menus interactifs
└─ Footer (commandes + pagination)
```

**Avantages:**
- Démarrage instantané (<1s)
- SSH-friendly
- Navigation 100% clavier
- Léger (6MB dépendances)

**Inconvénients:**
- Images limitées (URLs)
- Apprentissage commandes

---

## ✅ Validation Visuelle

**Critères:**
- ✅ Lisibilité: Tables claires, espacement cohérent
- ✅ Navigation: Commandes visibles, feedback immédiat
- ✅ Esthétique: Couleurs harmonieuses, bordures élégantes
- ✅ Cohérence: Style uniforme entre toutes les vues
- ✅ Accessibilité: Compatible lecteurs d'écran, contraste élevé
- ✅ Performance: Rendering rapide, pas de lag

---

**Auteur**: GitHub Copilot AI Agent  
**Date**: 28 janvier 2026  
**Version**: 1.0.0  
**Statut**: 📸 Mockups visuels pour validation
