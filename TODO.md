# 📋 TODO - Liste des tâches et améliorations

> 📌 **Voir aussi**: [ROADMAP.md](ROADMAP.md) pour la vision stratégique à long terme (court, moyen et long terme)

## 🔴 Priorité Haute

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

### Interface Web (musique-gui.py)
- [ ] Export CSV/JSON filtré depuis l'interface
- [ ] Graphiques temporels (lectures par jour/semaine/mois)
- [ ] Tri personnalisé des listes (date, artiste, album, plays)
- [ ] Pagination si >1000 pistes (performance)
- [ ] Détection albums complets (5+ pistes dans une session)
- [ ] Mode sombre / thème personnalisable
- [ ] Responsive mobile (layout adaptatif)

### Analyse et rapports
- [ ] Dashboard avec statistiques avancées
- [ ] Détection de patterns d'écoute par genre
- [ ] Recommandations basées sur l'historique
- [ ] Export PDF des rapports d'analyse
- [ ] Intégration avec Spotify playlists

### Tracker Roon (chk-roon.py)
- [ ] Support multi-utilisateurs avec base de données
- [ ] Notifications push lors de nouvelles lectures
- [ ] Intégration avec Discord/Telegram
- [ ] Support d'autres services (Tidal, Qobuz)

---

## 🟢 Priorité Basse

### Maintenance et qualité
- [ ] Tests unitaires pour tous les modules
- [ ] Documentation API complète (Sphinx)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Dockerfile pour déploiement conteneurisé
- [ ] Logging structuré (Winston/structlog)

### Features expérimentales
- [ ] Reconnaissance vocale pour recherche
- [ ] Intégration lyrics/paroles
- [ ] Visualisations audio (spectrogrammes)
- [ ] Support podcasts et audiobooks

---

## ✅ Complété

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

**Dernière mise à jour:** 25 janvier 2026  
**Mainteneur:** Patrick Ostertag
