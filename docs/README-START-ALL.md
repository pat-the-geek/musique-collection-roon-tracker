# 🚀 Guide d'utilisation de start-all.sh

## Vue d'ensemble

Le script `start-all.sh` permet de lancer **simultanément** le tracker Roon et l'interface web Streamlit en un seul clic, simplifiant ainsi l'utilisation quotidienne du système de tracking musical.

## Fonctionnalités

- ✅ Démarrage simultané du tracker Roon et de l'interface Streamlit
- ✅ Gestion propre de l'arrêt des deux processus (Ctrl+C)
- ✅ Option pour désactiver l'ouverture automatique du navigateur
- ✅ Messages d'état clairs et informatifs
- ✅ Vérification de l'environnement virtuel
- ✅ Temporisation pour un démarrage optimal

## Utilisation

### Lancement standard (avec navigateur)

```bash
# Depuis la racine du projet
./start-all.sh
```

Ce mode :
- Lance le tracker Roon en arrière-plan
- Lance l'interface Streamlit en arrière-plan
- **Ouvre automatiquement** l'interface web dans votre navigateur par défaut
- Affiche les URLs et informations de connexion

### Lancement sans navigateur

```bash
# Pour éviter l'ouverture automatique du navigateur
./start-all.sh --no-browser
```

Ce mode est utile lorsque :
- Vous avez déjà un onglet ouvert sur l'interface
- Vous voulez utiliser un navigateur différent
- Vous lancez les services sur un serveur distant
- Vous préférez ouvrir manuellement l'URL

### Arrêt des services

Pour arrêter proprement les deux services :

```bash
# Appuyez sur Ctrl+C dans le terminal
```

Le script :
- Capture le signal d'interruption
- Arrête le tracker Roon
- Arrête l'interface Streamlit
- Affiche des messages de confirmation

## Flux d'exécution

1. **Vérification** : Le script vérifie que l'environnement virtuel `.venv` existe
2. **Activation** : Active l'environnement virtuel Python
3. **Options** : Détecte l'option `--no-browser` si présente
4. **Tracker Roon** : Lance `python3 src/trackers/chk-roon.py` en arrière-plan
5. **Pause** : Attend 2 secondes pour stabiliser le tracker
6. **Streamlit** : Lance `streamlit run src/gui/musique-gui.py` avec ou sans navigateur
7. **Attente** : Reste actif et surveille les processus jusqu'à Ctrl+C

## Messages affichés

### Au démarrage

```
🚀 Démarrage des services...

📻 Démarrage du tracker Roon...
✅ Tracker Roon lancé (PID: 12345)

🌐 Démarrage de l'interface Streamlit...
✅ Streamlit lancé (PID: 12346)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Services démarrés avec succès!

📻 Tracker Roon: Surveillance des lectures en cours...
🌐 Interface Web: http://localhost:8501

Appuyez sur Ctrl+C pour arrêter les deux services
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### À l'arrêt (Ctrl+C)

```
🛑 Arrêt des services...
✅ Tracker Roon arrêté
✅ Streamlit arrêté
```

## Cas d'erreur

### Environnement virtuel manquant

Si `.venv` n'existe pas :
```
❌ Environnement virtuel non trouvé.
Exécutez d'abord: ./scripts/setup-roon-tracker.sh
```

**Solution** : Lancez le script de setup :
```bash
./scripts/setup-roon-tracker.sh
```

## Emplacements du script

Le script existe en deux versions identiques :

1. **`./start-all.sh`** (racine du projet) - **RECOMMANDÉ**
   - Plus rapide à taper
   - Cohérent avec `./start-roon-tracker.sh`

2. **`./scripts/start-all.sh`** (dans le répertoire scripts)
   - Cohérent avec l'organisation du projet
   - Utilise `cd "$(dirname "$0")/..` pour remonter à la racine

Les deux versions fonctionnent de manière identique.

## Comparaison avec le lancement séparé

### Avant (lancement manuel)

```bash
# Terminal 1
./start-roon-tracker.sh

# Terminal 2
./scripts/start-streamlit.sh
```

**Inconvénients** :
- Nécessite deux terminaux
- Difficile d'arrêter les deux services en même temps
- Plus de manipulation

### Maintenant (start-all.sh)

```bash
# Un seul terminal
./start-all.sh
```

**Avantages** :
- ✅ Un seul terminal nécessaire
- ✅ Arrêt simultané avec Ctrl+C
- ✅ Moins d'étapes
- ✅ Plus rapide

## Configuration requise

### Prérequis

- Environnement virtuel Python créé (`.venv`)
- Dépendances installées (`pip install -r requirements.txt`)
- Configuration `.env` présente dans `data/config/`
- Roon Core accessible sur le réseau (pour le tracker)

### Ports utilisés

- **Roon API** : 9330 (auto-découvert)
- **Streamlit** : 8501 (par défaut)

## Dépannage

### Le script ne démarre pas

1. Vérifiez que l'environnement virtuel existe :
   ```bash
   ls -la .venv
   ```

2. Si absent, créez-le :
   ```bash
   ./scripts/setup-roon-tracker.sh
   ```

### Streamlit ne s'ouvre pas

- Vérifiez que le port 8501 n'est pas déjà utilisé :
  ```bash
  lsof -i :8501
  ```

- Si occupé, arrêtez le processus existant ou utilisez un autre port

### Le tracker Roon ne se connecte pas

- Vérifiez que Roon Core est en cours d'exécution
- Vérifiez votre configuration réseau
- Consultez `docs/README-ROON-TRACKER.md` pour plus de détails

## Architecture technique

### Gestion des processus

Le script utilise :
- **Jobs en arrière-plan** : `&` pour lancer les processus
- **PIDs** : Stockés dans `$ROON_PID` et `$STREAMLIT_PID`
- **Trap** : `trap cleanup SIGINT SIGTERM` pour capturer Ctrl+C
- **Cleanup** : Fonction pour tuer proprement les processus

### Code de cleanup

```bash
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    if [ ! -z "$ROON_PID" ]; then
        kill $ROON_PID 2>/dev/null
        echo "✅ Tracker Roon arrêté"
    fi
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null
        echo "✅ Streamlit arrêté"
    fi
    exit 0
}
```

## Intégration future

### Améliorations possibles

- [ ] Support pour lancer des services supplémentaires
- [ ] Configuration du port Streamlit via argument
- [ ] Logs vers fichiers avec rotation
- [ ] Détection automatique de services déjà lancés
- [ ] Mode daemon (détacher du terminal)
- [ ] Fichier de configuration pour personnaliser les options

### Commandes potentielles

```bash
# Futures options envisageables
./start-all.sh --port 8502          # Port custom
./start-all.sh --log-file app.log   # Logs dans un fichier
./start-all.sh --daemon             # Mode détaché
./start-all.sh --status             # Vérifier l'état
./start-all.sh --stop               # Arrêter les services
```

## Voir aussi

- **[README-ROON-TRACKER.md](README-ROON-TRACKER.md)** : Configuration du tracker Roon
- **[README-MUSIQUE-GUI.md](README-MUSIQUE-GUI.md)** : Utilisation de l'interface Streamlit
- **[README.md](../README.md)** : Documentation principale du projet

---

**Auteur** : Patrick Ostertag  
**Date** : 26 janvier 2026  
**Version** : 1.0.0
