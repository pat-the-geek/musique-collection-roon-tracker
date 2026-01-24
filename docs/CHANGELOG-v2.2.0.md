# Changelog - Version 2.2.0

**Date:** 21 janvier 2026  
**Auteur:** Patrick Ostertag

## 🎯 Objectif

Améliorer la fiabilité de la recherche de pochettes d'album sur Spotify en corrigeant les faux positifs et en validant strictement la correspondance artiste/album.

## ⚠️ Problème identifié

**Exemple d'échec:** Album "9 [Italian]" d'Eros Ramazzotti retournait une mauvaise image.

**Causes:**
1. La fonction `clean_album_name()` ne supprimait pas les crochets `[]` → "9 [Italian]" restait tel quel
2. Aucune validation de l'artiste dans les résultats Spotify
3. Acceptation du premier résultat sans vérification de pertinence

## ✨ Améliorations implémentées

### 1. Nettoyage amélioré des métadonnées

**Avant:**
```python
# Supprimait uniquement les parenthèses ()
re.sub(r'\s*\([^)]*\)\s*$', '', album_name)
```

**Après:**
```python
# Supprime AUSSI les crochets []
re.sub(r'\s*[\(\[][^\)\]]*[\)\]]\s*$', '', album_name)
```

**Impact:**
- "9 [Italian]" → "9"
- "Best of [Deluxe Edition]" → "Best of"
- "Album (Remastered)" → "Album"

### 2. Validation stricte de l'artiste

**Nouvelles fonctions:**

```python
def normalize_string_for_comparison(s: str) -> str:
    """Normalise pour comparaison (minuscules, sans espaces multiples)"""
    return ' '.join(s.lower().strip().split())

def artist_matches(search_artist: str, found_artist: str) -> bool:
    """Vérifie si deux noms d'artistes correspondent avec tolérance"""
    # Gère: "Nina Simone" = "nina simone" (case insensitive)
    # Gère: "Various" = "Various Artists"
    # Gère: "The Beatles" contient "Beatles"
```

**Application:**
- Tous les résultats Spotify sont maintenant validés
- Rejet automatique si l'artiste ne correspond pas
- Messages de debug: `⚠️ Artiste non correspondant: recherché 'X', trouvé 'Y'`

### 3. Système de scoring pour sélection du meilleur match

**Stratégie:**
1. Recherche de **5 résultats** au lieu de 1
2. Pour chaque résultat:
   - Validation de l'artiste (requis)
   - Calcul d'un score de similarité du titre d'album:
     - **100 points**: Correspondance exacte
     - **80 points**: Contenu l'un dans l'autre
     - **50 points**: Ratio de mots en commun
3. Sélection du meilleur score (seuil minimal: 50 pour recherche principale, 30 pour fallback)

**Exemple de logs:**
```
[DEBUG] 🎯 Match trouvé: '9' par 'Eros Ramazzotti' (score: 100.0)
[DEBUG] ✅ Spotify album '9' (score: 100.0): https://...
```

### 4. Fallback amélioré avec même logique

**Avant:** Fallback acceptait n'importe quel résultat sans validation  
**Après:** Fallback applique la même validation d'artiste + scoring

## 📊 Résultats attendus

### Avant version 2.2.0
- ❌ "9 [Italian]" d'Eros Ramazzotti → Mauvaise image
- ❌ Recherches floues acceptées sans validation
- ❌ Premier résultat pris sans vérification

### Après version 2.2.0
- ✅ "9 [Italian]" → nettoyé en "9" → validation artiste → bonne image
- ✅ Validation stricte de tous les résultats
- ✅ Sélection du meilleur match basée sur un score de pertinence
- ✅ Messages de debug détaillés pour traçabilité

## 🔧 Fichiers modifiés

### Code source
- **chk-roon.py** (v2.1.0 → v2.2.0)
  - Modification de `clean_album_name()` (ligne ~233-262)
  - Ajout de `normalize_string_for_comparison()` (ligne ~520)
  - Ajout de `artist_matches()` (ligne ~522-545)
  - Refonte complète de `search_spotify_album_image()` (ligne ~547-725)

### Documentation
- **README-ROON-TRACKER.md**
  - Section "Fonctionnalités" mise à jour
  - Tableau "Modules principaux" enrichi
  - Exemples de nettoyage complétés
  - Version mise à jour (v2.2.0)

- **.github/copilot-instructions.md**
  - Section "Metadata Cleaning Strategy" enrichie
  - Section "Spotify Image Enrichment" renommée et détaillée
  - Documentation du système de validation d'artiste
  - Documentation du système de scoring

### Backup
- **backup-python/backup-20260121-112416/chk-roon.py**
  - Sauvegarde de la version 2.1.0 avant modifications

## 🧪 Tests recommandés

1. **Tester avec des albums difficiles:**
   ```bash
   # Exemples de cas limites
   - "9 [Italian]" (Eros Ramazzotti)
   - "Various Artists" albums
   - Titres courts ("9", "1", "Abbey Road")
   - Titres avec versions: "Best of [Deluxe]"
   ```

2. **Vérifier les logs de debug:**
   ```
   [DEBUG] 🎯 Match trouvé: ...
   [DEBUG] ⚠️ Artiste non correspondant: ...
   [DEBUG] ✅ Spotify album '...' (score: X.X)
   ```

3. **Valider les images récupérées:**
   - Comparer visuellement les pochettes
   - Vérifier la correspondance artiste/album

## 📝 Notes de migration

Aucune action requise pour les utilisateurs existants. Les modifications sont **rétrocompatibles**.

Le cache existant reste valide. Les nouvelles recherches utiliseront automatiquement la logique améliorée.

## 🔮 Améliorations futures possibles

1. **Configurable scoring thresholds** - Permettre d'ajuster les seuils (50/30)
2. **Fuzzy matching** - Utiliser une bibliothèque comme `fuzzywuzzy` pour comparaisons avancées
3. **Multi-language support** - Gérer les titres dans différentes langues
4. **Image quality validation** - Vérifier la taille/qualité de l'image avant sélection

---

**Version complète:** 2.2.0  
**Version précédente:** 2.1.0  
**Breaking changes:** Aucun  
**Nécessite migration:** Non
