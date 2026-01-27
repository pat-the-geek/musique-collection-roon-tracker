# Tests - Musique Collection & Tracker

Ce répertoire contient la suite de tests unitaires et d'intégration pour le projet Musique Collection & Tracker.

## Structure des tests

```
src/tests/
├── conftest.py                  # Configuration pytest et fixtures communes
├── test_ai_service.py           # Tests du service AI (37 tests) ✨ Nouveau v2.0.0
├── test_metadata_cleaner.py     # Tests du module metadata_cleaner (27 tests)
├── test_scheduler.py            # Tests du module scheduler (29 tests)
├── test_spotify_service.py      # Tests du service Spotify (49 tests)
└── test_constants.py            # Tests du module constants (57 tests)
```

## Couverture de code

| Module | Tests | Couverture | Status |
|--------|-------|-----------|--------|
| `constants.py` | 57 | 100% | ✅ |
| `spotify_service.py` | 49 | 88% | ✅ |
| `metadata_cleaner.py` | 27 | ~95% | ✅ |
| `scheduler.py` | 29 | ~90% | ✅ |
| `ai_service.py` | 37 | 97% | ✅ |
| **Total** | **199** | **~93%** | ✅ |

## Exécution des tests

### Tous les tests
```bash
cd /home/runner/work/musique-collection-roon-tracker/musique-collection-roon-tracker
python3 -m pytest src/tests/ -v
```

### Tests spécifiques
```bash
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

### test_ai_service.py (37 tests)

Tests complets du service d'intégration EurIA API avec mock des appels.

#### `TestEnsureEnvLoaded` (2 tests)
- Chargement des variables d'environnement
- Gestion du fichier .env absent/présent

#### `TestGetEuriaConfig` (2 tests)
- Récupération de la configuration API EurIA
- Validation des valeurs par défaut
- Gestion des credentials manquants

#### `TestAskForIa` (10 tests)
- Appel API EurIA avec recherche web
- Nettoyage des espaces dans les réponses
- Validation des credentials (URL, bearer token)
- Retry logic sur timeout et erreurs réseau
- Gestion des réponses JSON invalides
- Timeout personnalisé

#### `TestGenerateAlbumInfo` (7 tests)
- Génération d'informations d'albums
- Limite de caractères configurable
- Gestion des stations de radio
- Gestion des artistes inconnus
- Passage correct des paramètres (max_attempts, timeout)

#### `TestGetAlbumInfoFromDiscogs` (10 tests)
- Recherche dans la collection Discogs
- Recherche insensible à la casse
- Gestion des espaces
- Filtrage des résumés vides et génériques
- Gestion des erreurs JSON et I/O
- Albums sans champ Resume

#### `TestIntegrationScenarios` (2 tests)
- Fallback Discogs → API EurIA
- Évitement des appels API si Discogs a l'info

#### `TestEdgeCases` (4 tests)
- Caractères Unicode (accents français)
- Titres d'albums très longs
- Caractères spéciaux dans les prompts
- Collection Discogs vide

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

### Prochaines étapes (Priorité Haute)

#### Tests unitaires AI service (Issue #23 - Priorité Haute)
- [ ] Convertir `test_ai_service.py` en tests pytest
  - Tests unitaires pour `ask_for_ia()` avec mock API
  - Tests unitaires pour `generate_album_info()`
  - Tests unitaires pour `get_album_info_from_discogs()`
  - Mock des appels HTTP vers EurIA API
  - Tests de gestion d'erreurs et retry

**Estimation**: 3-5 jours  
**Bénéfice**: Couverture complète des services centraux

#### Tests d'intégration
- [ ] `test_chk_roon_integration.py`: Tests end-to-end du tracker Roon
  - Mock des réponses Roon API
  - Vérification écriture `chk-roon.json`
  - Test enrichissement Spotify/Last.fm
  - Validation gestion des radios
- [ ] `test_scheduler_integration.py`: Tests d'intégration du scheduler
  - Exécution réelle des tâches (sandbox)
  - Persistance de l'état
  - Configuration dynamique

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
