# Guide complet : Installer et compiler pgvector sur Windows

## Étape 1 : Installer Visual Studio Build Tools

1. **Téléchargez Visual Studio Build Tools** :
   - https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
   - Cliquez sur "Build Tools for Visual Studio 2022"

2. **Installez avec ces composants** :
   - ✅ **C++ build tools**
   - ✅ **Windows 10/11 SDK** (dernière version)
   - ✅ **CMake tools for Windows** (optionnel mais recommandé)

3. **Redémarrez votre ordinateur** après l'installation

## Étape 2 : Ouvrir le Developer Command Prompt

1. Appuyez sur `Win` et cherchez : **"x64 Native Tools Command Prompt for VS 2022"**
2. **Cliquez dessus** (cela ouvre un terminal avec nmake configuré)

## Étape 3 : Compiler pgvector

Dans le Developer Command Prompt, exécutez :

```cmd
cd %TEMP%\pgvector
set "PGROOT=C:\Program Files\PostgreSQL\18"
nmake /F Makefile.win
```

Si la compilation réussit, installez :

```cmd
nmake /F Makefile.win install
```

**Note** : Vous devrez peut-être exécuter en tant qu'administrateur pour l'installation.

## Étape 4 : Redémarrer PostgreSQL et activer l'extension

Dans PowerShell (en tant qu'administrateur) :

```powershell
Stop-Service postgresql-x64-18
Start-Service postgresql-x64-18

$env:PGPASSWORD = "root"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Vérification

```powershell
python scripts/check_pgvector_status.py
```

## Alternative : Utiliser Visual Studio Community

Si vous préférez installer Visual Studio Community (plus complet) :
- https://visualstudio.microsoft.com/fr/visual-studio-community/
- Installez avec "Développement Desktop en C++"

