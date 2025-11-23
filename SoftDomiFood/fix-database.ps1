# Script de Reparación de Base de Datos - SoftDomiFood
# Ejecutar desde el directorio raíz del proyecto

Write-Host "`n🔧 REPARACIÓN DE BASE DE DATOS - SOFTDOMIFOOD" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Paso 1: Limpiar todo
Write-Host "🛑 Paso 1/8: Deteniendo y limpiando contenedores y volúmenes..." -ForegroundColor Yellow
docker-compose down -v 2>$null
$volumeName = (docker volume ls --format "{{.Name}}" | Select-String "postgres_data")
if ($volumeName) {
    docker volume rm $volumeName -ErrorAction SilentlyContinue
    Write-Host "   ✅ Volúmenes eliminados" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No se encontraron volúmenes para eliminar" -ForegroundColor Gray
}

# Paso 2: Verificar .env
Write-Host "`n📝 Paso 2/8: Verificando archivo .env del backend..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match "softdomifood_db") {
        Write-Host "   ✅ .env configurado correctamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  .env puede tener configuración incorrecta" -ForegroundColor Red
        Write-Host "   📋 Verifica que DATABASE_URL apunte a softdomifood_db" -ForegroundColor Yellow
    }
} else {
    Write-Host "   📋 Creando .env desde env.example..." -ForegroundColor Yellow
    Copy-Item "backend\env.example" "backend\.env"
    Write-Host "   ✅ .env creado" -ForegroundColor Green
}

# Paso 3: Levantar postgres
Write-Host "`n🚀 Paso 3/8: Levantando contenedor de PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d postgres
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Postgres iniciado" -ForegroundColor Green
} else {
    Write-Host "   ❌ Error al iniciar postgres" -ForegroundColor Red
    exit 1
}

# Esperar a que postgres esté listo
Write-Host "   ⏳ Esperando a que PostgreSQL esté listo (20 segundos)..." -ForegroundColor Gray
Start-Sleep -Seconds 20

# Verificar que postgres esté saludable
$healthCheck = docker-compose exec -T postgres pg_isready -U softdomifood_user 2>&1
if ($healthCheck -match "accepting connections") {
    Write-Host "   ✅ PostgreSQL está listo" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  PostgreSQL puede no estar completamente listo" -ForegroundColor Yellow
}

# Paso 4: Verificar/Crear base de datos
Write-Host "`n🔍 Paso 4/8: Verificando existencia de la base de datos..." -ForegroundColor Yellow
$dbExists = docker-compose exec -T postgres psql -U softdomifood_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='softdomifood_db';" 2>&1
if ($dbExists -match "1") {
    Write-Host "   ✅ Base de datos 'softdomifood_db' existe" -ForegroundColor Green
} else {
    Write-Host "   📦 Creando base de datos 'softdomifood_db'..." -ForegroundColor Yellow
    docker-compose exec -T postgres psql -U softdomifood_user -d postgres -c "CREATE DATABASE softdomifood_db;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Base de datos creada" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Error al crear la base de datos" -ForegroundColor Red
        exit 1
    }
}

# Paso 5: Levantar backend
Write-Host "`n🚀 Paso 5/8: Levantando contenedor del backend..." -ForegroundColor Yellow
docker-compose up -d backend
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Backend iniciado" -ForegroundColor Green
} else {
    Write-Host "   ❌ Error al iniciar backend" -ForegroundColor Red
    exit 1
}

# Esperar a que el backend se inicialice
Write-Host "   ⏳ Esperando inicialización del backend (10 segundos)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Paso 6: Crear tablas con Prisma
Write-Host "`n📊 Paso 6/8: Creando tablas con Prisma db push..." -ForegroundColor Yellow
$prismaPush = docker-compose exec -T backend npx prisma db push --accept-data-loss 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Tablas creadas exitosamente" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Error al crear tablas. Intentando con force-reset..." -ForegroundColor Yellow
    docker-compose exec -T backend npx prisma db push --accept-data-loss --force-reset 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Tablas creadas con force-reset" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Error crítico al crear tablas" -ForegroundColor Red
        Write-Host "   📋 Revisa los logs: docker-compose logs backend" -ForegroundColor Yellow
        exit 1
    }
}

# Verificar tablas creadas
Write-Host "   🔍 Verificando tablas creadas..." -ForegroundColor Gray
$tables = docker-compose exec -T postgres psql -U softdomifood_user -d softdomifood_db -tAc "\dt" 2>&1
$tableCount = ($tables -split "`n" | Where-Object { $_ -match "public" }).Count
Write-Host "   ✅ Se encontraron $tableCount tablas" -ForegroundColor Green

# Paso 7: Ejecutar seed
Write-Host "`n🌱 Paso 7/8: Ejecutando script de seed..." -ForegroundColor Yellow
$seedOutput = docker-compose exec -T backend npm run prisma:seed 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Seed ejecutado exitosamente" -ForegroundColor Green
    # Mostrar resumen del seed
    $seedOutput | Select-String "Created|✅" | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  Error al ejecutar seed" -ForegroundColor Yellow
    Write-Host "   📋 Revisa los logs: docker-compose logs backend" -ForegroundColor Yellow
}

# Verificar datos
Write-Host "   🔍 Verificando datos insertados..." -ForegroundColor Gray
$productCount = docker-compose exec -T postgres psql -U softdomifood_user -d softdomifood_db -tAc "SELECT COUNT(*) FROM products;" 2>&1
$userCount = docker-compose exec -T postgres psql -U softdomifood_user -d softdomifood_db -tAc "SELECT COUNT(*) FROM users;" 2>&1
Write-Host "   📦 Productos: $productCount" -ForegroundColor Cyan
Write-Host "   👤 Usuarios: $userCount" -ForegroundColor Cyan

# Paso 8: Levantar frontend
Write-Host "`n🎨 Paso 8/8: Levantando contenedor del frontend..." -ForegroundColor Yellow
docker-compose up -d frontend
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Frontend iniciado" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Error al iniciar frontend (puede continuar)" -ForegroundColor Yellow
}

# Resumen final
Write-Host "`n" -NoNewline
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ REPARACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "==========================================`n" -ForegroundColor Cyan

Write-Host "📊 Estado de los servicios:" -ForegroundColor Yellow
docker-compose ps

Write-Host "`n📝 Comandos útiles:" -ForegroundColor Yellow
Write-Host "   Ver logs:           docker-compose logs -f" -ForegroundColor Gray
Write-Host "   Ver logs postgres:  docker-compose logs postgres" -ForegroundColor Gray
Write-Host "   Ver logs backend:   docker-compose logs backend" -ForegroundColor Gray
Write-Host "   Conectar a BD:      docker-compose exec postgres psql -U softdomifood_user -d softdomifood_db" -ForegroundColor Gray
Write-Host "   Listar tablas:      docker-compose exec postgres psql -U softdomifood_user -d softdomifood_db -c '\dt'" -ForegroundColor Gray

Write-Host "`n🔗 URLs:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:5000/api" -ForegroundColor Cyan
Write-Host "   Health:   http://localhost:5000/api/health" -ForegroundColor Cyan

Write-Host "`n👤 Usuario Admin:" -ForegroundColor Yellow
Write-Host "   Email:    admin@softdomifood.com" -ForegroundColor Cyan
Write-Host "   Password: admin123" -ForegroundColor Cyan

Write-Host "`n" -NoNewline

