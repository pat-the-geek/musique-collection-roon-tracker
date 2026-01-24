# 🔗 Dépendances Inter-Projets

## Vue d'ensemble

Ce document documente les dépendances entre le projet **Musique** et d'autres projets de l'écosystème **DataForIA**, notamment le projet **Cinéma**.

**Date:** 24 janvier 2026  
**Version projet:** 3.0.0

---

## 🎬 Projet Cinéma → Projet Musique

### Dépendance: `catalogue.json`

Le script [src/collection/generate-soundtrack.py](../src/collection/generate-soundtrack.py) dépend du fichier `catalogue.json` du projet Cinéma pour identifier les bandes originales de films dans la collection musicale.

#### Structure des répertoires requise

```
Documents/DataForIA/
├── Cinéma/                          ← PROJET EXTERNE (requis)
│   ├── catalogue.json               ← Source de vérité pour films
│   ├── films/
│   └── [autres fichiers Cinéma...]
│
└── Musique/                         ← CE PROJET
    ├── src/collection/
    │   └── generate-soundtrack.py   ← Script dépendant
    ├── data/collection/
    │   ├── discogs-collection.json  ← Source musique
    │   └── soundtrack.json          ← Sortie générée
    └── [...]
```

#### Chemin de dépendance

```python
# Dans generate-soundtrack.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# → /Users/patrickostertag/Documents/DataForIA/Musique/src/collection

PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
# → /Users/patrickostertag/Documents/DataForIA/Musique

DATAFORLA_ROOT = os.path.dirname(PROJECT_ROOT)
# → /Users/patrickostertag/Documents/DataForIA

# Chemin complet vers catalogue.json
CINEMA_PATH = os.path.join(DATAFORLA_ROOT, 'Cinéma', 'catalogue.json')
# → /Users/patrickostertag/Documents/DataForIA/Cinéma/catalogue.json
```

#### Structure de `catalogue.json` attendue

**Format requis:**
```json
[
  {
    "OriginalTitle": "La Môme",
    "ProductionYear": 2007,
    "TMDB": {
      "realisateur": "Olivier Dahan",
      "id": 123456,
      "vote_average": 7.5
    }
  },
  {
    "OriginalTitle": "The Godfather",
    "ProductionYear": 1972,
    "TMDB": {
      "realisateur": "Francis Ford Coppola"
    }
  }
]
```

**Champs utilisés par generate-soundtrack.py:**
- `OriginalTitle` (string, requis): Titre original du film
- `ProductionYear` (int, requis): Année de production
- `TMDB.realisateur` (string, optionnel): Nom du réalisateur (depuis TMDB API)

**Champs ignorés:**
- Tout autre champ du catalogue est disponible mais non utilisé actuellement

---

## 🎵 Algorithme de Matching

### Logique de correspondance

Le script effectue un **matching par préfixe** entre titres de films et d'albums :

```python
# Normalisation lowercase
film_titles = {item['OriginalTitle'].lower() for item in catalogue}
album_titles = {item['Titre'].lower() for item in discogs_collection}

# Matching: album commence par titre de film
common_titles = [
    (film, album)
    for film in film_titles
    for album in album_titles
    if album.startswith(film)  # ← Clé du matching
]
```

### Exemples de matching

| Film Title (Cinéma) | Album Title (Musique) | Match? | Raison |
|---------------------|----------------------|--------|--------|
| `"La Môme"` | `"La Môme"` | ✅ | Exact match |
| `"The Godfather"` | `"The Godfather (Original Soundtrack)"` | ✅ | Préfixe identique |
| `"Blade Runner"` | `"Blade Runner (Vangelis)"` | ✅ | Préfixe identique |
| `"Amélie"` | `"Le Fabuleux Destin d'Amélie Poulain"` | ❌ | Pas de préfixe commun |
| `"Star Wars"` | `"Star Wars Episode IV"` | ✅ | Préfixe identique |

### Limites de l'algorithme

**Faux négatifs possibles:**
- Films avec titre différent de l'album (ex: "Amélie" vs "Le Fabuleux Destin...")
- Variations orthographiques (ex: "Star Wars" vs "Starwars")
- Titres avec accents non normalisés

**Faux positifs possibles:**
- Albums commençant par un mot très court (ex: "A" match tous les albums "A ...")
- Rare en pratique grâce à la spécificité des titres de films

---

## 📤 Sortie Générée: `soundtrack.json`

### Structure du fichier

**Emplacement:** `data/collection/soundtrack.json`

**Format:**
```json
[
  {
    "film_title": "La Môme",
    "album_title": "la môme",
    "year": 2007,
    "director": "Olivier Dahan"
  },
  {
    "film_title": "Blade Runner",
    "album_title": "blade runner (vangelis)",
    "year": 1982,
    "director": "Ridley Scott"
  }
]
```

**Caractéristiques:**
- Trié alphabétiquement par `film_title` (normalisation accents)
- Titres d'albums en lowercase (préserve la casse originale dans discogs-collection.json)
- Année = année de production du film (pas de l'album)
- Réalisateur extrait depuis TMDB via le projet Cinéma

### Utilisation des données

**1. Interface Web Streamlit (`src/gui/musique-gui.py`):**
```python
# Chargement
soundtracks = load_soundtrack_data()  # Lit soundtrack.json

# Vérification
if is_soundtrack(album['Titre'], soundtracks):
    st.markdown("🎬 **SOUNDTRACK / BANDE ORIGINALE DE FILM**")
    
# Affichage métadonnées
soundtrack_info = get_soundtrack_info(album['Titre'], soundtracks)
st.markdown(f"**🎬 Film:** {soundtrack_info['film_title']}")
st.markdown(f"**📅 Année du film:** {soundtrack_info['year']}")
st.markdown(f"**🎥 Réalisateur:** {soundtrack_info['director']}")

# Filtrage
if only_soundtracks:
    filtered = [a for a in albums if is_soundtrack(a['Titre'], soundtracks)]
```

**2. Statistiques Collection:**
```python
# Comptage soundtracks
soundtrack_count = sum(1 for album in albums 
                      if is_soundtrack(album['Titre'], soundtracks))
st.metric("🎬 BOF", soundtrack_count)
```

**3. Future: Analytics avancées**
- Corrélation goûts musicaux ↔ préférences cinématographiques
- Recommandations de films basées sur albums écoutés
- Timeline combinée cinéma/musique

---

## ⚠️ Gestion des Erreurs

### Script échoue si catalogue.json absent

**Erreur rencontrée:**
```bash
FileNotFoundError: [Errno 2] No such file or directory: 
'/Users/patrickostertag/Documents/DataForIA/Cinéma/catalogue.json'
```

**Solutions:**

**Option 1: Installer le projet Cinéma (recommandé)**
```bash
cd ~/Documents/DataForIA
git clone [repo-cinema] Cinéma
# Ou créer manuellement le projet Cinéma
```

**Option 2: Créer un catalogue.json minimal**
```bash
mkdir -p ~/Documents/DataForIA/Cinéma
cat > ~/Documents/DataForIA/Cinéma/catalogue.json << 'EOF'
[
  {
    "OriginalTitle": "La Môme",
    "ProductionYear": 2007,
    "TMDB": {
      "realisateur": "Olivier Dahan"
    }
  }
]
EOF
```

**Option 3: Désactiver le script (temporaire)**
- Ne pas exécuter `generate-soundtrack.py`
- `soundtrack.json` ne sera pas généré
- L'interface Streamlit fonctionnera sans filtre BOF

### Validation de la dépendance

**Script de vérification:**
```bash
# Vérifier que le fichier existe
if [ -f ~/Documents/DataForIA/Cinéma/catalogue.json ]; then
    echo "✅ catalogue.json trouvé"
    python3 -m json.tool ~/Documents/DataForIA/Cinéma/catalogue.json > /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Format JSON valide"
    else
        echo "❌ Format JSON invalide"
    fi
else
    echo "❌ catalogue.json introuvable"
    echo "   Chemin attendu: ~/Documents/DataForIA/Cinéma/catalogue.json"
fi
```

---

## 🔮 Évolutions Futures

### Extensions prévues du partage de données

**1. Acteurs ↔ Artistes**
- Détecter les acteurs qui sont aussi musiciens
- Cross-référence biographies (films joués ↔ albums sortis)
- Exemple: David Bowie (acteur + musicien)

**2. Réalisateurs ↔ Compositeurs**
- Identifier les réalisateurs qui composent leurs propres BO
- Exemple: John Carpenter, Clint Eastwood

**3. Timeline unifiée**
- Fusionner chronologies cinéma + musique
- Visualiser l'activité culturelle par période
- Analyse des tendances par décennie

**4. Recommandations croisées**
- "Vous aimez ce film? Écoutez cette musique"
- "Vous aimez cet album? Regardez ce film"
- ML sur préférences combinées

### Autres projets potentiels

**Livres** (`../Livres/catalogue.json`):
- Auteurs qui ont écrit sur la musique
- Biographies de musiciens
- Livres mentionnés dans paroles

**Expositions** (`../Expositions/visites.json`):
- Concerts vus en lien avec albums
- Festivals musicaux
- Expositions sur musiciens

---

## 🛠️ Maintenance de la Dépendance

### Synchronisation des structures

**Si le projet Cinéma change sa structure de `catalogue.json`:**

1. **Notification:** Le mainteneur Cinéma doit notifier les projets dépendants
2. **Adaptation:** Mettre à jour `generate-soundtrack.py` si nécessaire
3. **Tests:** Valider que le matching fonctionne toujours
4. **Documentation:** Mettre à jour ce document

### Versioning des structures

**Proposition de conventions:**
```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-01-24T10:30:00Z",
  "films": [...]
}
```

Pour détecter les breaking changes dans le format JSON.

### Checklist avant modifications

**Avant de modifier catalogue.json (projet Cinéma):**
- [ ] Vérifier si des scripts Musique en dépendent
- [ ] Notifier maintainers des projets dépendants
- [ ] Tester generate-soundtrack.py avec nouvelle structure
- [ ] Mettre à jour documentation si nécessaire

**Avant de modifier generate-soundtrack.py:**
- [ ] Vérifier compatibilité avec catalogue.json actuel
- [ ] Tester avec données réelles
- [ ] Mettre à jour CROSS-PROJECT-DEPENDENCIES.md
- [ ] Incrémenter version du script

---

## 📝 Convention de Nommage

Pour faciliter l'identification des dépendances inter-projets:

**Commentaire standard dans le code:**
```python
# ⚠️ EXTERNAL DEPENDENCY - Project: Cinéma
# File: ../../../Cinéma/catalogue.json
# Reason: Reuse TMDB metadata to avoid duplicate API calls
# Impact: Script will fail if Cinéma project is not present
```

**Variable nommage:**
```python
DATAFORLA_ROOT = os.path.dirname(PROJECT_ROOT)  # Clarifier que c'est hors projet
CINEMA_PATH = os.path.join(DATAFORLA_ROOT, 'Cinéma', 'catalogue.json')
```

---

## 🧪 Tests de Validation

### Test d'existence de la dépendance

**Script de test recommandé:**
```python
#!/usr/bin/env python3
"""Test de validation des dépendances inter-projets."""

import os
import json
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATAFORLA_ROOT = os.path.dirname(PROJECT_ROOT)
CINEMA_CATALOGUE = os.path.join(DATAFORLA_ROOT, 'Cinéma', 'catalogue.json')

def test_cinema_dependency():
    """Teste la présence et validité du catalogue Cinéma."""
    print("🧪 Test des dépendances inter-projets\n")
    
    # Test 1: Fichier existe
    print("Test 1: Existence de catalogue.json...", end=" ")
    if not os.path.exists(CINEMA_CATALOGUE):
        print("❌ ÉCHEC")
        print(f"   Chemin attendu: {CINEMA_CATALOGUE}")
        print(f"   Solution: Installer le projet Cinéma")
        return False
    print("✅ OK")
    
    # Test 2: Format JSON valide
    print("Test 2: Format JSON valide...", end=" ")
    try:
        with open(CINEMA_CATALOGUE, 'r', encoding='utf-8') as f:
            catalogue = json.load(f)
        print("✅ OK")
    except json.JSONDecodeError as e:
        print("❌ ÉCHEC")
        print(f"   Erreur: {e}")
        return False
    
    # Test 3: Structure attendue
    print("Test 3: Structure attendue...", end=" ")
    if not isinstance(catalogue, list):
        print("❌ ÉCHEC (pas une liste)")
        return False
    
    if len(catalogue) == 0:
        print("⚠️  VIDE (catalogue sans films)")
        return True
    
    # Vérifier premier élément
    first_film = catalogue[0]
    required_fields = ['OriginalTitle', 'ProductionYear']
    missing = [f for f in required_fields if f not in first_film]
    
    if missing:
        print(f"❌ ÉCHEC (champs manquants: {missing})")
        return False
    
    print("✅ OK")
    print(f"   Nombre de films: {len(catalogue)}")
    
    return True

if __name__ == "__main__":
    success = test_cinema_dependency()
    sys.exit(0 if success else 1)
```

### Exécution du test

```bash
cd ~/Documents/DataForIA/Musique
source .venv/bin/activate
python3 tests/test_cross_dependencies.py
```

---

## 📊 Impact et Justification

### Pourquoi cette dépendance?

**Avantages:**
1. **Évite duplication API TMDB:**
   - Le projet Cinéma a déjà récupéré les métadonnées TMDB (réalisateur, année, etc.)
   - Réutiliser ces données économise des appels API coûteux
   - Pas besoin de clé API TMDB dans le projet Musique

2. **Cohérence des données:**
   - Source unique de vérité pour les métadonnées films
   - Garantit que les informations sont identiques entre projets
   - Mises à jour Cinéma → automatiquement propagées à Musique

3. **Enrichissement bidirectionnel:**
   - Musique identifie ses BOF via Cinéma
   - Futur: Cinéma pourrait enrichir ses films avec musiques associées
   - Crée un écosystème de données interconnectées

**Inconvénients:**
1. **Couplage fort:**
   - Le script Musique dépend de la présence du projet Cinéma
   - Changements dans catalogue.json peuvent casser generate-soundtrack.py

2. **Complexité de déploiement:**
   - Installation nécessite deux projets
   - Ordre d'installation important (Cinéma avant Musique pour cette feature)

3. **Fragilité:**
   - Si Cinéma est supprimé/déplacé → soundtrack.json ne peut plus être généré
   - Pas de fallback automatique

### Alternatives envisagées

**Option 1: API TMDB directe dans Musique**
- ❌ Duplication des appels API
- ❌ Coût supplémentaire
- ❌ Maintenance de deux systèmes de cache

**Option 2: Base de données partagée**
- ✅ Source unique de vérité
- ✅ Pas de dépendance fichier
- ❌ Complexité infrastructure
- ❌ Overkill pour POC

**Option 3: Fichier de données centralisé**
- ✅ Indépendance des projets
- ❌ Perte de la séparation logique
- ❌ Conflits de merge potentiels

**Décision:** Conserver la dépendance actuelle pour la simplicité et l'évitement de duplication API.

---

## 🔄 Workflow de Synchronisation

### Mise à jour du catalogue Cinéma

```bash
# 1. Mettre à jour le catalogue films (projet Cinéma)
cd ~/Documents/DataForIA/Cinéma
python3 update_catalogue.py  # (exemple)

# 2. Régénérer les soundtracks (projet Musique)
cd ~/Documents/DataForIA/Musique
source .venv/bin/activate
python3 src/collection/generate-soundtrack.py

# 3. Vérifier les nouvelles BOF détectées
diff data/collection/soundtrack.json backups/json/soundtrack/soundtrack-*.json

# 4. Relancer l'interface pour voir les changements
./scripts/start-streamlit.sh
```

### Fréquence de synchronisation recommandée

- **Après ajout de films:** Relancer generate-soundtrack.py
- **Après ajout d'albums:** Relancer generate-soundtrack.py
- **Automatisation possible:** Cron job ou file watcher

---

## 📋 Checklist pour Nouveaux Projets Dépendants

Si vous créez un nouveau projet qui dépend d'un autre:

- [ ] Documenter la dépendance dans ce fichier (CROSS-PROJECT-DEPENDENCIES.md)
- [ ] Ajouter commentaires `# ⚠️ EXTERNAL DEPENDENCY` dans le code
- [ ] Créer variables explicites (`DATAFORLA_ROOT`, pas juste `../../../`)
- [ ] Gérer gracieusement l'absence du fichier externe (try/except)
- [ ] Documenter la structure attendue du fichier externe
- [ ] Ajouter tests de validation
- [ ] Mentionner dans README.md principal
- [ ] Mettre à jour ARCHITECTURE-OVERVIEW.md
- [ ] Informer maintainers du projet source

---

## 🔗 Liens Utiles

- [generate-soundtrack.py](../src/collection/generate-soundtrack.py): Code source
- [ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md): Diagrammes de flux
- [README-MUSIQUE-GUI.md](README-MUSIQUE-GUI.md): Utilisation des BOF dans l'interface

---

**Maintenu par:** Patrick Ostertag  
**Dernière mise à jour:** 24 janvier 2026
