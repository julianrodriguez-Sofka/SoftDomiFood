"""
Ejemplo de test para la API FastAPI
Este archivo sirve como plantilla para crear tus propios tests.

Para ejecutar este test:
    ./qa_automated/run_qa.sh tests/example_test.py
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Importar la aplicación FastAPI
from api.main import app


class TestHealthEndpoint:
    """Tests para el endpoint de health check"""
    
    def test_health_endpoint(self):
        """Test básico del endpoint de health"""
        client = TestClient(app)
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data


class TestRootEndpoint:
    """Tests para el endpoint raíz"""
    
    def test_root_endpoint(self):
        """Test del endpoint raíz"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


# Ejemplo de test asíncrono (requiere pytest-asyncio)
@pytest.mark.asyncio
class TestAsyncExample:
    """Ejemplo de tests asíncronos"""
    
    async def test_async_example(self):
        """Ejemplo de test asíncrono con AsyncClient"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/health")
            assert response.status_code == 200


# Ejemplo de test con marcadores
@pytest.mark.smoke
def test_smoke_test():
    """Test marcado como smoke test"""
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200

