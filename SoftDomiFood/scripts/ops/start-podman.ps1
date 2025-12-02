# Script para iniciar el proyecto SoftDomiFood usando Podman

Write-Host "Iniciando proyecto SoftDomiFood con Podman" -ForegroundColor Green
Write-Host ""

Write-Host "Verificando Podman..." -ForegroundColor Yellow
try {
    $podmanVersion = podman --version
    Write-Host "OK: $podmanVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Podman no esta instalado." -ForegroundColor Red
    exit 1
}

Write-Host "Limpiando contenedores previos..." -ForegroundColor Yellow
podman stop softdomifood-admin-frontend softdomifood-frontend softdomifood-worker softdomifood-api softdomifood-rabbitmq softdomifood-db 2>$null | Out-Null
podman rm softdomifood-admin-frontend softdomifood-frontend softdomifood-worker softdomifood-api softdomifood-rabbitmq softdomifood-db 2>$null | Out-Null

Write-Host "Creando red..." -ForegroundColor Yellow
podman network rm softdomifood-network 2>$null | Out-Null
podman network create softdomifood-network

Write-Host "Creando volumenes..." -ForegroundColor Yellow
podman volume create softdomifood_postgres_data 2>$null | Out-Null
podman volume create softdomifood_rabbitmq_data 2>$null | Out-Null

Write-Host "Iniciando PostgreSQL..." -ForegroundColor Yellow
podman run -d --name softdomifood-db --network softdomifood-network -e POSTGRES_USER=softdomifood_user -e POSTGRES_PASSWORD=softdomifood_pass -e POSTGRES_DB=softdomifood_db -p 5432:5432 -v softdomifood_postgres_data:/var/lib/postgresql/data postgres:15-alpine

Write-Host "Iniciando RabbitMQ..." -ForegroundColor Yellow
podman run -d --name softdomifood-rabbitmq --network softdomifood-network -e RABBITMQ_DEFAULT_USER=admin -e RABBITMQ_DEFAULT_PASS=admin123 -p 5672:5672 -p 15672:15672 -v softdomifood_rabbitmq_data:/var/lib/rabbitmq rabbitmq:3-management-alpine

Write-Host "Esperando servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "Construyendo API..." -ForegroundColor Yellow
podman build -t softdomifood-api ./api

Write-Host "Iniciando API..." -ForegroundColor Yellow
podman run -d --name softdomifood-api --network softdomifood-network -e DATABASE_URL=postgresql://softdomifood_user:softdomifood_pass@softdomifood-db:5432/softdomifood_db -e RABBITMQ_URL=amqp://admin:admin123@softdomifood-rabbitmq:5672/ -e JWT_SECRET=your-super-secret-jwt-key-change-in-production -e JWT_EXPIRES_IN=7d -e PORT=5000 -e "CORS_ORIGIN=http://localhost:3000,http://localhost:3001" -p 5000:5000 -v ${PWD}/api:/app:z softdomifood-api

Write-Host "Construyendo Worker..." -ForegroundColor Yellow
podman build -t softdomifood-worker ./worker

Write-Host "Iniciando Worker..." -ForegroundColor Yellow
podman run -d --name softdomifood-worker --network softdomifood-network -e DATABASE_URL=postgresql://softdomifood_user:softdomifood_pass@softdomifood-db:5432/softdomifood_db -e RABBITMQ_URL=amqp://admin:admin123@softdomifood-rabbitmq:5672/ -v ${PWD}/worker:/app:z softdomifood-worker

Write-Host "Construyendo Frontend..." -ForegroundColor Yellow
podman build -t softdomifood-frontend ./frontend

Write-Host "Iniciando Frontend..." -ForegroundColor Yellow
podman run -d --name softdomifood-frontend --network softdomifood-network -e VITE_API_URL=http://localhost:5000/api -p 3000:3000 -v ${PWD}/frontend:/app:z softdomifood-frontend

Write-Host "Construyendo Admin Frontend..." -ForegroundColor Yellow
podman build -t softdomifood-admin-frontend ./admin-frontend

Write-Host "Iniciando Admin Frontend..." -ForegroundColor Yellow
podman run -d --name softdomifood-admin-frontend --network softdomifood-network -e VITE_API_URL=http://localhost:5000/api -p 3001:3001 -v ${PWD}/admin-frontend:/app:z softdomifood-admin-frontend

Write-Host ""
Write-Host "COMPLETADO!" -ForegroundColor Green
Write-Host "Frontend Cliente: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Frontend Admin: http://localhost:3001" -ForegroundColor Cyan
Write-Host "API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "RabbitMQ: http://localhost:15672" -ForegroundColor Cyan
