# Guide d'installation de pgvector pour PostgreSQL 18 sur Windows

## Étape 1 : Télécharger pgvector

1. Allez sur : https://github.com/pgvector/pgvector/releases
2. Téléchargez la dernière version (ex: `pgvector-v0.5.1.zip`)
3. Ou directement : https://github.com/pgvector/pgvector/releases/latest

## Étape 2 : Extraire les fichiers

1. Extrayez le fichier ZIP
2. Vous devez trouver :
   - `vector.dll` (dans le dossier `lib` ou à la racine)
   - `vector.control` (dans le dossier `share/extension` ou à la racine)
   - Un dossier `vector/` avec des fichiers SQL

## Étape 3 : Copier les fichiers

### Pour PostgreSQL 18 :

Copiez les fichiers vers :
- `vector.dll` → `C:\Program Files\PostgreSQL\18\lib\vector.dll`
- `vector.control` → `C:\Program Files\PostgreSQL\18\share\extension\vector.control`
- Dossier `vector/` → `C:\Program Files\PostgreSQL\18\share\extension\vector\`

**Note** : Vous aurez besoin des droits administrateur.

## Étape 4 : Redémarrer PostgreSQL

```powershell
# Arrêter PostgreSQL
Stop-Service postgresql-x64-18

# Démarrer PostgreSQL
Start-Service postgresql-x64-18
```

## Étape 5 : Activer l'extension

```powershell
$env:PGPASSWORD = "root"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Alternative : Installation via Stack Builder

1. Ouvrez **PostgreSQL Stack Builder** (depuis le menu Démarrer)
2. Sélectionnez votre installation PostgreSQL 18
3. Dans les extensions, cherchez **pgvector**
4. Installez-le

## Vérification

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

Si vous voyez une ligne, c'est bon !

