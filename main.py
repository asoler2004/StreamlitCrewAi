import streamlit as st
import os
from dotenv import load_dotenv
from crew.story_crew import StoryCrew
from utils.config import check_environment_variables
import agentops

# Cargar variables de entorno
load_dotenv()
print("en main.py = " + os.getenv('GEMINI_API_KEY'))


agentops_key = os.getenv('AGENTOPS_API_KEY')

agentops.init(
    api_key= agentops_key,
    tags=['crewai']
)


def main():
    st.set_page_config(
        page_title="Creador de Historias Visuales",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📖 Creador de Historias Visuales")
    st.markdown("### Crea contenido visual atractivo para redes sociales")
    
    # Verificar variables de entorno (pero permitir continuar)
    env_check = check_environment_variables()
    if not env_check:
        st.warning("⚠️ Algunas credenciales no están configuradas. Ve a Configuración para completar la configuración.")
        st.info("💡 Puedes ver historias archivadas y configurar credenciales sin problemas.")
    
    # Inicializar el crew
    if 'story_crew' not in st.session_state:
        st.session_state.story_crew = StoryCrew()
    
    # Ejecutar la interfaz principal
    st.session_state.story_crew.run_interface()

if __name__ == "__main__":
    main()
