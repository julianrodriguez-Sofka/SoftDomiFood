# Script para restaurar un backup de la base de datos PostgreSQL
# Uso: .\scripts\restore-database.ps1 -BackupFile "database\backups\backup_20241123_104500.sql"

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$ContainerName = "softdomifood-db",
    [string]$DbUser = "softdomifood_user",
    [string]$DbName = "softdomifood_db"
)

Write-Host "📥 Iniciando restauración de la base de datos..." -ForegroundColor Green
Write-Host ""

# Verificar que el archivo de backup exista
if (-not (Test-Path $BackupFile)) {
    Write-Host "❌ Error: El archivo de backup no existe: $BackupFile" -ForegroundColor Red
    exit 1
}

# Verificar que el contenedor esté corriendo
Write-Host "🔍 Verificando que el contenedor de PostgreSQL esté corriendo..." -ForegroundColor Yellow
$containerExists = docker ps --filter "name=$ContainerName" --format "{{.Names}}" | Select-String -Pattern $ContainerName

if (-not $containerExists) {
    Write-Host "❌ Error: El contenedor '$ContainerName' no está corriendo." -ForegroundColor Red
    Write-Host "   Por favor, inicia los servicios con: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Contenedor encontrado: $ContainerName" -ForegroundColor Green
Write-Host "✅ Archivo de backup encontrado: $BackupFile" -ForegroundColor Green

# Mostrar advertencia
Write-Host ""
Write-Host "⚠️  ADVERTENCIA: Esta operación reemplazará todos los datos existentes en la base de datos." -ForegroundColor Yellow
$confirmation = Read-Host "¿Deseas continuar? (S/N)"

if ($confirmation -ne "S" -and $confirmation -ne "s" -and $confirmation -ne "Y" -and $confirmation -ne "y") {
    Write-Host "❌ Operación cancelada por el usuario." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🔄 Restaurando backup..." -ForegroundColor Yellow

    try {
        # Método 1: Intentar restaurar directamente desde el archivo
        Write-Host "   Ejecutando restore..." -ForegroundColor Gray
        Get-Content $BackupFile | docker exec -i $ContainerName psql -U $DbUser -d postgres
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Restauración completada exitosamente!" -ForegroundColor Green
            Write-Host ""
            Write-Host "💡 Puede ser necesario reiniciar los servicios para aplicar los cambios:" -ForegroundColor Cyan
            Write-Host "   docker-compose restart api worker" -ForegroundColor Gray
        } else {
            Write-Host "❌ Error al restaurar el backup (código: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "   Intentando método alternativo..." -ForegroundColor Yellow
            
            # Método alternativo: copiar al contenedor y ejecutar
            $tempBackupName = "temp_restore.sql"
            docker cp $BackupFile "${ContainerName}:/tmp/$tempBackupName"
            
            if ($LASTEXITCODE -eq 0) {
                docker exec $ContainerName psql -U $DbUser -d postgres -f "/tmp/$tempBackupName"
                docker exec $ContainerName rm -f "/tmp/$tempBackupName" 2>$null
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Restauración completada con método alternativo!" -ForegroundColor Green
                } else {
                    Write-Host "❌ Error al restaurar el backup con método alternativo" -ForegroundColor Red
                    exit 1
                }
            } else {
                Write-Host "❌ Error al copiar el archivo al contenedor" -ForegroundColor Red
                exit 1
            }
        }
    
} catch {
    Write-Host "❌ Error durante la restauración: $_" -ForegroundColor Red
    exit 1
}

