# Guide de Démarrage Rapide

Ce guide vous permet de démarrer rapidement avec le projet de recommandation de films.

## Prérequis rapides

1. PostgreSQL 14+ installé
2. Python 3.9+ installé
3. Extension pgvector installée

## Installation en 5 minutes

### 1. Configuration de l'environnement

```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration de la base de données

Créez un fichier `.env` à la racine du projet :

```env
DB_NAME=filmsrec
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

### 3. Initialisation de la base de données

```bash
# Créer la base de données PostgreSQL
sudo -u postgres psql
CREATE DATABASE filmsrec;
\c filmsrec
CREATE EXTENSION IF NOT EXISTS vector;
\q

# Ou utilisez le script automatique
python scripts/setup_database.py
```

### 4. Utiliser les données d'exemple

```bash
# Créer des films d'exemple
python scripts/create_sample_data.py

# Générer les embeddings
python scripts/generate_embeddings.py

# Créer l'index HNSW
psql -U postgres -d filmsrec -f sql/index_hnsw.sql
```

### 5. Lancer l'API

```bash
uvicorn api.main:app --reload
```

Ouvrez votre navigateur sur : `http://localhost:8000/docs`

## Test rapide

### Test avec curl

```bash
# Rechercher des films
curl "http://localhost:8000/search?q=sci-fi space&k=5"

# Obtenir des recommandations pour un film
curl "http://localhost:8000/recommend/by-film/1?k=5"

# Voir les statistiques
curl "http://localhost:8000/stats"
```

### Test avec l'interface Swagger

1. Ouvrez `http://localhost:8000/docs`
2. Testez les endpoints interactivement

## Avec vos propres données

### Format CSV requis

Créez un fichier CSV avec ces colonnes :

```csv
title,year,genres,cast,synopsis
Mon Film,2020,"Drama,Action","Acteur 1|Acteur 2","Description du film..."
```

### Pipeline complet

```bash
# 1. Ingérer vos données
python scripts/ingest_films.py data/mes_films.csv

# 2. Générer les embeddings
python scripts/generate_embeddings.py

# 3. Créer l'index (IMPORTANT: après les embeddings!)
psql -U postgres -d filmsrec -f sql/index_hnsw.sql

# 4. Lancer l'API
uvicorn api.main:app --reload
```

### Pipeline en une commande

```bash
python scripts/run_all.py --csv data/mes_films.csv
```

## Problèmes courants

### "extension vector does not exist"

```sql
-- Dans psql
CREATE EXTENSION IF NOT EXISTS vector;
```

### "No module named 'sentence_transformers'"

```bash
pip install -r requirements.txt
```

### "Connection refused"

Vérifiez que PostgreSQL est démarré :

```bash
# Linux
sudo systemctl status postgresql

# macOS
brew services list
```

Vérifiez aussi votre fichier `.env`.

## Prochaines étapes

1. Consultez le [README.md](README.md) pour la documentation complète
2. Explorez l'API sur `/docs`
3. Personnalisez les modèles d'embeddings dans `.env`
4. Ajoutez vos propres données

Bon développement ! 🚀

