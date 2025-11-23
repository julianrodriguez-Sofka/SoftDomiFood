#!/bin/bash
# Script de ejecución de análisis de seguridad estática
# Propósito: Ejecutar análisis SAST con Bandit en contenedor Docker
# Uso: ./qa_automated/run_security_analysis.sh

set -e

# Variables de configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKERFILE_PATH="$SCRIPT_DIR/Dockerfile.qa"
IMAGE_NAME="softdomifood-qa:latest"
CONTAINER_NAME="softdomifood-security-analysis"

# Verificar que estamos en la raíz del proyecto
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ] && [ ! -d "$PROJECT_ROOT/api" ]; then
    echo "❌ Error: Este script debe ejecutarse desde la raíz del repositorio"
    echo "   Directorio actual: $(pwd)"
    echo "   Se esperaba encontrar: docker-compose.yml o directorio api/"
    exit 1
fi

echo "🛡️  Iniciando análisis de seguridad estática"
echo "   Directorio del proyecto: $PROJECT_ROOT"
echo "   Dockerfile: $DOCKERFILE_PATH"

# Cambiar al directorio raíz del proyecto
cd "$PROJECT_ROOT"

# Verificar que Docker está disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado o no está en PATH"
    exit 1
fi

# Limpiar contenedor anterior si existe
if docker ps -aq -f "name=$CONTAINER_NAME" | grep -q .; then
    echo "🧹 Limpiando contenedor anterior..."
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
fi

# Construir imagen de testing (si no existe)
if ! docker images -q "$IMAGE_NAME" | grep -q .; then
    echo "📦 Construyendo imagen de testing..."
    docker build -f "$DOCKERFILE_PATH" -t "$IMAGE_NAME" "$PROJECT_ROOT"
    if [ $? -ne 0 ]; then
        echo "❌ Error al construir la imagen Docker"
        exit 1
    fi
    echo "✅ Imagen construida exitosamente"
fi

# Ejecutar análisis de seguridad
echo "🔍 Ejecutando análisis de seguridad estática..."
echo ""

docker run --rm \
    --name "$CONTAINER_NAME" \
    -v "${PROJECT_ROOT}:/app" \
    "$IMAGE_NAME" \
    python /app/qa_automated/tests/security_analysis.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Análisis de seguridad completado exitosamente"
    exit 0
elif [ $EXIT_CODE -eq 1 ]; then
    echo ""
    echo "⚠️  Análisis completado: Se encontraron vulnerabilidades de seguridad"
    echo "   Por favor, revisa los resultados arriba y corrige los problemas."
    exit 1
else
    echo ""
    echo "❌ Error al ejecutar análisis de seguridad"
    exit $EXIT_CODE
fi

