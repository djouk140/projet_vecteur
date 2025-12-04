@echo off
REM Script pour compiler et installer pgvector avec Visual Studio 2022
REM À exécuter depuis "x64 Native Tools Command Prompt for VS 2022"

echo ============================================================
echo COMPILATION ET INSTALLATION DE PGVECTOR
echo ============================================================
echo.

set "PGROOT=C:\Program Files\PostgreSQL\18"
set "PGVECTOR_PATH=%TEMP%\pgvector"

if not exist "%PGVECTOR_PATH%" (
    echo [X] pgvector non trouve dans %PGVECTOR_PATH%
    echo Clonez d'abord: git clone https://github.com/pgvector/pgvector.git %PGVECTOR_PATH%
    pause
    exit /b 1
)

cd /d "%PGVECTOR_PATH%"

echo PGROOT: %PGROOT%
echo pgvector: %PGVECTOR_PATH%
echo.

echo Etape 1: Compilation...
nmake /F Makefile.win
if errorlevel 1 (
    echo [X] Erreur lors de la compilation
    pause
    exit /b 1
)

echo [OK] Compilation reussie
echo.

echo Etape 2: Installation...
nmake /F Makefile.win install
if errorlevel 1 (
    echo [X] Erreur lors de l'installation
    echo Essayez en tant qu'administrateur
    pause
    exit /b 1
)

echo [OK] Installation reussie
echo.

echo ============================================================
echo COMPILATION TERMINEE!
echo ============================================================
echo.
echo Redemarrez PostgreSQL puis activez l'extension:
echo   Stop-Service postgresql-x64-18
echo   Start-Service postgresql-x64-18
echo   psql -U postgres -d filmsrec -c "CREATE EXTENSION vector;"
echo.

pause

