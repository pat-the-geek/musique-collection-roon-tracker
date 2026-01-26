# 🎵 Musique GUI - Interface Streamlit

Interface web moderne pour visualiser, éditer et gérer une collection musicale avec historique d'écoute Roon/Last.fm.

## 🎯 Objectif Principal

**Créer des fichiers JSON exploitables avec URLs publiques**

En enregistrant les lectures musicales avec des URLs d'images publiques (Spotify, Last.fm) plutôt que des références internes Roon, le système permet:

- ✅ **Exploitation par IA**: Génération de résumés, descriptions, analyses sans accès direct à Roon
- ✅ **Traitement automatisé**: Scripts Python peuvent accéder aux images et métadonnées
- ✅ **Intégration externe**: Autres logiciels peuvent consommer les données JSON
- ✅ **Persistance**: URLs publiques restent accessibles indépendamment de Roon
- ✅ **Portabilité**: Données utilisables sur n'importe quel système

Le fichier `chk-roon.json` devient ainsi une **source de données universelle** exploitable par n'importe quel outil moderne.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Interface utilisateur](#interface-utilisateur)
- [Modifications récentes](#modifications-récentes)
- [Intégration](#intégration)

## 🌟 Vue d'ensemble

Application Streamlit complète intégrant trois sources de données musicales :
- **Collection Discogs** : Albums avec métadonnées complètes
- **Historique Roon/Last.fm** : Lectures musicales en temps réel
- **Métadonnées films** : Cross-référence pour bandes originales

## ✨ Fonctionnalités

### Collection Discogs
- 🔍 Recherche et filtrage (titre, artiste)
- 🎬 Filtre spécifique bandes originales
- 📝 Édition en ligne avec sauvegarde JSON
- 🖼️ Double affichage images (Discogs + Spotify)
- 🔗 Liens directs Spotify et Discogs
- 📊 Métadonnées films pour BOF
- 📄 Résumés générés par IA (EurIA API)
- 🤖 Génération de résumé à la demande (bouton intégré)

### Journal Roon
- 📻 Visualisation chronologique des écoutes
- 🔍 Filtres multiples (source, recherche, favoris)
- 🖼️ Triple affichage images :
  - Image artiste (Spotify)
  - Pochette album (Spotify)
  - Pochette album (Last.fm)
- 📊 Statistiques temps réel
- ❤️ Marquage favoris
- 📱 Interface compacte et optimisée

## 🔧 Installation

### Prérequis
```bash
# Python 3.8+
python --version

# Streamlit
pip install streamlit pillow requests
```

### Fichiers requis
```
musique-gui.py                 # Application principale
discogs-collection.json        # Collection Discogs
chk-roon.json                  # Historique Roon/Last.fm
soundtrack.json                # Métadonnées films (optionnel)
.env                           # Variables d'environnement (EurIA API)
```

### Configuration EurIA
Créer un fichier `.env` avec les clés API EurIA :
```env
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=votre_token_euria
```

### Configuration Streamlit (réseau)

Le projet inclut une configuration Streamlit (`.streamlit/config.toml`) qui permet l'accès depuis d'autres machines du réseau :

```toml
[server]
address = "0.0.0.0"           # Écoute sur toutes les interfaces
port = 8501                    # Port par défaut
enableCORS = false             # Désactive CORS
enableXsrfProtection = false   # Désactive protection XSRF
```

Cette configuration est **automatiquement appliquée** au lancement de Streamlit. Aucune action supplémentaire requise.

**Personnalisation :** Vous pouvez modifier `.streamlit/config.toml` pour ajuster le port ou d'autres paramètres selon vos besoins.

**🦁 Safari :** Pour accès réseau, changez l'User-Agent en "Edge" (Safari > Développement > Agent utilisateur > Microsoft Edge). Safari fonctionne ensuite parfaitement.

## 🚀 Utilisation

### Lancement simple
```bash
streamlit run musique-gui.py
```

### Lancement avec script
```bash
./start-streamlit.sh
```

### Accès à l'interface

#### Accès local
L'application s'ouvre automatiquement dans le navigateur sur `http://localhost:8501`

#### Accès réseau
Grâce à la configuration `.streamlit/config.toml`, l'interface est accessible depuis d'autres machines du réseau local :

```
http://[adresse-ip-serveur]:8501
```

**Exemple :** Si le serveur a l'IP `192.168.1.100`, accédez via `http://192.168.1.100:8501`

**Pour trouver l'adresse IP du serveur :**
```bash
# Linux/macOS
hostname -I

# Ou
ip addr show
```

**Note de sécurité :** Cette configuration désactive CORS et XSRF pour faciliter l'accès réseau. À utiliser uniquement dans un réseau local de confiance.

#### Compatibilité navigateurs (accès réseau)

✅ **Tous les navigateurs supportés** - y compris Safari avec configuration spéciale :

**Navigateurs fonctionnant nativement :**
- **Microsoft Edge** : Fonctionne parfaitement
- **Google Chrome** : Fonctionne parfaitement
- **Mozilla Firefox** : Fonctionne parfaitement

**Safari - Solution de contournement :**
- ⚠️ Safari bloque les WebSockets Streamlit en accès réseau par défaut
- ✅ **Solution** : Changer l'User-Agent en "Edge" dans Safari
  - **Safari > Développement > Agent utilisateur > Microsoft Edge**
  - L'interface fonctionnera alors parfaitement
- Cette restriction Safari est basée sur l'User-Agent, pas sur la technologie

**Note :** En accès local (`localhost:8501`), Safari fonctionne normalement sans configuration. Le problème n'affecte que l'accès depuis d'autres machines du réseau.

## 🏗️ Architecture

### Structure des données

#### discogs-collection.json
```json
{
    "release_id": 123456,
    "Titre": "Kind of Blue",
    "Artiste": ["Miles Davis"],
    "Année": 1959,
    "Spotify_Date": 2015,
    "Labels": ["Columbia"],
    "Support": "Vinyle",
    "Pochette": "https://...",
    "Spotify_URL": "https://open.spotify.com/...",
    "Spotify_Cover_URL": "https://...",
    "Resume": "Description détaillée..."
}
```

#### chk-roon.json
```json
{
    "tracks": [
        {
            "timestamp": 1768648694,
            "date": "2026-01-21 14:30",
            "artist": "Nina Simone",
            "title": "Feeling Good",
            "album": "I Put a Spell on You",
            "loved": false,
            "artist_spotify_image": "https://...",
            "album_spotify_image": "https://...",
            "album_lastfm_image": "https://...",
            "source": "roon"
        }
    ]
}
```

### Flux de données
```
┌─────────────────┐
│  chk-roon.py    │──┐
│  (v2.2.0)       │  │
└─────────────────┘  │
                     ├──► chk-roon.json ──┐
┌─────────────────┐  │                    │
│  chk-last-fm.py │──┘                    │
└─────────────────┘                       │
                                          ▼
┌─────────────────┐              ┌──────────────┐
│ Read-discogs-   │──────────►   │ musique-gui  │
│ ia.py           │              │   .py        │
└─────────────────┘              └──────────────┘
        │                               ▲
        ▼                               │
discogs-collection.json ────────────────┘
```

## 📸 Captures d'écran

Des captures d'écran de l'interface sont disponibles dans [samples/](../samples/) :

### Interface Streamlit
- **[Vue principale Collection Discogs](../samples/Screen%20Capture%20-%20musique-gui.py%20-%20Bibliothèque%20Discogs%20-%20Main.png)** : Interface complète avec sidebar, recherche et détails album
- **[Onglet Album Art](../samples/Screen%20Capture%20-%20musique-gui.py%20-%20Bibliothèque%20Discogs%20-%20Album%20Art.png)** : Gestion pochettes Discogs et Spotify
- **[Onglet Liens](../samples/Screen%20Capture%20-%20musique-gui.py%20-%20Bibliothèque%20Discogs%20-%20Links%20Spotify%20-%20Discogs.png)** : Liens externes Spotify et Discogs
- **[Métadonnées Soundtrack](../samples/Screen%20Capture%20-%20musique-gui.py%20-%20Bibliothèque%20Discogs%20-%20Soundtrack%20informations.png)** : Affichage enrichi bandes originales avec info film
- **[Journal Roon](../samples/Screen%20Capture%20-%20musique-gui.py%20-%20Roon%20Journal.png)** : Historique écoutes avec triple affichage images

### Exports
- **[Collection Markdown](../samples/discogs-collection.md)** : Exemple export Markdown complet
- **[Collection PDF](../samples/discogs-collection.pdf)** : Version imprimable collection
- **[Présentation Haïku PDF](../samples/generate-haiku-20260124-092110.pdf)** : Exemple génération iA Presenter
- **[Rapport Patterns](../samples/listening-patterns-20260120-165954.txt)** : Exemple analyse d'écoute

## 🎨 Interface utilisateur

### Navigation
- **📀 Collection Discogs** : Gestion collection
- **📻 Journal Roon** : Historique écoutes

### Layout Journal Roon (optimisé v2.0)

```
┌─────────────────────────────────────┬─────────────────────────────┐
│ Date: 2026-01-21 14:30      Source: Roon        ❤️ Aimé          │
├─────────────────────────────────────┼─────────────────────────────┤
│ 🎤 Nina Simone                      │ [img] [img] [img]          │
│ Feeling Good                        │  🎤   💿S   💿L            │
│ I Put a Spell on You                │ 100px 100px 100px          │
└─────────────────────────────────────┴─────────────────────────────┘
```

### Génération de résumé EurIA (v2.1)

Interface de génération dans l'onglet "Informations" :

```
┌──────────────────────────────────────────────────────┐
│ **Résumé**                                           │
├──────────────────────────────────┬───────────────────┤
│ [Zone de texte résumé]           │ 🤖 Générer avec  │
│ (200px height)                   │    EurIA         │
│                                  │                   │
│ Résumé existant ou généré...     │ (bouton)         │
└──────────────────────────────────┴───────────────────┘
```

**Processus :**
1. Clic sur "🤖 Générer avec EurIA"
2. Spinner : "Génération en cours..."
3. Appel API EurIA avec prompt de 30 lignes
4. Sauvegarde automatique dans JSON
5. Rafraîchissement de l'interface
6. Message de confirmation

### Style CSS personnalisé
- Texte noir sur fond gris clair pour tous les champs
- Hauteur réduite des lignes (50% plus compact)
- Espacement minimal entre entrées
- Images optimisées (100px width)

## 📝 Modifications récentes

### Version 2.1 - 21 janvier 2026

#### Génération de résumé via EurIA API
✅ **Bouton intégré** : Génération à la demande dans l'onglet Informations  
✅ **API EurIA** : Utilise Qwen3 avec recherche web activée  
✅ **Résumés de 30 lignes** : Format identique à complete-resumes.py  
✅ **Sauvegarde automatique** : Mise à jour immédiate du JSON  
✅ **Gestion des erreurs** : Messages clairs en cas de problème  
✅ **Interface intuitive** : Layout 2 colonnes avec spinner pendant génération

#### Journal Roon - Optimisations visuelles (v2.0)
✅ **Images réduites 4x** : Passage de pleine largeur à 100px  
✅ **Layout réorganisé** : Texte à gauche (2/3), images à droite (1/3)  
✅ **Images horizontales** : Les 3 images alignées sur une ligne  
✅ **Interface compacte** : Hauteur de ligne réduite de 50%  
✅ **Style unifié** : Tous les champs avec fond gris clair et texte noir  
✅ **Espacement optimisé** : Marges réduites autour des dividers (0.5rem)

#### CSS ajouté
```css
/* Champs de saisie */
.stTextInput, .stTextArea, .stNumberInput, .stSelectbox {
    background-color: #f0f2f6;
    color: #000000;
}

/* Journal Roon compact */
.roon-track h3 {
    font-size: 1.2rem;
    margin: 0.2rem 0;
}

.roon-track p {
    margin-bottom: 0.2rem;
    line-height: 1.2;
}

/* Dividers compacts */
hr {
    margin: 0.5rem 0;
}
```

### Bénéfices des modifications
- 📊 **+100% de contenu visible** : Deux fois plus d'écoutes à l'écran
- 🎯 **Meilleure lisibilité** : Contraste texte amélioré
- 🚀 **Navigation fluide** : Moins de défilement nécessaire
- 💎 **Interface moderne** : Design cohérent et professionnel

## 🔗 Intégration

### Scripts liés
- `chk-roon.py` : Tracker Roon/Last.fm (v2.2.0)
- `chk-last-fm.py` : Tracker Last.fm standalone
- `Read-discogs-ia.py` : Import Discogs avec résumés IA
- `generate-haiku.py` : Génération présentations albums
- `complete-resumes.py` : Complétion résumés manquants
- `complete-images-roon.py` : Réparation images manquantes
- `analyze-listening-patterns.py` : Analytics avancées

### Documentation
- `README-ROON-TRACKER.md` : Documentation tracker Roon
- `.github/copilot-instructions.md` : Guide développement complet
- `ARCHITECTURE-OVERVIEW.md` : Diagrammes de flux

## 🎯 Workflow typique

1. **Lancement tracking** : `python chk-roon.py` (surveillance continue)
2. **Visualisation** : `streamlit run musique-gui.py`
3. **Navigation** : Basculer entre Collection et Journal
4. **Édition** : Modifier métadonnées dans l'interface
5. **Génération résumé** : Clic "🤖 Générer avec EurIA" pour créer un nouveau résumé
6. **Sauvegarde** : Clic "💾 Sauvegarder" pour persister (automatique pour résumés générés)

## 📊 Performance

- **Chargement initial** : ~200ms pour 500 albums
- **Filtrage** : <50ms (opérations Python pures)
- **Images** : Cache après 1er chargement
- **Scroll** : Virtualisé par Streamlit

## 🐛 Dépannage

### Interface ne s'affiche pas
```bash
# Vérifier Streamlit
streamlit --version

# Relancer proprement
streamlit run musique-gui.py --server.headless true
```

### Erreur JSON
```bash
# Vérifier fichiers
python -m json.tool discogs-collection.json
python -m json.tool chk-roon.json
```

### Images ne s'affichent pas
- Vérifier connexion Internet
- Les URLs doivent être HTTPS
- User-Agent Mozilla requis pour certains CDN

### ⚠️ Erreurs de cache d'images (Problème connu)

**Symptôme:**
```
MediaFileStorageError: Bad filename 'xxx.jpg'. 
(No media file with id 'xxx')
```

**Cause:**
- Problème de cache interne Streamlit lors des reruns
- Les IDs d'images en mémoire deviennent invalides
- Se produit aléatoirement lors de la navigation

**Impact:**
- Messages d'erreur dans la console (rouge)
- N'empêche pas l'utilisation de l'interface
- Les images se rechargent au prochain rerun

**Solution actuelle:**
- Try/except autour des `st.image()` pour éviter les crashs
- Cache avec `@st.cache_resource` au lieu de `@st.cache_data`
- **Limitation Streamlit non résolue** - nécessite investigation approfondie

**Workaround utilisateur:**
- Ignorer les messages rouges dans la console
- Rafraîchir la page (F5) si les images ne s'affichent pas
- Les erreurs n'affectent pas les données JSON

**Statut:** 🔴 Non résolu - voir TODO.md

## 🔮 Évolutions futures

- [ ] **Résoudre erreurs cache d'images Streamlit** (priorité haute)
- [ ] Export CSV/JSON filtré
- [ ] Graphiques temporels (lectures par jour)
- [ ] Tri personnalisé (date, artiste, album)
- [ ] Pagination si >1000 pistes
- [ ] Détection albums complets (5+ pistes)
- [ ] Mode sombre
- [ ] Responsive mobile

## 👤 Auteur

**Patrick Ostertag**  
Version: 2.1  
Date: 21 janvier 2026

## 📜 Licence

Projet personnel

---

**Note** : Ce README documente l'interface Streamlit. Pour le système de tracking complet, voir `README-ROON-TRACKER.md`.
