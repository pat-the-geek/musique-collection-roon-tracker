# 🗄️ Schéma de Base de Données - Migration SQLite

**Version: 1.0.0** | **Date: 27 janvier 2026**

Ce document décrit le schéma relationnel conçu pour migrer le projet depuis le stockage JSON vers une base de données SQLite.

---

## 📋 Objectifs de la Migration

### Pourquoi SQLite ?

1. **Performance** : Requêtes rapides avec index optimisés
2. **Intégrité** : Contraintes relationnelles et validation automatique
3. **Scalabilité** : Gestion de millions d'écoutes sans dégradation
4. **Concurrence** : Accès multi-utilisateurs sans corruption de données
5. **Requêtage** : SQL standard pour analyses complexes

### Avantages du Modèle Relationnel

- ✅ **Normalisation** : Élimination de la redondance (artistes/albums uniques)
- ✅ **Relations Many-to-Many** : Support natif des albums multi-artistes
- ✅ **Index performants** : Recherche rapide par nom, date, source
- ✅ **Évolutivité** : Ajout facile de nouvelles tables/relations
- ✅ **Intégrité référentielle** : Cascade de suppression automatique

---

## 🏗️ Architecture du Schéma

### Diagramme Entité-Relations (ERD)

```mermaid
erDiagram
    ARTISTS ||--o{ ALBUM_ARTIST : "participe_a"
    ALBUMS ||--o{ ALBUM_ARTIST : "contient"
    ALBUMS ||--o{ TRACKS : "contient"
    TRACKS ||--o{ LISTENING_HISTORY : "ecoute"
    ARTISTS ||--o{ IMAGES : "possede"
    ALBUMS ||--o{ IMAGES : "possede"
    ALBUMS ||--|| METADATA : "enrichi_par"
    
    ARTISTS {
        int id PK
        string name UK
        string spotify_id
        string lastfm_url
        datetime created_at
        datetime updated_at
    }
    
    ALBUMS {
        int id PK
        string title
        int year
        string support
        string discogs_id UK
        string spotify_url
        string discogs_url
        datetime created_at
        datetime updated_at
    }
    
    TRACKS {
        int id PK
        int album_id FK
        string title
        int track_number
        int duration_seconds
        string spotify_id
        datetime created_at
        datetime updated_at
    }
    
    LISTENING_HISTORY {
        int id PK
        int track_id FK
        int timestamp
        string date
        string source
        boolean loved
        datetime created_at
    }
    
    IMAGES {
        int id PK
        string url
        string image_type
        string source
        int artist_id FK
        int album_id FK
        datetime created_at
        datetime updated_at
    }
    
    METADATA {
        int id PK
        int album_id FK_UK
        string ai_info
        text resume
        boolean is_soundtrack
        string film_title
        int film_year
        string film_director
        datetime created_at
        datetime updated_at
    }
    
    ALBUM_ARTIST {
        int album_id FK_PK
        int artist_id FK_PK
        datetime created_at
    }
```

---

## 📊 Description des Tables

### 1. **artists** - Artistes Musicaux

Stocke les artistes de manière unique et centralisée.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identifiant unique |
| `name` | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | Nom de l'artiste |
| `spotify_id` | VARCHAR(100) | NULL | Identifiant Spotify |
| `lastfm_url` | VARCHAR(500) | NULL | URL Last.fm |
| `created_at` | DATETIME | DEFAULT NOW | Date de création |
| `updated_at` | DATETIME | DEFAULT NOW, ON UPDATE | Date de mise à jour |

**Index:** `idx_artists_name` sur `name`

**Relations:**
- Many-to-Many avec `albums` via `album_artist`
- One-to-Many avec `images` (images d'artiste)

---

### 2. **albums** - Albums Musicaux

Stocke les albums avec métadonnées enrichies.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identifiant unique |
| `title` | VARCHAR(500) | NOT NULL, INDEX | Titre de l'album |
| `year` | INTEGER | NULL | Année sortie/réédition |
| `support` | VARCHAR(50) | NULL | Format (Vinyle, CD, etc.) |
| `discogs_id` | VARCHAR(100) | NULL, UNIQUE | ID Discogs |
| `spotify_url` | VARCHAR(500) | NULL | URL Spotify |
| `discogs_url` | VARCHAR(500) | NULL | URL Discogs |
| `created_at` | DATETIME | DEFAULT NOW | Date de création |
| `updated_at` | DATETIME | DEFAULT NOW, ON UPDATE | Date de mise à jour |

**Index:**
- `idx_albums_title` sur `title`
- `idx_album_title_year` sur (`title`, `year`)

**Relations:**
- Many-to-Many avec `artists` via `album_artist`
- One-to-Many avec `tracks`
- One-to-Many avec `images` (pochettes)
- One-to-One avec `metadata` (via `album_metadata` relationship)

---

### 3. **tracks** - Pistes Musicales

Stocke les pistes individuelles liées aux albums.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identifiant unique |
| `album_id` | INTEGER | FOREIGN KEY (albums), NOT NULL | Album parent |
| `title` | VARCHAR(500) | NOT NULL | Titre de la piste |
| `track_number` | INTEGER | NULL | Numéro de piste |
| `duration_seconds` | INTEGER | NULL | Durée en secondes |
| `spotify_id` | VARCHAR(100) | NULL | ID Spotify |
| `created_at` | DATETIME | DEFAULT NOW | Date de création |
| `updated_at` | DATETIME | DEFAULT NOW, ON UPDATE | Date de mise à jour |

**Index:** `idx_track_album_title` sur (`album_id`, `title`)

**Relations:**
- Many-to-One avec `albums`
- One-to-Many avec `listening_history`

---

### 4. **listening_history** - Historique d'Écoute

Enregistre chaque écoute avec source et timestamp.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identifiant unique |
| `track_id` | INTEGER | FOREIGN KEY (tracks), NOT NULL | Piste écoutée |
| `timestamp` | INTEGER | NOT NULL, INDEX | Timestamp Unix |
| `date` | VARCHAR(20) | NOT NULL | Date formatée (YYYY-MM-DD HH:MM) |
| `source` | VARCHAR(20) | NOT NULL, INDEX | Source (roon/lastfm) |
| `loved` | BOOLEAN | DEFAULT FALSE | Marqueur favori |
| `created_at` | DATETIME | DEFAULT NOW | Date de création |

**Index:**
- `idx_listening_history_timestamp` sur `timestamp`
- `idx_listening_history_source` sur `source`
- `idx_timestamp_source` sur (`timestamp`, `source`)

**Contraintes:**
- `UNIQUE (track_id, timestamp)` - Évite doublons

**Relations:**
- Many-to-One avec `tracks`

---

### 5. **images** - URLs d'Images

Stocke les URLs d'images publiques (Spotify, Last.fm, Discogs).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identifiant unique |
| `url` | VARCHAR(1000) | NOT NULL | URL de l'image |
| `image_type` | VARCHAR(50) | NOT NULL | Type (artist_image, album_cover) |
| `source` | VARCHAR(50) | NOT NULL | Source (spotify, lastfm, discogs) |
| `artist_id` | INTEGER | FOREIGN KEY (artists), NULL | Artiste associé |
| `album_id` | INTEGER | FOREIGN KEY (albums), NULL | Album associé |
| `created_at` | DATETIME | DEFAULT NOW | Date de création |
| `updated_at` | DATETIME | DEFAULT NOW, ON UPDATE | Date de mise à jour |

**Index:**
- `idx_image_artist` sur (`artist_id`, `image_type`, `source`)
- `idx_image_album` sur (`album_id`, `image_type`, `source`)

**Relations:**
- Many-to-One avec `artists` (si artist_id renseigné)
- Many-to-One avec `albums` (si album_id renseigné)

---

### 6. **metadata** - Métadonnées Supplémentaires

Enrichit les albums avec informations IA, résumés, BOF.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identifiant unique |
| `album_id` | INTEGER | FOREIGN KEY (albums), NOT NULL, UNIQUE | Album associé |
| `ai_info` | VARCHAR(500) | NULL | Info courte générée par IA |
| `resume` | TEXT | NULL | Résumé détaillé |
| `is_soundtrack` | BOOLEAN | DEFAULT FALSE | Indicateur BOF |
| `film_title` | VARCHAR(500) | NULL | Titre du film |
| `film_year` | INTEGER | NULL | Année du film |
| `film_director` | VARCHAR(255) | NULL | Réalisateur |
| `created_at` | DATETIME | DEFAULT NOW | Date de création |
| `updated_at` | DATETIME | DEFAULT NOW, ON UPDATE | Date de mise à jour |

**Relations:**
- One-to-One avec `albums`

---

### 7. **album_artist** - Table de Liaison (Many-to-Many)

Gère la relation Many-to-Many entre artistes et albums.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `album_id` | INTEGER | FOREIGN KEY (albums), PRIMARY KEY | Album |
| `artist_id` | INTEGER | FOREIGN KEY (artists), PRIMARY KEY | Artiste |
| `created_at` | DATETIME | DEFAULT NOW | Date de création |

**Contraintes:**
- `PRIMARY KEY (album_id, artist_id)`

---

## 🚀 Exemples de Requêtes SQL

### Recherche d'Albums par Artiste

```sql
SELECT a.title, a.year, ar.name as artist
FROM albums a
JOIN album_artist aa ON a.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
WHERE ar.name = 'Nina Simone'
ORDER BY a.year DESC;
```

### Top 10 Pistes les Plus Écoutées

```sql
SELECT t.title, al.title as album, ar.name as artist, COUNT(lh.id) as play_count
FROM tracks t
JOIN albums al ON t.album_id = al.id
JOIN album_artist aa ON al.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
JOIN listening_history lh ON t.id = lh.track_id
GROUP BY t.id
ORDER BY play_count DESC
LIMIT 10;
```

### Historique d'Écoute du Jour

```sql
SELECT ar.name as artist, t.title, al.title as album, lh.date, lh.source
FROM listening_history lh
JOIN tracks t ON lh.track_id = t.id
JOIN albums al ON t.album_id = al.id
JOIN album_artist aa ON al.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
WHERE DATE(datetime(lh.timestamp, 'unixepoch')) = DATE('now')
ORDER BY lh.timestamp DESC;
```

### Albums avec Informations IA

```sql
SELECT a.title, a.year, ar.name as artist, m.ai_info
FROM albums a
JOIN album_artist aa ON a.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
LEFT JOIN metadata m ON a.id = m.album_id
WHERE m.ai_info IS NOT NULL;
```

### Statistiques par Source (Roon vs Last.fm)

```sql
SELECT source, COUNT(*) as total_plays
FROM listening_history
WHERE timestamp >= strftime('%s', 'now', '-30 days')
GROUP BY source;
```

---

## 📦 Mapping JSON → SQLite

### Structure JSON Actuelle

#### `data/history/chk-roon.json`
```json
{
  "tracks": [
    {
      "timestamp": 1768674069,
      "date": "2026-01-17 18:21",
      "artist": "Serge Gainsbourg",
      "title": "Couleur Cafe (Live)",
      "album": "Le Zenith De Gainsbourg",
      "loved": false,
      "artist_spotify_image": "https://...",
      "album_spotify_image": "https://...",
      "album_lastfm_image": "https://...",
      "source": "roon",
      "ai_info": "Album description..."
    }
  ]
}
```

#### `data/collection/discogs-collection.json`
```json
[
  {
    "Titre": "Pastel Blues",
    "Artiste": ["Nina Simone"],
    "Annee": 1965,
    "Support": "Vinyle",
    "Pochette": "https://...",
    "Spotify_Cover_URL": "https://...",
    "Resume": "Album summary...",
    "discogs_url": "https://..."
  }
]
```

### Stratégie de Migration

#### Phase 1: Import Collection Discogs

1. **Créer artistes** depuis `Artiste` array (dédupliquer)
2. **Créer albums** depuis `Titre`, `Annee`, `Support`
3. **Créer relations** album_artist
4. **Créer images** depuis `Pochette`, `Spotify_Cover_URL`
5. **Créer metadata** depuis `Resume`, soundtrack.json

#### Phase 2: Import Historique Roon

1. **Créer artistes** si non existants
2. **Créer albums** si non existants
3. **Créer tracks** depuis `title` (dédupliquer par album + titre)
4. **Créer listening_history** depuis `timestamp`, `date`, `source`, `loved`
5. **Créer images** depuis `*_spotify_image`, `*_lastfm_image`
6. **Créer metadata.ai_info** depuis `ai_info` si présent

#### Phase 3: Validation et Déduplication

1. **Normaliser noms d'artistes** (supprimer suffixes Discogs, annotations)
2. **Fusionner doublons** (albums identiques, artistes homonymes)
3. **Vérifier intégrité** (clés étrangères, contraintes)
4. **Créer index** pour performance

---

## 🛠️ Implémentation Technique

### Stack Technologique

- **ORM**: SQLAlchemy 2.0+ (Python)
- **Base de données**: SQLite 3.x
- **Migrations**: Alembic (optionnel, futur)
- **Tests**: pytest + fixtures

### Fichiers Créés

```
src/models/
├── __init__.py          # Exports des modèles
└── schema.py            # Définitions SQLAlchemy

src/maintenance/
└── migrate_to_sqlite.py # Script de migration (à créer)

src/tests/
└── test_models.py       # Tests unitaires (à créer)

data/
└── musique.db           # Base SQLite (générée)
```

### Exemple d'Utilisation

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.schema import Base, Artist, Album, Track

# Créer la base de données
engine = create_engine('sqlite:///data/musique.db')
Base.metadata.create_all(engine)

# Créer une session
Session = sessionmaker(bind=engine)
session = Session()

# Créer un artiste
artist = Artist(name="Nina Simone", spotify_id="abc123")
session.add(artist)

# Créer un album
album = Album(title="Pastel Blues", year=1965, support="Vinyle")
album.artists.append(artist)
session.add(album)

# Commit
session.commit()

# Requête
results = session.query(Artist).filter_by(name="Nina Simone").all()
```

---

## 🎯 Prochaines Étapes

### Court Terme (Sprint actuel)

- [x] Définir le schéma SQLAlchemy complet
- [x] Créer la documentation avec diagramme Mermaid
- [x] Ajouter SQLAlchemy aux dépendances
- [ ] Créer tests unitaires pour les modèles
- [ ] Valider contraintes et relations

### Moyen Terme (Prochains sprints)

- [ ] Implémenter script de migration `migrate_to_sqlite.py`
- [ ] Tester migration avec données réelles
- [ ] Créer backup automatique JSON avant migration
- [ ] Adapter scripts existants pour utiliser SQLite
- [ ] Mesurer amélioration des performances

### Long Terme (Évolution future)

- [ ] Migrer tous les scripts vers SQLite
- [ ] Ajouter Alembic pour migrations incrémentales
- [ ] Implémenter cache requêtes fréquentes
- [ ] Créer API REST pour accès externe
- [ ] Support multi-utilisateurs avec authentification

---

## 📚 Références

### Documentation

- [SQLAlchemy ORM Documentation](https://docs.sqlalchemy.org/en/20/orm/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)

### Fichiers Projet

- `src/models/schema.py` - Définitions des modèles
- `.github/copilot-instructions.md` - Guide complet du projet
- `docs/ARCHITECTURE-OVERVIEW.md` - Architecture actuelle JSON

### Issues GitHub

- [#42 - Préparer la migration vers SQLite](https://github.com/pat-the-geek/musique-collection-roon-tracker/issues/42)

---

**Auteur:** Patrick Ostertag  
**Date:** 27 janvier 2026  
**Version:** 1.0.0  
**Statut:** ✅ Documentation Complète
