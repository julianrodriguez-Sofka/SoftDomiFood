"""
Script para verificar si la tabla addresses existe en la base de datos
"""
import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('api/.env')

DATABASE_URL = os.getenv('DATABASE_URL', '')

async def verify_addresses_table():
    if not DATABASE_URL:
        print('❌ DATABASE_URL no está configurada')
        print('💡 Asegúrate de tener un archivo .env en la carpeta api/')
        sys.exit(1)
    
    try:
        print(f'🔍 Conectando a la base de datos...')
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Verificar si la tabla existe
            table_exists = await conn.fetchval('''
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'addresses'
                );
            ''')
            
            if table_exists:
                print('✅ La tabla addresses ya existe')
                
                # Verificar estructura
                columns = await conn.fetch('''
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'addresses'
                    ORDER BY ordinal_position;
                ''')
                
                print(f'📋 Columnas encontradas: {len(columns)}')
                for col in columns:
                    nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                    print(f'   - {col["column_name"]}: {col["data_type"]} ({nullable})')
                
                # Contar registros
                count = await conn.fetchval('SELECT COUNT(*) FROM addresses')
                print(f'📊 Registros en la tabla: {count}')
            else:
                print('⚠️  La tabla addresses NO existe')
                print('💡 Se creará automáticamente al iniciar el servidor API')
                print('   (El servidor ejecuta init_db.py en el startup)')
                
        finally:
            await conn.close()
            print('✅ Conexión cerrada')
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(verify_addresses_table())

