# Guide de Contribution et Organisation du Travail

Ce document décrit comment organiser le travail en équipe de 4 personnes pour ce projet.

## Rôles et Responsabilités

### 👤 Rôle 1 : Données et Ingestion

**Responsabilités :**
- Collecte et préparation des données de films
- Nettoyage et formatage des données
- Création et maintenance des scripts d'ingestion
- Documentation des sources de données

**Livrables attendus :**
- ✅ Scripts d'ingestion fonctionnels (`scripts/ingest_films.py`)
- ✅ Documentation des champs et formats de données
- ✅ Échantillons de données validés
- ✅ Guide de préparation des données CSV

**Fichiers principaux :**
- `scripts/ingest_films.py`
- `scripts/create_sample_data.py`
- `data/` (fichiers de données)
- Documentation des sources

**Checklist :**
- [ ] Identifier et collecter les sources de données
- [ ] Nettoyer et normaliser les données
- [ ] Tester le script d'ingestion avec un échantillon
- [ ] Ingérer l'ensemble complet des données
- [ ] Vérifier l'intégrité des données dans la base

---

### 🧠 Rôle 2 : Embeddings et Indexation

**Responsabilités :**
- Choix et configuration du modèle d'embeddings
- Génération des embeddings pour tous les films
- Création et optimisation de l'index HNSW
- Tuning des performances

**Livrables attendus :**
- ✅ Script de génération d'embeddings (`scripts/generate_embeddings.py`)
- ✅ Pipeline reproductible et documenté
- ✅ Rapport de performances (temps, mémoire)
- ✅ Documentation du choix de modèle

**Fichiers principaux :**
- `scripts/generate_embeddings.py`
- `sql/index_hnsw.sql`
- `config/database.py` (partie index)
- Documentation technique

**Checklist :**
- [ ] Tester différents modèles d'embeddings
- [ ] Choisir le modèle optimal
- [ ] Générer les embeddings pour tous les films
- [ ] Créer l'index HNSW
- [ ] Mesurer les performances (latence, précision)
- [ ] Optimiser les paramètres si nécessaire

---

### 🔌 Rôle 3 : API et Intégration

**Responsabilités :**
- Développement des endpoints FastAPI
- Connexion et requêtes à la base de données
- Gestion des erreurs et validation
- Tests et documentation de l'API

**Livrables attendus :**
- ✅ API fonctionnelle avec tous les endpoints
- ✅ Tests unitaires pour les endpoints
- ✅ Documentation Swagger complète
- ✅ Guide de déploiement

**Fichiers principaux :**
- `api/main.py`
- `config/database.py`
- Tests (à créer : `tests/`)
- Documentation API

**Checklist :**
- [ ] Implémenter tous les endpoints
- [ ] Ajouter la validation des entrées
- [ ] Gérer les erreurs correctement
- [ ] Tester tous les endpoints manuellement
- [ ] Écrire des tests unitaires
- [ ] Documenter l'utilisation de l'API

---

### 📊 Rôle 4 : Évaluation et Rapport

**Responsabilités :**
- Définition du protocole d'évaluation
- Création du ground truth (labels de pertinence)
- Calcul des métriques de performance
- A/B testing de variantes
- Présentation des résultats

**Livrables attendus :**
- ✅ Notebook d'évaluation avec visualisations
- ✅ Scripts de calcul de métriques
- ✅ Rapport d'évaluation complet
- ✅ Recommandations d'amélioration
- ✅ Présentation finale

**Fichiers principaux :**
- `evaluation/metrics.py`
- `evaluation/evaluate_recommendations.py`
- Notebook Jupyter d'évaluation
- Rapports et graphiques

**Checklist :**
- [ ] Créer le ground truth (labels manuels)
- [ ] Implémenter toutes les métriques
- [ ] Évaluer les recommandations
- [ ] Comparer différentes variantes (A/B testing)
- [ ] Générer des visualisations
- [ ] Rédiger le rapport d'évaluation
- [ ] Préparer la présentation

---

## Workflow de Collaboration

### 1. Gestion de Version (Git)

#### Branches par rôle
```bash
# Créer une branche pour chaque rôle
git checkout -b role1-data-ingestion
git checkout -b role2-embeddings-indexing
git checkout -b role3-api-integration
git checkout -b role4-evaluation-reporting
```

#### Workflow recommandé
1. Travailler sur votre branche de rôle
2. Faire des commits réguliers avec messages clairs
3. Pousser vers le dépôt distant
4. Créer des Pull Requests pour intégrer dans `main`
5. Code review croisée avant merge

#### Messages de commit
Format recommandé :
```
[Rôle] Description brève

Détails si nécessaire
```

Exemples :
```
[Rôle1] Ajout du script d'ingestion avec nettoyage des données
[Rôle2] Optimisation de l'index HNSW avec nouveaux paramètres
[Rôle3] Ajout de l'endpoint de recherche sémantique
[Rôle4] Calcul des métriques Precision@K et Recall@K
```

### 2. Environnement de Développement

#### Configuration partagée
- `requirements.txt` : Toutes les dépendances
- `.env.example` : Template de configuration
- `.gitignore` : Fichiers à ignorer

#### Variables d'environnement
Chaque développeur crée son propre `.env` :
```bash
cp .env.example .env
# Éditer .env avec ses propres credentials
```

### 3. Coordination et Communication

#### Réunions régulières
- **Kick-off** : Répartition des rôles et planning
- **Check-point hebdomadaire** : Progression de chaque rôle
- **Sprint final** : Intégration et tests

#### Points de synchronisation
1. **Après Rôle 1** : Données disponibles pour Rôle 2
2. **Après Rôle 2** : Embeddings prêts pour Rôle 3 et 4
3. **Pendant Rôle 3** : Tests avec Rôle 4 en parallèle
4. **Rôle 4** : Utilise l'API de Rôle 3 pour évaluation

### 4. Documentation

#### Standards
- Code commenté en français
- Docstrings pour toutes les fonctions
- README à jour
- Guides spécifiques par rôle

#### Structure de documentation
```
README.md              # Vue d'ensemble
QUICKSTART.md          # Démarrage rapide
CONTRIBUTING.md        # Ce fichier
docs/
  ├── ARCHITECTURE.md  # Architecture technique
  ├── API.md           # Documentation API (Rôle 3)
  ├── DATA.md          # Documentation données (Rôle 1)
  └── EVALUATION.md    # Protocole évaluation (Rôle 4)
```

## Checklist Générale du Projet

### Phase 1 : Setup (Semaine 1)
- [ ] Installation PostgreSQL et pgvector
- [ ] Configuration de l'environnement Python
- [ ] Création de la base de données
- [ ] Setup du dépôt Git

### Phase 2 : Ingestion (Semaine 1-2)
- [ ] Collecte des données (Rôle 1)
- [ ] Nettoyage et formatage (Rôle 1)
- [ ] Script d'ingestion fonctionnel (Rôle 1)
- [ ] Données ingérées dans PostgreSQL (Rôle 1)

### Phase 3 : Embeddings (Semaine 2-3)
- [ ] Choix du modèle (Rôle 2)
- [ ] Génération des embeddings (Rôle 2)
- [ ] Création de l'index HNSW (Rôle 2)
- [ ] Tests de performance (Rôle 2)

### Phase 4 : API (Semaine 3-4)
- [ ] Endpoints FastAPI (Rôle 3)
- [ ] Tests unitaires (Rôle 3)
- [ ] Documentation Swagger (Rôle 3)
- [ ] Déploiement de test (Rôle 3)

### Phase 5 : Évaluation (Semaine 4-5)
- [ ] Création du ground truth (Rôle 4)
- [ ] Calcul des métriques (Rôle 4)
- [ ] Visualisations (Rôle 4)
- [ ] Rapport final (Rôle 4)

### Phase 6 : Finalisation (Semaine 5)
- [ ] Intégration complète
- [ ] Tests finaux
- [ ] Documentation finale
- [ ] Présentation

## Conseils pour un Travail Efficace

### Partage de Code
- Faire des PRs régulières (pas tout à la fin)
- Demander des reviews tôt
- Communiquer les changements importants

### Tests
- Tester son code avant de partager
- Tester l'intégration avec les autres rôles
- Documenter les bugs trouvés

### Documentation
- Documenter au fur et à mesure
- Mettre à jour le README quand nécessaire
- Garder les commentaires de code à jour

### Gestion des Problèmes
- Communiquer les blocages rapidement
- Demander de l'aide si nécessaire
- Partager les solutions trouvées

## Ressources Utiles

### Documentation
- [pgvector](https://github.com/pgvector/pgvector)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Sentence Transformers](https://www.sbert.net/)

### Outils
- Git pour le versioning
- PostgreSQL pour la base de données
- Postman/curl pour tester l'API
- Jupyter pour l'évaluation

---

Bonne chance pour votre projet ! 🚀

