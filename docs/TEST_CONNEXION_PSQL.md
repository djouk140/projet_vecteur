# Guide : Tester la connexion PostgreSQL avec psql

## Sur Windows PowerShell

### Méthode 1 : Utiliser le chemin complet

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432
```

### Méthode 2 : Ajouter PostgreSQL au PATH (temporairement)

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\17\bin"
psql -U postgres -h localhost -p 5432
```

### Méthode 3 : Créer un alias (pour cette session)

```powershell
Set-Alias psql "C:\Program Files\PostgreSQL\17\bin\psql.exe"
psql -U postgres -h localhost -p 5432
```

## Explication des paramètres

- `-U postgres` : Utilisateur PostgreSQL (remplacez par votre utilisateur si différent)
- `-h localhost` : Hôte (localhost = votre machine)
- `-p 5432` : Port (5432 est le port par défaut de PostgreSQL)

## Ce qui va se passer

1. **Si le mot de passe est demandé** : Entrez le mot de passe de l'utilisateur `postgres`
2. **Si la connexion réussit** : Vous verrez un prompt `postgres=#` ou `postgres=>`
3. **Si la connexion échoue** : Vous verrez un message d'erreur

## Commandes utiles une fois connecté

```sql
-- Voir les bases de données
\l

-- Se connecter à une base de données
\c filmsrec

-- Voir les tables
\dt

-- Créer la base de données si elle n'existe pas
CREATE DATABASE filmsrec;

-- Activer l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Quitter
\q
```

## Tester avec un mot de passe en ligne de commande (non recommandé)

```powershell
$env:PGPASSWORD="votre_mot_de_passe"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432
```

## Vérifier quelle version de PostgreSQL utiliser

Vous avez PostgreSQL 17 et 18 installés. Vérifiez quel port utilise chaque version :

```powershell
# PostgreSQL 17 utilise généralement le port 5432
# PostgreSQL 18 utilise généralement le port 5433
```

Pour tester avec PostgreSQL 18 (si sur le port 5433) :
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5433
```

