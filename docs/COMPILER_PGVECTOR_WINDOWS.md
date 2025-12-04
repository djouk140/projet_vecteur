# Compiler pgvector sur Windows

## Prérequis

Vous avez besoin de **Visual Studio Build Tools** ou **Visual Studio** avec les outils C++.

## Option 1 : Installer Visual Studio Build Tools (Recommandé)

1. Téléchargez **Visual Studio Build Tools** :
   - https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
   - Ou cherchez "Build Tools for Visual Studio 2022"

2. Installez avec :
   - **C++ build tools**
   - **Windows SDK** (dernière version)

3. Redémarrez votre terminal

## Option 2 : Utiliser Visual Studio Developer Command Prompt

Si vous avez déjà Visual Studio installé :

1. Ouvrez **"x64 Native Tools Command Prompt for VS 2022"** (ou version similaire)
   - Cherchez dans le menu Démarrer : "Developer Command Prompt"

2. Naviguez vers le dossier pgvector :
   ```cmd
   cd %TEMP%\pgvector
   ```

3. Compilez :
   ```cmd
   set "PGROOT=C:\Program Files\PostgreSQL\18"
   nmake /F Makefile.win
   nmake /F Makefile.win install
   ```

## Option 3 : Utiliser les binaires précompilés (si disponibles)

Certaines versions de pgvector ont des binaires précompilés. Vérifiez :
- https://github.com/pgvector/pgvector/releases
- Cherchez des fichiers `.dll` ou `.zip` pour Windows

## Après compilation

1. Les fichiers seront installés dans PostgreSQL
2. Redémarrez PostgreSQL :
   ```powershell
   Stop-Service postgresql-x64-18
   Start-Service postgresql-x64-18
   ```

3. Activez l'extension :
   ```powershell
   $env:PGPASSWORD = "root"
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

