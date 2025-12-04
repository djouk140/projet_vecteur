#!/bin/bash
# Script de démarrage de l'API
# Utilisation: ./start_api.sh

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Vérifier que le fichier .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Le fichier .env n'existe pas!"
    echo "Créez-le à partir de .env.example"
    exit 1
fi

# Démarrer l'API
echo "🚀 Démarrage de l'API..."
echo "🌐 L'API sera accessible sur http://127.0.0.1:8000"
echo "📖 Documentation Swagger: http://127.0.0.1:8000/docs"
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

