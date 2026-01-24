# 📋 Configuration Roon - Documentation

## Vue d'ensemble

Le fichier `roon-config.json` contient tous les paramètres de configuration pour le système de tracking Roon/Last.fm. Ce fichier est généré et mis à jour automatiquement par `chk-roon.py`, mais peut être modifié manuellement si nécessaire.

## Structure du fichier

### Champs de connexion Roon (auto-générés)

#### `token` (string)
- **Description**: Token d'authentification Roon Core
- **Format**: UUID (ex: `"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`)
- **Génération**: Automatique lors de la première connexion
- **Modification**: ⚠️ Ne pas modifier manuellement sauf réinitialisation
- **Utilisation**: Authentifie l'application auprès de Roon Core

```json
"token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

#### `host` (string)
- **Description**: Adresse IP du serveur Roon Core
- **Format**: IPv4 (ex: `"192.168.1.100"`)
- **Génération**: Auto-découverte réseau au démarrage
- **Modification**: ✅ Modifiable si Roon Core change d'IP
- **Note**: Doit être sur le même réseau local

```json
"host": "192.168.1.100"
```

#### `port` (string)
- **Description**: Port de connexion Roon Core
- **Format**: String numérique (ex: `"9330"`)
- **Valeur par défaut**: `"9330"` (port standard Roon)
- **Modification**: ⚠️ Rarement nécessaire sauf configuration spéciale

```json
"port": "9330"
```

### Plage horaire d'écoute (configurables)

#### `listen_start_hour` (integer)
- **Description**: Heure de début d'enregistrement des lectures
- **Format**: Entier 0-23 (heure système 24h)
- **Valeur par défaut**: `6` (6h du matin)
- **Modification**: ✅ Modifiable selon vos préférences
- **Exemple**: `8` pour commencer à 8h

```json
"listen_start_hour": 6
```

**Cas d'usage:**
- `6`: Enregistrement dès le réveil
- `8`: Enregistrement à partir du petit-déjeuner
- `18`: Uniquement soirées

#### `listen_end_hour` (integer)
- **Description**: Heure de fin d'enregistrement des lectures
- **Format**: Entier 0-23 (heure système 24h)
- **Valeur par défaut**: `23` (23h, jusqu'à 23h59)
- **Modification**: ✅ Modifiable selon vos préférences
- **Note**: L'heure de fin est **inclusive** (23h inclut 23h00-23h59)

```json
"listen_end_hour": 23
```

**Cas d'usage:**
- `23`: Enregistrement jusqu'à la fin de soirée
- `22`: Arrêt avant le coucher
- `20`: Uniquement journée et début de soirée

### Stations de radio (configurables)

#### `radio_stations` (array of strings)
- **Description**: Liste des stations de radio à détecter et traiter
- **Format**: Array de chaînes de caractères
- **Modification**: ✅ Ajout/suppression libre selon vos stations
- **Utilisation**: Détection automatique + extraction métadonnées musicales

```json
"radio_stations": [
    "RTS La Première",
    "RTS Couleur 3",
    "RTS Espace 2",
    "RTS Option Musique",
    "Radio Meuh",
    "Radio Nova"
]
```

**Fonctionnement:**
Lorsqu'une de ces stations est détectée dans le flux Roon:
1. Le tracker identifie qu'il s'agit d'une radio
2. Parse le champ `artist` au format `"Artiste - Titre"`
3. Recherche l'album sur Spotify
4. Enregistre les métadonnées complètes

**Pour ajouter une station:**
```json
"radio_stations": [
    "RTS La Première",
    "RTS Couleur 3",
    "Ma Station Radio"  // Nouvelle station
]
```

## Exemples de configuration

### Configuration par défaut
```json
{
  "token": "auto-généré",
  "host": "auto-découvert",
  "port": "9330",
  "listen_start_hour": 6,
  "listen_end_hour": 23,
  "radio_stations": [
    "RTS La Première",
    "RTS Couleur 3",
    "RTS Espace 2",
    "RTS Option Musique",
    "Radio Meuh",
    "Radio Nova"
  ]
}
```

### Configuration journée de travail (9h-18h)
```json
{
  "listen_start_hour": 9,
  "listen_end_hour": 18,
  ...
}
```

### Configuration soirées uniquement (18h-minuit)
```json
{
  "listen_start_hour": 18,
  "listen_end_hour": 23,
  ...
}
```

### Configuration 24/7 (enregistrement continu)
```json
{
  "listen_start_hour": 0,
  "listen_end_hour": 23,
  ...
}
```

## Modification du fichier

### Méthode manuelle

1. **Arrêter le tracker** (important):
   ```bash
   # Dans le terminal où tourne chk-roon.py
   Ctrl+C
   ```

2. **Éditer le fichier**:
   ```bash
   # Avec VSCode
   code roon-config.json
   
   # Ou avec nano
   nano roon-config.json
   ```

3. **Vérifier la syntaxe JSON** (recommandé):
   ```bash
   python -m json.tool roon-config.json
   ```

4. **Relancer le tracker**:
   ```bash
   ./start-roon-tracker.sh
   ```

### Méthode programmatique (Python)

```python
import json

# Charger la configuration
with open('roon-config.json', 'r') as f:
    config = json.load(f)

# Modifier les paramètres
config['listen_start_hour'] = 8
config['listen_end_hour'] = 22
config['radio_stations'].append('Ma Radio')

# Sauvegarder
with open('roon-config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Validation et dépannage

### Vérifier la syntaxe JSON

```bash
python -m json.tool roon-config.json
```

✅ **Correct**: Affiche le JSON formaté  
❌ **Erreur**: Affiche l'erreur de syntaxe à corriger

### Problèmes courants

#### Erreur: "Aucun Roon Core trouvé"
- Vérifier que `host` correspond à l'IP actuelle de Roon Core
- Vérifier que Roon Core est démarré
- Vérifier la connexion réseau

#### Erreur: "Token non reçu"
- Supprimer le champ `token` du fichier
- Relancer le tracker
- Réautoriser dans Roon > Paramètres > Extensions

#### Pistes non enregistrées
- Vérifier `listen_start_hour` et `listen_end_hour`
- S'assurer que l'heure actuelle est dans la plage
- Vérifier les logs de debug

## Intégration avec chk-roon.py

### Lecture de la configuration

Le script `chk-roon.py` lit ce fichier via la fonction `load_roon_config()`:

```python
def load_roon_config() -> dict:
    """Charge la configuration Roon depuis le fichier JSON."""
    if os.path.exists(ROON_CONFIG_FILE):
        with open(ROON_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Valeurs par défaut si manquantes
            if 'listen_start_hour' not in config:
                config['listen_start_hour'] = 6
            if 'listen_end_hour' not in config:
                config['listen_end_hour'] = 23
            return config
    return {'listen_start_hour': 6, 'listen_end_hour': 23}
```

### Sauvegarde automatique

Le fichier est mis à jour automatiquement:
- **À la première connexion**: Enregistre `token`, `host`, `port`
- **Après changement de serveur**: Met à jour `host` et `port`
- **Préserve toujours**: Les heures d'écoute et stations radio

## Sauvegarde et restauration

### Créer une sauvegarde

```bash
# Backup manuel
cp roon-config.json roon-config.json.backup

# Backup avec date
cp roon-config.json "roon-config-$(date +%Y%m%d-%H%M%S).json"
```

### Restaurer une sauvegarde

```bash
# Arrêter le tracker
# Terminal où tourne chk-roon.py: Ctrl+C

# Restaurer
cp roon-config.json.backup roon-config.json

# Relancer
./start-roon-tracker.sh
```

## Réinitialisation complète

Pour repartir de zéro:

```bash
# 1. Arrêter le tracker
# Ctrl+C dans le terminal

# 2. Sauvegarder l'ancien config (optionnel)
mv roon-config.json roon-config.json.old

# 3. Créer nouvelle configuration minimale
cat > roon-config.json << 'EOF'
{
  "listen_start_hour": 6,
  "listen_end_hour": 23,
  "radio_stations": [
    "RTS La Première",
    "RTS Couleur 3",
    "RTS Espace 2",
    "RTS Option Musique",
    "Radio Meuh",
    "Radio Nova"
  ]
}
EOF

# 4. Relancer (va recréer token, host, port)
./start-roon-tracker.sh

# 5. Réautoriser dans Roon
# Roon > Paramètres > Extensions > Autoriser "Python Roon Tracker"
```

## Sécurité et confidentialité

### Informations sensibles

- ⚠️ **Token**: Unique à votre installation, ne pas partager
- ⚠️ **Host**: IP privée, pas d'exposition publique
- ✅ **Heures/stations**: Configuration personnelle, sans risque

### Bonnes pratiques

1. **Ne pas versionner avec Git** (si projet public)
   ```bash
   echo "roon-config.json" >> .gitignore
   ```

2. **Permissions fichier** (Linux/macOS)
   ```bash
   chmod 600 roon-config.json
   ```

3. **Backup régulier**
   ```bash
   # Ajouter à crontab (chaque semaine)
   0 0 * * 0 cp /chemin/roon-config.json /chemin/backups/roon-config-$(date +\%Y\%m\%d).json
   ```

## Voir aussi

- [README-ROON-TRACKER.md](README-ROON-TRACKER.md) - Documentation complète du tracker
- [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Guide développement
- [chk-roon.py](../src/trackers/chk-roon.py) - Code source du tracker

---

**Version**: 1.0  
**Dernière mise à jour**: 23 janvier 2026  
**Auteur**: Patrick Ostertag
