# Nouvelles Fonctionnalités - Guide d'Utilisation

## 🎉 Fonctionnalités Ajoutées

### 1. Système d'Authentification
- **Inscription** : Création de compte avec username, email, mot de passe et genre
- **Connexion** : Authentification par username/email et mot de passe
- **Sessions** : Gestion automatique des sessions avec cookies sécurisés
- **Avatars** : Génération automatique d'avatars basés sur le genre (homme/femme/autre)

### 2. Affichage des Images de Films
- **Affiches** : Intégration avec l'API TMDB pour récupérer les affiches réelles
- **Backdrops** : Images de fond pour les détails de films
- **Placeholders** : Images de secours si l'affiche n'est pas disponible

### 3. Bandes Annonces (Trailers)
- **Intégration YouTube** : Affichage des bandes annonces directement dans la modal
- **Embed automatique** : Récupération depuis TMDB et affichage intégré

### 4. Liens vers les Plateformes de Streaming
- **Logos des plateformes** : Affichage des logos (Netflix, Disney+, Amazon Prime, etc.)
- **Disponibilité** : Information sur les plateformes où le film est disponible
- **Intégration TMDB** : Données récupérées depuis l'API TMDB

### 5. Historique des Recherches
- **Stockage automatique** : Toutes les recherches sont enregistrées
- **Affichage** : Section dédiée pour consulter l'historique
- **Réutilisation** : Clic sur une recherche pour la relancer

### 6. Films Visionnés
- **Marquage** : Possibilité de marquer un film comme visionné
- **Notes** : Système de notation (1-5 étoiles)
- **Historique** : Liste des films visionnés par l'utilisateur

### 7. Tableau de Bord Admin
- **KPI** : Indicateurs clés de performance
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

- **Gestion des Utilisateurs** :
  - Liste de tous les utilisateurs
  - Blocage/Déblocage
  - Suppression de comptes
  - Vue des informations utilisateur

- **Gestion des Sessions** :
  - Liste de toutes les sessions actives
  - Informations IP et User-Agent
  - Dates de création et d'expiration

- **Historique Global** :
  - Toutes les recherches effectuées
  - Filtres appliqués
  - Nombre de résultats

## 📋 Installation et Configuration

### 1. Mise à jour de la Base de Données

Exécutez le script SQL pour créer les nouvelles tables :

```bash
psql -U postgres -d filmsrec -f sql/users_schema.sql
```

### 2. Configuration de l'API TMDB (Optionnel mais recommandé)

Pour récupérer les affiches, trailers et informations de streaming, vous devez obtenir une clé API TMDB :

1. Créez un compte sur [TMDB](https://www.themoviedb.org/)
2. Générez une clé API dans vos paramètres
3. Ajoutez-la dans votre fichier `.env` :

```env
TMDB_API_KEY=votre_cle_api_tmdb
```

**Note** : Sans clé TMDB, l'application fonctionnera toujours mais utilisera des images placeholder.

### 3. Création d'un Compte Admin

#### Méthode 1 : Via l'API (Recommandé)

1. Inscrivez-vous normalement via `/static/login.html`
2. Connectez-vous à PostgreSQL et exécutez :

```sql
UPDATE users SET role = 'admin' WHERE username = 'votre_username';
```

#### Méthode 2 : Via Python

```python
from api.auth import hash_password
from config.database import get_connection_dict

conn, cur = get_connection_dict()
password_hash = hash_password("votre_mot_de_passe")
cur.execute("""
    INSERT INTO users (username, email, password_hash, role, avatar_url)
    VALUES (%s, %s, %s, 'admin', %s)
""", ('admin', 'admin@example.com', password_hash, 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin'))
conn.commit()
```

### 4. Installation des Dépendances

```bash
pip install -r requirements.txt
```

Les nouvelles dépendances incluent :
- `requests` : Pour l'API TMDB
- `python-multipart` : Pour les formulaires

## 🚀 Utilisation

### Pour les Utilisateurs

1. **Accéder à l'application** : `http://localhost:8000`
2. **S'inscrire** : Cliquez sur "Créer un compte" sur la page de connexion
3. **Se connecter** : Utilisez vos identifiants
4. **Rechercher des films** : Utilisez la recherche sémantique
5. **Consulter l'historique** : Cliquez sur "📜 Historique" dans le header
6. **Voir les détails** : Cliquez sur une carte de film pour voir :
   - Affiche du film
   - Bande annonce (si disponible)
   - Plateformes de streaming (si disponibles)
   - Synopsis, genres, cast

### Pour les Administrateurs

1. **Accéder au tableau de bord** : `http://localhost:8000/admin` ou cliquez sur "⚙️ Admin" dans le header
2. **Consulter les KPI** : Vue d'ensemble en haut de la page
3. **Analyser les graphiques** : Tendances des utilisateurs et recherches
4. **Gérer les utilisateurs** : Onglet "👥 Utilisateurs"
   - Voir tous les utilisateurs
   - Bloquer/Débloquer
   - Supprimer des comptes
5. **Surveiller les sessions** : Onglet "🔐 Sessions"
6. **Consulter l'historique global** : Onglet "📜 Historique"

## 🔒 Sécurité

- **Hachage des mots de passe** : SHA-256 avec salt
- **Sessions sécurisées** : Cookies HttpOnly
- **Protection CSRF** : SameSite cookies
- **Validation des rôles** : Vérification admin pour les endpoints sensibles
- **Gestion des blocages** : Système de blocage/déblocage d'utilisateurs

## 📊 Structure de la Base de Données

### Nouvelles Tables

- **users** : Utilisateurs de l'application
- **user_sessions** : Sessions actives
- **search_history** : Historique des recherches
- **watched_films** : Films visionnés par les utilisateurs
- **film_metadata** : Métadonnées des films (affiches, trailers, streaming)

## 🐛 Dépannage

### Les images ne s'affichent pas

1. Vérifiez que vous avez configuré `TMDB_API_KEY` dans `.env`
2. Vérifiez votre connexion internet
3. Les images placeholder s'afficheront si TMDB n'est pas disponible

### Impossible de se connecter

1. Vérifiez que les tables `users` et `user_sessions` existent
2. Vérifiez que vous avez bien créé un compte
3. Vérifiez les logs de l'API pour les erreurs

### Le tableau de bord admin ne s'affiche pas

1. Vérifiez que votre compte a le rôle `admin`
2. Vérifiez que vous êtes bien connecté
3. Vérifiez la console du navigateur pour les erreurs

## 📝 Notes

- Les avatars sont générés automatiquement via [DiceBear](https://dicebear.com/)
- Les données TMDB sont mises en cache dans la table `film_metadata`
- Les sessions expirent après 30 jours
- Les recherches sont automatiquement enregistrées pour les utilisateurs connectés

