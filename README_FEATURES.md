# Nouvelles Fonctionnalités - Recommandation de Films

## 🎉 Fonctionnalités Ajoutées

### 1. Système d'Authentification
- **Page de connexion/inscription** (`/static/login.html`)
- Inscription avec choix de genre (homme/femme/autre)
- Avatar automatique basé sur le genre choisi
- Gestion des sessions utilisateur
- Protection des routes par authentification

### 2. Affichage des Images de Films
- Intégration avec l'API TMDB pour récupérer les affiches
- Affichage des posters de films dans les résultats
- Fallback vers placeholder si l'image n'est pas disponible
- Cache des métadonnées en base de données

### 3. Bandes Annonces (Trailers)
- Récupération des bandes annonces depuis TMDB/YouTube
- Affichage du lien vers la bande annonce
- Intégration d'un lecteur YouTube dans les détails du film

### 4. Liens vers les Plateformes de Streaming
- Affichage des plateformes disponibles (Netflix, Disney+, Amazon Prime, etc.)
- Logos des plateformes
- Informations de disponibilité

### 5. Historique des Recherches
- Enregistrement automatique de toutes les recherches
- Affichage de l'historique dans une section dédiée
- Possibilité de relancer une recherche depuis l'historique
- Filtres sauvegardés avec chaque recherche

### 6. Tableau de Bord Administrateur
- **KPI (Indicateurs clés)** :
  - Nombre total d'utilisateurs
  - Nombre d'administrateurs
  - Sessions actives
  - Recherches totales
  - Films visionnés
  - Utilisateurs actifs aujourd'hui
  - Recherches aujourd'hui

- **Graphiques** :
  - Courbe des nouveaux utilisateurs (7 derniers jours)
  - Graphique en barres des recherches (7 derniers jours)
  - Top genres recherchés

- **Gestion des utilisateurs** :
  - Liste de tous les utilisateurs
  - Bloquer/Débloquer des utilisateurs
  - Supprimer des utilisateurs
  - Voir les détails (email, rôle, statut)

- **Gestion des sessions** :
  - Vue sur toutes les sessions actives
  - Informations (IP, user-agent, dates)

- **Historique global** :
  - Toutes les recherches effectuées
  - Filtres par utilisateur

## 📋 Installation et Configuration

### 1. Créer les tables de la base de données

```bash
psql -U postgres -d filmsrec -f sql/users_schema.sql
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Configurer l'API TMDB (optionnel)

Ajoutez votre clé API TMDB dans le fichier `.env` :

```env
TMDB_API_KEY=votre_cle_api_tmdb
```

Pour obtenir une clé API TMDB :
1. Créez un compte sur [TMDB](https://www.themoviedb.org/)
2. Allez dans Paramètres > API
3. Créez une nouvelle clé API

**Note** : L'application fonctionne sans clé TMDB, mais utilisera des placeholders pour les images.

### 4. Créer un utilisateur administrateur

```bash
python scripts/create_admin_user.py
```

Suivez les instructions pour créer votre compte admin.

### 5. Démarrer l'API

```bash
uvicorn api.main:app --reload
```

## 🎯 Utilisation

### Pour les utilisateurs classiques

1. Accédez à `http://localhost:8000/login`
2. Créez un compte ou connectez-vous
3. Recherchez des films en langage naturel
4. Consultez votre historique de recherches
5. Cliquez sur un film pour voir :
   - Les détails complets
   - L'affiche du film
   - La bande annonce (si disponible)
   - Les plateformes de streaming

### Pour les administrateurs

1. Connectez-vous avec un compte admin
2. Cliquez sur le bouton "⚙️ Admin" dans le header
3. Accédez au tableau de bord avec :
   - Tous les KPI
   - Graphiques et statistiques
   - Gestion des utilisateurs
   - Vue sur les sessions
   - Historique global

## 🔐 Rôles Utilisateurs

- **User (classique)** : Peut rechercher des films, voir son historique
- **Admin** : Accès complet au tableau de bord et gestion des utilisateurs

## 📁 Nouveaux Fichiers

### Backend
- `api/auth.py` - Module d'authentification
- `api/tmdb_service.py` - Service d'intégration TMDB
- `sql/users_schema.sql` - Schéma de base de données pour les utilisateurs
- `scripts/create_admin_user.py` - Script pour créer un admin

### Frontend
- `static/login.html` - Page de connexion/inscription
- `static/login.css` - Styles de la page de connexion
- `static/login.js` - Logique de connexion/inscription
- `static/admin.html` - Tableau de bord admin
- `static/admin.css` - Styles du tableau de bord
- `static/admin.js` - Logique du tableau de bord

## 🔧 Endpoints API Ajoutés

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/me` - Informations utilisateur actuel

### Utilisateur
- `GET /api/search-history` - Historique des recherches
- `POST /api/films/{film_id}/watch` - Marquer un film comme visionné
- `GET /api/watched-films` - Films visionnés

### Films
- `GET /api/film/{film_id}/metadata` - Métadonnées complètes (affiche, trailer, streaming)

### Admin
- `GET /api/admin/dashboard` - Tableau de bord avec KPI
- `GET /api/admin/users` - Liste des utilisateurs
- `GET /api/admin/sessions` - Liste des sessions
- `GET /api/admin/search-history` - Historique global
- `POST /api/admin/users/{user_id}/block` - Bloquer un utilisateur
- `POST /api/admin/users/{user_id}/unblock` - Débloquer un utilisateur
- `DELETE /api/admin/users/{user_id}` - Supprimer un utilisateur

## 🎨 Améliorations Visuelles

- Header avec informations utilisateur et avatar
- Modal amélioré pour les détails de films avec affiche, trailer et streaming
- Section historique avec design moderne
- Tableau de bord admin avec graphiques Chart.js
- Interface responsive et moderne

## 📝 Notes

- Les avatars sont générés automatiquement via DiceBear API
- Les métadonnées des films sont mises en cache en base de données
- L'historique est sauvegardé automatiquement lors de chaque recherche
- Les sessions expirent après 30 jours

