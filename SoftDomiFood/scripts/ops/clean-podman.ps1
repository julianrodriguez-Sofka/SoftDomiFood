# Script para limpiar completamente el proyecto SoftDomiFood en Podman

Write-Host "🧹 Limpieza completa de SoftDomiFood en Podman" -ForegroundColor Yellow
Write-Host ""

# Advertencia
Write-Host "⚠️  ADVERTENCIA: Esta operación eliminará:" -ForegroundColor Red
Write-Host "   - Todos los contenedores del proyecto" -ForegroundColor Yellow
Write-Host "   - Todos los volúmenes (incluyendo datos de la base de datos)" -ForegroundColor Yellow
Write-Host "   - Todas las imágenes construidas del proyecto" -ForegroundColor Yellow
Write-Host "   - La red del proyecto" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "¿Estás seguro? Escribe 'SI' para continuar"

if ($confirmation -ne "SI") {
    Write-Host "❌ Operación cancelada" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🛑 Deteniendo y eliminando contenedores..." -ForegroundColor Yellow

# Detener y eliminar contenedores
$containers = @(
    "softdomifood-admin-frontend",
    "softdomifood-frontend",
    "softdomifood-worker",
    "softdomifood-api",
    "softdomifood-rabbitmq",
    "softdomifood-db"
)

foreach ($container in $containers) {
    Write-Host "Deteniendo y eliminando $container..." -ForegroundColor Gray
    podman stop $container 2>$null | Out-Null
    podman rm $container 2>$null | Out-Null
}

Write-Host ""
Write-Host "🗑️  Eliminando volúmenes..." -ForegroundColor Yellow

# Eliminar volúmenes del proyecto
$volumes = podman volume ls --format "{{.Name}}" | Select-String "softdomifood"
if ($volumes) {
    foreach ($volume in $volumes) {
        Write-Host "Eliminando volumen: $volume" -ForegroundColor Gray
        podman volume rm $volume 2>$null
    }
}

Write-Host ""
Write-Host "🖼️  Eliminando imágenes..." -ForegroundColor Yellow

# Eliminar imágenes del proyecto
$images = @(
    "softdomifood-admin-frontend",
    "softdomifood-frontend",
    "softdomifood-worker",
    "softdomifood-api"
)

foreach ($image in $images) {
    $imageExists = podman images --format "{{.Repository}}" | Select-String $image
    if ($imageExists) {
        Write-Host "Eliminando imagen: $image" -ForegroundColor Gray
        podman rmi $image 2>$null
    }
}

Write-Host ""
Write-Host "🌐 Eliminando red..." -ForegroundColor Yellow
podman network rm softdomifood-network 2>$null

Write-Host ""
Write-Host "🧼 Limpieza adicional..." -ForegroundColor Yellow

# Limpiar contenedores detenidos
podman container prune -f 2>$null

# Limpiar imágenes sin usar
podman image prune -f 2>$null

# Limpiar volúmenes sin usar
podman volume prune -f 2>$null

# Limpiar redes sin usar
podman network prune -f 2>$null

Write-Host ""
Write-Host "✅ Limpieza completa finalizada" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Estado actual:" -ForegroundColor Cyan
Write-Host ""

# Mostrar estado
Write-Host "Contenedores restantes del proyecto:" -ForegroundColor White
$remainingContainers = podman ps -a --format "{{.Names}}" | Select-String "softdomifood"
if ($remainingContainers) {
    $remainingContainers
} else {
    Write-Host "   Ninguno" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Volúmenes restantes del proyecto:" -ForegroundColor White
$remainingVolumes = podman volume ls --format "{{.Name}}" | Select-String "softdomifood"
if ($remainingVolumes) {
    $remainingVolumes
} else {
    Write-Host "   Ninguno" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Imágenes restantes del proyecto:" -ForegroundColor White
$remainingImages = podman images --format "{{.Repository}}" | Select-String "softdomifood"
if ($remainingImages) {
    $remainingImages
} else {
    Write-Host "   Ninguno" -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 Para iniciar nuevamente el proyecto, usa: .\start-podman.ps1" -ForegroundColor Cyan
Write-Host ""
