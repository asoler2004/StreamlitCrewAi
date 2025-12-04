#!/usr/bin/env python3
"""
Script de inicio para el Creador de Historias Visuales
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    try:
        import streamlit
        import crewai
        import supabase
        import transformers
        import PIL
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("💡 Ejecuta: uv sync o pip install -e .")
        return False

def check_env_file():
    """Verifica que el archivo .env exista"""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  Archivo .env no encontrado")
        print("💡 Crea un archivo .env con las variables necesarias")
        print("📖 Consulta el README.md para más información")
        return False
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando Creador de Historias Visuales...")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar archivo .env
    if not check_env_file():
        print("⚠️  Continuando sin verificar variables de entorno...")
    
    # Crear directorio de historias si no existe
    stories_dir = Path("stories")
    stories_dir.mkdir(exist_ok=True)
    
    # Ejecutar Streamlit
    try:
        print("🌐 Abriendo aplicación en el navegador...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.headless", "false",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()