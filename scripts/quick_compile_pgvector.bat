@echo off
REM Script rapide pour compiler pgvector
REM Trouve automatiquement Visual Studio et compile

echo Recherche de Visual Studio...
set "VS_PATH="

REM Chercher Visual Studio 2022
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
    set "VS_TYPE=Community"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat"
    set "VS_TYPE=Professional"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat"
    set "VS_TYPE=Enterprise"
)

if "%VS_PATH%"=="" (
    echo [X] Visual Studio 2022 non trouve
    echo Ouvrez manuellement "x64 Native Tools Command Prompt for VS 2022"
    echo Puis executez: scripts\compile_pgvector_simple.bat
    pause
    exit /b 1
)

echo [OK] Visual Studio 2022 %VS_TYPE% trouve
echo.

set "PGROOT=C:\Program Files\PostgreSQL\18"
set "PGVECTOR_PATH=%TEMP%\pgvector"

if not exist "%PGVECTOR_PATH%" (
    echo [X] pgvector non trouve dans %PGVECTOR_PATH%
    pause
    exit /b 1
)

echo Configuration de l'environnement Visual Studio...
call "%VS_PATH%" x64 >nul 2>&1

echo Compilation de pgvector...
cd /d "%PGVECTOR_PATH%"

nmake /F Makefile.win
if errorlevel 1 (
    echo [X] Erreur lors de la compilation
    pause
    exit /b 1
)

echo [OK] Compilation reussie
echo.

echo Installation...
nmake /F Makefile.win install
if errorlevel 1 (
    echo [X] Erreur lors de l'installation - essayez en tant qu'administrateur
    pause
    exit /b 1
)

echo [OK] Installation reussie!
echo.
echo Redemarrez PostgreSQL et activez l'extension avec:
echo   python scripts\setup_complete.ps1
echo.

pause

