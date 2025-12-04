# Projet de Recommandation de Films avec pgvector

Système complet de recommandation de films utilisant la recherche sémantique avec PostgreSQL et l'extension pgvector. Ce projet implémente un cas d'usage professionnel de recommandation basé sur les embeddings de synopsis, genres, cast et métadonnées des films.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Organisation du travail](#organisation-du-travail)
- [API](#api)
- [Évaluation](#évaluation)
- [Documentation technique](#documentation-technique)

## ✨ Fonctionnalités

- **Ingestion de données** : Import de films depuis CSV avec nettoyage automatique
- **Génération d'embeddings** : Utilisation de modèles SentenceTransformer pour créer des représentations vectorielles
- **Index HNSW** : Index haute performance pour recherches de similarité rapides
- **Recommandations** : Suggestions de films similaires basées sur la similarité cosinus
- **Recherche sémantique** : Recherche textuelle convertie en embeddings pour trouver des films pertinents
- **API REST** : Interface FastAPI complète avec documentation Swagger
- **Évaluation** : Métriques de pertinence (Precision@K, Recall@K, nDCG, MAP)

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   CSV/Data  │ --> │  Ingestion   │ --> │  PostgreSQL │
└─────────────┘     └──────────────┘     └─────────────┘
                                              │
                    ┌──────────────┐         │
                    │  Embeddings  │ <-------┘
                    └──────────────┘
                          │
                    ┌──────────────┐
                    │  Index HNSW  │
                    └──────────────┘
                          │
                    ┌──────────────┐
                    │  FastAPI     │
                    └──────────────┘
                          │
                    ┌──────────────┐
                    │  Evaluation  │
                    └──────────────┘
```

## 📦 Prérequis

### Système

- **PostgreSQL** : Version 14+ (recommandée)
- **Python** : Version 3.9+
- **pgvector** : Extension PostgreSQL à installer

### Installation de PostgreSQL et pgvector

#### Ubuntu/Debian

```bash
# Installer PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Installer pgvector
sudo apt install postgresql-14-pgvector  # ou version correspondante
```

#### macOS

```bash
# Avec Homebrew
brew install postgresql
brew install pgvector
```

#### Windows

Téléchargez PostgreSQL depuis [postgresql.org](https://www.postgresql.org/download/windows/) et suivez les instructions d'installation de pgvector.

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd Projet_pgvector-recommendations-films
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données
CREATE DATABASE filmsrec;

# Se connecter à la base
\c filmsrec

# Activer l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;
```

Ou utiliser les scripts SQL fournis :

```bash
psql -U postgres -f sql/schema.sql
```

### 5. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```bash
cp .env.example .env
```

Modifiez `.env` avec vos paramètres :

```env
DB_NAME=filmsrec
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

API_HOST=0.0.0.0
API_PORT=8000

EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
EMBEDDING_DIMENSION=768
```

## ⚙️ Configuration

### Modèle d'embeddings

Le projet utilise par défaut `sentence-transformers/all-mpnet-base-v2` (768 dimensions). Vous pouvez modifier le modèle dans `.env` :

- `all-mpnet-base-v2` : Meilleure qualité (768 dim)
- `all-MiniLM-L6-v2` : Plus rapide (384 dim) - nécessite de modifier la dimension dans le schéma SQL
- `paraphrase-multilingual-mpnet-base-v2` : Support multilingue

## 📖 Utilisation

### 1. Ingestion des données

Le projet inclut un fichier `data/films.csv` avec une collection de films. Vous pouvez également utiliser votre propre fichier CSV.

Format CSV attendu (colonnes) :

- `title` (obligatoire) : Titre du film
- `year` : Année de sortie (int ou float, ex: 2009 ou 2009.0)
- `genres` : Genres au format liste Python `['Action', 'Adventure']` ou séparés par `|`, `,` ou `;`
- `cast` : Acteurs au format liste Python `['Actor1', 'Actor2']` ou séparés par `|`, `,` ou `;`
- `synopsis` : Description du film
- `meta` : JSON optionnel avec métadonnées

Exemples de formats supportés :

```csv
title,year,genres,cast,synopsis
The Matrix,1999,"Sci-Fi,Action","Keanu Reeves|Laurence Fishburne","A computer hacker learns..."
Avatar,2009.0,"['Action', 'Adventure', 'Fantasy']",,"Un marine paraplégique..."
```

Pour ingérer le fichier `films.csv` inclus :

```bash
python scripts/ingest_films.py data/films.csv
```

Ou avec votre propre fichier :

```bash
python scripts/ingest_films.py data/vos_films.csv
```

### 2. Génération des embeddings

Générez les embeddings pour tous les films :

```bash
python scripts/generate_embeddings.py
```

Options disponibles :
- `--model` : Modèle SentenceTransformer à utiliser
- `--batch-size` : Taille des lots (défaut: 32)
- `--no-normalize` : Désactiver la normalisation

### 3. Création de l'index HNSW

**Important** : Créez l'index **après** avoir inséré tous les embeddings.

```bash
psql -U postgres -d filmsrec -f sql/index_hnsw.sql
```

Ou manuellement :

```sql
CREATE INDEX film_embeddings_hnsw_cosine
ON film_embeddings USING hnsw (embedding vector_cosine_ops);

VACUUM ANALYZE film_embeddings;
```

### 4. Lancer l'API

```bash
uvicorn api.main:app --reload
```

L'API sera accessible sur `http://localhost:8000`

Documentation interactive :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

### 5. Évaluation (optionnel)

Préparez un fichier JSON de ground truth :

```json
{
  "1": [2, 5, 10],
  "3": [4, 7, 12]
}
```

Où les clés sont les IDs de films de requête et les valeurs sont les IDs de films pertinents.

Puis évaluez :

```bash
python evaluation/evaluate_recommendations.py data/ground_truth.json --output results/evaluation.json
```

## 📁 Structure du projet

```
Projet_pgvector-recommendations-films/
│
├── api/                      # API FastAPI
│   ├── __init__.py
│   └── main.py              # Endpoints de l'API
│
├── config/                   # Configuration
│   ├── __init__.py
│   └── database.py          # Connexion à la base de données
│
├── data/                     # Données
│   ├── sample_films.csv     # Exemple de CSV
│   └── ...                  # Vos fichiers de données
│
├── evaluation/               # Évaluation
│   ├── __init__.py
│   ├── metrics.py           # Métriques (Precision, Recall, nDCG, MAP)
│   └── evaluate_recommendations.py
│
├── scripts/                  # Scripts utilitaires
│   ├── __init__.py
│   ├── ingest_films.py      # Ingestion depuis CSV
│   └── generate_embeddings.py
│
├── sql/                      # Scripts SQL
│   ├── schema.sql           # Schéma de base de données
│   └── index_hnsw.sql       # Index HNSW
│
├── .env.example              # Exemple de configuration
├── .gitignore
├── requirements.txt          # Dépendances Python
└── README.md                # Ce fichier
```

## 👥 Organisation du travail

Ce projet est conçu pour être réalisé en équipe de 4 personnes :

### **Rôle 1 : Données et ingestion**
- Responsable de la collecte et nettoyage des données
- Import dans la table `films`
- **Livrables** :
  - Scripts d'ingestion fonctionnels
  - Documentation des champs
  - Échantillons de données validés

### **Rôle 2 : Embeddings et indexation**
- Choix et optimisation du modèle d'embeddings
- Génération des embeddings
- Création et tuning de l'index HNSW
- **Livrables** :
  - Script de génération d'embeddings
  - Pipeline reproductible
  - Rapport de performances

### **Rôle 3 : API et intégration**
- Développement des endpoints FastAPI
- Connexion à la base de données
- Requêtes de recommandation et recherche
- **Livrables** :
  - API fonctionnelle avec documentation
  - Tests unitaires
  - Guide de déploiement

### **Rôle 4 : Évaluation et rapport**
- Protocole d'évaluation de pertinence
- Calcul des métriques
- A/B testing de variantes
- **Livrables** :
  - Notebook d'évaluation
  - Graphiques et visualisations
  - Recommandations d'amélioration

## 🔌 API

### Endpoints principaux

#### 1. Recommandations par film

```http
GET /recommend/by-film/{film_id}?k=10
```

Retourne les `k` films les plus similaires à un film donné.

Paramètres :
- `film_id` (path) : ID du film de référence
- `k` (query, optionnel) : Nombre de recommandations (défaut: 10, max: 100)
- `exclude_genres` (query, optionnel) : Genres à exclure (séparés par virgules)
- `min_year` (query, optionnel) : Année minimum
- `max_year` (query, optionnel) : Année maximum

Exemple :

```bash
curl "http://localhost:8000/recommend/by-film/1?k=5"
```

#### 2. Recherche sémantique

```http
GET /search?q={query}&k=10
```

Recherche sémantique de films à partir d'une requête textuelle.

Paramètres :
- `q` (query) : Requête textuelle
- `k` (query, optionnel) : Nombre de résultats (défaut: 10)
- `genres` (query, optionnel) : Genres requis (séparés par virgules)
- `min_year` (query, optionnel) : Année minimum
- `max_year` (query, optionnel) : Année maximum

Exemple :

```bash
curl "http://localhost:8000/search?q=sci-fi space adventure&k=10"
```

#### 3. Détails d'un film

```http
GET /films/{film_id}
```

Retourne les détails complets d'un film.

#### 4. Statistiques

```http
GET /stats
```

Retourne des statistiques sur la base de données (nombre de films, embeddings, etc.).

## 📊 Évaluation

### Métriques implémentées

- **Precision@K** : Proportion de résultats pertinents dans les K premiers
- **Recall@K** : Proportion de résultats pertinents trouvés sur le total
- **nDCG@K** : Gain cumulatif normalisé (prend en compte le rang)
- **MAP** : Mean Average Precision

### Utilisation

Voir la section [Évaluation](#5-évaluation-optionnel) dans Utilisation.

## 📚 Documentation technique

### Schéma de base de données

#### Table `films`

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Identifiant unique |
| title | TEXT | Titre du film |
| year | INT | Année de sortie |
| genres | TEXT[] | Liste de genres |
| cast | TEXT[] | Liste d'acteurs |
| synopsis | TEXT | Description |
| meta | JSONB | Métadonnées additionnelles |
| created_at | TIMESTAMP | Date de création |
| updated_at | TIMESTAMP | Date de mise à jour |

#### Table `film_embeddings`

| Colonne | Type | Description |
|---------|------|-------------|
| film_id | INT | Référence vers films.id |
| embedding | vector(768) | Embedding vectoriel |
| created_at | TIMESTAMP | Date de création |

### Index

- **HNSW** : Index pour recherches de similarité rapides sur `embedding`
- **GIN** : Index sur `genres`, `cast`, `meta` pour recherches textuelles
- **B-tree** : Index sur `year` et `title`

### Requêtes SQL importantes

#### Recommandation par similarité

```sql
WITH q AS (
  SELECT embedding FROM film_embeddings WHERE film_id = $1
)
SELECT f.id, f.title, f.year, f.genres
FROM film_embeddings fe
JOIN films f ON f.id = fe.film_id
JOIN q ON TRUE
WHERE f.id <> $1
ORDER BY fe.embedding <=> (SELECT embedding FROM q)
LIMIT 10;
```

## 🔧 Dépannage

### Erreur : "extension vector does not exist"

Assurez-vous que pgvector est installé et que l'extension est activée :

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Erreur : "dimension mismatch"

Vérifiez que la dimension dans `schema.sql` correspond à celle du modèle choisi (768 pour `all-mpnet-base-v2`).

### Performances lentes

1. Vérifiez que l'index HNSW est créé
2. Exécutez `VACUUM ANALYZE film_embeddings;`
3. Augmentez les ressources de PostgreSQL si nécessaire

## 📝 Licence

Ce projet est fourni à des fins éducatives.

## 👤 Auteurs

Projet réalisé en équipe de 4 étudiants.

## 🙏 Remerciements

- [pgvector](https://github.com/pgvector/pgvector) pour l'extension PostgreSQL
- [Sentence Transformers](https://www.sbert.net/) pour les modèles d'embeddings
- [FastAPI](https://fastapi.tiangolo.com/) pour le framework API

