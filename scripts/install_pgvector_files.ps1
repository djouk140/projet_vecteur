# Script pour installer les fichiers pgvector compilés
# À exécuter en tant qu'administrateur

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INSTALLATION DES FICHIERS PGVECTOR" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les privilèges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[!] Ce script necessite des privileges administrateur" -ForegroundColor Red
    Write-Host "  Relancez PowerShell en tant qu'administrateur" -ForegroundColor Yellow
    exit 1
}

$pgPath = "C:\Program Files\PostgreSQL\18"
$pgvectorPath = "$env:TEMP\pgvector"

# Vérifier que les fichiers compilés existent
$vectorDll = Join-Path $pgvectorPath "vector.dll"
if (-not (Test-Path $vectorDll)) {
    Write-Host "[X] vector.dll non trouve dans $pgvectorPath" -ForegroundColor Red
    Write-Host "  Compilez d'abord pgvector" -ForegroundColor Yellow
    exit 1
}

Write-Host "Fichiers sources trouves dans: $pgvectorPath" -ForegroundColor Green
Write-Host ""

# Copier vector.dll
Write-Host "1. Copie de vector.dll..." -ForegroundColor Yellow
$dllDest = Join-Path $pgPath "lib\vector.dll"
try {
    Copy-Item -Path $vectorDll -Destination $dllDest -Force
    Write-Host "[OK] vector.dll copie vers: $dllDest" -ForegroundColor Green
} catch {
    Write-Host "[X] Erreur: $_" -ForegroundColor Red
    exit 1
}

# Copier vector.control
Write-Host "2. Copie de vector.control..." -ForegroundColor Yellow
$controlSource = Join-Path $pgvectorPath "vector.control"
if (Test-Path $controlSource) {
    $controlDest = Join-Path $pgPath "share\extension\vector.control"
    $controlDestDir = Split-Path $controlDest
    if (-not (Test-Path $controlDestDir)) {
        New-Item -ItemType Directory -Path $controlDestDir -Force | Out-Null
    }
    Copy-Item -Path $controlSource -Destination $controlDest -Force
    Write-Host "[OK] vector.control copie" -ForegroundColor Green
}

# Copier les fichiers SQL
Write-Host "3. Copie des fichiers SQL..." -ForegroundColor Yellow
$sqlSource = Join-Path $pgvectorPath "sql"
if (Test-Path $sqlSource) {
    $sqlDest = Join-Path $pgPath "share\extension"
    $vectorSqlDest = Join-Path $sqlDest "vector"
    
    # Copier tous les fichiers SQL
    $sqlFiles = Get-ChildItem -Path $sqlSource -Filter "*.sql"
    foreach ($sqlFile in $sqlFiles) {
        Copy-Item -Path $sqlFile.FullName -Destination $sqlDest -Force
        Write-Host "  [OK] $($sqlFile.Name) copie" -ForegroundColor Gray
    }
    
    # Copier aussi dans le dossier vector/ si nécessaire
    if (-not (Test-Path $vectorSqlDest)) {
        New-Item -ItemType Directory -Path $vectorSqlDest -Force | Out-Null
    }
    foreach ($sqlFile in $sqlFiles) {
        Copy-Item -Path $sqlFile.FullName -Destination $vectorSqlDest -Force
    }
    Write-Host "[OK] Fichiers SQL copies" -ForegroundColor Green
}

Write-Host ""
Write-Host "[OK] Installation des fichiers terminee!" -ForegroundColor Green
Write-Host ""
Write-Host "Redemarrez PostgreSQL et activez l'extension avec:" -ForegroundColor Cyan
Write-Host "  python scripts\setup_complete.ps1" -ForegroundColor White
Write-Host ""

