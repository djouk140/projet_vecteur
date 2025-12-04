# 🔧 Correction : Accès à l'API

## Problème Résolu

L'erreur `ERR_ADDRESS_INVALID` sur `0.0.0.0:8000` a été corrigée.

## ✅ Solution Appliquée

Le serveur utilise maintenant `127.0.0.1` (ou `localhost`) par défaut au lieu de `0.0.0.0`, ce qui permet l'accès depuis votre navigateur.

## 🌐 Accès à l'API

Après avoir lancé l'API, utilisez ces adresses :

- **API principale** : `http://127.0.0.1:8000`
- **Documentation Swagger** : `http://127.0.0.1:8000/docs`
- **Alternative** : `http://localhost:8000`

## 🚀 Lancer l'API

### Méthode 1 : Script automatique (recommandé)

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Lancer l'API
.\start_api.bat
```

### Méthode 2 : Commande manuelle

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Lancer l'API
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Méthode 3 : Via Python directement

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Lancer l'API
python api/main.py
```

## 📝 Note importante

- **`127.0.0.1` ou `localhost`** : Accès uniquement depuis votre machine (recommandé pour le développement)
- **`0.0.0.0`** : Accès depuis toutes les interfaces réseau (utile pour tester depuis d'autres machines sur votre réseau)

Si vous voulez utiliser `0.0.0.0` (pour accès réseau), modifiez votre fichier `.env` :
```env
API_HOST=0.0.0.0
```

Puis accédez à l'API via : `http://localhost:8000` ou `http://127.0.0.1:8000` (pas `0.0.0.0:8000`)

## ✅ Vérification

Après le lancement, vous devriez voir :
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Puis ouvrez votre navigateur sur : `http://127.0.0.1:8000/docs`

