@echo off
REM Script pour finaliser l'installation de pgvector
REM À EXÉCUTER EN TANT QU'ADMINISTRATEUR

echo ============================================================
echo FINALISATION DE L'INSTALLATION PGVECTOR
echo ============================================================
echo.

set "PGROOT=C:\Program Files\PostgreSQL\18"
set "PGVECTOR_SOURCE=%TEMP%\pgvector"

echo Copie des fichiers...
echo.

REM Copier vector.dll
copy "%PGVECTOR_SOURCE%\vector.dll" "%PGROOT%\lib\vector.dll" /Y
if errorlevel 1 (
    echo [X] Erreur lors de la copie de vector.dll
    echo Executez ce script en tant qu'administrateur
    pause
    exit /b 1
)
echo [OK] vector.dll copie

REM Créer le dossier extension s'il n'existe pas
if not exist "%PGROOT%\share\extension" mkdir "%PGROOT%\share\extension"

REM Copier vector.control
copy "%PGVECTOR_SOURCE%\vector.control" "%PGROOT%\share\extension\vector.control" /Y
if errorlevel 1 (
    echo [X] Erreur lors de la copie de vector.control
) else (
    echo [OK] vector.control copie
)

REM Copier les fichiers SQL
copy "%PGVECTOR_SOURCE%\sql\*.sql" "%PGROOT%\share\extension\" /Y
if errorlevel 1 (
    echo [X] Erreur lors de la copie des fichiers SQL
) else (
    echo [OK] Fichiers SQL copies
)

echo.
echo ============================================================
echo INSTALLATION TERMINEE!
echo ============================================================
echo.
echo Redemarrez PostgreSQL et activez l'extension avec:
echo   python scripts\setup_complete.ps1
echo.

pause

