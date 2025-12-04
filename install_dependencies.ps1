# Script d'installation des dépendances pour Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation des dépendances du projet" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
Write-Host "[1/4] Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Créer l'environnement virtuel s'il n'existe pas
Write-Host ""
Write-Host "[2/4] Création de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Environnement virtuel existe déjà" -ForegroundColor Green
} else {
    Write-Host "Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Environnement virtuel créé avec succès" -ForegroundColor Green
    } else {
        Write-Host "✗ Erreur lors de la création de l'environnement virtuel" -ForegroundColor Red
        exit 1
    }
}

# Activer l'environnement virtuel
Write-Host ""
Write-Host "[3/4] Activation de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✓ Environnement virtuel activé" -ForegroundColor Green
} else {
    Write-Host "✗ Script d'activation introuvable" -ForegroundColor Red
    exit 1
}

# Mettre à jour pip
Write-Host ""
Write-Host "Mise à jour de pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip mis à jour" -ForegroundColor Green

# Installer les dépendances
Write-Host ""
Write-Host "[4/4] Installation des dépendances..." -ForegroundColor Yellow
Write-Host "Cela peut prendre plusieurs minutes..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✓ Installation terminée avec succès!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Pour activer l'environnement virtuel plus tard:" -ForegroundColor Cyan
        Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host ""
        Write-Host "Pour lancer l'API:" -ForegroundColor Cyan
        Write-Host "  uvicorn api.main:app --reload" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "✗ Erreur lors de l'installation des dépendances" -ForegroundColor Red
        Write-Host "Vérifiez les messages d'erreur ci-dessus" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✗ Fichier requirements.txt introuvable" -ForegroundColor Red
    exit 1
}

