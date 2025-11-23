"""
🛡️ Script de Análisis de Seguridad Estática (SAST)
====================================================

Este script ejecuta análisis estático de seguridad para el código Python
usando Bandit, una herramienta diseñada para encontrar vulnerabilidades
comunes en código Python.

Componente analizado: api/ (toda la API FastAPI)

Herramienta: Bandit (https://bandit.readthedocs.io/)
Nivel de severidad: Alto y Medio

El script retorna un error si se encuentran vulnerabilidades de seguridad.
"""

import subprocess
import sys
import os
import json
from pathlib import Path


# Configuración
BANDIT_CONFIG = {
    "severity_level": ["high", "medium"],  # Solo reportar vulnerabilidades altas y medias
    "confidence_level": ["high", "medium"],  # Solo reportar con alta y media confianza
    "exclude_dirs": ["venv", "__pycache__", ".git", "node_modules", "tests"],
    "target_dirs": ["api/"],  # Directorios a analizar
}

# Códigos de salida
EXIT_SUCCESS = 0
EXIT_VULNERABILITIES_FOUND = 1
EXIT_BANDIT_NOT_INSTALLED = 2
EXIT_ERROR = 3


def check_bandit_installed():
    """Verificar si Bandit está instalado"""
    try:
        result = subprocess.run(
            ["bandit", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_bandit():
    """Instalar Bandit si no está disponible"""
    print("📦 Instalando Bandit...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "bandit[toml]"],
            check=True,
            timeout=120
        )
        print("✅ Bandit instalado correctamente")
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"❌ Error instalando Bandit: {e}")
        return False


def run_bandit_analysis(target_dir="api/", output_format="json", output_file=None):
    """
    Ejecutar análisis de seguridad con Bandit
    
    Args:
        target_dir: Directorio a analizar
        output_format: Formato de salida (json, txt, csv)
        output_file: Archivo de salida (opcional)
    
    Returns:
        tuple: (return_code, output_text, vulnerabilities_found)
    """
    # Verificar que el directorio existe
    if not os.path.exists(target_dir):
        print(f"⚠️  Advertencia: El directorio {target_dir} no existe")
        return EXIT_ERROR, f"Directorio {target_dir} no encontrado", 0
    
    # Construir comando Bandit
    cmd = [
        "bandit",
        "-r",  # Recursivo
        target_dir,
        "-f", output_format,  # Formato de salida
        "-ll",  # Nivel de logging: solo mostrar warnings y errores
        "-i",  # Mostrar solo issues (vulnerabilidades)
        "--severity-level", "medium",  # Solo reportar medium y high
        "--confidence-level", "medium",  # Solo reportar medium y high
    ]
    
    # Agregar exclusiones
    for exclude_dir in BANDIT_CONFIG["exclude_dirs"]:
        cmd.extend(["-x", exclude_dir])
    
    # Excluir explícitamente venv si existe
    if os.path.exists(os.path.join(target_dir, "venv")):
        cmd.extend(["--exclude", os.path.join(target_dir, "venv")])
    
    # Si se especifica archivo de salida
    if output_file:
        cmd.extend(["-o", output_file])
    
    try:
        print(f"🔍 Ejecutando análisis de seguridad en {target_dir}...")
        print(f"   Comando: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        output = result.stdout + result.stderr
        
        # Parsear resultados si es JSON
        vulnerabilities_found = 0
        if output_format == "json" and result.returncode == 1:
            try:
                # Bandit retorna código 1 cuando encuentra vulnerabilidades
                # Intentar parsear el JSON de stdout
                if result.stdout:
                    json_output = json.loads(result.stdout)
                    vulnerabilities_found = json_output.get("metrics", {}).get("_totals", {}).get("SEVERITY.HIGH", 0)
                    vulnerabilities_found += json_output.get("metrics", {}).get("_totals", {}).get("SEVERITY.MEDIUM", 0)
            except json.JSONDecodeError:
                # Si no se puede parsear, contar líneas con "Issue:"
                vulnerabilities_found = output.count("Issue:")
        
        return result.returncode, output, vulnerabilities_found
    
    except subprocess.TimeoutExpired:
        return EXIT_ERROR, "⏱️  Timeout: El análisis tomó más de 5 minutos", 0
    except Exception as e:
        return EXIT_ERROR, f"❌ Error ejecutando Bandit: {str(e)}", 0


def parse_bandit_results(output_text, output_format="json"):
    """Parsear y formatear resultados de Bandit"""
    if output_format == "json":
        try:
            data = json.loads(output_text)
            metrics = data.get("metrics", {}).get("_totals", {})
            
            high_severity = metrics.get("SEVERITY.HIGH", 0)
            medium_severity = metrics.get("SEVERITY.MEDIUM", 0)
            low_severity = metrics.get("SEVERITY.LOW", 0)
            
            issues = data.get("results", [])
            
            return {
                "high": high_severity,
                "medium": medium_severity,
                "low": low_severity,
                "total": high_severity + medium_severity + low_severity,
                "issues": issues
            }
        except json.JSONDecodeError:
            return None
    return None


def print_summary(results):
    """Imprimir resumen de resultados"""
    if not results:
        return
    
    print("\n" + "="*70)
    print("📊 RESUMEN DE ANÁLISIS DE SEGURIDAD")
    print("="*70)
    print(f"🔴 Vulnerabilidades CRÍTICAS (High):    {results['high']}")
    print(f"🟡 Vulnerabilidades MEDIAS (Medium):    {results['medium']}")
    print(f"🟢 Vulnerabilidades BAJAS (Low):        {results['low']}")
    print(f"📈 TOTAL de vulnerabilidades:           {results['total']}")
    print("="*70)
    
    if results['high'] > 0 or results['medium'] > 0:
        print("\n⚠️  VULNERABILIDADES ENCONTRADAS:")
        print("-"*70)
        
        for issue in results['issues']:
            severity = issue.get('issue_severity', 'UNKNOWN')
            confidence = issue.get('issue_confidence', 'UNKNOWN')
            
            # Solo mostrar high y medium
            if severity in ['HIGH', 'MEDIUM']:
                print(f"\n🔍 {severity} ({confidence})")
                print(f"   Archivo: {issue.get('filename', 'N/A')}")
                print(f"   Línea: {issue.get('line_number', 'N/A')}")
                print(f"   Test ID: {issue.get('test_id', 'N/A')}")
                print(f"   Descripción: {issue.get('issue_text', 'N/A')}")
                if issue.get('code'):
                    print(f"   Código: {issue.get('code', 'N/A')[:100]}")


def main():
    """Función principal"""
    print("🛡️  INICIANDO ANÁLISIS DE SEGURIDAD ESTÁTICA")
    print("="*70)
    
    # Verificar instalación de Bandit
    if not check_bandit_installed():
        print("⚠️  Bandit no está instalado")
        print("   Intentando instalar...")
        if not install_bandit():
            print("❌ No se pudo instalar Bandit")
            print("   Instala manualmente con: pip install bandit[toml]")
            return EXIT_BANDIT_NOT_INSTALLED
    
    # Obtener directorio raíz del proyecto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    api_dir = project_root / "api"
    
    # Verificar que existe el directorio api/
    if not api_dir.exists():
        print(f"❌ Error: No se encontró el directorio {api_dir}")
        return EXIT_ERROR
    
    # Ejecutar análisis
    return_code, output, vuln_count = run_bandit_analysis(
        target_dir=str(api_dir),
        output_format="json"
    )
    
    # Mostrar salida
    print("\n" + output)
    
    # Parsear y mostrar resumen
    results = parse_bandit_results(output, "json")
    if results:
        print_summary(results)
    
    # Determinar código de salida
    if return_code == 1:  # Bandit retorna 1 cuando encuentra vulnerabilidades
        print("\n❌ ANÁLISIS COMPLETADO: Se encontraron vulnerabilidades de seguridad")
        print("   Por favor, revisa los resultados arriba y corrige los problemas.")
        return EXIT_VULNERABILITIES_FOUND
    elif return_code == 0:
        print("\n✅ ANÁLISIS COMPLETADO: No se encontraron vulnerabilidades críticas")
        return EXIT_SUCCESS
    else:
        print("\n❌ ERROR: El análisis falló")
        return EXIT_ERROR


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

