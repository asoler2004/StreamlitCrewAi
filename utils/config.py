import os
import streamlit as st
from dotenv import load_dotenv, set_key

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
        
        with st.expander("🔧 Configurar Variables de Entorno", expanded=True):
            st.markdown("Introduce las credenciales necesarias:")
            
            # Formulario para configurar variables
            with st.form("config_form"):
                new_vars = {}
                
                if 'GEMINI_API_KEY' in missing_vars:
                    new_vars['GEMINI_API_KEY'] = st.text_input(
                        "🤖 Clave API de Gemini:",
                        type="password",
                        help="Obtén tu clave en https://makersuite.google.com/app/apikey"
                    )
                
                if 'SUPABASE_URL' in missing_vars:
                    new_vars['SUPABASE_URL'] = st.text_input(
                        "🌐 URL de Supabase:",
                        help="URL de tu proyecto Supabase (ej: https://xxx.supabase.co)"
                    )
                
                if 'SUPABASE_KEY' in missing_vars:
                    new_vars['SUPABASE_KEY'] = st.text_input(
                        "🔑 Clave Pública de Supabase:",
                        type="password",
                        help="Clave anon/public de tu proyecto Supabase"
                    )
                
                if 'SUPABASE_SECRET_KEY' in missing_vars:
                    new_vars['SUPABASE_SECRET_KEY'] = st.text_input(
                        "🔐 Clave Secreta de Supabase:",
                        type="password",
                        help="Clave service_role de tu proyecto Supabase"
                    )
                
                if 'AGENTOPS_API_KEY' in missing_vars:
                    new_vars['AGENTOPS_API_KEY'] = st.text_input(
                        "📊 Clave API de AgentOps:",
                        type="password",
                        help="Clave de AgentOps (opcional para monitoreo)"
                    )
                
                if st.form_submit_button("💾 Guardar Configuración", type="primary"):
                    return save_environment_variables(new_vars)
            
            st.markdown("""
            **Alternativamente**, puedes configurar manualmente las variables en tu archivo `.env`:
            
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

def save_environment_variables(new_vars: dict) -> bool:
    """Guarda las nuevas variables de entorno en el archivo .env"""
    try:
        env_file = '.env'
        
        # Crear archivo .env si no existe
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f:
                f.write("# Configuración de variables de entorno\n")
        
        # Guardar cada variable
        for key, value in new_vars.items():
            if value.strip():  # Solo guardar si no está vacío
                set_key(env_file, key, value.strip())
                os.environ[key] = value.strip()
        
        st.success("✅ Configuración guardada exitosamente. Recarga la página para aplicar los cambios.")
        st.info("🔄 Por favor, recarga la página (F5) para que los cambios tomen efecto.")
        return True
        
    except Exception as e:
        st.error(f"❌ Error al guardar configuración: {str(e)}")
        return False

def update_credentials_interface():
    """Interfaz para actualizar credenciales existentes"""
    st.subheader("🔧 Actualizar Credenciales")
    
    with st.form("update_credentials_form"):
        st.markdown("Actualiza las credenciales existentes (deja en blanco para mantener las actuales):")
        
        new_gemini_key = st.text_input(
            "🤖 Nueva Clave API de Gemini:",
            type="password",
            placeholder="Dejar en blanco para mantener actual"
        )
        
        new_supabase_url = st.text_input(
            "🌐 Nueva URL de Supabase:",
            placeholder="Dejar en blanco para mantener actual"
        )
        
        new_supabase_key = st.text_input(
            "🔑 Nueva Clave Pública de Supabase:",
            type="password",
            placeholder="Dejar en blanco para mantener actual"
        )
        
        new_supabase_secret = st.text_input(
            "🔐 Nueva Clave Secreta de Supabase:",
            type="password",
            placeholder="Dejar en blanco para mantener actual"
        )
        
        new_agentops_key = st.text_input(
            "📊 Nueva Clave API de AgentOps:",
            type="password",
            placeholder="Dejar en blanco para mantener actual"
        )
        
        if st.form_submit_button("🔄 Actualizar Credenciales", type="primary"):
            updates = {}
            
            if new_gemini_key.strip():
                updates['GEMINI_API_KEY'] = new_gemini_key.strip()
                print(new_gemini_key)
            if new_supabase_url.strip():
                updates['SUPABASE_URL'] = new_supabase_url.strip()
            if new_supabase_key.strip():
                updates['SUPABASE_KEY'] = new_supabase_key.strip()
            if new_supabase_secret.strip():
                updates['SUPABASE_SECRET_KEY'] = new_supabase_secret.strip()
            if new_agentops_key.strip():
                updates['AGENTOPS_API_KEY'] = new_agentops_key.strip()
            
            if updates:
                if save_environment_variables(updates):
                    st.balloons()
            else:
                st.warning("⚠️ No se proporcionaron nuevas credenciales para actualizar.")

def get_config():
    """Obtiene la configuración de las variables de entorno"""
    return {
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_key': os.getenv('SUPABASE_KEY'),
        'supabase_secret_key': os.getenv('SUPABASE_SECRET_KEY'),
        'agentops_api_key': os.getenv('AGENTOPS_API_KEY')
    }