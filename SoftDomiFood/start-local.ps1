# Script para iniciar el proyecto localmente (sin Docker para frontend, backend y worker)

Write-Host "🚀 Iniciando proyecto SoftDomiFood (modo local)" -ForegroundColor Green
Write-Host ""

# Verificar que Docker Desktop esté corriendo
Write-Host "📦 Verificando Docker..." -ForegroundColor Yellow
docker ps > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Desktop no está corriendo. Por favor inicia Docker Desktop primero." -ForegroundColor Red
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Iniciar PostgreSQL y RabbitMQ en Docker
Write-Host "🐘 Iniciando PostgreSQL y RabbitMQ en Docker..." -ForegroundColor Yellow
docker-compose up -d postgres rabbitmq

# Esperar a que los servicios estén listos
Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "✅ PostgreSQL y RabbitMQ iniciados" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Instrucciones:" -ForegroundColor Cyan
Write-Host "1. Abre 3 terminales adicionales en esta carpeta" -ForegroundColor White
Write-Host "2. Terminal 1 - Backend API:" -ForegroundColor White
Write-Host "   cd api" -ForegroundColor Gray
Write-Host "   python -m venv venv" -ForegroundColor Gray
Write-Host "   .\\venv\\Scripts\\Activate.ps1" -ForegroundColor Gray
Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   Copy-Item .env.local .env" -ForegroundColor Gray
Write-Host "   uvicorn main:app --reload --host 0.0.0.0 --port 5000" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Terminal 2 - Worker:" -ForegroundColor White
Write-Host "   cd worker" -ForegroundColor Gray
Write-Host "   Copy-Item .env.local .env" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Terminal 3 - Frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:5000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:5000/docs" -ForegroundColor White
Write-Host "   RabbitMQ: http://localhost:15672 (admin/admin123)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Presiona Ctrl+C en cada terminal para detener los servicios" -ForegroundColor Yellow
Write-Host ""
