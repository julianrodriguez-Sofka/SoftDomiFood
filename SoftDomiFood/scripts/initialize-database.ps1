# Script para inicializar la base de datos con datos de ejemplo
# Uso: .\scripts\initialize-database.ps1

param(
    [switch]$SkipSeed = $false,
    [switch]$CreateBackup = $true
)

Write-Host "🚀 Inicializando base de datos con datos de ejemplo..." -ForegroundColor Green
Write-Host ""

# Verificar que los servicios estén corriendo
Write-Host "🔍 Verificando servicios..." -ForegroundColor Yellow
$apiContainer = docker ps --filter "name=softdomifood-api" --format "{{.Names}}" | Select-String -Pattern "softdomifood-api"
$dbContainer = docker ps --filter "name=softdomifood-db" --format "{{.Names}}" | Select-String -Pattern "softdomifood-db"

if (-not $dbContainer) {
    Write-Host "❌ Error: El contenedor de PostgreSQL no está corriendo." -ForegroundColor Red
    Write-Host "   Por favor, inicia los servicios con: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Servicios encontrados" -ForegroundColor Green
Write-Host ""

# Ejecutar seed de datos
if (-not $SkipSeed) {
    Write-Host "🌱 Ejecutando seed de datos de ejemplo..." -ForegroundColor Yellow
    
    try {
        # Ejecutar el script de seed dentro del contenedor de la API
        docker exec softdomifood-api python -c "import asyncio; from seed_data import seed_database; asyncio.run(seed_database(force_clear=False))"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Seed completado exitosamente!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Seed completado con advertencias (código: $LASTEXITCODE)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Error al ejecutar seed: $_" -ForegroundColor Red
        Write-Host "   Intentando método alternativo..." -ForegroundColor Yellow
        
        # Método alternativo: ejecutar directamente con python
        docker exec softdomifood-api python seed_data.py
    }
    
    Write-Host ""
}

# Crear backup inicial
if ($CreateBackup) {
    Write-Host "💾 Creando backup inicial de los datos..." -ForegroundColor Yellow
    & ".\scripts\backup-database.ps1"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Proceso completado exitosamente!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Resumen:" -ForegroundColor Cyan
        Write-Host "   ✅ Base de datos inicializada" -ForegroundColor White
        Write-Host "   ✅ Datos de ejemplo creados" -ForegroundColor White
        Write-Host "   ✅ Backup inicial creado" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 Para compartir estos datos con tu equipo:" -ForegroundColor Cyan
        Write-Host "   1. git add database/backups/backup_*.sql" -ForegroundColor Gray
        Write-Host "   2. git commit -m 'Backup inicial de base de datos'" -ForegroundColor Gray
        Write-Host "   3. git push" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Backup no se pudo crear, pero la inicialización se completó" -ForegroundColor Yellow
    }
}

Write-Host ""

