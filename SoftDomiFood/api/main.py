from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import engine, Base, get_db
from routers import auth, products, orders, admin, addresses
from init_db import init_database, check_tables_exist, create_admin_user
from services.rabbitmq import get_channel, close_connection

load_dotenv()

# Crear tablas al iniciar (solo para desarrollo)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Inicializando base de datos...")
    try:
        # Verificar si las tablas existen
        tables_exist = await check_tables_exist()
        if not tables_exist:
            print("📊 Creando tablas en la base de datos...")
            success = await init_database()
            if success:
                print("✅ Base de datos inicializada correctamente")
            else:
                print("⚠️  Advertencia: No se pudieron crear todas las tablas")
                # Intentar forzar creación de nuevo
                print("🔄 Intentando forzar creación de tablas...")
                await init_database()
        else:
            print("✅ Las tablas ya existen en la base de datos")
            # Asegurar que el usuario admin existe
            await create_admin_user()
    except Exception as e:
        print(f"⚠️  Error al verificar/inicializar base de datos: {e}")
        import traceback
        traceback.print_exc()
        print("   Intentando forzar creación de tablas...")
        try:
            await init_database()
        except Exception as e2:
            print(f"   ❌ Error al forzar creación: {e2}")
            print("   Continuando de todas formas...")
    
    # Inicializar conexión RabbitMQ
    print("🐰 Inicializando conexión RabbitMQ...")
    try:
        await get_channel()
        print("✅ Conexión RabbitMQ inicializada correctamente")
    except Exception as e:
        print(f"⚠️  Error al inicializar RabbitMQ: {e}")
        print("   La aplicación continuará, pero los mensajes no se publicarán")
        import traceback
        traceback.print_exc()
    
    yield
    # Shutdown
    print("🛑 Cerrando conexiones...")
    try:
        await close_connection()
    except Exception as e:
        print(f"⚠️  Error al cerrar conexión RabbitMQ: {e}")

app = FastAPI(
    title="SoftDomiFood API",
    description="API Producer para sistema de pedidos",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    # Permitir ambos frontends: cliente (3000) y admin (3001)
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(addresses.router, prefix="/api", tags=["addresses"])

@app.get("/")
async def root():
    return {
        "message": "SoftDomiFood API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "message": "SoftDomiFood API is running",
        "service": "producer"
    }

if __name__ == "__main__":
    import uvicorn
    # Configuración segura: usar variables de entorno con valores por defecto seguros
    # En desarrollo, usar 127.0.0.1 (solo localhost) es más seguro
    # En producción con Docker, configurar HOST=0.0.0.0 en docker-compose.yml
    host = os.getenv("HOST", "127.0.0.1")  # Default seguro: solo localhost
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run(app, host=host, port=port)

