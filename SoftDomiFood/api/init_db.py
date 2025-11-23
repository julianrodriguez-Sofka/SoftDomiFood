"""
Script de inicialización de la base de datos.
Crea todas las tablas necesarias si no existen.
"""
import asyncpg
import os
import asyncio
import sys
from typing import Optional

# Agregar el directorio actual al path para importar servicios
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Script SQL para crear todas las tablas
INIT_SQL = """
-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear enums
DO $$ BEGIN
    CREATE TYPE "UserRole" AS ENUM ('CUSTOMER', 'ADMIN', 'DELIVERY');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "ProductCategory" AS ENUM ('SALCHIPAPAS', 'BEBIDAS', 'ADICIONALES', 'COMBOS');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "OrderStatus" AS ENUM ('PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'ON_DELIVERY', 'DELIVERED', 'CANCELLED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "PaymentMethod" AS ENUM ('CASH', 'CARD');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Tabla users
CREATE TABLE IF NOT EXISTS "users" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    role "UserRole" DEFAULT 'CUSTOMER',
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
);

-- Tabla addresses
CREATE TABLE IF NOT EXISTS "addresses" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "userId" UUID NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    "zipCode" VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'Colombia',
    "isDefault" BOOLEAN DEFAULT false,
    instructions TEXT,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_address_user FOREIGN KEY ("userId") REFERENCES "users"(id) ON DELETE CASCADE
);

-- Tabla products
CREATE TABLE IF NOT EXISTS "products" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image VARCHAR(500),
    category "ProductCategory" NOT NULL,
    "isAvailable" BOOLEAN DEFAULT true,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
);

-- Tabla orders
CREATE TABLE IF NOT EXISTS "orders" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "userId" UUID NOT NULL,
    "addressId" UUID NOT NULL,
    status "OrderStatus" DEFAULT 'PENDING',
    total DECIMAL(10, 2) NOT NULL,
    "paymentMethod" "PaymentMethod" DEFAULT 'CASH',
    notes TEXT,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_order_user FOREIGN KEY ("userId") REFERENCES "users"(id),
    CONSTRAINT fk_order_address FOREIGN KEY ("addressId") REFERENCES "addresses"(id)
);

-- Tabla order_items
CREATE TABLE IF NOT EXISTS "order_items" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "orderId" UUID NOT NULL,
    "productId" UUID NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_order_item_order FOREIGN KEY ("orderId") REFERENCES "orders"(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_item_product FOREIGN KEY ("productId") REFERENCES "products"(id)
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_users_email ON "users"(email);
CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON "addresses"("userId");
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON "orders"("userId");
CREATE INDEX IF NOT EXISTS idx_orders_status ON "orders"(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON "order_items"("orderId");
CREATE INDEX IF NOT EXISTS idx_products_category ON "products"(category);
CREATE INDEX IF NOT EXISTS idx_products_is_available ON "products"("isAvailable");
"""

async def create_admin_user():
    """Crear usuario administrador por defecto"""
    if not DATABASE_URL:
        return False
    
    try:
        # Importar aquí para evitar problemas de importación circular
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Verificar si el usuario admin ya existe
            existing_admin = await conn.fetchrow(
                'SELECT id FROM users WHERE email = $1',
                'Admin@sofka.com'
            )
            
            if existing_admin:
                print("✅ Usuario admin ya existe")
                return True
            
            # Crear hash de la contraseña
            hashed_password = pwd_context.hash('Admin 123')
            
            # Insertar usuario admin
            await conn.execute("""
                INSERT INTO users (id, email, password, name, phone, role, "createdAt", "updatedAt")
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, NOW(), NOW())
            """, 'Admin@sofka.com', hashed_password, 'Administrador', None, 'ADMIN')
            
            print("✅ Usuario admin creado exitosamente")
            print("   Email: Admin@sofka.com")
            print("   Contraseña: Admin 123")
            return True
        finally:
            await conn.close()
    except Exception as e:
        print(f"⚠️  Error al crear usuario admin: {e}")
        import traceback
        traceback.print_exc()
        return False

async def init_database():
    """Inicializar la base de datos creando todas las tablas necesarias"""
    if not DATABASE_URL:
        print("⚠️  DATABASE_URL no está configurada")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Ejecutar script de inicialización
            await conn.execute(INIT_SQL)
            print("✅ Base de datos inicializada correctamente")
            
            # Verificar que todas las tablas se crearon
            tables_to_check = ['users', 'products', 'addresses', 'orders', 'order_items']
            for table in tables_to_check:
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = $1
                    );
                """, table)
                if exists:
                    print(f"   ✅ Tabla '{table}' creada/verificada")
                else:
                    print(f"   ⚠️  Tabla '{table}' NO existe después de la inicialización")
            
            # Crear usuario admin
            await create_admin_user()
            
            return True
        finally:
            await conn.close()
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_tables_exist() -> bool:
    """Verificar si las tablas principales existen"""
    if not DATABASE_URL:
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Verificar si existen todas las tablas necesarias
            tables_to_check = ['users', 'products', 'addresses', 'orders', 'order_items']
            for table in tables_to_check:
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = $1
                    );
                """, table)
                if not result:
                    print(f"⚠️  Tabla '{table}' no existe")
                    return False
            return True
        finally:
            await conn.close()
    except Exception as e:
        print(f"⚠️  Error verificando tablas: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(init_database())

