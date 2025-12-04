# Script PowerShell pour installer pgvector sur Windows
# Nécessite des privilèges administrateur

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INSTALLATION DE PGVECTOR POUR POSTGRESQL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Détecter la version de PostgreSQL
$pgVersions = @("18", "17", "16", "15", "14", "13", "12")
$pgPath = $null
$pgVersion = $null

foreach ($version in $pgVersions) {
    $testPath = "C:\Program Files\PostgreSQL\$version"
    if (Test-Path $testPath) {
        $pgPath = $testPath
        $pgVersion = $version
        Write-Host "✓ PostgreSQL $version trouvé dans: $pgPath" -ForegroundColor Green
        break
    }
}

if (-not $pgPath) {
    Write-Host "✗ PostgreSQL non trouvé dans les emplacements standards" -ForegroundColor Red
    Write-Host "  Veuillez installer pgvector manuellement" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Version détectée: PostgreSQL $pgVersion" -ForegroundColor Cyan
Write-Host ""

# Vérifier si pgvector est déjà installé
$vectorDll = Join-Path $pgPath "lib\vector.dll"
if (Test-Path $vectorDll) {
    Write-Host "✓ pgvector semble déjà installé (vector.dll trouvé)" -ForegroundColor Green
    Write-Host "  Tentative d'activation de l'extension..." -ForegroundColor Yellow
    
    $env:PGPASSWORD = "root"
    & "$pgPath\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Extension pgvector activée avec succès!" -ForegroundColor Green
        exit 0
    }
}

Write-Host ""
Write-Host "pgvector n'est pas installé. Options d'installation:" -ForegroundColor Yellow
Write-Host ""
Write-Host "OPTION 1: Installation manuelle (Recommandé)" -ForegroundColor Cyan
Write-Host "1. Téléchargez pgvector depuis:" -ForegroundColor White
Write-Host "   https://github.com/pgvector/pgvector/releases" -ForegroundColor White
Write-Host "2. Téléchargez la version pour PostgreSQL $pgVersion (Windows x64)" -ForegroundColor White
Write-Host "3. Extrayez les fichiers:" -ForegroundColor White
Write-Host "   - vector.dll -> $pgPath\lib\" -ForegroundColor White
Write-Host "   - vector.control et dossier vector/ -> $pgPath\share\extension\" -ForegroundColor White
Write-Host "4. Redémarrez le service PostgreSQL" -ForegroundColor White
Write-Host ""
Write-Host "OPTION 2: Installation via Stack Builder" -ForegroundColor Cyan
Write-Host "1. Ouvrez PostgreSQL Stack Builder" -ForegroundColor White
Write-Host "2. Sélectionnez votre installation PostgreSQL $pgVersion" -ForegroundColor White
Write-Host "3. Cherchez 'pgvector' dans les extensions disponibles" -ForegroundColor White
Write-Host "4. Installez-le" -ForegroundColor White
Write-Host ""
Write-Host "OPTION 3: Compilation depuis les sources" -ForegroundColor Cyan
Write-Host "Nécessite Visual Studio et les outils de développement PostgreSQL" -ForegroundColor White
Write-Host ""

# Vérifier si on peut télécharger automatiquement
Write-Host "Tentative de téléchargement automatique..." -ForegroundColor Yellow
$releaseUrl = "https://api.github.com/repos/pgvector/pgvector/releases/latest"
try {
    $release = Invoke-RestMethod -Uri $releaseUrl
    Write-Host "✓ Dernière version: $($release.tag_name)" -ForegroundColor Green
    
    # Chercher l'asset Windows pour PostgreSQL 18
    $windowsAsset = $release.assets | Where-Object { $_.name -like "*windows*" -or $_.name -like "*win*" }
    if ($windowsAsset) {
        Write-Host "  Asset Windows trouvé: $($windowsAsset.name)" -ForegroundColor Green
        Write-Host "  URL: $($windowsAsset.browser_download_url)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Téléchargez manuellement depuis le lien ci-dessus" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Impossible de récupérer les informations de version" -ForegroundColor Red
}

Write-Host ""
Write-Host "Après installation, exécutez:" -ForegroundColor Cyan
Write-Host "  python scripts/test_postgres_connection.py" -ForegroundColor White

