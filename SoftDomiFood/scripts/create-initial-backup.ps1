# Script para crear un backup inicial con datos de ejemplo
# Este script inicializa la base de datos con datos de ejemplo y crea un backup
# Uso: .\scripts\create-initial-backup.ps1

Write-Host "📦 Creando backup inicial de la base de datos..." -ForegroundColor Green
Write-Host ""

# Verificar que los servicios estén corriendo
$dbContainer = docker ps --filter "name=softdomifood-db" --format "{{.Names}}" | Select-String -Pattern "softdomifood-db"

if (-not $dbContainer) {
    Write-Host "❌ Error: El contenedor de PostgreSQL no está corriendo." -ForegroundColor Red
    Write-Host "   Por favor, inicia los servicios con: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Crear backup
$outputDir = "database\backups"
$backupFile = Join-Path $outputDir "initial_data.sql"

Write-Host "💾 Creando backup en: $backupFile" -ForegroundColor Yellow

# Ejecutar backup
& ".\scripts\backup-database.ps1"

# Renombrar el último backup como initial_data.sql
$latestBackup = Get-ChildItem -Path $outputDir -Filter "backup_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestBackup) {
    # Si ya existe initial_data.sql, crear un backup
    if (Test-Path $backupFile) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $oldBackup = Join-Path $outputDir "initial_data_backup_$timestamp.sql"
        Move-Item -Path $backupFile -Destination $oldBackup -Force
        Write-Host "   📋 Backup anterior guardado como: $oldBackup" -ForegroundColor Gray
    }
    
    Copy-Item -Path $latestBackup.FullName -Destination $backupFile -Force
    Write-Host ""
    Write-Host "✅ Backup inicial creado: $backupFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Este archivo puede ser compartido con tu equipo." -ForegroundColor Cyan
    Write-Host "   Para restaurar: .\scripts\restore-database.ps1 -BackupFile `"$backupFile`"" -ForegroundColor Gray
} else {
    Write-Host "❌ No se pudo crear el backup inicial" -ForegroundColor Red
    exit 1
}

