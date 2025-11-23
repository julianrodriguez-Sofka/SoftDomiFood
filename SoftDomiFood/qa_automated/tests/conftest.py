"""
Configuración de pytest para tests funcionales
===============================================

Este archivo configura el entorno de testing ANTES de que se importen
los módulos de la aplicación, solucionando el problema de DATABASE_URL.

Solución 3: Configurar entorno en conftest.py
"""

import os
import sys
from pathlib import Path

# Configurar variables de entorno ANTES de importar cualquier módulo de la app
# Esto debe hacerse antes de que pytest cargue los módulos de test

# Obtener rutas del proyecto
project_root = Path(__file__).parent.parent.parent
api_dir = project_root / "api"

# Agregar al path si no está
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS PARA TESTS
# ============================================================================

# Configurar DATABASE_URL para usar SQLite en memoria (no requiere PostgreSQL)
# SQLite en memoria es perfecto para tests: rápido y aislado
if not os.getenv("DATABASE_URL"):
    # Usar SQLite en memoria para tests
    # aiosqlite es necesario para async SQLite
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Configurar JWT_SECRET si no existe (necesario para tests de autenticación)
if not os.getenv("JWT_SECRET"):
    os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"

# ============================================================================
# FIXTURES GLOBALES
# ============================================================================

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Importar app DESPUÉS de configurar las variables de entorno
# Esto asegura que database.py reciba DATABASE_URL configurada
from api.main import app


@pytest.fixture(scope="session")
def test_client():
    """
    Cliente de prueba síncrono para toda la sesión de tests
    """
    return TestClient(app)


@pytest.fixture
async def async_client():
    """
    Cliente de prueba asíncrono
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# CONFIGURACIÓN ADICIONAL
# ============================================================================

def pytest_configure(config):
    """
    Hook de pytest que se ejecuta antes de cargar los módulos de test
    Aquí podemos hacer configuraciones adicionales
    """
    # Verificar que DATABASE_URL está configurada
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("⚠️  WARNING: DATABASE_URL no configurada, usando SQLite en memoria")
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    
    print(f"✅ DATABASE_URL configurada para tests: {os.getenv('DATABASE_URL')[:50]}...")


def pytest_collection_modifyitems(config, items):
    """
    Hook que se ejecuta después de recopilar los tests
    Puede usarse para modificar o marcar tests
    """
    pass

