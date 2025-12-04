# Installation de pgvector sur Windows

## Méthode 1 : Installation via pgAdmin ou psql (Recommandé)

### Pour PostgreSQL 18

1. Téléchargez pgvector depuis : https://github.com/pgvector/pgvector/releases
2. Téléchargez la version correspondant à PostgreSQL 18 (fichier `.zip`)
3. Extrayez le fichier `vector.dll` dans le dossier `lib` de PostgreSQL :
   - `C:\Program Files\PostgreSQL\18\lib\`
4. Extrayez le fichier `vector.control` et le dossier `vector` dans :
   - `C:\Program Files\PostgreSQL\18\share\extension\`

### Pour PostgreSQL 17

Même procédure mais avec le chemin :
- `C:\Program Files\PostgreSQL\17\lib\`
- `C:\Program Files\PostgreSQL\17\share\extension\`

## Méthode 2 : Installation via SQL (si les fichiers sont déjà présents)

Si les fichiers sont déjà dans les bons dossiers, activez simplement l'extension :

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Vérification

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

Si vous voyez une ligne, l'extension est activée !

