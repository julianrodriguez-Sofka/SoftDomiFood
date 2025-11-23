# Script para hacer backup de la base de datos PostgreSQL
# Uso: .\scripts\backup-database.ps1

param(
    [string]$ContainerName = "softdomifood-db",
    [string]$DbUser = "softdomifood_user",
    [string]$DbName = "softdomifood_db",
    [string]$OutputDir = "database\backups"
)

Write-Host "📦 Iniciando backup de la base de datos..." -ForegroundColor Green
Write-Host ""

# Verificar que el contenedor esté corriendo
Write-Host "🔍 Verificando que el contenedor de PostgreSQL esté corriendo..." -ForegroundColor Yellow
$containerExists = docker ps --filter "name=$ContainerName" --format "{{.Names}}" | Select-String -Pattern $ContainerName

if (-not $containerExists) {
    Write-Host "❌ Error: El contenedor '$ContainerName' no está corriendo." -ForegroundColor Red
    Write-Host "   Por favor, inicia los servicios con: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Contenedor encontrado: $ContainerName" -ForegroundColor Green

# Crear directorio de salida si no existe
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "✅ Directorio creado: $OutputDir" -ForegroundColor Green
}

# Generar nombre de archivo con timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFileName = "backup_$timestamp.sql"
$backupPath = Join-Path $OutputDir $backupFileName

Write-Host ""
Write-Host "💾 Creando backup en: $backupPath" -ForegroundColor Yellow

# Ejecutar pg_dump dentro del contenedor
try {
    docker exec $ContainerName pg_dump -U $DbUser -d $DbName --clean --if-exists --create > $backupPath
    
    if ($LASTEXITCODE -eq 0) {
        $fileSize = (Get-Item $backupPath).Length / 1KB
        Write-Host ""
        Write-Host "✅ Backup completado exitosamente!" -ForegroundColor Green
        Write-Host "   Archivo: $backupPath" -ForegroundColor White
        Write-Host "   Tamaño: $([math]::Round($fileSize, 2)) KB" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 Para restaurar este backup:" -ForegroundColor Cyan
        Write-Host "   .\scripts\restore-database.ps1 -BackupFile `"$backupPath`"" -ForegroundColor Gray
    } else {
        Write-Host "❌ Error al crear el backup (código: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error al ejecutar el backup: $_" -ForegroundColor Red
    exit 1
}

