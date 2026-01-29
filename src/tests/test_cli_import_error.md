# Test: CLI Dependency Error Handling

## Purpose
Verify that the CLI provides a helpful error message when dependencies are missing.

## Test Setup

To test the error handling, you need to temporarily make the `click` or `rich` module unavailable.

## Manual Test Steps

### Option 1: Test in clean virtual environment

```bash
# Create a fresh virtual environment without dependencies
python3 -m venv /tmp/test_cli_env
source /tmp/test_cli_env/bin/activate

# Try to run the CLI without installing dependencies
cd /path/to/musique-collection-roon-tracker
python3 -m src.cli.main collection list
```

**Expected Output:**
```
❌ Erreur: Le module 'click' n'est pas installé.

📦 Pour installer les dépendances CLI, utilisez l'une de ces méthodes:

   Méthode 1 (Recommandée) - Utiliser le script de lancement:
   $ ./start-cli.sh

   Méthode 2 - Installer toutes les dépendances:
   $ pip install -r requirements.txt

   Méthode 3 - Installer uniquement les dépendances CLI:
   $ pip install rich click prompt-toolkit

📚 Voir la documentation: src/cli/README.md
```

### Option 2: Test with specific module temporarily hidden

```bash
# Create a script that temporarily hides the module
python3 << 'EOF'
import sys
import subprocess

# Remove site-packages from sys.path to hide installed modules
original_path = sys.path.copy()
sys.path = [p for p in sys.path if 'site-packages' not in p and 'dist-packages' not in p]

# Try to run the CLI module
result = subprocess.run(
    [sys.executable, '-m', 'src.cli.main', 'collection', 'list'],
    capture_output=True,
    text=True
)

print(result.stdout)
print(result.stderr)
print(f"Exit code: {result.returncode}")
EOF
```

### Option 3: Test with dependencies installed (verify it still works)

```bash
# With dependencies installed, the CLI should work normally
python3 -m src.cli.main collection list
```

**Expected Output:**
```
Collection list - Page 1, 25 par page
Implémentation à venir dans Phase 2...
```

## Automated Testing Note

This error handling is difficult to test with pytest because pytest itself requires the dependencies to be installed. The manual tests above are the recommended way to verify the error handling works correctly.

## Verification Checklist

- [ ] Error message is displayed when `click` is missing
- [ ] Error message is displayed when `rich` is missing
- [ ] Error message includes 3 installation methods
- [ ] Error message mentions the documentation
- [ ] CLI works normally when dependencies are installed
- [ ] Exit code is 1 when dependency is missing
