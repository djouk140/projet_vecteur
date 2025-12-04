#!/bin/bash
# Script d'installation des dépendances pour Linux/Mac

echo "========================================"
echo "Installation des dépendances du projet"
echo "========================================"
echo ""

# Vérifier si Python est installé
echo "[1/4] Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python trouvé: $PYTHON_VERSION"
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✓ Python trouvé: $PYTHON_VERSION"
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo "✗ Python n'est pas installé ou pas dans le PATH"
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
echo ""
echo "[2/4] Création de l'environnement virtuel..."
if [ -d "venv" ]; then
    echo "✓ Environnement virtuel existe déjà"
else
    echo "Création de l'environnement virtuel..."
    $PYTHON_CMD -m venv venv
    if [ $? -eq 0 ]; then
        echo "✓ Environnement virtuel créé avec succès"
    else
        echo "✗ Erreur lors de la création de l'environnement virtuel"
        exit 1
    fi
fi

# Activer l'environnement virtuel
echo ""
echo "[3/4] Activation de l'environnement virtuel..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo "✓ Environnement virtuel activé"
else
    echo "✗ Erreur lors de l'activation de l'environnement virtuel"
    exit 1
fi

# Mettre à jour pip
echo ""
echo "Mise à jour de pip..."
$PIP_CMD install --upgrade pip --quiet
echo "✓ pip mis à jour"

# Installer les dépendances
echo ""
echo "[4/4] Installation des dépendances..."
echo "Cela peut prendre plusieurs minutes..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================"
        echo "✓ Installation terminée avec succès!"
        echo "========================================"
        echo ""
        echo "Pour activer l'environnement virtuel plus tard:"
        echo "  source venv/bin/activate"
        echo ""
        echo "Pour lancer l'API:"
        echo "  uvicorn api.main:app --reload"
    else
        echo ""
        echo "✗ Erreur lors de l'installation des dépendances"
        echo "Vérifiez les messages d'erreur ci-dessus"
        exit 1
    fi
else
    echo "✗ Fichier requirements.txt introuvable"
    exit 1
fi

