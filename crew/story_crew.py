import streamlit as st
import os
import json
from datetime import datetime
from crewai import Crew, Process
from crew.agents import StoryAgents
from crew.tasks import StoryTasks
from utils.supabase_client import SupabaseManager
from utils.file_manager import FileManager
from typing import Dict, Any, List

class StoryCrew:
    def __init__(self):
        self.agents = StoryAgents()
        self.tasks = StoryTasks(self.agents)
        self.supabase_manager = SupabaseManager()
        self.file_manager = FileManager()
        
        # Inicializar estado de la sesión
        if 'current_story' not in st.session_state:
            st.session_state.current_story = None
        if 'user_id' not in st.session_state:
            st.session_state.user_id = "demo_user"  # En producción, esto vendría de autenticación
    
    def run_interface(self):
        """Ejecuta la interfaz principal de Streamlit"""
        
        # Sidebar para navegación
        with st.sidebar:
            st.header("🎯 Navegación")
            
            mode = st.radio(
                "Selecciona una opción:",
                ["📝 Crear Nueva Historia", "📚 Ver Historias Archivadas"],
                key="main_mode"
            )
        
        if mode == "📝 Crear Nueva Historia":
            self.create_story_interface()
        else:
            self.view_archived_stories_interface()
    
    def create_story_interface(self):
        """Interfaz para crear una nueva historia"""
        st.header("📝 Crear Nueva Historia Visual")
        
        # Paso 1: Selección de imagen
        st.subheader("1️⃣ Selecciona tu imagen")
        
        uploaded_file = st.file_uploader(
            "Sube una imagen para tu historia",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Formatos soportados: PNG, JPG, JPEG, GIF, BMP"
        )
        
        if uploaded_file is not None:
            # Mostrar imagen
            st.image(uploaded_file, caption="Imagen seleccionada", use_column_width=True)
            
            # Guardar imagen temporalmente
            temp_image_path = f"temp_{uploaded_file.name}"
            with open(temp_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Paso 2: Configuración de la historia
            st.subheader("2️⃣ Configura tu historia")
            
            col1, col2 = st.columns(2)
            
            with col1:
                platform = st.selectbox(
                    "Plataforma de publicación:",
                    ["Facebook", "LinkedIn", "Instagram", "Twitter/X"],
                    help="Selecciona la red social donde publicarás"
                )
            
            with col2:
                tone = st.selectbox(
                    "Tono de la publicación:",
                    ["Profesional", "Divertido", "Inspiracional", "Educativo", "Casual", "Formal"],
                    help="El tono influirá en el estilo del contenido"
                )
            
            # Especificaciones adicionales
            additional_specs = st.text_area(
                "Especificaciones adicionales (opcional):",
                placeholder="Ej: Mencionar un producto específico, incluir estadísticas, dirigirse a una audiencia particular...",
                help="Proporciona detalles específicos sobre lo que quieres incluir en tu historia"
            )
            
            # Paso 3: Generar historia
            if st.button("🚀 Generar Historia", type="primary"):
                with st.spinner("Analizando imagen y creando contenido..."):
                    try:
                        # Crear especificaciones del usuario
                        user_specs = {
                            'platform': platform,
                            'tone': tone.lower(),
                            'additional_specs': additional_specs
                        }
                        
                        # Ejecutar el crew
                        result = self.execute_story_creation(temp_image_path, user_specs)
                        
                        if result:
                            st.session_state.current_story = result
                            st.success("✅ ¡Historia creada exitosamente!")
                            
                            # Mostrar resultado
                            self.display_story_result(result)
                            
                            # Opciones de almacenamiento
                            self.storage_options_interface(result)
                        
                    except Exception as e:
                        st.error(f"❌ Error al crear la historia: {str(e)}")
                    
                    finally:
                        # Limpiar archivo temporal
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)
    
    def execute_story_creation(self, image_path: str, user_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el proceso de creación de historia usando CrewAI"""
        
        # Crear tareas
        analyze_task = self.tasks.analyze_image_task(image_path)
        
        # Determinar qué agente de plataforma usar
        platform = user_specs['platform'].lower()
        if platform == 'facebook':
            content_task = self.tasks.create_facebook_content_task("", user_specs)
            content_agent = self.agents.facebook_agent()
        elif platform == 'linkedin':
            content_task = self.tasks.create_linkedin_content_task("", user_specs)
            content_agent = self.agents.linkedin_agent()
        elif platform == 'instagram':
            content_task = self.tasks.create_instagram_content_task("", user_specs)
            content_agent = self.agents.instagram_agent()
        else:  # Twitter/X
            content_task = self.tasks.create_twitter_content_task("", user_specs)
            content_agent = self.agents.twitter_agent()
        
        # Crear crew
        crew = Crew(
            agents=[self.agents.vision_agent(), content_agent],
            tasks=[analyze_task, content_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Ejecutar crew
        result = crew.kickoff()
        
        # Procesar resultado
        try:
            # El resultado debería ser un JSON string del último task
            content_data = json.loads(str(result))
            
            return {
                'content': content_data,
                'platform': user_specs['platform'],
                'tone': user_specs['tone'],
                'image_path': image_path,
                'created_at': datetime.now().isoformat(),
                'user_specs': user_specs
            }
        except json.JSONDecodeError:
            # Si no es JSON válido, crear estructura básica
            return {
                'content': {
                    'title': 'Historia Generada',
                    'full_text': str(result)
                },
                'platform': user_specs['platform'],
                'tone': user_specs['tone'],
                'image_path': image_path,
                'created_at': datetime.now().isoformat(),
                'user_specs': user_specs
            }
    
    def display_story_result(self, story_data: Dict[str, Any]):
        """Muestra el resultado de la historia creada"""
        st.subheader("📖 Tu Historia Generada")
        
        content = story_data.get('content', {})
        
        # Mostrar información básica
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Plataforma", story_data.get('platform', 'N/A'))
        with col2:
            st.metric("Tono", story_data.get('tone', 'N/A').title())
        with col3:
            st.metric("Fecha", datetime.fromisoformat(story_data.get('created_at', datetime.now().isoformat())).strftime("%d/%m/%Y"))
        
        # Mostrar contenido
        if 'title' in content:
            st.markdown(f"### {content['title']}")
        
        if 'hook' in content:
            st.markdown("**🎣 Gancho:**")
            st.info(content['hook'])
        
        if 'body' in content and isinstance(content['body'], list):
            st.markdown("**📝 Contenido:**")
            for i, paragraph in enumerate(content['body'], 1):
                st.markdown(f"{i}. {paragraph}")
        
        if 'call_to_action' in content:
            st.markdown("**📢 Llamada a la Acción:**")
            st.success(content['call_to_action'])
        
        if 'hashtags' in content:
            st.markdown("**#️⃣ Hashtags:**")
            st.markdown(" ".join(content['hashtags']))
        
        # Texto completo
        if 'full_text' in content:
            st.markdown("**📄 Texto Completo:**")
            st.text_area("", content['full_text'], height=150, disabled=True)
        
        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Regenerar Historia"):
                st.session_state.current_story = None
                st.rerun()
        
        with col2:
            if st.button("✅ Aprobar Historia"):
                st.success("Historia aprobada. Procede al almacenamiento.")
    
    def storage_options_interface(self, story_data: Dict[str, Any]):
        """Interfaz para opciones de almacenamiento"""
        st.subheader("💾 Opciones de Almacenamiento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Almacenamiento Local:**")
            local_formats = st.multiselect(
                "Selecciona formatos:",
                ["JSON", "Markdown", "HTML", "PDF"],
                default=["JSON"]
            )
        
        with col2:
            st.markdown("**Almacenamiento Remoto:**")
            save_to_supabase = st.checkbox("Guardar en Supabase", value=True)
        
        if st.button("💾 Guardar Historia", type="primary"):
            with st.spinner("Guardando historia..."):
                self.save_story(story_data, local_formats, save_to_supabase)
    
    def save_story(self, story_data: Dict[str, Any], local_formats: List[str], save_to_supabase: bool):
        """Guarda la historia según las opciones seleccionadas"""
        saved_files = []
        
        try:
            # Almacenamiento local
            for format_type in local_formats:
                if format_type == "JSON":
                    filepath = self.file_manager.save_as_json(story_data)
                    saved_files.append(f"JSON: {filepath}")
                elif format_type == "Markdown":
                    filepath = self.file_manager.save_as_markdown(story_data)
                    saved_files.append(f"Markdown: {filepath}")
                elif format_type == "HTML":
                    filepath = self.file_manager.save_as_html(story_data)
                    saved_files.append(f"HTML: {filepath}")
                elif format_type == "PDF":
                    filepath = self.file_manager.save_as_pdf(story_data)
                    saved_files.append(f"PDF: {filepath}")
            
            # Almacenamiento remoto
            if save_to_supabase:
                result = self.supabase_manager.save_story(
                    user_id=st.session_state.user_id,
                    title=story_data.get('content', {}).get('title', 'Historia Sin Título'),
                    content=story_data.get('content', {}),
                    tone=story_data.get('tone', 'profesional'),
                    metadata=story_data.get('user_specs', {})
                )
                
                if result['success']:
                    saved_files.append(f"Supabase: ID {result['data']['id']}")
                else:
                    st.error(f"Error guardando en Supabase: {result['error']}")
            
            # Mostrar confirmación
            if saved_files:
                st.success("✅ Historia guardada exitosamente:")
                for file_info in saved_files:
                    st.write(f"• {file_info}")
            
        except Exception as e:
            st.error(f"❌ Error al guardar: {str(e)}")
    
    def view_archived_stories_interface(self):
        """Interfaz para ver historias archivadas"""
        st.header("📚 Historias Archivadas")
        
        # Opciones de fuente
        source = st.radio(
            "Selecciona la fuente:",
            ["💻 Archivos Locales", "☁️ Base de Datos Remota (Supabase)"],
            key="archive_source"
        )
        
        if source == "💻 Archivos Locales":
            self.display_local_stories()
        else:
            self.display_remote_stories()
    
    def display_local_stories(self):
        """Muestra historias guardadas localmente"""
        stories = self.file_manager.load_stories_from_folder()
        
        if not stories:
            st.info("📭 No se encontraron historias locales.")
            return
        
        st.write(f"📊 Se encontraron {len(stories)} historias locales.")
        
        for i, story in enumerate(stories):
            with st.expander(f"📖 {story.get('content', {}).get('title', f'Historia {i+1}')} - {story.get('platform', 'N/A')}"):
                self.display_story_details(story)
    
    def display_remote_stories(self):
        """Muestra historias de la base de datos remota"""
        try:
            result = self.supabase_manager.get_stories(st.session_state.user_id)
            
            if not result['success']:
                st.error(f"❌ Error al cargar historias: {result['error']}")
                return
            
            stories = result['data']
            
            if not stories:
                st.info("📭 No se encontraron historias remotas.")
                return
            
            st.write(f"📊 Se encontraron {len(stories)} historias remotas.")
            
            for story in stories:
                with st.expander(f"📖 {story.get('title', 'Sin título')} - {story.get('tone', 'N/A')}"):
                    # Convertir formato de Supabase al formato local
                    story_data = {
                        'content': story.get('content', {}),
                        'platform': story.get('metadata', {}).get('platform', 'N/A'),
                        'tone': story.get('tone', 'N/A'),
                        'created_at': story.get('created_at', ''),
                        'id': story.get('id')
                    }
                    self.display_story_details(story_data)
        
        except Exception as e:
            st.error(f"❌ Error al conectar con Supabase: {str(e)}")
    
    def display_story_details(self, story_data: Dict[str, Any]):
        """Muestra los detalles de una historia específica"""
        content = story_data.get('content', {})
        
        # Información básica
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Plataforma", story_data.get('platform', 'N/A'))
        with col2:
            st.metric("Tono", story_data.get('tone', 'N/A').title())
        with col3:
            created_at = story_data.get('created_at', '')
            if created_at:
                try:
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    st.metric("Fecha", date_obj.strftime("%d/%m/%Y"))
                except:
                    st.metric("Fecha", "N/A")
        
        # Contenido
        if 'full_text' in content:
            st.markdown("**📄 Contenido:**")
            st.text_area("", content['full_text'], height=100, disabled=True, key=f"story_{story_data.get('id', hash(str(story_data)))}")
        
        # Botón para usar como plantilla
        if st.button(f"📋 Usar como Plantilla", key=f"template_{story_data.get('id', hash(str(story_data)))}"):
            st.session_state.current_story = story_data
            st.success("✅ Historia cargada como plantilla. Ve a 'Crear Nueva Historia' para editarla.")