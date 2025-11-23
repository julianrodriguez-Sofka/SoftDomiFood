# Script de ejecución de análisis de seguridad estática (PowerShell)
# Propósito: Ejecutar análisis SAST con Bandit en contenedor Docker
# Uso: .\qa_automated\run_security_analysis.ps1

$ErrorActionPreference = "Stop"

# Variables de configuración
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$DockerfilePath = Join-Path $ScriptDir "Dockerfile.qa"
$ImageName = "softdomifood-qa:latest"
$ContainerName = "softdomifood-security-analysis"

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path (Join-Path $ProjectRoot "docker-compose.yml")) -and 
    -not (Test-Path (Join-Path $ProjectRoot "api"))) {
    Write-Host "❌ Error: Este script debe ejecutarse desde la raíz del repositorio" -ForegroundColor Red
    Write-Host "   Directorio actual: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "   Se esperaba encontrar: docker-compose.yml o directorio api/" -ForegroundColor Yellow
    exit 1
}

Write-Host "🛡️  Iniciando análisis de seguridad estática" -ForegroundColor Green
Write-Host "   Directorio del proyecto: $ProjectRoot" -ForegroundColor Cyan
Write-Host "   Dockerfile: $DockerfilePath" -ForegroundColor Cyan

# Cambiar al directorio raíz del proyecto
Set-Location $ProjectRoot

# Verificar que Docker está disponible
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Docker no está instalado o no está en PATH" -ForegroundColor Red
    exit 1
}

# Limpiar contenedor anterior si existe
$ExistingContainer = docker ps -aq -f "name=$ContainerName" 2>$null
if ($ExistingContainer) {
    Write-Host "🧹 Limpiando contenedor anterior..." -ForegroundColor Yellow
    docker rm -f $ContainerName 2>$null | Out-Null
}

# Construir imagen de testing (si no existe)
$ImageExists = docker images -q $ImageName 2>$null
if (-not $ImageExists) {
    Write-Host "📦 Construyendo imagen de testing..." -ForegroundColor Green
    try {
        docker build -f $DockerfilePath -t $ImageName $ProjectRoot
        if ($LASTEXITCODE -ne 0) {
            throw "Error al construir la imagen Docker"
        }
        Write-Host "✅ Imagen construida exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error al construir la imagen Docker" -ForegroundColor Red
        exit 1
    }
}

# Ejecutar análisis de seguridad
Write-Host "🔍 Ejecutando análisis de seguridad estática..." -ForegroundColor Green
Write-Host ""

try {
    docker run --rm `
        --name $ContainerName `
        -v "${ProjectRoot}:/app" `
        $ImageName `
        python /app/qa_automated/tests/security_analysis.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Análisis de seguridad completado exitosamente" -ForegroundColor Green
        exit 0
    } elseif ($LASTEXITCODE -eq 1) {
        Write-Host ""
        Write-Host "⚠️  Análisis completado: Se encontraron vulnerabilidades de seguridad" -ForegroundColor Yellow
        Write-Host "   Por favor, revisa los resultados arriba y corrige los problemas." -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host ""
        Write-Host "❌ Error al ejecutar análisis de seguridad" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "❌ Error al ejecutar análisis de seguridad: $_" -ForegroundColor Red
    exit 1
}

