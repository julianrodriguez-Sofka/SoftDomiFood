# Script de ejecución de pruebas automatizadas (PowerShell)
# Propósito: Ejecutar tests en contenedor Docker desde la raíz del repositorio
# Uso: .\qa_automated\run_qa.ps1 [opciones de pytest]

$ErrorActionPreference = "Stop"

# Variables de configuración
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$DockerfilePath = Join-Path $ScriptDir "Dockerfile.qa"
$ImageName = "softdomifood-qa:latest"
$ContainerName = "softdomifood-qa-runner"

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path (Join-Path $ProjectRoot "docker-compose.yml")) -and 
    -not (Test-Path (Join-Path $ProjectRoot "api"))) {
    Write-Host "[ERROR] Este script debe ejecutarse desde la raiz del repositorio" -ForegroundColor Red
    Write-Host "   Directorio actual: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "   Se esperaba encontrar: docker-compose.yml o directorio api/" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Iniciando entorno de testing automatizado" -ForegroundColor Green
Write-Host "   Directorio del proyecto: $ProjectRoot" -ForegroundColor Cyan
Write-Host "   Dockerfile: $DockerfilePath" -ForegroundColor Cyan

# Cambiar al directorio raíz del proyecto
Set-Location $ProjectRoot

# Verificar que Docker está disponible
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker no esta instalado o no esta en PATH" -ForegroundColor Red
    exit 1
}

# Limpiar contenedor anterior si existe
$ExistingContainer = docker ps -aq -f "name=$ContainerName" 2>$null
if ($ExistingContainer) {
    Write-Host "[INFO] Limpiando contenedor anterior..." -ForegroundColor Yellow
    docker rm -f $ContainerName 2>$null | Out-Null
}

# Construir imagen de testing
Write-Host "[INFO] Construyendo imagen de testing..." -ForegroundColor Green
Write-Host "   Contexto: $ProjectRoot" -ForegroundColor Cyan
Write-Host "   Dockerfile: $DockerfilePath" -ForegroundColor Cyan

try {
    docker build -f $DockerfilePath -t $ImageName $ProjectRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Error al construir la imagen Docker"
    }
} catch {
    Write-Host "[ERROR] Error al construir la imagen Docker" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Imagen construida exitosamente" -ForegroundColor Green

# Obtener argumentos adicionales de pytest (si se proporcionan)
$PytestArgs = $args -join " "

# Si no se proporcionan argumentos, usar configuración por defecto
if ([string]::IsNullOrWhiteSpace($PytestArgs)) {
    $PytestArgs = "-v --tb=short --cov=/app/api --cov-report=term-missing"
}

# Ejecutar contenedor con pruebas
Write-Host "[INFO] Ejecutando pruebas..." -ForegroundColor Green
Write-Host "   Argumentos de pytest: $PytestArgs" -ForegroundColor Cyan

try {
    # Usar sh -c para ejecutar el comando completo con argumentos
    $Command = "pytest /app/qa_automated/ $PytestArgs"
    
    docker run --rm `
        --name $ContainerName `
        -v "${ProjectRoot}:/app" `
        $ImageName `
        sh -c $Command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Pruebas completadas exitosamente" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[ERROR] Pruebas fallaron con codigo de salida: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "Error al ejecutar pruebas: $_" -ForegroundColor Red
    exit 1
}

