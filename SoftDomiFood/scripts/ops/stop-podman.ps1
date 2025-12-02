# Script para detener el proyecto SoftDomiFood usando Podman

Write-Host "🛑 Deteniendo proyecto SoftDomiFood..." -ForegroundColor Yellow
Write-Host ""

# Detener contenedores en orden inverso al inicio
$containers = @(
    "softdomifood-admin-frontend",
    "softdomifood-frontend",
    "softdomifood-worker",
    "softdomifood-api",
    "softdomifood-rabbitmq",
    "softdomifood-db"
)

foreach ($container in $containers) {
    Write-Host "Deteniendo $container..." -ForegroundColor Gray
    podman stop $container 2>$null | Out-Null
}

Write-Host ""
Write-Host "✅ Servicios detenidos exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Los contenedores y volúmenes de datos se mantienen intactos" -ForegroundColor Cyan
Write-Host "   Para eliminar todo (contenedores y volúmenes), usa: .\clean-podman.ps1" -ForegroundColor Gray
Write-Host "   Para reiniciar, usa: .\start-podman.ps1" -ForegroundColor Gray
Write-Host ""
