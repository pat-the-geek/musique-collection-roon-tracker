# 📋 TODO - Liste des tâches et améliorations

> 📌 **Voir aussi**: [ROADMAP.md](ROADMAP.md) pour la vision stratégique à long terme (court, moyen et long terme)

## ✅ Complété Récemment

### v3.4.0 (28 janvier 2026)
- ✅ **Issue #46** - Timeline View pour visualisation horaire des écoutes
  - Vue Timeline avec navigation horizontale par heures (6h-23h)
  - Alternance de couleurs par heure pour meilleure lisibilité
  - Modes compact (pochettes seules) et détaillé (pochettes + métadonnées)
  - Sélecteur de date avec format lisible
  - Statistiques journalières (total, uniques, peak hour)
  - Limitation à 20 tracks max par heure pour performance
- ✅ **Issue #57** - Fix Timeline Roon pour cas limites
  - Amélioration robustesse parsing dates
  - Fix affichage heures vides
  - Optimisation performances pour grandes collections

### v3.3.1 (27 janvier 2026)
- ✅ **Issue #38** - Éviter doublons lors de la création de playlists
  - Détection et suppression automatique des doublons
  - Normalisation des métadonnées (artiste + titre + album)
  - Affichage du nombre de doublons supprimés
- ✅ **Issue #32** - Correction timezone décalage horaire (1h de différence)
  - Correction dans chk-roon.py (3 endroits)
  - Correction dans chk-last-fm.py
  - Ajout test_timestamp_fix.py (5 tests)
  - Script de vérification verify_timezone_fix.py
  - Documentation complète FIX-TIMEZONE-ISSUE-32.md
- ✅ **Issue #19** - Génération de playlists basée sur patterns d'écoute
  - Nouveau module generate-playlist.py (800+ lignes)
  - 7 algorithmes de génération (top_sessions, artist_correlations, etc.)
  - Support génération par IA avec prompt personnalisé
  - Export multi-formats (JSON, M3U, CSV, TXT)
  - Intégration avec scheduler pour génération automatique

### v3.3.0+ (27 janvier 2026)
- ✅ **Issue #28** - Amélioration infrastructure de tests
- ✅ Conversion test_ai_service.py de tests manuels → 37 tests pytest
- ✅ Correction 3 tests défaillants dans test_metadata_cleaner.py
- ✅ Création test_chk_roon_integration.py (5 tests réels + 23 stubs blueprint)
- ✅ 223/223 tests passants (100%)
- ✅ Couverture globale 91% (était 88%)

### v3.3.0 (27 janvier 2026)
- ✅ **Issue #21** - Intégration IA pour enrichissement automatique des albums
- ✅ Service AI centralisé (`ai_service.py`)
- ✅ Journal technique IA avec logs quotidiens (24h retention)
- ✅ Affichage info IA dans interface GUI (expandeurs)
- ✅ Tests unitaires pour service IA (37 tests)
- ✅ **Issue #18** - Application Web fonctionne sur Safari iPhone (responsive design)
- ✅ **Issue #15** - Lancement simultané Roon tracker + Streamlit (start-all.sh)
- ✅ **Issue #13** - Configuration Streamlit pour accès réseau (0.0.0.0:8501)
- ✅ **Issue #9** - Affichage haïkus depuis fichier markdown (correctif GUI)

### v3.2.0 (25 janvier 2026)
- ✅ **Issue #23** - Amélioration qualité code et tests
- ✅ Système de scheduler complet avec 4 tâches planifiées
- ✅ Intégration scheduler dans tracker Roon
- ✅ Configuration du scheduler via interface GUI
- ✅ Visualisation des haïkus et rapports dans GUI
- ✅ Tests unitaires pour scheduler (29 tests, 302 lignes)

## 🔴 Priorité Haute

### Détection fausse albums lors stations de radio (Issue #31)
**Statut:** En analyse  
**Date:** 27 janvier 2026  
**Impact:** Moyen (génération d'entrées incorrectes dans le journal)

**Description:**
Le système détecte à tort des albums lors de l'écoute de stations de radio. 
Exemple: "La 1ère" (station RTS) identifiée comme artiste avec album "Stella Nera".

**Cause identifiée:**
- Pattern de détection trop permissif pour les radios
- Stations de radio non référencées dans roon-config.json
- Génération d'info IA pour des artistes/albums inexistants

**Solutions potentielles à explorer:**
- [ ] Améliorer la détection des patterns radio dans chk-roon.py
- [ ] Ajouter validation croisée avec APIs musicales avant génération IA
- [ ] Créer liste blanche/noire de stations connues
- [ ] Ajouter filtrage post-détection pour éliminer faux positifs

**Lié à Issue #26**: Hallucinations IA pour descriptions albums radio

**Références:**
- `src/trackers/chk-roon.py` : Fonction de détection radio (ligne ~600-700)
- `data/config/roon-config.json` : Liste stations radio existantes

---

### Problème de cache d'images Streamlit
**Statut:** Non résolu  
**Date:** 25 janvier 2026  
**Impact:** Moyen (messages d'erreur console, pas de blocage fonctionnel)

**Description:**
Erreurs `MediaFileStorageError` lors des reruns Streamlit :
```
MediaFileStorageError: Bad filename 'xxx.jpg'. 
(No media file with id 'xxx')
```

**Cause identifiée:**
- Cache interne Streamlit invalide les IDs d'images en mémoire
- Se produit aléatoirement lors de la navigation entre vues
- Problème survient même avec `@st.cache_resource` et `try/except`

**Tentatives de correction:**
1. ✅ Ajout `try/except` autour de tous les `st.image()` - Partiellement efficace
2. ✅ Migration `@st.cache_data` → `@st.cache_resource` - Toujours des erreurs
3. ❌ Désactivation du cache - Non testé (impact performance)

**Solutions potentielles à explorer:**
- [ ] Charger les images en base64 directement dans le HTML
- [ ] Utiliser `st.image(url)` directement sans cache PIL
- [ ] Implémenter un cache custom avec diskcache ou joblib
- [ ] Rapporter le bug à Streamlit (vérifier si déjà connu)
- [ ] Migrer vers une autre solution d'affichage (HTML img tags)

**Références:**
- `src/gui/musique-gui.py` : Fonction `load_image_from_url()` ligne ~740
- `docs/README-MUSIQUE-GUI.md` : Section "Problèmes connus"

---

## 🟡 Priorité Moyenne

### Hallucinations IA pour descriptions albums radio (Issue #26)
**Statut:** En analyse  
**Date:** 27 janvier 2026  
**Impact:** Faible (qualité données, pas de blocage)

**Description:**
L'IA génère des descriptions inventées pour certains albums détectés depuis des stations de radio.

**Cause identifiée:**
- Prompt IA ne spécifie pas clairement de refuser si données inexistantes
- Albums/artistes fictifs passent la validation
- Pas de vérification croisée avec base de données musicales

**Solutions:**
- [ ] Améliorer le prompt IA pour éviter les hallucinations
- [ ] Ajouter validation via MusicBrainz ou Spotify avant génération IA
- [ ] Retourner message explicite "Aucune information disponible" si album introuvable
- [ ] Filtrer les entrées radio avant envoi à l'IA

**Lié à Issue #31**: Détection fausse albums

**Références:**
- `src/services/ai_service.py` : Fonction `generate_album_info()` (ligne ~150-200)
- `resources/prompts/` : Templates de prompts IA

---

### Paramètre nombre maximum fichiers output (Issue #17)
**Statut:** En attente  
**Date:** 26 janvier 2026  
**Impact:** Faible (maintenance manuelle nécessaire)

**Description:**
Les répertoires `output/haikus`, `output/reports`, `output/playlists` accumulent des fichiers sans limite.

**Solutions proposées:**
- [ ] Ajouter paramètre `max_output_files` dans `roon-config.json` (défaut: 10)
- [ ] Créer fonction de nettoyage automatique dans chaque générateur
- [ ] Ajouter configuration dans l'interface GUI (page Paramètres)
- [ ] Appliquer rétention lors de la création de nouveaux fichiers
- [ ] Documenter dans README-ROON-CONFIG.md

**Estimation:** 1-2 jours  
**Bénéfice:** Gestion automatique de l'espace disque, maintenance réduite

---

### Intelligence Artificielle
- [x] Génération automatique de descriptions d'albums via IA (v3.3.0) ✅
- [x] Fallback intelligent Discogs → IA (v3.3.0) ✅
- [ ] Support multilingue (EN, FR, DE, IT) pour descriptions IA
- [ ] Feedback utilisateur sur qualité des descriptions
- [ ] Cache persistant des descriptions IA (au-delà de 24h)
### Interface Web (musique-gui.py)
- [ ] Export CSV/JSON filtré depuis l'interface
- [ ] Graphiques temporels (lectures par jour/semaine/mois)
- [ ] Tri personnalisé des listes (date, artiste, album, plays)
- [ ] Pagination si >1000 pistes (performance)
- [ ] Détection albums complets (5+ pistes dans une session)
- [ ] Mode sombre / thème personnalisable
- [ ] Responsive mobile (layout adaptatif)

### Analyse et rapports
- [x] Système de scheduler pour tâches automatiques (v3.2.0) ✅
- [x] Génération automatique de haikus via scheduler (v3.2.0) ✅
- [x] Analyse des patterns d'écoute automatisée (v3.2.0) ✅
- [x] Génération de playlists basée sur patterns d'écoute (v3.3.1) ✅ **Issue #19**
- [x] Export playlists multi-formats (JSON, M3U, CSV, TXT) ✅
- [x] Génération playlists avec IA via prompt personnalisé ✅
- [ ] Dashboard avec statistiques avancées
- [ ] Détection de patterns d'écoute par genre
- [ ] Recommandations basées sur l'historique
- [ ] Export PDF des rapports d'analyse

### Tracker Roon (chk-roon.py)
- [ ] Support multi-utilisateurs avec base de données
- [ ] Notifications push lors de nouvelles lectures
- [ ] Intégration avec Discord/Telegram
- [ ] Support d'autres services (Tidal, Qobuz)

---

## 🟢 Priorité Basse

### Maintenance et qualité
- [x] Infrastructure de tests unitaires (v3.1.0) ✅
- [x] Tests pour metadata_cleaner (27 tests, 98% couverture) ✅ - **3 échecs corrigés (Issue #28)**
- [x] Tests pour scheduler (29 tests, 47% couverture) ✅
- [x] Tests pour spotify_service (49 tests, 88% couverture) ✅
- [x] Tests pour constants (57 tests, 100% couverture) ✅
- [x] Tests unitaires pytest pour ai_service (37 tests, 97% couverture) ✅ **COMPLÉTÉ (Issue #28)**
- [x] Tests d'intégration pour chk-roon.py (28 tests: 5 réels + 23 stubs blueprint) ✅ **PARTIELLEMENT (Issue #28)**
- [ ] Compléter les 23 tests stubs restants dans test_chk_roon_integration.py
- [ ] Documentation API complète (Sphinx)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Dockerfile pour déploiement conteneurisé
- [ ] Logging structuré (Winston/structlog)

**Infrastructure de tests actuelle**: 
- **228 tests unitaires** (était 223)
- **~2340 lignes de code de tests** (était ~2300)
- **91% couverture globale** (maintenue)
- **100% tests passants** (228/228) ✅
- **Issue #28**: +61 tests, +3% couverture, 3 échecs corrigés
- **Issue #32**: +5 tests timezone (test_timestamp_fix.py)

### Features expérimentales
- [ ] Reconnaissance vocale pour recherche
- [ ] Intégration lyrics/paroles
- [ ] Visualisations audio (spectrogrammes)
- [ ] Support podcasts et audiobooks

---

## ✅ Complété

### v3.3.1 (27 janvier 2026) - Issues #38, #32, #19
- ✅ **Issue #38** - Éviter doublons lors création playlists
  - Normalisation métadonnées (artiste + titre + album)
  - Détection automatique doublons
  - Affichage nombre doublons supprimés
- ✅ **Issue #32** - Correction timezone décalage horaire
  - 4 corrections dans trackers (chk-roon.py, chk-last-fm.py)
  - Ajout tests timezone (5 tests)
  - Script migration verify_timezone_fix.py
  - Documentation FIX-TIMEZONE-ISSUE-32.md
- ✅ **Issue #19** - Génération playlists patterns d'écoute
  - Module generate-playlist.py complet (800+ lignes)
  - 7 algorithmes génération + IA
  - Export multi-formats (JSON, M3U, CSV, TXT Roon)
  - Intégration scheduler
  - Détection/suppression doublons automatique (v1.2.0)

### v3.3.0+ (27 janvier 2026) - Issue #28
- ✅ **Amélioration infrastructure de tests**
- ✅ Conversion test_ai_service.py: tests manuels → 37 tests pytest
- ✅ Correction 3 tests défaillants metadata_cleaner
  - `test_empty_list`: Gestion liste vide
  - `test_partial_match`: Correction expectation score
  - `test_empty_strings`: Vérification chaînes vides
- ✅ Création test_chk_roon_integration.py (28 tests)
  - 5 tests réels implémentés
  - 23 stubs blueprint pour futures implémentations
- ✅ 223/223 tests passants (100%)
- ✅ Couverture globale 91% (+3%)
- ✅ Documentation complète: tests/TEST-STATUS.md, issues/ISSUE-28-TEST-IMPROVEMENTS.md

### v3.3.0 (27 janvier 2026)
- ✅ Intégration IA pour enrichissement automatique des albums
- ✅ Service AI centralisé avec API EurIA (Qwen3)
- ✅ Journal technique IA avec logs quotidiens (24h retention)
- ✅ Fallback Discogs → IA pour optimisation
- ✅ Interface GUI enrichie avec expandeurs Info IA
- ✅ Tests unitaires pour service IA

### v3.2.0 (25 janvier 2026)
- ✅ Système de scheduler complet (4 tâches planifiées)
- ✅ Intégration transparente dans tracker Roon
- ✅ Configuration scheduler via GUI
- ✅ Visualisation haïkus et rapports dans GUI
- ✅ Tests unitaires scheduler (302 lignes)

### v3.1.0 (24 janvier 2026)
- ✅ Module services partagés (spotify_service, metadata_cleaner)
- ✅ Constantes centralisées (constants.py, 100+ constantes)
- ✅ Infrastructure de tests complète (pytest + fixtures)
  - ✅ 49 tests spotify_service (88% couverture)
  - ✅ 57 tests constants (100% couverture)
  - ✅ 27 tests metadata_cleaner (~95% couverture)
  - ✅ Total: 133 tests unitaires au total pour v3.1.0
- ✅ Corrections imports dupliqués

### v3.0.0 (23 janvier 2026)
- ✅ Réorganisation complète en structure modulaire
- ✅ Séparation stricte `src/`, `data/`, `output/`, `docs/`
- ✅ Backups organisés par type et horodatage
- ✅ Documentation centralisée

### v2.2.0 (21 janvier 2026)
- ✅ Validation stricte artiste Spotify avec scoring
- ✅ Retry automatique sur erreurs 401/429
- ✅ Gestion intelligente des stations de radio

### v2.1.0 (20-21 janvier 2026)
- ✅ Interface Web Streamlit avec génération résumés EurIA
- ✅ Journal Roon avec triple affichage images
- ✅ Détection doublons albums (generate-haiku.py)

---

**Dernière mise à jour:** 27 janvier 2026 (v3.3.1 - Issues #38, #32, #19 complétées)  
**Mainteneur:** Patrick Ostertag
