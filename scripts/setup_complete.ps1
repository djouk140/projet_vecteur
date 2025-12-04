# Script complet pour configurer pgvector et la base de données
# À exécuter après avoir compilé pgvector

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CONFIGURATION COMPLETE DE LA BASE DE DONNEES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1: Redémarrer PostgreSQL
Write-Host "1. Redemarrage de PostgreSQL..." -ForegroundColor Yellow
try {
    Stop-Service postgresql-x64-18 -Force -ErrorAction Stop
    Start-Sleep -Seconds 2
    Start-Service postgresql-x64-18 -ErrorAction Stop
    Start-Sleep -Seconds 3
    Write-Host "[OK] PostgreSQL redemarre" -ForegroundColor Green
} catch {
    Write-Host "[!] Erreur lors du redemarrage: $_" -ForegroundColor Yellow
    Write-Host "  Redemarrez manuellement PostgreSQL" -ForegroundColor Yellow
}

Write-Host ""

# Étape 2: Activer l'extension pgvector
Write-Host "2. Activation de l'extension pgvector..." -ForegroundColor Yellow
$pgPath = "C:\Program Files\PostgreSQL\18"
$env:PGPASSWORD = "root"

try {
    $result = & "$pgPath\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Extension pgvector activee" -ForegroundColor Green
    } else {
        Write-Host "[!] Erreur: $result" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Erreur: $_" -ForegroundColor Yellow
}

Write-Host ""

# Étape 3: Vérifier l'extension
Write-Host "3. Verification de l'extension..." -ForegroundColor Yellow
try {
    $result = & "$pgPath\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "SELECT * FROM pg_extension WHERE extname = 'vector';" 2>&1
    if ($result -match "vector") {
        Write-Host "[OK] Extension pgvector verifiee" -ForegroundColor Green
    }
} catch {
    Write-Host "[!] Impossible de verifier" -ForegroundColor Yellow
}

Write-Host ""

# Étape 4: Configurer le schéma de base de données
Write-Host "4. Configuration du schema de base de donnees..." -ForegroundColor Yellow
python scripts/setup_database.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Schema configure" -ForegroundColor Green
} else {
    Write-Host "[!] Erreur lors de la configuration du schema" -ForegroundColor Yellow
}

Write-Host ""

# Étape 5: Vérification finale
Write-Host "5. Verification finale..." -ForegroundColor Yellow
python scripts/check_pgvector_status.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ETAPES SUIVANTES:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "1. Ingerez les films: python scripts/ingest_films.py data/films.csv" -ForegroundColor White
Write-Host "2. Generez les embeddings: python scripts/generate_embeddings.py" -ForegroundColor White
Write-Host "3. Creez l'index: python scripts/run_all.py --skip-setup --skip-ingestion --skip-embeddings" -ForegroundColor White
Write-Host ""

