# Architecture du Projet

## Vue d'ensemble

Ce projet implémente un système de recommandation de films basé sur la recherche sémantique utilisant PostgreSQL avec l'extension pgvector.

## Composants principaux

### 1. Base de données PostgreSQL

#### Extension pgvector
- Permet le stockage et la recherche de vecteurs
- Supporte les distances cosinus, L2, et produit interne
- Index HNSW pour recherches rapides

#### Tables

**films**
- Stocke les métadonnées des films
- Colonnes indexées (genres, cast, meta) pour filtrage rapide

**film_embeddings**
- Stocke les embeddings vectoriels (768 dimensions)
- Référence vers films via clé étrangère
- Index HNSW sur embedding

### 2. Génération d'embeddings

#### Modèle
- **Par défaut** : `sentence-transformers/all-mpnet-base-v2`
- **Dimension** : 768
- **Normalisation** : Oui (pour distance cosinus)

#### Pipeline
1. Concaténation des champs : `title + synopsis + genres + cast`
2. Encodage via SentenceTransformer
3. Normalisation des vecteurs
4. Stockage dans PostgreSQL

### 3. Index HNSW

#### Configuration
- Type : HNSW (Hierarchical Navigable Small World)
- Distance : Cosinus (vector_cosine_ops)
- Optimisé pour : Recherches de similarité rapides

#### Création
L'index est créé **après** l'insertion de tous les embeddings pour optimiser les performances.

### 4. API FastAPI

#### Endpoints

**GET /recommend/by-film/{film_id}**
- Recommandations basées sur un film
- Utilise la similarité cosinus sur embeddings
- Supporte le filtrage (genres, années)

**GET /search?q={query}**
- Recherche sémantique textuelle
- Convertit la requête en embedding
- Compare avec les embeddings des films

**GET /films/{film_id}**
- Détails d'un film

**GET /stats**
- Statistiques de la base

#### Structure
- Modèles Pydantic pour validation
- Gestion d'erreurs HTTP
- Documentation Swagger automatique

### 5. Évaluation

#### Métriques implémentées
- **Precision@K** : Précision dans les K premiers
- **Recall@K** : Rappel sur les K premiers
- **nDCG@K** : Gain cumulatif normalisé
- **MAP** : Mean Average Precision

#### Workflow
1. Chargement du ground truth (JSON)
2. Récupération des recommandations depuis la base
3. Calcul des métriques
4. Génération de rapports

## Flux de données

### Ingestion
```
CSV → Nettoyage → PostgreSQL (table films)
```

### Génération d'embeddings
```
Films (PostgreSQL) → SentenceTransformer → Embeddings → PostgreSQL (film_embeddings)
```

### Recherche
```
Requête utilisateur → Embedding → Comparaison (pgvector) → Résultats
```

### Recommandation
```
Film ID → Embedding → Comparaison (pgvector) → Films similaires
```

## Performance

### Optimisations

1. **Index HNSW**
   - Recherches O(log n) au lieu de O(n)
   - Paramètres ajustables selon le corpus

2. **Batch processing**
   - Génération d'embeddings par lots
   - Insertions groupées

3. **Filtrage précoce**
   - Filtres WHERE avant calcul de similarité
   - Réduction du domaine de recherche

4. **Normalisation**
   - Embeddings normalisés pour distance cosinus optimale
   - Comparaisons plus rapides

### Scalabilité

- **Petit corpus** (< 10K films) : HNSW par défaut suffit
- **Moyen corpus** (10K-100K) : Ajuster les paramètres HNSW
- **Grand corpus** (> 100K) : Considérer sharding ou clusters

## Sécurité

### Bonnes pratiques

1. **Variables d'environnement**
   - Credentials dans `.env` (non versionné)
   - Pas de mots de passe en dur

2. **Connexions**
   - Pool de connexions pour l'API
   - Fermeture propre des connexions

3. **Validation**
   - Validation Pydantic des entrées
   - Protection contre injection SQL (psycopg2)

## Extension future

### Améliorations possibles

1. **Cache**
   - Cache Redis pour requêtes fréquentes
   - Cache des embeddings de requêtes

2. **Modèles**
   - Support multilingue
   - Modèles spécialisés par domaine

3. **Hybrid search**
   - Combinaison recherche vectorielle + textuelle
   - Filtrage avancé avec facettes

4. **ML Pipeline**
   - Fine-tuning des embeddings
   - Réentraînement périodique

