# 🎵 Album Haiku Generator

Générateur automatique de présentations courtes (haïkus) pour albums musicaux sélectionnés aléatoirement depuis votre collection Discogs et votre historique d'écoutes Roon.

## 📋 Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du fichier de sortie](#structure-du-fichier-de-sortie)
- [Architecture](#architecture)
- [Exemples](#exemples)
- [Dépannage](#dépannage)

## 🎯 Présentation

Ce script Python génère automatiquement des présentations courtes et poétiques pour 20 albums musicaux :
- **10 albums** de votre collection Discogs
- **10 albums** de votre historique d'écoutes Roon

Chaque album est accompagné d'une description concise (35 mots maximum) générée par l'intelligence artificielle EurIA (Qwen3), avec images, métadonnées et liens vers Spotify et Discogs.

Le résultat est un fichier texte formaté pour **iA Presenter**, prêt à être utilisé pour une présentation visuelle de votre passion musicale.

## ✨ Fonctionnalités

### Sélection intelligente
- ✅ Sélection **aléatoire sécurisée** avec `secrets.SystemRandom()`
- ✅ Extraction des albums **uniques** depuis l'historique Roon
- ✅ Filtrage automatique des entrées "Inconnu"

### Génération de contenu
- 🤖 Descriptions **générées par IA** (EurIA/Qwen3)
- 🌐 Recherche web activée pour contexte enrichi
- 📝 Limite de **35 mots** par description
- 🇫🇷 Réponses en français uniquement

### Enrichissement visuel
- 🖼️ Images d'albums depuis **Spotify** et **Last.fm**
- 🎨 Support des couvertures haute résolution
- 📊 Affichage des métadonnées complètes

### Formatage intelligent
- 📄 Formatage automatique pour **iA Presenter**
- 📏 Découpage de texte en lignes de 45 caractères
- 🔗 Liens cliquables vers Spotify et Discogs
- 📅 Gestion des rééditions et dates

## 🔧 Prérequis

### Système
- Python 3.8 ou supérieur
- macOS, Linux ou Windows

### Fichiers requis
- `discogs-collection.json` - Collection Discogs exportée
- `chk-roon.json` - Historique d'écoutes Roon

### Compte API
- **Infomaniak EurIA API** - Clé d'accès pour l'IA Qwen3

## 📦 Installation

### 1. Créer l'environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
# ou
.venv\Scripts\activate     # Sur Windows
```

### 2. Installer les dépendances

```bash
pip install requests python-dotenv
```

### 3. Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Configuration EurIA API (Infomaniak)
URL=https://api.infomaniak.com/2/ai/106561/openai/v1/chat/completions
bearer=votre_token_euria_ici
max_attempts=5
default_error_message=Aucune information disponible
```

**Obtenir votre token EurIA :**
1. Connectez-vous à votre compte Infomaniak
2. Accédez à la section API
3. Générez un token pour l'API EurIA

## ⚙️ Configuration

### Fichiers de données

Le script attend deux fichiers JSON dans le même répertoire :

#### `discogs-collection.json`
Collection Discogs avec la structure suivante :
```json
[
  {
    "release_id": 123456,
    "Titre": "Album Title",
    "Artiste": ["Artist Name"],
    "Année": 2020,
    "Pochette": "https://...",
    "Support": "Vinyle",
    "Spotify_URL": "https://...",
    "Spotify_Date": 2020,
    "Spotify_Cover_URL": "https://..."
  }
]
```

#### `chk-roon.json`
Historique Roon avec la structure suivante :
```json
{
  "tracks": [
    {
      "artist": "Artist Name",
      "album": "Album Title",
      "album_spotify_image": "https://...",
      "album_lastfm_image": "https://...",
      "artist_spotify_image": "https://..."
    }
  ]
}
```

### Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `URL` | URL de l'API EurIA | https://api.infomaniak.com/... |
| `bearer` | Token d'authentification | votre_token_euria |
| `max_attempts` | Tentatives max par requête | 5 |
| `default_error_message` | Message par défaut si échec | Aucune information disponible |

## 🚀 Utilisation

### Lancement simple

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer le générateur
python3 generate-haiku.py
```

### Sortie console

Le script affiche sa progression en temps réel :

```
Nina Simone
Pastel Blues (1965)
https://open.spotify.com/album/...
Pastel Blues capture Nina Simone dans toute sa
puissance vocale, mêlant blues profond et
gospel...
---

[...]

Les résultats ont été enregistrés dans generate-haiku-20260121-095530.txt.
```

### Fichier généré

Un fichier `generate-haiku-YYYYMMDD-HHMMSS.txt` est créé avec :
- En-tête avec date poétique
- Statistiques (nombre d'albums par source)
- 20 présentations d'albums formatées
- Footer avec signature

## 📄 Structure du fichier de sortie

### En-tête

```markdown
# Album Haïku
#### The 21 of January, 2026
		10 albums from Discogs collection
		10 albums from Roon listening history
		Random discs spin,
		whispers of vinyl dreams rise
		eyes wide, heart adrift
---
```

### Présentation d'un album

```markdown
# Nina Simone
#### Pastel Blues (1965)
	###### 🎧 [Listen with Spotify](https://open.spotify.com/album/...)  👥 [Read on Discogs](https://www.discogs.com/release/123456)
	###### 💿 Vinyle
		Pastel Blues capture Nina Simone dans toute sa
		puissance vocale, mêlant blues profond et
		gospel émotionnel avec des arrangements
		orchestraux subtils.

<img src='https://i.scdn.co/image/...' />
---
```

### Cas particuliers

#### Album avec réédition
```markdown
#### Album Title (1980) - Reissue 2020
```

#### Album depuis Roon (sans Discogs)
```markdown
	###### 🎧 From Roon listening history
```

## 🏗️ Architecture

### Modules et fonctions

| Fonction | Description |
|----------|-------------|
| `decouper_en_lignes(texte)` | Découpe le texte en lignes de 45 caractères avec indentation |
| `ask_for_ia(prompt, max_attempts, timeout)` | Envoie un prompt à l'API EurIA avec gestion des erreurs |
| `nettoyer_nom_artiste(nom_artiste)` | Nettoie les noms d'artistes (liste → string, suppression "(n)") |
| `get_current_datetime_forFileName()` | Génère un timestamp YYYYMMDD-HHMMSS |
| `poetic_date()` | Formate la date en style poétique anglais |
| `generate_haiku_from_artist_and_album(artist, album)` | Génère la description de l'album via IA |

### Flux d'exécution

```
┌──────────────────────┐
│ Chargement .env      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Lecture JSON         │
│ - discogs-collection │
│ - chk-roon           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Extraction albums    │
│ uniques (Roon)       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Sélection aléatoire  │
│ - 10 Discogs         │
│ - 10 Roon            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Pour chaque album:   │
│ - Nettoyage données  │
│ - Génération IA      │
│ - Formatage texte    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Écriture fichier     │
│ .txt formaté         │
└──────────────────────┘
```

## 💡 Exemples

### Exemple de prompt envoyé à l'IA

```
Présente moi l'album pastel blues de nina simone. 
N'ajoute pas de questions ou de commentaires. 
Limite ta réponse à 35 mots maximum.
Réponds uniquement en français.
```

### Exemple de réponse IA

```
Pastel Blues capture Nina Simone dans toute sa puissance vocale, 
mêlant blues profond et gospel émotionnel avec des arrangements 
orchestraux subtils qui soulignent son engagement politique naissant.
```

### Exemple de découpage

Le texte est automatiquement découpé en lignes de 45 caractères :

```
		Pastel Blues capture Nina Simone dans
		toute sa puissance vocale, mêlant blues
		profond et gospel émotionnel avec des
		arrangements orchestraux subtils.
```

## 🔍 Dépannage

### Erreur : "ValueError: invalid literal for int()"

**Cause** : Données manquantes dans le JSON

**Solution** : Le script gère maintenant cette erreur. Vérifiez que vos fichiers JSON sont bien formés.

### Erreur : "No module named 'requests'"

**Cause** : Dépendances non installées

**Solution** :
```bash
pip install requests python-dotenv
```

### Erreur : "FileNotFoundError: discogs-collection.json"

**Cause** : Fichiers JSON manquants

**Solution** : Assurez-vous que les fichiers suivants existent :
- `discogs-collection.json`
- `chk-roon.json`

### Erreur API : "Erreur 401 Unauthorized"

**Cause** : Token EurIA invalide ou expiré

**Solution** :
1. Vérifiez votre fichier `.env`
2. Régénérez un token sur Infomaniak
3. Mettez à jour la variable `bearer`

### Images manquantes dans le résultat

**Cause** : URL d'image non disponible dans le JSON source

**Solution** : Normal pour certains albums. Le script utilise les images disponibles :
1. Spotify (priorité)
2. Last.fm (fallback)
3. Discogs (fallback)

### L'IA retourne toujours le même message d'erreur

**Cause** : Problème de connexion à l'API ou quota dépassé

**Solution** :
1. Vérifiez votre connexion Internet
2. Vérifiez votre quota API sur Infomaniak
3. Augmentez `max_attempts` dans `.env`

## 📊 Statistiques et performance

### Temps d'exécution moyen

- **20 albums** : ~2-3 minutes
  - ~5-8 secondes par requête API
  - Dépend de la vitesse réseau et de la charge API

### Consommation API

- **20 requêtes** EurIA par exécution
- Environ **700-1000 mots** générés au total
- Recherche web activée pour contexte enrichi

## 🔒 Sécurité

### Gestion des secrets

- ✅ **Jamais** commiter le fichier `.env`
- ✅ Utiliser `.gitignore` pour exclure `.env`
- ✅ Token EurIA stocké uniquement localement

### Exemple `.gitignore`

```gitignore
.env
.venv/
*.pyc
__pycache__/
```

## 🤝 Contribution

### Améliorations possibles

- [ ] Support de sources additionnelles (Apple Music, Deezer)
- [ ] Paramétrage du nombre d'albums par source
- [ ] Choix de la langue de description
- [ ] Export en formats additionnels (PDF, HTML)
- [ ] Interface graphique (GUI)

## 📝 Changelog

### Version 2.1.0 (21 janvier 2026)
- ✨ Détection et élimination des doublons entre Discogs et Roon
- ✨ Fonction normalize_album_key() pour normalisation
- 🐛 Garantit 20 albums uniques (pas de répétitions)

### Version 2.0.0 (21 janvier 2026)
- ✨ Ajout du support des albums Roon (10 + 10 albums)
- ✨ Extraction automatique des albums uniques depuis l'historique
- 📝 Documentation complète avec docstrings Python
- 🐛 Correction de la gestion des valeurs None/vides
- 🐛 Gestion sécurisée de la conversion des types

### Version 1.0.0
- 🎉 Version initiale
- ✅ Sélection de 10 albums depuis Discogs
- ✅ Génération de descriptions via EurIA
- ✅ Export formaté pour iA Presenter

## 📚 Références

- [API Infomaniak EurIA](https://www.infomaniak.com/fr/euria)
- [iA Presenter](https://ia.net/presenter)
- [Discogs API](https://www.discogs.com/developers)
- [Python dotenv](https://github.com/theskumar/python-dotenv)

## 📄 Licence

Projet personnel - Patrick Ostertag © 2026

---

**Version**: 2.1.0  
**Dernière mise à jour**: 21 janvier 2026  
**Auteur**: Patrick Ostertag
