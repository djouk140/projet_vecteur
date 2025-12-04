# Installation simple de pgvector

## Instructions rapides

### Étape 1 : Lancer PowerShell en tant qu'administrateur

1. Appuyez sur `Win + X`
2. Sélectionnez **"Windows PowerShell (Admin)"** ou **"Terminal (Admin)"**
3. Naviguez vers le projet :
   ```powershell
   cd C:\projet_vecteur
   ```

### Étape 2 : Exécuter le script d'installation

```powershell
python scripts/download_install_pgvector.py
```

Le script va :
- Télécharger automatiquement pgvector depuis GitHub
- Installer les fichiers dans PostgreSQL 18
- Redémarrer PostgreSQL
- Activer l'extension

### Alternative : Installation manuelle

Si le script automatique ne fonctionne pas :

1. **Téléchargez pgvector** :
   - Allez sur : https://github.com/pgvector/pgvector/releases/latest
   - Téléchargez le fichier ZIP pour Windows

2. **Extrayez les fichiers** dans :
   - `vector.dll` → `C:\Program Files\PostgreSQL\18\lib\vector.dll`
   - `vector.control` → `C:\Program Files\PostgreSQL\18\share\extension\vector.control`
   - Dossier `vector/` → `C:\Program Files\PostgreSQL\18\share\extension\vector\`

3. **Redémarrez PostgreSQL** :
   ```powershell
   Stop-Service postgresql-x64-18
   Start-Service postgresql-x64-18
   ```

4. **Activez l'extension** :
   ```powershell
   $env:PGPASSWORD = "root"
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

### Vérification

```powershell
python scripts/check_pgvector_status.py
```

Si vous voyez "Extension pgvector activée", c'est bon !

