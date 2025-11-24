"""
Script de migración para agregar el campo stock a la tabla products
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('api/.env')

DATABASE_URL = os.getenv('DATABASE_URL', '')

MIGRATION_SQL = """
-- Agregar columna stock a la tabla products si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'products' AND column_name = 'stock'
    ) THEN
        ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0 NOT NULL;
        -- Establecer stock inicial de 50 para productos existentes
        UPDATE products SET stock = 50 WHERE stock = 0;
        -- Crear índice para mejorar consultas por stock
        CREATE INDEX IF NOT EXISTS idx_products_stock ON products(stock);
        RAISE NOTICE 'Columna stock agregada exitosamente';
    ELSE
        RAISE NOTICE 'La columna stock ya existe';
    END IF;
END $$;
"""

async def run_migration():
    """Ejecutar migración para agregar campo stock"""
    if not DATABASE_URL:
        print('❌ DATABASE_URL no está configurada')
        return False
    
    try:
        print('🔍 Conectando a la base de datos...')
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            print('📊 Ejecutando migración: agregar campo stock...')
            await conn.execute(MIGRATION_SQL)
            print('✅ Migración completada exitosamente')
            
            # Verificar que la columna existe
            column_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'stock'
                );
            """)
            
            if column_exists:
                print('   ✅ Columna stock verificada')
                # Mostrar algunos productos con su stock
                products = await conn.fetch("SELECT name, stock FROM products LIMIT 5")
                if products:
                    print('   📦 Stock de productos:')
                    for p in products:
                        print(f'      - {p["name"]}: {p["stock"]} unidades')
            else:
                print('   ⚠️  La columna stock no se encontró después de la migración')
            
            return True
        finally:
            await conn.close()
    except Exception as e:
        print(f'❌ Error durante la migración: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    asyncio.run(run_migration())

