# Tests - Musique Collection & Tracker

Ce répertoire contient la suite de tests unitaires et d'intégration pour le projet Musique Collection & Tracker.

## Structure des tests

```
src/tests/
├── conftest.py                      # Configuration pytest et fixtures communes
├── test_ai_service.py               # Tests du service AI EurIA (31 tests) ✨ Nouveau
├── test_chk_roon_integration.py     # Tests d'intégration tracker Roon (28 tests) ✨ Nouveau
├── test_metadata_cleaner.py         # Tests du module metadata_cleaner (27 tests)
├── test_scheduler.py                # Tests du module scheduler (29 tests)
├── test_spotify_service.py          # Tests du service Spotify (49 tests)
└── test_constants.py                # Tests du module constants (57 tests)
```

## Couverture de code

| Module | Tests | Couverture | Status |
|--------|-------|-----------|--------|
| `constants.py` | 57 | 100% | ✅ |
| `spotify_service.py` | 49 | 88% | ✅ |
| `ai_service.py` | 31 | ~85% | ✅ |
| `metadata_cleaner.py` | 27 | ~95% | ✅ |
| `scheduler.py` | 29 | ~90% | ✅ |
| `chk-roon.py (integration)` | 28 | N/A | ✅ |
| **Total** | **221** | **~91%** | ✅ |

**Note**: Les tests d'intégration pour chk-roon.py testent les flux de données et l'intégration entre composants, pas la couverture de code ligne par ligne.

## Exécution des tests

### Tous les tests
```bash
cd /home/runner/work/musique-collection-roon-tracker/musique-collection-roon-tracker
python3 -m pytest src/tests/ -v
```

### Tests spécifiques
```bash
# Tests Roon integration uniquement
python3 -m pytest src/tests/test_chk_roon_integration.py -v

# Tests AI service uniquement
python3 -m pytest src/tests/test_ai_service.py -v

# Tests Spotify service uniquement
python3 -m pytest src/tests/test_spotify_service.py -v

# Tests constants uniquement
python3 -m pytest src/tests/test_constants.py -v

# Tests metadata cleaner uniquement
python3 -m pytest src/tests/test_metadata_cleaner.py -v

# Tests scheduler uniquement
python3 -m pytest src/tests/test_scheduler.py -v
```

### Avec couverture de code
```bash
# Couverture complète
python3 -m pytest src/tests/ -v --cov=services --cov=constants --cov-report=term-missing

# Rapport HTML
python3 -m pytest src/tests/ --cov=services --cov=constants --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

### Filtrer par marqueurs
```bash
# Tests unitaires uniquement
python3 -m pytest src/tests/ -v -m unit

# Tests d'intégration uniquement
python3 -m pytest src/tests/ -v -m integration

# Exclure les tests lents
python3 -m pytest src/tests/ -v -m "not slow"
```

## Organisation des tests

### test_ai_service.py (31 tests) ✨ Nouveau

Tests complets du service d'intégration AI EurIA avec mock des appels API.

#### `TestGetEuriaConfig` (2 tests)
- Chargement de la configuration depuis variables d'environnement
- Valeurs par défaut si variables absentes

#### `TestAskForIA` (11 tests)
- Appel API réussi avec parsing de réponse
- Nettoyage des espaces superflus
- Gestion des credentials manquants
- Retry automatique sur timeout
- Retry automatique sur erreurs réseau
- Gestion des réponses JSON invalides
- Gestion des réponses sans champ 'choices'
- Timeout personnalisé
- Délai entre les tentatives (2 secondes)
- Activation de la recherche web (enable_web_search)

#### `TestGenerateAlbumInfo` (6 tests)
- Génération d'information d'album réussie
- Limite de caractères personnalisée
- Valeur par défaut de max_characters (2000)
- Génération avec artiste inconnu
- Paramètres de timeout corrects (max_attempts=3, timeout=45)
- Gestion des erreurs

#### `TestGetAlbumInfoFromDiscogs` (9 tests)
- Récupération d'album avec résumé valide
- Album non trouvé retourne None
- Album avec résumé générique ("Aucune information disponible") retourne None
- Album avec résumé vide retourne None
- Recherche insensible à la casse
- Fichier Discogs non trouvé
- Fichier JSON invalide
- Gestion des espaces en trop
- Collection vide
- Album sans champ 'Titre'

#### `TestEdgeCasesAndIntegration` (3 tests)
- Gestion des caractères Unicode dans les prompts
- Titre d'album très long
- Caractères spéciaux dans artiste/album

### test_chk_roon_integration.py (28 tests) ✨ Nouveau

Tests d'intégration end-to-end du tracker Roon avec mock des APIs externes.

#### `TestMetadataCleaning` (3 tests)
- Nettoyage des noms d'artistes simples et multiples
- Nettoyage des noms d'albums avec versions

#### `TestDuplicateDetection` (2 tests)
- Détection de pistes non-dupliquées avec timestamps différents
- Détection de doublons dans les 60 secondes

#### `TestSpotifyEnrichment` (3 tests)
- Récupération de token Spotify
- Recherche d'images d'artistes
- Recherche d'images d'albums

#### `TestRadioStationHandling` (2 tests)
- Détection des stations de radio
- Parsing du champ artiste pour les radios

#### `TestLastfmEnrichment` (1 test)
- Recherche d'images d'albums via Last.fm (skipped si pylast non installé)

#### `TestAIEnrichment` (4 tests)
- Récupération d'info AI depuis Discogs si disponible
- Génération d'info AI si pas dans Discogs
- Log des infos AI dans fichiers quotidiens
- Nettoyage automatique des vieux logs (>24h)

#### `TestDataPersistence` (2 tests)
- Sauvegarde de pistes dans chk-roon.json
- Préservation de l'historique existant

#### `TestListeningHours` (2 tests)
- Vérification des heures dans la plage d'écoute
- Vérification des heures hors plage d'écoute

#### `TestFileLocking` (3 tests)
- Acquisition de verrou quand disponible
- Verrou non acquis si déjà pris
- Libération correcte du verrou

#### `TestEndToEndIntegration` (2 tests)
- Flux complet de traitement d'une piste (skipped si roonapi non installé)
- Intégration Last.fm (skipped si pylast non installé)

#### `TestErrorHandling` (4 tests)
- Gestion fichier config manquant
- Gestion fichier historique corrompu
- Continuation sur échec API Spotify
- Continuation sur échec API AI

### test_spotify_service.py (49 tests)

Tests complets du service d'intégration Spotify avec mock des appels API.

#### `TestSpotifyCache` (8 tests)
- Initialisation et persistance du cache
- Gestion du token avec expiration
- Cache d'images d'artistes
- Cache d'images d'albums avec clés composites

#### `TestGetSpotifyToken` (10 tests)
- Authentification OAuth Client Credentials Flow
- Gestion du cache de token
- Validation des credentials
- Gestion des erreurs réseau et timeouts
- Réponses JSON invalides

#### `TestSearchSpotifyArtistImage` (10 tests)
- Recherche d'images d'artistes
- Cache hit/miss
- Nettoyage automatique des métadonnées
- Retry logic sur erreurs 401 (token expiré) et 429 (rate limit)
- Gestion des erreurs HTTP

#### `TestSearchSpotifyAlbumImage` (6 tests)
- Recherche primaire avec artiste + album
- Fallback search (album seul) pour Various Artists
- Cache et nettoyage des métadonnées
- Gestion des échecs multiples

#### `TestFindBestAlbumMatch` (7 tests)
- Système de scoring (100/80/50 points)
- Validation de l'artiste
- Sélection du meilleur résultat
- Gestion des albums sans images

#### `TestSearchAlbumInternal` (4 tests)
- Fonctions internes `_search_album_with_artist` et `_search_album_only`
- Retry automatique sur erreurs

#### `TestEdgeCasesAndBoundaryConditions` (4 tests)
- Caractères Unicode et spéciaux
- Chaînes très longues
- Épuisement des tentatives de retry

### test_constants.py (57 tests)

Tests de cohérence et validation des constantes du projet.

#### Catégories testées:
- **Valeurs par défaut** (3 tests): `UNKNOWN_ARTIST`, `UNKNOWN_ALBUM`, etc.
- **Sources de données** (3 tests): `SOURCE_ROON`, `SOURCE_LASTFM`, etc.
- **Formats de support** (5 tests): `SUPPORT_VINYL`, `SUPPORT_CD`, `VALID_SUPPORTS`
- **Configuration Spotify** (6 tests): URLs, scores, limites de recherche
- **Configuration Last.fm** (3 tests): Tailles d'images
- **Délais et retries** (5 tests): `DEFAULT_RETRY_COUNT`, timeouts
- **Plages horaires** (3 tests): Heures d'écoute par défaut
- **Détection de sessions** (4 tests): Seuils et paramètres
- **Normalisation** (4 tests): Caractères à ignorer
- **Messages d'erreur** (2 tests): Validation des messages
- **Formats de date** (3 tests): Formats strftime
- **Backup** (2 tests): Configuration de rétention
- **Noms de fichiers** (4 tests): Extensions et validité
- **URLs d'APIs** (3 tests): HTTPS et domaines valides
- **User Agents** (2 tests): Identifiants
- **Utilisation en contexte** (5 tests): Tests d'intégration réelle

### test_metadata_cleaner.py (27 tests)

Tests des fonctions de nettoyage et normalisation des métadonnées.

#### Classes de tests:
- `TestCleanArtistName`: Nettoyage des noms d'artistes
- `TestCleanAlbumName`: Nettoyage des noms d'albums
- `TestNettoyerNomArtiste`: Format Discogs spécifique
- `TestNormalizeStringForComparison`: Normalisation pour comparaison
- `TestArtistMatches`: Validation de correspondance d'artistes
- `TestCalculateAlbumMatchScore`: Système de scoring d'albums

### test_scheduler.py (29 tests)

Tests du système de planification des tâches.

#### Classes de tests:
- `TestTaskSchedulerInit`: Initialisation du scheduler
- `TestTaskSchedulerMethods`: Méthodes de gestion des tâches
- `TestTaskSchedulerFrequencyUnits`: Unités de fréquence (hour, day, month, year)
- `TestTaskSchedulerPersistence`: Persistance de la configuration

## Fixtures communes (conftest.py)

### Fixtures disponibles:
- `sample_artist_names`: Exemples de noms d'artistes pour tests
- `sample_album_names`: Exemples de noms d'albums pour tests
- `mock_spotify_token`: Token Spotify simulé
- `mock_env_vars`: Variables d'environnement de test

### Marqueurs pytest:
- `@pytest.mark.unit`: Tests unitaires (rapides, sans dépendances externes)
- `@pytest.mark.integration`: Tests d'intégration (peuvent nécessiter APIs)
- `@pytest.mark.slow`: Tests lents (ex: appels API réels)

## Dépendances de test

```txt
pytest>=7.0.0                 # Framework de tests
pytest-cov>=4.0.0             # Couverture de code
pytest-mock>=3.15.0           # Mocking amélioré
```

Installation:
```bash
pip install -r requirements.txt
```

## Meilleures pratiques

### Écrire un nouveau test

1. **Créer une classe de test logique**
```python
class TestMyNewFeature:
    """Tests pour ma nouvelle fonctionnalité."""
    
    def test_basic_behavior(self):
        """Teste le comportement de base."""
        result = my_function()
        assert result is not None
```

2. **Utiliser des fixtures pour éviter la duplication**
```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

3. **Mocker les dépendances externes**
```python
@patch('module.external_api_call')
def test_with_mock(mock_api):
    mock_api.return_value = "mocked response"
    result = my_function_using_api()
    assert result == "expected"
```

4. **Tester les cas limites et erreurs**
```python
def test_empty_input():
    with pytest.raises(ValueError):
        my_function("")

def test_none_input():
    result = my_function(None)
    assert result is None
```

### Conventions de nommage

- **Fichiers**: `test_<module_name>.py`
- **Classes**: `Test<FeatureName>`
- **Fonctions**: `test_<what_is_tested>`

### Docstrings

Chaque test doit avoir une docstring explicative:
```python
def test_token_expiration(self):
    """Teste qu'un token expiré n'est pas retourné par le cache."""
    # ...
```

## CI/CD

Les tests sont automatiquement exécutés:
- À chaque push sur une branche
- À chaque pull request
- Avant chaque merge sur main

Configuration GitHub Actions: `.github/workflows/tests.yml` (à créer)

## Contribuer

1. Écrire des tests pour toute nouvelle fonctionnalité
2. S'assurer que tous les tests passent avant de commit
3. Maintenir une couverture de code > 80%
4. Documenter les tests complexes

## Roadmap des tests

### ✅ Complété (v3.1.0 - v3.3.0)

#### Tests unitaires pour services
- [x] `test_spotify_service.py`: 49 tests (88% couverture)
  - Authentification OAuth
  - Recherche artistes/albums
  - Cache et retry logic
  - Gestion d'erreurs 401/429
  - Timeouts et rate limiting
- [x] `test_ai_service.py`: 31 tests (~85% couverture) ✨ Complété Issue #28
  - Appels API EurIA avec mocking complet
  - Génération de descriptions d'albums
  - Recherche dans collection Discogs
  - Retry automatique et gestion d'erreurs
  - Tests de cas limites et Unicode
- [x] `test_constants.py`: 57 tests (100% couverture)
  - Validation de toutes les constantes du projet
  - Tests de cohérence et utilisation en contexte
- [x] `test_metadata_cleaner.py`: 27 tests (~95% couverture)
  - Nettoyage noms artistes/albums
  - Normalisation pour comparaison
  - Scoring de correspondance
- [x] `test_scheduler.py`: 29 tests (~90% couverture)
  - Initialisation et configuration
  - Gestion des tâches planifiées
  - Persistance de l'état
- [x] `test_chk_roon_integration.py`: 28 tests (intégration) ✨ Complété Issue #28
  - Tests end-to-end du tracker Roon
  - Mock des APIs Roon, Spotify, Last.fm, EurIA
  - Validation du flux complet de traitement
  - Gestion des radios et enrichissement AI
  - Tests de persistance et résilience

### Prochaines étapes (Priorité Basse)

#### Tests d'intégration avancés
- [ ] Tests avec vraies APIs (optionnels, marqueur @slow)
  - Validation des résultats réels vs mocks
  - Rate limiting et retry logic en conditions réelles
- [ ] CI/CD automatisé avec GitHub Actions
  - Exécution automatique des tests sur chaque PR
  - Rapport de couverture de code
  - Notifications sur échecs

**Estimation**: 1 semaine  
**Bénéfice**: Confiance accrue dans les déploiements

#### Tests API réels (marqueur @slow)
- [ ] Tests avec vraies APIs (rate-limited, optionnels)
- [ ] Validation des résultats réels vs mocks

## Support

Pour toute question sur les tests:
- Consulter la documentation pytest: https://docs.pytest.org/
- Voir les exemples dans les fichiers de test existants
- Ouvrir une issue GitHub avec le tag `tests`

---

**Version**: 1.0.0  
**Dernière mise à jour**: 26 janvier 2026  
**Auteur**: Patrick Ostertag
