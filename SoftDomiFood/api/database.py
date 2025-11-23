from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Obtener DATABASE_URL del entorno
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Si no hay DATABASE_URL, usar SQLite en memoria (útil para tests)
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
# Si es PostgreSQL, convertir a asyncpg
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Crear engine (funciona con PostgreSQL asyncpg o SQLite aiosqlite)
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

