import streamlit as st
import os
from dotenv import load_dotenv
from crew.story_crew import StoryCrew
from utils.config import check_environment_variables

# Cargar variables de entorno
load_dotenv()
print("en main.py = " + os.getenv('GEMINI_API_KEY'))

def main():
    st.set_page_config(
        page_title="Creador de Historias Visuales",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📖 Creador de Historias Visuales")
    st.markdown("### Crea contenido visual atractivo para redes sociales")
    
    # Verificar variables de entorno
    if not check_environment_variables():
        st.error("⚠️ Faltan variables de entorno necesarias. Por favor, configúralas en el archivo .env")
        return
    
    # Inicializar el crew
    if 'story_crew' not in st.session_state:
        st.session_state.story_crew = StoryCrew()
    
    # Ejecutar la interfaz principal
    st.session_state.story_crew.run_interface()

if __name__ == "__main__":
    main()
