# 🚀 Guide de Démarrage Rapide

## Installation en 3 étapes

### 1. Créer et activer l'environnement virtuel

```powershell
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1
```

**Note** : Si vous avez une erreur de politique d'exécution PowerShell, exécutez :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Installer les dépendances

```powershell
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer toutes les dépendances
pip install -r requirements.txt
```

**Ou utilisez le script automatique :**
```powershell
.\install_dependencies.ps1
```

### 3. Lancer l'API

```powershell
# Vérifier que l'environnement virtuel est activé (vous devriez voir "(venv)" avant le prompt)
# Puis lancer l'API
uvicorn api.main:app --reload
```

L'API sera accessible sur : `http://localhost:8000`

Documentation interactive : `http://localhost:8000/docs`

## ⚠️ Erreurs Courantes

### Erreur : "ModuleNotFoundError: No module named 'fastapi'"

**Solution** : Les dépendances ne sont pas installées dans l'environnement virtuel.

1. Vérifiez que l'environnement virtuel est activé (vous devriez voir `(venv)` dans votre prompt)
2. Installez les dépendances : `pip install -r requirements.txt`

### Erreur : "cannot activate script"

**Solution** : Politique d'exécution PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Puis réessayez d'activer l'environnement virtuel.

### Erreur : "Port 8000 already in use"

**Solution** : Changez le port dans `.env` :
```env
API_PORT=8001
```

## 📝 Checklist de Démarrage

- [ ] Environnement virtuel créé (`venv`)
- [ ] Environnement virtuel activé (voir `(venv)` dans le prompt)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` créé avec les bonnes configurations
- [ ] Base de données PostgreSQL configurée
- [ ] Extension pgvector activée
- [ ] Tables créées (`python scripts/setup_database.py`)
- [ ] Films ingérés (optionnel, pour tester)
- [ ] Embeddings générés (optionnel, pour tester)
- [ ] API lancée (`uvicorn api.main:app --reload`)

## 🔧 Commandes Utiles

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Vérifier l'installation
python scripts/check_setup.py

# Créer la base de données
python scripts/setup_database.py

# Créer des données d'exemple
python scripts/create_sample_data.py

# Générer les embeddings
python scripts/generate_embeddings.py

# Lancer l'API
uvicorn api.main:app --reload
```

## ✅ Vérification Rapide

Testez que tout fonctionne :

```powershell
# 1. Vérifier les imports
python -c "from fastapi import FastAPI; print('✓ FastAPI OK')"
python -c "from sentence_transformers import SentenceTransformer; print('✓ SentenceTransformers OK')"

# 2. Lancer l'API
uvicorn api.main:app --reload

# 3. Ouvrir dans le navigateur
start http://localhost:8000/docs
```

## 🆘 Besoin d'aide ?

Consultez :
- `README.md` : Documentation complète
- `TROUBLESHOOTING.md` : Solutions aux problèmes courants
- `CONTRIBUTING.md` : Organisation du travail en équipe

