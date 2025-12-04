# Guide de Dépannage

Ce guide vous aide à résoudre les erreurs courantes lors de l'utilisation du projet.

## Erreurs SQL

### Erreur : "parameter mismatch" ou "not enough parameters"

**Cause** : L'ordre des paramètres dans la requête SQL ne correspond pas à l'ordre dans le tableau de paramètres.

**Solution** : ✅ **CORRIGÉ** dans `api/main.py`. Les paramètres sont maintenant construits dans le bon ordre.

Si vous voyez encore cette erreur, vérifiez que vous avez la dernière version du fichier.

## Erreurs PowerShell

### Erreur : "Le jeton « && » n'est pas un séparateur d'instruction valide"

**Cause** : PowerShell n'accepte pas `&&` comme séparateur de commandes (c'est une syntaxe bash).

**Solution** : Utilisez `;` ou séparez les commandes :

```powershell
# ❌ Incorrect
cd dossier && python script.py

# ✅ Correct - Option 1
cd dossier; python script.py

# ✅ Correct - Option 2 (sur plusieurs lignes)
cd dossier
python script.py

# ✅ Correct - Option 3 (utiliser le script .bat)
.\start_api.bat
```

## Erreurs d'import Python

### Erreur : "No module named 'sentence_transformers'"

**Cause** : Les dépendances ne sont pas installées ou l'environnement virtuel n'est pas activé.

**Solution** :

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Erreur : "No module named 'config'"

**Cause** : Le répertoire parent n'est pas dans le PYTHONPATH.

**Solution** : Assurez-vous d'exécuter les scripts depuis la racine du projet :

```bash
# Depuis la racine du projet
python scripts/ingest_films.py data/films.csv
```

## Erreurs de connexion à la base de données

### Erreur : "could not connect to server"

**Cause** : PostgreSQL n'est pas démarré ou les paramètres de connexion sont incorrects.

**Solution** :

1. **Vérifier que PostgreSQL est démarré** :
   ```powershell
   # Windows
   Get-Service postgresql*
   
   # Démarrer si nécessaire
   Start-Service postgresql-x64-14
   ```

2. **Vérifier le fichier `.env`** :
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=filmsrec
   DB_USER=postgres
   DB_PASSWORD=votre_mot_de_passe
   ```

3. **Tester la connexion** :
   ```bash
   python scripts/setup_database.py
   ```

### Erreur : "database does not exist"

**Cause** : La base de données `filmsrec` n'a pas été créée.

**Solution** :

```sql
-- Dans psql
CREATE DATABASE filmsrec;
\c filmsrec
CREATE EXTENSION IF NOT EXISTS vector;
```

Ou utilisez le script :
```bash
python scripts/setup_database.py
```

### Erreur : "extension vector does not exist"

**Cause** : L'extension pgvector n'est pas installée ou activée.

**Solution** :

1. **Installer pgvector** :
   - Windows : Suivez les instructions sur https://github.com/pgvector/pgvector
   - Linux : `sudo apt install postgresql-14-pgvector`
   - Mac : `brew install pgvector`

2. **Activer l'extension** :
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## Erreurs de l'API

### Erreur : "Port 8000 already in use"

**Cause** : Un autre processus utilise déjà le port 8000.

**Solution** :

1. **Changer le port** dans `.env` :
   ```env
   API_PORT=8001
   ```

2. **Ou arrêter le processus** :
   ```powershell
   # Windows - Trouver le processus
   netstat -ano | findstr :8000
   
   # Arrêter le processus (remplacer PID par le numéro trouvé)
   taskkill /PID <PID> /F
   ```

### Erreur : "Table 'films' does not exist"

**Cause** : Le schéma de base de données n'a pas été créé.

**Solution** :

```bash
# Option 1 : Utiliser le script
python scripts/setup_database.py

# Option 2 : Exécuter manuellement
psql -U postgres -d filmsrec -f sql/schema.sql
```

### Erreur : "Index 'film_embeddings_hnsw_cosine' does not exist"

**Cause** : L'index HNSW n'a pas été créé.

**Solution** :

```bash
# Créer l'index (après avoir généré les embeddings!)
psql -U postgres -d filmsrec -f sql/index_hnsw.sql
```

**Important** : Créez l'index APRÈS avoir généré tous les embeddings pour optimiser les performances.

## Erreurs lors de la génération d'embeddings

### Erreur : "CUDA out of memory"

**Cause** : Le modèle essaie d'utiliser le GPU mais il n'y a pas assez de mémoire.

**Solution** :

1. **Forcer l'utilisation du CPU** :
   ```python
   # Dans scripts/generate_embeddings.py
   model = SentenceTransformer(model_name, device='cpu')
   ```

2. **Réduire la taille des lots** :
   ```bash
   python scripts/generate_embeddings.py --batch-size 16
   ```

### Erreur : "dimension mismatch"

**Cause** : La dimension des embeddings ne correspond pas à celle définie dans le schéma SQL.

**Solution** :

1. **Vérifier la dimension du modèle** :
   - `all-mpnet-base-v2` : 768 dimensions
   - `all-MiniLM-L6-v2` : 384 dimensions

2. **Adapter le schéma SQL** si nécessaire :
   ```sql
   -- Pour 384 dimensions
   ALTER TABLE film_embeddings ALTER COLUMN embedding TYPE vector(384);
   ```

## Erreurs lors des requêtes

### Erreur : "operator does not exist: vector <=> vector"

**Cause** : L'extension pgvector n'est pas correctement activée ou la syntaxe est incorrecte.

**Solution** :

1. **Vérifier que pgvector est activé** :
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

2. **Vérifier la syntaxe** : Utilisez bien `<=>` pour la distance cosinus.

## Vérification rapide

Utilisez le script de vérification pour diagnostiquer les problèmes :

```bash
python scripts/check_setup.py
```

Ce script vérifie :
- ✅ Fichiers présents
- ✅ Packages Python installés
- ✅ Configuration `.env`
- ✅ Connexion à la base de données
- ✅ Tables et index créés

## Obtenir de l'aide

Si vous rencontrez une erreur non listée ici :

1. Vérifiez les logs de l'API (dans le terminal)
2. Vérifiez les logs PostgreSQL
3. Utilisez `python scripts/check_setup.py` pour un diagnostic
4. Consultez la documentation dans `README.md`

## Commandes utiles

```bash
# Vérifier l'installation complète
python scripts/check_setup.py

# Configurer la base de données
python scripts/setup_database.py

# Créer des données d'exemple
python scripts/create_sample_data.py

# Générer les embeddings
python scripts/generate_embeddings.py

# Lancer l'API
uvicorn api.main:app --reload
```

