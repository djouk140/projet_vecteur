@echo off
REM Script de démarrage de l'API pour Windows
REM Utilisation: start_api.bat

REM Activer l'environnement virtuel si présent
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Vérifier que le fichier .env existe
if not exist .env (
    echo ⚠️  Le fichier .env n'existe pas!
    echo Créez-le à partir de .env.example
    exit /b 1
)

REM Démarrer l'API
echo 🚀 Démarrage de l'API...
echo 🌐 L'API sera accessible sur http://127.0.0.1:8000
echo 📖 Documentation Swagger: http://127.0.0.1:8000/docs
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

