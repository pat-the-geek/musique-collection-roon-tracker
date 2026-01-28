# 🎵 Release Notes - Version 3.3.1

**Date de publication:** 27 janvier 2026  
**Version:** 3.3.1 (Génération Playlists + Timezone Fix + Déduplication)  
**Auteur:** Patrick Ostertag

---

## 📋 Résumé Exécutif

La version 3.3.1 apporte des fonctionnalités majeures et des corrections critiques au projet Musique Collection & Roon Tracker. Cette version se concentre sur l'amélioration de l'expérience utilisateur avec la génération intelligente de playlists, la correction d'un bug d'affichage de l'heure, et l'amélioration de la qualité des données générées.

---

## 🎯 Nouvelles Fonctionnalités

### 🎵 Génération de Playlists Intelligentes (Issue #19)

**Module:** `src/analysis/generate-playlist.py` (800+ lignes)

#### Caractéristiques principales
- **7 algorithmes de génération** pour créer des playlists adaptées à différents besoins:
  - `top_sessions`: Pistes des sessions d'écoute les plus longues
  - `artist_correlations`: Artistes souvent écoutés ensemble
  - `artist_flow`: Transitions naturelles entre artistes
  - `time_based`: Pistes selon périodes temporelles
  - `complete_albums`: Albums écoutés en entier
  - `rediscovery`: Pistes aimées mais non écoutées récemment
  - `ai_generated`: 🆕 Génération par IA avec prompt personnalisé

#### Export multi-formats
- **JSON**: Métadonnées complètes avec images
- **M3U**: Compatible VLC, iTunes, Foobar2000
- **CSV**: Import Excel/Google Sheets
- **TXT (Roon)**: Instructions d'import manuel dans Roon

#### Intégration scheduler
- Configuration via `roon-config.json`
- Génération automatique planifiée
- Support prompt IA personnalisé
- Paramétrage flexible (type, fréquence, formats)

#### Utilisation
```bash
# Génération manuelle
cd src/analysis
python3 generate-playlist.py --algorithm top_sessions --max-tracks 25

# Génération avec IA
python3 generate-playlist.py --algorithm ai_generated --ai-prompt "jazz cool pour le soir"
```

**Documentation:** [docs/README-GENERATE-PLAYLIST.md](docs/README-GENERATE-PLAYLIST.md)

---

## 🔧 Corrections et Améliorations

### 🔧 Déduplication Automatique (Issue #38, v1.2.0)

**Problème résolu:** Les playlists générées contenaient des doublons dus à des variations mineures dans les métadonnées.

**Solution implémentée:**
- Détection automatique des doublons par normalisation
- Clé normalisée: (artiste + titre + album)
- Ignore variations de casse et espaces
- Affichage du nombre de doublons supprimés
- Appliqué à toutes les playlists générées

**Exemple:**
```
AVANT (avec doublons):
1. The Clash - London Calling (remastered)
2. The Clash - London Calling (Remastered)  ← DOUBLON
3. Roxy Music - Love Is the Drug
4. Roxy Music - Love Is The Drug  ← DOUBLON

APRÈS (dédupliqués):
1. The Clash - London Calling (remastered)
2. Roxy Music - Love Is the Drug

Doublons supprimés: 2
```

**Impact:**
- Playlists plus propres et cohérentes
- Amélioration de la qualité des exports
- Réduction de la redondance

---

### 🕐 Correction Timezone (Issue #32)

**Problème résolu:** Les timestamps affichaient l'heure UTC au lieu de l'heure locale, causant un décalage d'1 heure (en CET).

**Exemples de problème:**
- Écoute réelle: 11:19 CET
- Affichage journal: 10:19 (UTC)
- Différence: -1 heure ❌

**Solution implémentée:**
- Ajout de `.astimezone()` pour conversion UTC → local time
- 4 corrections dans le code:
  - `chk-roon.py`: 3 endroits (logs IA, tracks JSON)
  - `chk-last-fm.py`: 1 endroit (display date)

**Code corrigé:**
```python
# AVANT (incorrect)
datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M')

# APRÈS (correct)
datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
```

**Impact:**
- Journal Roon affiche l'heure locale correcte
- Journal IA affiche l'heure locale correcte
- Logs quotidiens utilisent l'heure locale
- Meilleure expérience utilisateur

**Tests ajoutés:**
- `test_timestamp_fix.py`: 5 tests unitaires
  - Conversion timestamp → local time
  - Format avec secondes
  - Timezone awareness
  - Cas spécifiques

**Documentation:**
- [TIMEZONE-FIX-SUMMARY.md](TIMEZONE-FIX-SUMMARY.md)
- [docs/FIX-TIMEZONE-ISSUE-32.md](docs/FIX-TIMEZONE-ISSUE-32.md)

**Outil de vérification:**
- `scripts/verify_timezone_fix.py`: Script pour vérifier/migrer anciennes entrées

---

## 📊 Statistiques Techniques

### Tests Unitaires
- **Total tests:** 228 tests (+5 depuis v3.3.0)
- **Nouveaux tests timezone:** 5 tests (test_timestamp_fix.py)
- **Couverture globale:** 91% (maintenue)
- **Taux de succès:** 100% (228/228 passants) ✅

### Lignes de Code
- **generate-playlist.py:** 800+ lignes
- **test_timestamp_fix.py:** 39 lignes
- **Code de tests total:** ~2340 lignes (+40)

### Fichiers Modifiés
- `src/analysis/generate-playlist.py` (nouveau)
- `src/trackers/chk-roon.py` (3 corrections)
- `src/trackers/chk-last-fm.py` (1 correction)
- `src/tests/test_timestamp_fix.py` (nouveau)
- `scripts/verify_timezone_fix.py` (nouveau)

### Documentation Ajoutée
- `docs/README-GENERATE-PLAYLIST.md` (15 KB, guide complet)
- `TIMEZONE-FIX-SUMMARY.md` (3 KB, résumé corrections)
- `docs/FIX-TIMEZONE-ISSUE-32.md` (documentation complète)

---

## 📋 Issues Fermées

### v3.3.1 (27 janvier 2026)
- ✅ **Issue #38:** Éviter doublons lors création playlists
- ✅ **Issue #32:** Correction timezone décalage horaire
- ✅ **Issue #19:** Génération playlists basée sur patterns d'écoute

**Total issues fermées cette version:** 3

---

## 🔄 Migration et Compatibilité

### Rétrocompatibilité
- ✅ Toutes les fonctionnalités existantes sont préservées
- ✅ Aucun changement breaking dans l'API interne
- ✅ Fichiers de données existants restent valides
- ⚠️ Anciennes entrées JSON conservent format UTC (outil migration disponible)

### Migration Timezone
Pour convertir les anciennes entrées au format local time:
```bash
cd scripts
python3 verify_timezone_fix.py
```

**Note:** La migration est optionnelle, les nouvelles entrées utilisent automatiquement le bon format.

---

## 📦 Installation et Mise à Jour

### Pour Utilisateurs Existants
```bash
# Mettre à jour le dépôt
git pull origin main

# Pas de nouvelles dépendances Python nécessaires
# Les modules existants suffisent

# Redémarrer le tracker pour appliquer les corrections timezone
./start-roon-tracker.sh
```

### Pour Nouveaux Utilisateurs
```bash
# Installation standard
./scripts/setup-roon-tracker.sh

# Lancement
./start-all.sh  # Tracker + GUI simultanés
```

---

## 🚀 Recommandations d'Utilisation

### Génération de Playlists
1. **Première utilisation**: Tester avec `top_sessions` (algorithme simple et efficace)
2. **Exploration**: Essayer `artist_correlations` pour découvrir des connexions
3. **Créativité**: Utiliser `ai_generated` avec des prompts variés
4. **Automatisation**: Configurer le scheduler pour génération hebdomadaire

### Timezone
- Les nouvelles lectures utilisent automatiquement le format correct
- Les anciennes entrées peuvent être migrées avec l'outil fourni
- Aucune action requise pour utilisation normale

### Déduplication
- Automatique dans toutes les playlists générées
- Pas de configuration nécessaire
- Le nombre de doublons supprimés est affiché

---

## 🐛 Problèmes Connus

Aucun nouveau problème identifié dans cette version.

### Issues Ouvertes (Non Critiques)
- **Issue #31:** Détection fausse albums lors stations radio (en analyse)
- **Issue #26:** Hallucinations IA pour descriptions albums radio (en analyse)
- **Issue #17:** Paramètre nombre max fichiers output (basse priorité)

---

## 📚 Documentation

### Nouveaux Documents
- **[docs/README-GENERATE-PLAYLIST.md](docs/README-GENERATE-PLAYLIST.md):** Guide complet génération playlists
- **[TIMEZONE-FIX-SUMMARY.md](TIMEZONE-FIX-SUMMARY.md):** Résumé corrections timezone
- **[docs/FIX-TIMEZONE-ISSUE-32.md](docs/FIX-TIMEZONE-ISSUE-32.md):** Documentation détaillée timezone

### Documents Mis à Jour
- **[TODO.md](TODO.md):** Issues v3.3.1 complétées, nouvelles issues ouvertes
- **[ROADMAP.md](ROADMAP.md):** Section v3.3.1, statistiques tests mises à jour
- **[README.md](README.md):** Nouvelles fonctionnalités v3.3.1, version actuelle

---

## 🎯 Prochaines Étapes (v3.3.2+)

### Priorité Haute
- [ ] Améliorer détection radios (Issue #31)
- [ ] Réduire hallucinations IA (Issue #26)

### Priorité Moyenne
- [ ] Paramètre max fichiers output (Issue #17)
- [ ] Tests intégration playlist generator
- [ ] Documentation vidéo génération playlists

### Priorité Basse
- [ ] Interface GUI pour génération playlists manuelle
- [ ] Visualisation statistiques playlists générées
- [ ] Export playlists vers services streaming

---

## 👥 Contributeurs

**Développeur Principal:** Patrick Ostertag  
**Assistance IA:** GitHub Copilot AI Agent  
**Tests et QA:** Patrick Ostertag

---

## 📞 Support et Feedback

- **Issues GitHub:** [github.com/pat-the-geek/musique-collection-roon-tracker/issues](https://github.com/pat-the-geek/musique-collection-roon-tracker/issues)
- **Email:** patrick.ostertag@gmail.com
- **Documentation:** [docs/](docs/)

---

## 🙏 Remerciements

Merci à tous les utilisateurs qui ont remonté des bugs et suggéré des améliorations, notamment:
- Issue #19: Suggestion de génération de playlists
- Issue #32: Signalement du bug timezone
- Issue #38: Identification des doublons dans les playlists

---

**Date de publication:** 27 janvier 2026  
**Version:** 3.3.1  
**Statut:** ✅ Stable et prêt pour production

---

[⬅️ Retour au README](README.md) | [📋 TODO](TODO.md) | [🗺️ ROADMAP](ROADMAP.md)
