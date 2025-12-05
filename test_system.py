#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema funciona correctamente
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Prueba las variables de entorno"""
    print("🔧 Probando variables de entorno...")
    
    load_dotenv()
    
    required_vars = [
        'GEMINI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SECRET_KEY'
    ]

    print(os.getenv('GEMINI_API_KEY'))
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"✅ {var}: Configurada")
    
    if missing:
        print(f"❌ Variables faltantes: {', '.join(missing)}")
        return False
    
    return True

def test_imports():
    """Prueba que todas las dependencias se puedan importar"""
    print("\n📦 Probando importaciones...")
    
    imports_to_test = [
        ('streamlit', 'Streamlit'),
        ('crewai', 'CrewAI'),
        ('supabase', 'Supabase'),
        ('transformers', 'Transformers'),
        ('PIL', 'Pillow'),
        ('reportlab', 'ReportLab'),
        ('dotenv', 'Python-dotenv')
    ]
    
    failed = []
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError:
            print(f"❌ {name}: Faltante")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Dependencias faltantes: {', '.join(failed)}")
        print("💡 Ejecuta: uv sync o uv pip install -e .")
        return False
    
    return True

def test_model_config():
    """Prueba la configuración del modelo Gemini"""
    print("\n🤖 Probando configuración del modelo...")
    
    try:
        from Models.gemini import gemini_llm
        print("✅ Configuración de Gemini: OK")
        return True
    except Exception as e:
        print(f"❌ Error en configuración de Gemini: {e}")
        return False

def test_tools():
    """Prueba las herramientas personalizadas"""
    print("\n🛠️ Probando herramientas...")
    
    try:
        from Tools.blip_caption_tool import blip_caption_tool
        print("✅ BLIP Caption Tool: OK")
        return True
    except Exception as e:
        print(f"❌ Error en BLIP Caption Tool: {e}")
        print("💡 Esto puede tardar en la primera ejecución (descarga del modelo)")
        return False

def test_supabase_connection():
    """Prueba la conexión a Supabase"""
    print("\n☁️ Probando conexión a Supabase...")
    
    try:
        from utils.supabase_client import SupabaseManager
        manager = SupabaseManager()
        
        # Intentar una operación simple
        result = manager.get_stories("test_user", limit=1)
        print("✅ Conexión a Supabase: OK")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a Supabase: {e}")
        return False

def test_file_system():
    """Prueba el sistema de archivos"""
    print("\n📁 Probando sistema de archivos...")
    
    try:
        # Crear directorio de prueba
        test_dir = Path("test_stories")
        test_dir.mkdir(exist_ok=True)
        
        # Probar escritura
        test_file = test_dir / "test.txt"
        test_file.write_text("Prueba")
        
        # Probar lectura
        content = test_file.read_text()
        
        # Limpiar
        test_file.unlink()
        test_dir.rmdir()
        
        print("✅ Sistema de archivos: OK")
        return True
    except Exception as e:
        print(f"❌ Error en sistema de archivos: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas del sistema...\n")
    
    tests = [
        ("Variables de entorno", test_environment),
        ("Importaciones", test_imports),
        ("Configuración del modelo", test_model_config),
        ("Herramientas", test_tools),
        ("Conexión Supabase", test_supabase_connection),
        ("Sistema de archivos", test_file_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
    
    print(f"\n📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
        print("🚀 Ejecuta 'python run.py' o 'streamlit run main.py' para iniciar")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa la configuración.")
        print("📖 Consulta el README.md para más información")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)