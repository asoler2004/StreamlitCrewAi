import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def check_environment_variables():
    """Verifica que todas las variables de entorno necesarias estén configuradas"""
    required_vars = [
        'GEMINI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SECRET_KEY',
        'AGENTOPS_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        st.error(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        
        with st.expander("🔧 Configurar Variables de Entorno"):
            st.markdown("""
            Para usar esta aplicación, necesitas configurar las siguientes variables en tu archivo `.env`:
            
            ```
            GEMINI_API_KEY=tu_clave_de_gemini
            SUPABASE_URL=tu_url_de_supabase
            SUPABASE_KEY=tu_clave_publica_de_supabase
            SUPABASE_SECRET_KEY=tu_clave_secreta_de_supabase
            AGENTOPS_API_KEY=tu_clave_de_agentops
            ```
            """)
        return False
    
    return True

def get_config():
    """Obtiene la configuración de las variables de entorno"""
    return {
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_key': os.getenv('SUPABASE_KEY'),
        'supabase_secret_key': os.getenv('SUPABASE_SECRET_KEY'),
        'agentops_api_key': os.getenv('AGENTOPS_API_KEY')
    }