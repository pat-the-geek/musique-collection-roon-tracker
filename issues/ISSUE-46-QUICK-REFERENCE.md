# Timeline View - Quick Reference Card

## 🎯 Vue d'Ensemble

**Nouvelle fonctionnalité**: Visualisation horaire des écoutes Roon  
**Version**: v3.4.0  
**Menu**: 📈 Timeline Roon  
**Localisation Code**: `src/gui/musique-gui.py` (ligne ~1338)

## 🖥️ Interface Utilisateur

### Layout Principal

```
╔══════════════════════════════════════════════════════════════════╗
║ 📈 Timeline d'écoute Roon                    [🔄 Actualiser]    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║ 📅 Jour: [▼ Mardi 28 Janvier 2026]  │ Lectures: 10  │ [✓] Comp.║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  TIMELINE HORIZONTALE (scroll ←→)                               ║
║  ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐     ║
║  │06h │07h │08h │09h │10h │11h │12h │13h │14h │15h │16h │ ... ║
║  │(0) │(0) │(3) │(1) │(1) │(1) │(0) │(0) │(0) │(0) │(1) │     ║
║  ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤     ║
║  │    │    │[🎵]│[🎵]│[🎵]│[🎵]│    │    │    │    │[🎵]│     ║
║  │    │    │8:30│9:40│    │    │    │    │    │    │    │     ║
║  │    │    │────│    │    │    │    │    │    │    │    │     ║
║  │    │    │[🎵]│    │    │    │    │    │    │    │    │     ║
║  │    │    │8:35│    │    │    │    │    │    │    │    │     ║
║  │    │    │────│    │    │    │    │    │    │    │    │     ║
║  │    │    │[🎵]│    │    │    │    │    │    │    │    │     ║
║  │    │    │8:40│    │    │    │    │    │    │    │    │     ║
║  └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘     ║
║   █░░  ░░░  █░░  ░░░  █░░  ░░░  █░░  ░░░  █░░  ░░░  █░░      ║
║   (Alternance de couleurs automatique)                          ║
╠══════════════════════════════════════════════════════════════════╣
║ Total: 10 │ Artistes: 10 │ Albums: 10 │ Pic: 08:00 (3)        ║
╚══════════════════════════════════════════════════════════════════╝
```

## 🎛️ Contrôles

### Sélecteur de Date
```
📅 Sélectionner un jour:
┌──────────────────────────────┐
│ ▼ Mardi 28 Janvier 2026      │
├──────────────────────────────┤
│   Lundi 27 Janvier 2026      │
│   Dimanche 26 Janvier 2026   │
│   Samedi 25 Janvier 2026     │
│   ...                        │
└──────────────────────────────┘
```

### Toggle Affichage
```
☐ Compact    →    ☑ Compact
(Mode détaillé)   (Mode compact)
```

### Bouton Refresh
```
[🔄 Actualiser]  →  Recharge les données depuis chk-roon.json
```

## 📊 Modes d'Affichage

### Mode Compact (par défaut)
```
┌──────┐
│      │
│ [🎵] │  ← Pochette seule
│      │
└──────┘
    ↑
    Tooltip au survol:
    "Miles Davis - So What
     Kind of Blue
     08:30"
```

### Mode Détaillé
```
┌──────────┐
│   [🎵]   │  ← Pochette
│   8:30   │  ← Heure
│  Miles   │  ← Artiste
│  Davis   │
└──────────┘
```

## 🎨 Couleurs

```
PAIR (Blanc)           IMPAIR (Gris)
┌──────────┐          ┌──────────┐
│  06:00   │          │  07:00   │
│ #FFFFFF  │          │ #F0F0F0  │
│ 50% opac.│          │ 50% opac.│
└──────────┘          └──────────┘
```

## 📈 Statistiques

```
┌─────────────┬─────────────┬─────────────┬──────────────────────┐
│Total tracks │Artistes uniq│ Albums uniq │  Heure la plus active│
│     10      │     10      │     10      │      08:00 (3)       │
└─────────────┴─────────────┴─────────────┴──────────────────────┘
```

## 🔄 Flux de Données

```
1. Utilisateur: Sélectionne une date
           ↓
2. Timeline: Charge données via load_roon_data() [cached]
           ↓
3. Timeline: Groupe par heure (0-23)
           ↓
4. Timeline: Limite à 20 tracks/heure
           ↓
5. Timeline: Génère HTML avec CSS
           ↓
6. Streamlit: Affiche via st.markdown(unsafe_allow_html=True)
           ↓
7. Navigateur: Render avec scroll horizontal
```

## ⚙️ Configuration

### Plage Horaire (roon-config.json)
```json
{
  "listen_start_hour": 6,   ← Heure de début (défaut: 6)
  "listen_end_hour": 23      ← Heure de fin (défaut: 23)
}
```

### Limite de Tracks
```python
# Limite codée en dur dans display_roon_timeline()
MAX_TRACKS_PER_HOUR = 20  # Pour lisibilité UI
```

## 🎯 Cas d'Usage

### Scénario 1: "Quelle musique hier matin?"
```
1. Menu → 📈 Timeline Roon
2. Date → [Hier]
3. Scroll → 06:00 - 12:00
4. Observer visuellement
   → Réponse immédiate!
```

### Scénario 2: "Mon heure préférée?"
```
1. Consulter plusieurs jours
2. Repérer colonnes les plus remplies
3. Lire stat "Heure la plus active"
   → Pattern identifié!
```

### Scénario 3: "Qu'ai-je écouté cet après-midi?"
```
1. Date → [Aujourd'hui]
2. Scroll → 14:00 - 18:00
3. Hover sur pochettes
   → Détails sans clic!
```

## ⌨️ Raccourcis Clavier

```
←  →  : Scroll horizontal (timeline)
↑  ↓  : Scroll vertical (page)
Esc   : Fermer tooltip (si applicable)
```

## 📱 Responsive

### Desktop (>1200px)
- 5-7 colonnes visibles
- Images 180px

### Tablet (768-1200px)
- 3-4 colonnes visibles
- Images 140px

### Mobile (<768px)
- 2 colonnes visibles
- Images 100px

## 🚀 Performance

```
Temps de chargement typique:
├─ Premier chargement:    ~300ms (cache miss)
├─ Changement de date:     ~50ms (cache hit)
├─ Toggle compact/détail:  <10ms (CSS only)
└─ Scroll horizontal:      <1ms (natif navigateur)
```

## 🐛 Limitations Connues

1. **Pas d'auto-scroll** sur heure actuelle
   - Nécessiterait JavaScript custom
   - Workaround: Sélecteur manuel de date

2. **Images externes**
   - Dépend disponibilité Spotify/Last.fm
   - Fallback: "Pas d'image"

3. **Limite 20 tracks/heure**
   - Tracks au-delà ne sont pas affichés
   - Compteur montre total (ex: "25")

## 🔗 Références

- **Code**: `src/gui/musique-gui.py` ligne 1338-1591
- **Doc Technique**: `issues/ISSUE-46-TIMELINE-VIEW-IMPLEMENTATION.md`
- **Maquettes**: `issues/ISSUE-46-TIMELINE-VIEW-MOCKUP.md`
- **Résumé**: `issues/ISSUE-46-SUMMARY.md`

## 📞 Support

En cas de problème:
1. Vérifier `chk-roon.json` existe avec tracks
2. Vérifier `roon-config.json` existe
3. Lancer avec: `streamlit run src/gui/musique-gui.py`
4. Console navigateur (F12) pour erreurs JS/CSS

---

**Version**: v3.4.0 | **Date**: 28 janvier 2026 | **Status**: ✅ Production
