# Script pour configurer l'environnement de compilation Visual Studio
# Utilisez ce script depuis un Developer Command Prompt

Write-Host "Configuration de l'environnement de compilation..." -ForegroundColor Cyan

$pgRoot = "C:\Program Files\PostgreSQL\18"
$pgvectorPath = "$env:TEMP\pgvector"

if (-not (Test-Path $pgvectorPath)) {
    Write-Host "pgvector non trouve dans $pgvectorPath" -ForegroundColor Red
    Write-Host "Clonez d'abord: git clone https://github.com/pgvector/pgvector.git $pgvectorPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "PGROOT: $pgRoot" -ForegroundColor Green
Write-Host "pgvector: $pgvectorPath" -ForegroundColor Green
Write-Host ""

# Vérifier nmake
$nmake = Get-Command nmake -ErrorAction SilentlyContinue
if (-not $nmake) {
    Write-Host "[!] nmake non trouve" -ForegroundColor Red
    Write-Host "Ouvrez 'x64 Native Tools Command Prompt for VS 2022' depuis le menu Demarrer" -ForegroundColor Yellow
    Write-Host "Puis executez:" -ForegroundColor Yellow
    Write-Host "  cd $pgvectorPath" -ForegroundColor White
    Write-Host "  set `"PGROOT=$pgRoot`"" -ForegroundColor White
    Write-Host "  nmake /F Makefile.win" -ForegroundColor White
    Write-Host "  nmake /F Makefile.win install" -ForegroundColor White
    exit 1
}

Write-Host "[OK] nmake trouve: $($nmake.Source)" -ForegroundColor Green
Write-Host ""

# Compiler
Write-Host "Compilation de pgvector..." -ForegroundColor Yellow
Set-Location $pgvectorPath
$env:PGROOT = $pgRoot

Write-Host "Etape 1: Compilation..." -ForegroundColor Cyan
& nmake /F Makefile.win
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Erreur lors de la compilation" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Compilation reussie" -ForegroundColor Green
Write-Host ""

Write-Host "Etape 2: Installation..." -ForegroundColor Cyan
& nmake /F Makefile.win install
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Erreur lors de l'installation" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Installation reussie" -ForegroundColor Green
Write-Host ""

Write-Host "Redemarrage de PostgreSQL..." -ForegroundColor Yellow
Stop-Service postgresql-x64-18 -Force
Start-Sleep -Seconds 2
Start-Service postgresql-x64-18
Start-Sleep -Seconds 3

Write-Host "[OK] PostgreSQL redemarre" -ForegroundColor Green
Write-Host ""

Write-Host "Activation de l'extension..." -ForegroundColor Yellow
$env:PGPASSWORD = "root"
& "$pgRoot\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "[OK] PGVECTOR INSTALLE ET ACTIVE!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
} else {
    Write-Host "[!] Extension non activee automatiquement" -ForegroundColor Yellow
    Write-Host "Essayez manuellement:" -ForegroundColor Yellow
    Write-Host "  psql -U postgres -d filmsrec -c `"CREATE EXTENSION vector;`"" -ForegroundColor White
}

