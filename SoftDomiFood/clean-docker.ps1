# Script para limpiar completamente Docker y reconstruir
Write-Host "Limpiando Docker..." -ForegroundColor Yellow

# Detener todos los contenedores
Write-Host "Deteniendo contenedores..." -ForegroundColor Cyan
docker-compose down -v

# Eliminar contenedores
Write-Host "Eliminando contenedores..." -ForegroundColor Cyan
docker container prune -f

# Limpiar build cache
Write-Host "Limpiando build cache..." -ForegroundColor Cyan
docker builder prune -af

# Limpiar sistema
Write-Host "Limpiando sistema Docker..." -ForegroundColor Cyan
docker system prune -af --volumes

Write-Host "Limpieza completada!" -ForegroundColor Green
Write-Host "Reconstruyendo imagenes..." -ForegroundColor Yellow
docker-compose build --no-cache

Write-Host "Proceso completado!" -ForegroundColor Green
Write-Host "Para iniciar los servicios, ejecuta: docker-compose up" -ForegroundColor Cyan
