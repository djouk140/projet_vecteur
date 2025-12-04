# Script PowerShell pour télécharger et installer pgvector automatiquement
# Nécessite des privilèges administrateur

param(
    [string]$PostgreSQLVersion = "18"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TÉLÉCHARGEMENT ET INSTALLATION DE PGVECTOR" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les privilèges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[!] Ce script necessite des privileges administrateur" -ForegroundColor Yellow
    Write-Host "  Relancez PowerShell en tant qu'administrateur" -ForegroundColor Yellow
    exit 1
}

# Chemin PostgreSQL
$pgPath = "C:\Program Files\PostgreSQL\$PostgreSQLVersion"
if (-not (Test-Path $pgPath)) {
    Write-Host "✗ PostgreSQL $PostgreSQLVersion non trouvé dans: $pgPath" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] PostgreSQL $PostgreSQLVersion trouve" -ForegroundColor Green
Write-Host ""

# Vérifier si déjà installé
$vectorDll = Join-Path $pgPath "lib\vector.dll"
if (Test-Path $vectorDll) {
    Write-Host "[OK] pgvector semble deja installe" -ForegroundColor Green
    Write-Host "  Fichier trouvé: $vectorDll" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Tentative d'activation de l'extension..." -ForegroundColor Yellow
    
    $env:PGPASSWORD = "root"
    & "$pgPath\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Extension pgvector activée avec succès!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[!] Extension non activee, mais fichiers presents" -ForegroundColor Yellow
        Write-Host "  Redémarrez peut-être PostgreSQL" -ForegroundColor Yellow
    }
}

# Télécharger la dernière version
Write-Host "Téléchargement de la dernière version de pgvector..." -ForegroundColor Yellow
$releaseUrl = "https://api.github.com/repos/pgvector/pgvector/releases/latest"

try {
    $release = Invoke-RestMethod -Uri $releaseUrl
    $version = $release.tag_name
    Write-Host "[OK] Derniere version trouvee: $version" -ForegroundColor Green
    
    # Chercher l'asset Windows
    $windowsAsset = $release.assets | Where-Object { 
        $_.name -like "*windows*" -or 
        $_.name -like "*win*" -or 
        $_.name -like "*.zip" 
    } | Select-Object -First 1
    
    if (-not $windowsAsset) {
        Write-Host "[X] Aucun binaire Windows trouve dans les releases" -ForegroundColor Red
        Write-Host "  Vous devrez compiler pgvector depuis les sources" -ForegroundColor Yellow
        Write-Host "  Voir: https://github.com/pgvector/pgvector#installation" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "  Asset trouvé: $($windowsAsset.name)" -ForegroundColor Gray
    Write-Host "  Taille: $([math]::Round($windowsAsset.size / 1MB, 2)) MB" -ForegroundColor Gray
    
    # Télécharger
    $downloadPath = Join-Path $env:TEMP "pgvector.zip"
    Write-Host ""
    Write-Host "Téléchargement en cours..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $windowsAsset.browser_download_url -OutFile $downloadPath
    Write-Host "[OK] Telechargement termine" -ForegroundColor Green
    
    # Extraire
    Write-Host ""
    Write-Host "Extraction des fichiers..." -ForegroundColor Yellow
    $extractPath = Join-Path $env:TEMP "pgvector_extract"
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
    
    # Chercher les fichiers
    $vectorDllSource = Get-ChildItem -Path $extractPath -Recurse -Filter "vector.dll" | Select-Object -First 1
    $vectorControlSource = Get-ChildItem -Path $extractPath -Recurse -Filter "vector.control" | Select-Object -First 1
    $vectorFolderSource = Get-ChildItem -Path $extractPath -Recurse -Directory -Filter "vector" | Select-Object -First 1
    
    if (-not $vectorDllSource) {
        Write-Host "[X] Fichier vector.dll non trouve dans l'archive" -ForegroundColor Red
        Write-Host "  Structure de l'archive:" -ForegroundColor Yellow
        Get-ChildItem -Path $extractPath -Recurse | Select-Object FullName | Format-Table -AutoSize
        exit 1
    }
    
    Write-Host "[OK] Fichiers trouves dans l'archive" -ForegroundColor Green
    
    # Copier les fichiers
    Write-Host ""
    Write-Host "Installation des fichiers..." -ForegroundColor Yellow
    
    # Copier vector.dll
    $vectorDllDest = Join-Path $pgPath "lib\vector.dll"
    Copy-Item -Path $vectorDllSource.FullName -Destination $vectorDllDest -Force
    Write-Host "[OK] vector.dll copie vers: $vectorDllDest" -ForegroundColor Green
    
    # Copier vector.control
    if ($vectorControlSource) {
        $vectorControlDest = Join-Path $pgPath "share\extension\vector.control"
        $extensionDir = Split-Path $vectorControlDest
        if (-not (Test-Path $extensionDir)) {
            New-Item -ItemType Directory -Path $extensionDir -Force | Out-Null
        }
        Copy-Item -Path $vectorControlSource.FullName -Destination $vectorControlDest -Force
        Write-Host "[OK] vector.control copie" -ForegroundColor Green
    }
    
    # Copier le dossier vector/
    if ($vectorFolderSource) {
        $vectorFolderDest = Join-Path $pgPath "share\extension\vector"
        if (Test-Path $vectorFolderDest) {
            Remove-Item $vectorFolderDest -Recurse -Force
        }
        Copy-Item -Path $vectorFolderSource.FullName -Destination $vectorFolderDest -Recurse -Force
        Write-Host "[OK] Dossier vector/ copie" -ForegroundColor Green
    } else {
        # Chercher les fichiers SQL individuellement
        $sqlFiles = Get-ChildItem -Path $extractPath -Recurse -Filter "*.sql"
        if ($sqlFiles) {
            $vectorFolderDest = Join-Path $pgPath "share\extension\vector"
            if (-not (Test-Path $vectorFolderDest)) {
                New-Item -ItemType Directory -Path $vectorFolderDest -Force | Out-Null
            }
            foreach ($sqlFile in $sqlFiles) {
                Copy-Item -Path $sqlFile.FullName -Destination $vectorFolderDest -Force
            }
            Write-Host "[OK] Fichiers SQL copies" -ForegroundColor Green
        }
    }
    
    # Nettoyer
    Remove-Item $downloadPath -Force
    Remove-Item $extractPath -Recurse -Force
    
    Write-Host ""
    Write-Host "[OK] Installation terminee!" -ForegroundColor Green
    Write-Host ""
    
    # Redémarrer PostgreSQL
    Write-Host "Redémarrage de PostgreSQL..." -ForegroundColor Yellow
    $serviceName = "postgresql-x64-$PostgreSQLVersion"
    Stop-Service -Name $serviceName -Force
    Start-Sleep -Seconds 2
    Start-Service -Name $serviceName
    Start-Sleep -Seconds 3
    Write-Host "[OK] PostgreSQL redemarre" -ForegroundColor Green
    
    # Activer l'extension
    Write-Host ""
    Write-Host "Activation de l'extension pgvector..." -ForegroundColor Yellow
    $env:PGPASSWORD = "root"
    & "$pgPath\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Extension pgvector activée avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "INSTALLATION RÉUSSIE!" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Cyan
    } else {
        Write-Host "[!] Erreur lors de l activation" -ForegroundColor Yellow
        Write-Host "  Essayez manuellement:" -ForegroundColor Yellow
        Write-Host "  psql -U postgres -d filmsrec -c `"CREATE EXTENSION vector;`"" -ForegroundColor White
    }
    
} catch {
    Write-Host "[X] Erreur lors du telechargement/installation: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation manuelle recommandée:" -ForegroundColor Yellow
    Write-Host "1. Téléchargez depuis: https://github.com/pgvector/pgvector/releases" -ForegroundColor White
    Write-Host "2. Suivez les instructions dans docs/INSTALL_PGVECTOR_WINDOWS.md" -ForegroundColor White
    exit 1
}

