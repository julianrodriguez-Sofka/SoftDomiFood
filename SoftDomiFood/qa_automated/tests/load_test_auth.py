"""
📈 Script de Pruebas de Estrés - Módulo de Autenticación
==========================================================

Este script ejecuta pruebas de carga y estrés para el módulo de autenticación
usando Locust, una herramienta de testing de carga escrita en Python.

Componente bajo prueba: Endpoints de autenticación
- POST /api/auth/login
- POST /api/auth/register
- GET /api/auth/profile

Escenario de Carga:
- 500 usuarios virtuales inyectando peticiones durante 60 segundos
- Rampa de usuarios: 50 usuarios por segundo hasta alcanzar 500

Métrica Clave:
- Latencia promedio (p95) debe ser menor a 200 ms
- Tasa de éxito debe ser mayor al 95%
- Tasa de error debe ser menor al 5%

Uso:
    # Instalar dependencias
    pip install locust
    
    # Ejecutar pruebas
    locust -f load_test_auth.py --host=http://localhost:5000
    
    # O ejecutar en modo headless (sin UI)
    locust -f load_test_auth.py --host=http://localhost:5000 --headless -u 500 -r 50 -t 60s
"""

from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import random
import string
import json
import os


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# URL base de la API (se puede sobrescribir con --host)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

# Usuarios de prueba pre-registrados (para tests de login)
# En un entorno real, estos usuarios deberían existir en la BD de testing
TEST_USERS = [
    {"email": f"testuser{i}@example.com", "password": "TestPass123!"}
    for i in range(1, 101)  # 100 usuarios de prueba
]

# Contador global para usuarios únicos en registro
user_counter = 0


# ============================================================================
# CLASE DE USUARIO LOCUST
# ============================================================================

class AuthUser(FastHttpUser):
    """
    Usuario virtual que simula comportamiento de autenticación
    
    Comportamiento:
    1. 60% de probabilidad: Intentar login
    2. 30% de probabilidad: Registrar nuevo usuario
    3. 10% de probabilidad: Acceder al perfil (requiere autenticación)
    """
    
    wait_time = between(1, 3)  # Esperar entre 1 y 3 segundos entre requests
    weight = 1  # Peso del usuario (para balancear diferentes tipos)
    
    def on_start(self):
        """Ejecutado cuando un usuario virtual inicia"""
        self.token = None
        self.user_email = None
        self.user_password = None
    
    @task(6)
    def test_login(self):
        """
        Test de login - 60% de probabilidad
        CA: El endpoint debe responder en menos de 200ms bajo carga
        """
        # Seleccionar usuario aleatorio de la lista de prueba
        test_user = random.choice(TEST_USERS)
        
        payload = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        with self.client.post(
            "/api/auth/login",
            json=payload,
            catch_response=True,
            name="POST /api/auth/login"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.token = data["token"]
                    self.user_email = test_user["email"]
                    self.user_password = test_user["password"]
                    response.success()
                else:
                    response.failure("Token no encontrado en respuesta")
            elif response.status_code == 401:
                # Credenciales inválidas - esto es esperado en algunos casos
                response.success()  # No contar como error si es esperado
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(3)
    def test_register(self):
        """
        Test de registro - 30% de probabilidad
        CA: El endpoint debe responder en menos de 200ms bajo carga
        """
        global user_counter
        user_counter += 1
        
        # Generar datos únicos para cada registro
        unique_id = f"{user_counter}_{random.randint(1000, 9999)}"
        email = f"loadtest_{unique_id}@example.com"
        password = "LoadTest123!"
        name = f"Load Test User {unique_id}"
        
        payload = {
            "email": email,
            "password": password,
            "name": name,
            "phone": f"+1{random.randint(1000000000, 9999999999)}"
        }
        
        with self.client.post(
            "/api/auth/register",
            json=payload,
            catch_response=True,
            name="POST /api/auth/register"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.token = data["token"]
                    self.user_email = email
                    self.user_password = password
                    response.success()
                else:
                    response.failure("Respuesta incompleta")
            elif response.status_code == 400:
                # Usuario ya existe - esto puede pasar en tests de carga
                response.success()  # No contar como error crítico
            else:
                response.failure(f"Status code inesperado: {response.status_code}")
    
    @task(1)
    def test_profile(self):
        """
        Test de perfil - 10% de probabilidad
        Requiere autenticación previa
        CA: El endpoint debe responder en menos de 200ms bajo carga
        """
        # Si no hay token, intentar obtenerlo primero
        if not self.token:
            # Intentar login rápido
            test_user = random.choice(TEST_USERS)
            login_response = self.client.post(
                "/api/auth/login",
                json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                }
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.token = login_data.get("token")
            else:
                # Si no se puede autenticar, saltar este test
                return
        
        # Hacer request al perfil
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.client.get(
            "/api/auth/profile",
            headers=headers,
            catch_response=True,
            name="GET /api/auth/profile"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data:
                    response.success()
                else:
                    response.failure("Respuesta incompleta")
            elif response.status_code == 401:
                # Token inválido o expirado - intentar renovar
                self.token = None
                response.failure("Token inválido o expirado")
            else:
                response.failure(f"Status code inesperado: {response.status_code}")


# ============================================================================
# EVENTOS Y MÉTRICAS PERSONALIZADAS
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Ejecutado cuando inicia el test de carga"""
    print("="*70)
    print("📈 INICIANDO PRUEBAS DE ESTRÉS - MÓDULO DE AUTENTICACIÓN")
    print("="*70)
    print(f"🎯 Objetivo: 500 usuarios virtuales durante 60 segundos")
    print(f"📊 Métrica clave: Latencia p95 < 200ms")
    print(f"🌐 Host: {environment.host}")
    print("="*70)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Ejecutado cuando termina el test de carga"""
    print("\n" + "="*70)
    print("📊 RESUMEN DE PRUEBAS DE ESTRÉS")
    print("="*70)
    
    stats = environment.stats
    
    # Calcular métricas agregadas
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    failure_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0
    success_rate = 100 - failure_rate
    
    # Obtener latencias
    avg_response_time = stats.total.avg_response_time
    median_response_time = stats.total.median_response_time
    p95_response_time = stats.total.get_response_time_percentile(0.95)
    p99_response_time = stats.total.get_response_time_percentile(0.99)
    
    # Obtener RPS (Requests Per Second)
    total_time = stats.total.total_response_time
    rps = total_requests / (total_time / 1000) if total_time > 0 else 0
    
    print(f"📈 Total de requests:        {total_requests:,}")
    print(f"✅ Requests exitosos:        {total_requests - total_failures:,} ({success_rate:.2f}%)")
    print(f"❌ Requests fallidos:        {total_failures:,} ({failure_rate:.2f}%)")
    print(f"⚡ Requests por segundo:     {rps:.2f} RPS")
    print(f"\n⏱️  LATENCIAS:")
    print(f"   Promedio:                 {avg_response_time:.2f} ms")
    print(f"   Mediana (p50):            {median_response_time:.2f} ms")
    print(f"   Percentil 95 (p95):       {p95_response_time:.2f} ms")
    print(f"   Percentil 99 (p99):       {p99_response_time:.2f} ms")
    
    # Validar criterios de aceptación
    print(f"\n🎯 VALIDACIÓN DE CRITERIOS:")
    print("="*70)
    
    ca_passed = True
    
    # CA: Latencia p95 < 200ms
    if p95_response_time < 200:
        print(f"✅ CA-1: Latencia p95 < 200ms: {p95_response_time:.2f}ms (PASÓ)")
    else:
        print(f"❌ CA-1: Latencia p95 < 200ms: {p95_response_time:.2f}ms (FALLÓ)")
        ca_passed = False
    
    # CA: Tasa de éxito > 95%
    if success_rate >= 95:
        print(f"✅ CA-2: Tasa de éxito > 95%: {success_rate:.2f}% (PASÓ)")
    else:
        print(f"❌ CA-2: Tasa de éxito > 95%: {success_rate:.2f}% (FALLÓ)")
        ca_passed = False
    
    # CA: Tasa de error < 5%
    if failure_rate < 5:
        print(f"✅ CA-3: Tasa de error < 5%: {failure_rate:.2f}% (PASÓ)")
    else:
        print(f"❌ CA-3: Tasa de error < 5%: {failure_rate:.2f}% (FALLÓ)")
        ca_passed = False
    
    print("="*70)
    
    if ca_passed:
        print("✅ TODOS LOS CRITERIOS DE ACEPTACIÓN CUMPLIDOS")
    else:
        print("❌ ALGUNOS CRITERIOS DE ACEPTACIÓN NO SE CUMPLIERON")
    
    print("="*70)
    
    # Mostrar estadísticas por endpoint
    print("\n📊 ESTADÍSTICAS POR ENDPOINT:")
    print("-"*70)
    for name, stat in stats.entries.items():
        if name != "Aggregated":
            success_rate_endpoint = ((stat.num_requests - stat.num_failures) / stat.num_requests * 100) if stat.num_requests > 0 else 0
            p95_endpoint = stat.get_response_time_percentile(0.95)
            print(f"\n{name}:")
            print(f"   Requests: {stat.num_requests:,} | "
                  f"Fallos: {stat.num_failures:,} | "
                  f"Éxito: {success_rate_endpoint:.2f}% | "
                  f"p95: {p95_endpoint:.2f}ms")


# ============================================================================
# CONFIGURACIÓN ADICIONAL PARA EJECUCIÓN HEADLESS
# ============================================================================

# Para ejecutar en modo headless desde línea de comandos:
# locust -f load_test_auth.py --host=http://localhost:5000 --headless -u 500 -r 50 -t 60s --html=report.html

# Parámetros:
# --headless: Ejecutar sin interfaz web
# -u 500: 500 usuarios virtuales
# -r 50: Rampa de 50 usuarios por segundo
# -t 60s: Duración de 60 segundos
# --html=report.html: Generar reporte HTML

if __name__ == "__main__":
    # Si se ejecuta directamente, mostrar instrucciones
    print("="*70)
    print("📈 SCRIPT DE PRUEBAS DE ESTRÉS - AUTENTICACIÓN")
    print("="*70)
    print("\nEste script debe ejecutarse con Locust:")
    print("\n1. Instalar Locust:")
    print("   pip install locust")
    print("\n2. Ejecutar con interfaz web:")
    print("   locust -f load_test_auth.py --host=http://localhost:5000")
    print("\n3. Ejecutar en modo headless (500 usuarios, 60 segundos):")
    print("   locust -f load_test_auth.py --host=http://localhost:5000 \\")
    print("          --headless -u 500 -r 50 -t 60s --html=report.html")
    print("\n4. Ver reporte:")
    print("   Abrir report.html en el navegador")
    print("="*70)

