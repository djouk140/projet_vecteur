# Instructions pour installer manuellement pgvector
# Les fichiers sont compilés dans %TEMP%\pgvector

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INSTRUCTIONS D'INSTALLATION MANUELLE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$pgvectorPath = "$env:TEMP\pgvector"
$pgPath = "C:\Program Files\PostgreSQL\18"

Write-Host "Fichiers compiles dans: $pgvectorPath" -ForegroundColor Green
Write-Host "Destination: $pgPath" -ForegroundColor Green
Write-Host ""

Write-Host "ETAPES MANUELLES (en tant qu'administrateur):" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Copiez vector.dll:" -ForegroundColor Cyan
Write-Host "   Source: $pgvectorPath\vector.dll" -ForegroundColor White
Write-Host "   Destination: $pgPath\lib\vector.dll" -ForegroundColor White
Write-Host ""

Write-Host "2. Copiez vector.control:" -ForegroundColor Cyan
Write-Host "   Source: $pgvectorPath\vector.control" -ForegroundColor White
Write-Host "   Destination: $pgPath\share\extension\vector.control" -ForegroundColor White
Write-Host ""

Write-Host "3. Copiez les fichiers SQL:" -ForegroundColor Cyan
Write-Host "   Source: $pgvectorPath\sql\*.sql" -ForegroundColor White
Write-Host "   Destination: $pgPath\share\extension\" -ForegroundColor White
Write-Host ""

Write-Host "OU utilisez ces commandes PowerShell (en tant qu'administrateur):" -ForegroundColor Yellow
Write-Host ""
Write-Host 'Copy-Item "$pgvectorPath\vector.dll" "$pgPath\lib\vector.dll" -Force' -ForegroundColor White
Write-Host 'Copy-Item "$pgvectorPath\vector.control" "$pgPath\share\extension\vector.control" -Force' -ForegroundColor White
Write-Host 'Copy-Item "$pgvectorPath\sql\*.sql" "$pgPath\share\extension\" -Force' -ForegroundColor White
Write-Host ""

Write-Host "4. Redemarrez PostgreSQL:" -ForegroundColor Cyan
Write-Host "   Stop-Service postgresql-x64-18" -ForegroundColor White
Write-Host "   Start-Service postgresql-x64-18" -ForegroundColor White
Write-Host ""

Write-Host "5. Activez l'extension:" -ForegroundColor Cyan
Write-Host '   $env:PGPASSWORD = "root"' -ForegroundColor White
Write-Host '   & "$pgPath\bin\psql.exe" -U postgres -h localhost -d filmsrec -c "CREATE EXTENSION IF NOT EXISTS vector;"' -ForegroundColor White
Write-Host ""

