#!/bin/bash

# Script de ejecución de pruebas automatizadas
# Propósito: Ejecutar tests en contenedor Docker desde la raíz del repositorio
# Uso: ./qa_automated/run_qa.sh [opciones de pytest]

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables de configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKERFILE_PATH="$SCRIPT_DIR/Dockerfile.qa"
IMAGE_NAME="softdomifood-qa:latest"
CONTAINER_NAME="softdomifood-qa-runner"

# Verificar que estamos en la raíz del proyecto
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ] && [ ! -d "$PROJECT_ROOT/api" ]; then
    echo -e "${RED}❌ Error: Este script debe ejecutarse desde la raíz del repositorio${NC}"
    echo "   Directorio actual: $(pwd)"
    echo "   Se esperaba encontrar: docker-compose.yml o directorio api/"
    exit 1
fi

echo -e "${GREEN}🚀 Iniciando entorno de testing automatizado${NC}"
echo "   Directorio del proyecto: $PROJECT_ROOT"
echo "   Dockerfile: $DOCKERFILE_PATH"

# Cambiar al directorio raíz del proyecto
cd "$PROJECT_ROOT"

# Verificar que Docker está disponible
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker no está instalado o no está en PATH${NC}"
    exit 1
fi

# Limpiar contenedor anterior si existe
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo -e "${YELLOW}🧹 Limpiando contenedor anterior...${NC}"
    docker rm -f $CONTAINER_NAME > /dev/null 2>&1 || true
fi

# Construir imagen de testing
echo -e "${GREEN}📦 Construyendo imagen de testing...${NC}"
echo "   Contexto: $PROJECT_ROOT"
echo "   Dockerfile: $DOCKERFILE_PATH"

if ! docker build \
    -f "$DOCKERFILE_PATH" \
    -t "$IMAGE_NAME" \
    "$PROJECT_ROOT"; then
    echo -e "${RED}❌ Error al construir la imagen Docker${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"

# Obtener argumentos adicionales de pytest (si se proporcionan)
PYTEST_ARGS="${@:-}"

# Si no se proporcionan argumentos, usar configuración por defecto
if [ -z "$PYTEST_ARGS" ]; then
    PYTEST_ARGS="-v --tb=short --cov=/app/api --cov-report=term-missing"
fi

# Ejecutar contenedor con pruebas
echo -e "${GREEN}🧪 Ejecutando pruebas...${NC}"
echo "   Argumentos de pytest: $PYTEST_ARGS"

# Ejecutar contenedor y capturar código de salida
if docker run --rm \
    --name "$CONTAINER_NAME" \
    -v "$PROJECT_ROOT:/app" \
    "$IMAGE_NAME" \
    pytest /app/qa_automated/ $PYTEST_ARGS; then
    echo -e "${GREEN}✅ Pruebas completadas exitosamente${NC}"
    exit 0
else
    EXIT_CODE=$?
    echo -e "${RED}❌ Pruebas fallaron con código de salida: $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi

