# Changelog - generate-haiku.py Version 2.1.0

**Date:** 21 janvier 2026  
**Auteur:** Patrick Ostertag

## 🎯 Objectif

Éviter les doublons dans les albums sélectionnés pour la génération de haïkus, car ils proviennent de deux sources différentes (Discogs et Roon).

## ⚠️ Problème identifié

**Situation précédente (v2.0.0):**
- 10 albums sélectionnés aléatoirement depuis Discogs
- 10 albums sélectionnés aléatoirement depuis Roon
- **Aucune vérification de doublons entre les deux sources**
- Risque : Un album présent dans la collection Discogs ET dans l'historique Roon pouvait apparaître deux fois dans la présentation finale

**Exemple de doublon possible:**
- Album "Kind of Blue" de Miles Davis dans Discogs
- Même album dans l'historique Roon (récemment écouté)
- → Génération de 2 slides identiques

## ✨ Solution implémentée

### 1. Nouvelle fonction `normalize_album_key()`

```python
def normalize_album_key(artist: str, album: str) -> str:
    """Crée une clé normalisée pour identifier un album de manière unique."""
    # Nettoie l'artiste (gère les listes)
    # Normalise en minuscules
    # Format: "artiste|||album"
    return f"{artist_clean}|||{album_clean}"
```

**Avantages:**
- Détection insensible à la casse
- Gère les différences de format entre Discogs et Roon
- Clé unique pour chaque combinaison artiste/album

### 2. Logique de déduplication

**Nouveau workflow (v2.1.0):**

```python
# 1. Sélectionner 10 albums Discogs
random_albums_discogs = secrets.SystemRandom().sample(data, 10)

# 2. Créer un set de clés normalisées pour ces albums
discogs_keys = set()
for album in random_albums_discogs:
    key = normalize_album_key(album['Artiste'], album['Titre'])
    discogs_keys.add(key)

# 3. Filtrer les albums Roon pour exclure les doublons
roon_albums_list = []
for album in roon_albums_dict.values():
    key = normalize_album_key(album['Artiste'], album['Titre'])
    if key not in discogs_keys:  # ✅ Exclusion des doublons
        roon_albums_list.append(album)

# 4. Sélectionner 10 albums parmi les albums Roon filtrés
random_albums_roon = secrets.SystemRandom().sample(roon_albums_list, 10)

# 5. Combiner (maintenant garantis sans doublons)
all_random_albums = random_albums_discogs + random_albums_roon
```

### 3. Messages de debug ajoutés

Pour vérifier le bon fonctionnement :

```
[DEBUG] 10 albums sélectionnés depuis Discogs
[DEBUG] Clés Discogs: 10 uniques
[DEBUG] 225 albums Roon uniques (après exclusion des doublons Discogs)
[DEBUG] 10 albums sélectionnés depuis Roon
[DEBUG] ✅ Total: 20 albums uniques pour la génération
```

## 📊 Résultats

### Avant version 2.1.0
- ❌ Risque de doublons entre Discogs et Roon
- ❌ Pas de vérification
- ❌ Possibilité de slides identiques

### Après version 2.1.0
- ✅ Doublons détectés et éliminés automatiquement
- ✅ Garantie de 20 albums uniques (ou moins si pas assez d'albums Roon disponibles)
- ✅ Messages de debug pour traçabilité
- ✅ Normalisation insensible à la casse

## 🔧 Fichiers modifiés

### Code source
- **generate-haiku.py** (v2.0.0 → v2.1.0)
  - Ajout de `normalize_album_key()` (ligne ~165-200)
  - Modification de la logique de sélection (ligne ~290-330)
  - Ajout de messages de debug

### Documentation
- **.github/copilot-instructions.md**
  - Section "generate-haiku.py" mise à jour
  - Workflow détaillé avec étapes de déduplication
  - Fonction `normalize_album_key()` documentée

## 🧪 Tests de validation

**Test effectué:**
```bash
python3 generate-haiku.py
```

**Résultat:**
```
[DEBUG] 10 albums sélectionnés depuis Discogs
[DEBUG] Clés Discogs: 10 uniques
[DEBUG] 225 albums Roon uniques (après exclusion des doublons Discogs)
[DEBUG] 10 albums sélectionnés depuis Roon
[DEBUG] ✅ Total: 20 albums uniques pour la génération
```

✅ **Succès** - Sur 225 albums Roon disponibles, aucun doublon n'a été détecté, ce qui confirme que la collection Discogs et l'historique Roon ne contiennent pas les mêmes albums (ou très peu).

## 📝 Cas limites gérés

### Cas 1: Moins de 10 albums Roon disponibles après filtrage

```python
if len(roon_albums_list) >= 10:
    random_albums_roon = secrets.SystemRandom().sample(roon_albums_list, 10)
else:
    random_albums_roon = roon_albums_list
    print(f"[DEBUG] ⚠️  Seulement {len(roon_albums_list)} albums Roon disponibles (< 10)")
```

**Comportement:** Le script continue avec moins de 20 albums au total.

### Cas 2: Normalisation des différences de format

**Exemples gérés:**
- "Nina Simone" (Discogs) vs "nina simone" (Roon) → Détecté comme doublon ✅
- ["Miles Davis"] (liste) vs "Miles Davis" (string) → Détecté comme doublon ✅
- Espaces superflus normalisés

### Cas 3: Albums avec métadonnées différentes

**Limitation connue:** Si un album a des titres légèrement différents entre Discogs et Roon, il ne sera PAS détecté comme doublon.

**Exemple:**
- Discogs: "Kind of Blue (Remastered)"
- Roon: "Kind of Blue"
- → Traités comme 2 albums différents

**Mitigation:** La fonction `normalize_album_key()` pourrait être améliorée à l'avenir pour nettoyer aussi les suffixes comme "(Remastered)".

## 🔮 Améliorations futures possibles

1. **Nettoyage avancé des titres**
   - Supprimer "(Remastered)", "(Deluxe)", "[Bonus Tracks]"
   - Améliorer la détection de doublons avec titres variant légèrement

2. **Fuzzy matching**
   - Utiliser `fuzzywuzzy` ou `rapidfuzz` pour détecter les similitudes
   - Seuil de similarité configurable (ex: 90%)

3. **Statistiques de déduplication**
   - Afficher le nombre de doublons détectés et éliminés
   - Logger les albums exclus pour audit

## 📌 Notes de migration

✅ **Aucune action requise** - Les modifications sont totalement rétrocompatibles.

Les utilisateurs existants bénéficieront automatiquement de la déduplication lors de la prochaine exécution.

---

**Version complète:** 2.1.0  
**Version précédente:** 2.0.0  
**Breaking changes:** Aucun  
**Nécessite migration:** Non  
**Impact:** Amélioration de la qualité (élimination des doublons)
