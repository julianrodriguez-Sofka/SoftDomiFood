# Script para detener los servicios de Docker

Write-Host "🛑 Deteniendo PostgreSQL y RabbitMQ..." -ForegroundColor Yellow
docker-compose stop postgres rabbitmq

Write-Host "✅ Servicios detenidos" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Recuerda detener manualmente (Ctrl+C) las terminales del backend, worker y frontend" -ForegroundColor Yellow
