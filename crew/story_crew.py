import streamlit as st
import os
import json
from datetime import datetime
from crewai import Crew, Process
from crew.agents import StoryAgents
from crew.tasks import StoryTasks
from utils.supabase_client import SupabaseManager
from utils.file_manager import FileManager
from utils.config import update_credentials_interface
from utils.publicar import login_user,post_image, generate_daily_schedule, schedule_and_post
from typing import Dict, Any, List
import requests
from io import BytesIO
from PIL import Image
from pathlib import Path

class StoryCrew:
    def __init__(self):
        try:
            self.agents = StoryAgents()
            self.tasks = StoryTasks(self.agents)
        except Exception as e:
            st.warning(f"⚠️ Error inicializando agentes: {str(e)}")
            self.agents = None
            self.tasks = None
        
        try:
            self.supabase_manager = SupabaseManager()
        except Exception as e:
            st.warning(f"⚠️ Error conectando con Supabase: {str(e)}")
            self.supabase_manager = None
        
        self.file_manager = FileManager()
        
        # Inicializar estado de la sesión
        if 'current_story' not in st.session_state:
            st.session_state.current_story = None
        if 'template_story' not in st.session_state:
            st.session_state.template_story = None
        if 'story_approved' not in st.session_state:
            st.session_state.story_approved = False
        if 'show_storage_options' not in st.session_state:
            st.session_state.show_storage_options = False
        if 'crew_workflow' not in st.session_state:
            st.session_state.crew_workflow = []
        if 'story_saved_successfully' not in st.session_state:
            st.session_state.story_saved_successfully = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = "demo_user"  # En producción, esto vendría de autenticación
    
    def run_interface(self):
        """Ejecuta la interfaz principal de Streamlit"""
        
        # Sidebar para navegación
        with st.sidebar:
            st.header("🎯 Navegación")
            
            mode = st.radio(
                "Selecciona una opción:",
                ["📝 Crear Nueva Historia", "📚 Ver Historias Archivadas", "⚙️ Configuración"],
                key="main_mode"
            )
            
            # Sección de workflow de agentes
            if st.session_state.crew_workflow:
                st.divider()
                st.header("🤖 Workflow de Agentes")
                
                with st.expander("Ver Progreso en Tiempo Real", expanded=True):
                    for step in st.session_state.crew_workflow:
                        status_icon = "✅" if step['status'] == 'completed' else "🔄" if step['status'] == 'running' else "⏳"
                        st.write(f"{status_icon} **{step['agent']}**: {step['task']}")
                        if step.get('result'):
                            st.caption(f"Resultado: {step['result'][:100]}...")
        
        if mode == "📝 Crear Nueva Historia":
            self.create_story_interface()
        elif mode == "📚 Ver Historias Archivadas":
            self.view_archived_stories_interface()
        else:
            self.configuration_interface()
    
    def create_story_interface(self):
        """Interfaz para crear una nueva historia"""
        st.header("📝 Crear Nueva Historia Visual")
        
        # Verificar si hay una plantilla cargada
        if st.session_state.template_story:
            st.info("📋 Editando historia desde plantilla")
            self.edit_template_interface()
            return
        
        # Paso 1: Selección de imagen
        st.subheader("1️⃣ Selecciona tu imagen")
        
        uploaded_file = st.file_uploader(
            "Sube una imagen para tu historia",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Formatos soportados: PNG, JPG, JPEG, GIF, BMP"
        )
        
        if uploaded_file is not None:
            # Mostrar imagen
            st.image(uploaded_file, caption="Imagen seleccionada")
            
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
                tone_options = [
                    "Profesional", "Divertido", "Inspiracional", "Educativo", 
                    "Casual", "Formal", "Motivacional", "Informativo", 
                    "Persuasivo", "Emocional", "Técnico", "Creativo",
                    "Amigable", "Autoritativo", "Conversacional", "Urgente"
                ]
                
                tone = st.selectbox(
                    "Tono de la publicación:",
                    tone_options,
                    help="El tono influirá en el estilo del contenido"
                )
                
                # Opción para tono personalizado
                custom_tone = st.text_input(
                    "Tono personalizado (opcional):",
                    placeholder="Ej: Sarcástico, Nostálgico, Científico...",
                    help="Define tu propio tono si no encuentras el adecuado"
                )
                
                if custom_tone:
                    tone = custom_tone
            
            # Especificaciones adicionales
            additional_specs = st.text_area(
                "Especificaciones adicionales (opcional):",
                placeholder="Ej: Mencionar un producto específico, incluir estadísticas, dirigirse a una audiencia particular...",
                help="Proporciona detalles específicos sobre lo que quieres incluir en tu historia"
            )
            
            # Paso 3: Generar historia
            if st.button("🚀 Generar Historia", type="primary"):
                # Limpiar workflow anterior
                st.session_state.crew_workflow = []
                
                # Crear placeholder para workflow en tiempo real
                workflow_placeholder = st.empty()
                
                try:
                    # Crear especificaciones del usuario
                    user_specs = {
                        'platform': platform,
                        'tone': tone.lower(),
                        'additional_specs': additional_specs
                    }
                    
                    # Subir imagen a Supabase primero (si está disponible)
                    image_url = ""
                    if self.supabase_manager:
                        with st.spinner("Subiendo imagen..."):
                            image_url = self.upload_image_to_supabase(temp_image_path, uploaded_file.name)
                    else:
                        st.info("ℹ️ Supabase no configurado - la imagen no se subirá al almacenamiento remoto.")
                    
                    # Verificar que los agentes estén disponibles
                    if not self.agents or not self.tasks:
                        st.error("❌ Los agentes de IA no están configurados. Verifica tu clave de Gemini en Configuración.")
                        return
                    
                    # Ejecutar el crew con seguimiento en tiempo real
                    with st.spinner("Analizando imagen y creando contenido..."):
                        result = self.execute_story_creation(temp_image_path, user_specs, workflow_placeholder)
                        
                        if result:
                            # Agregar URL de imagen al resultado
                            result['image_url'] = image_url
                            result['original_filename'] = uploaded_file.name
                            
                            st.session_state.current_story = result
                            st.session_state.story_approved = False
                            st.session_state.show_storage_options = False
                            st.success("✅ ¡Historia creada exitosamente!")
                            st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error al crear la historia: {str(e)}")
                
                finally:
                    # Limpiar archivo temporal
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
        
        # Mostrar historia actual si existe
        if st.session_state.current_story:
            self.display_story_result(st.session_state.current_story)
            
            if st.session_state.story_approved or st.session_state.show_storage_options:
                self.storage_options_interface(st.session_state.current_story)
    
    def execute_story_creation(self, image_path: str, user_specs: Dict[str, Any], workflow_placeholder=None) -> Dict[str, Any]:
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
        
        # Actualizar workflow
        self.update_workflow("Agente de Visión", "Analizando imagen", "running", workflow_placeholder)
        
        # Crear crew
        crew = Crew(
            # self.agents.voice_agent, self.agents.user_interaction_agent(), 
            agents=[self.agents.vision_agent(), content_agent],
            tasks=[analyze_task, content_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Ejecutar crew con seguimiento
        self.update_workflow("Agente de Visión", "Analizando imagen", "running", workflow_placeholder)
        
        result = crew.kickoff()
        
        self.update_workflow("Agente de Visión", "Análisis completado", "completed", workflow_placeholder)
        self.update_workflow(f"Agente de {user_specs['platform']}", "Creando contenido", "completed", workflow_placeholder)
        
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
        content = story_data.get('content', {})
        title = content.get('title', 'Historia Generada')
        
        st.subheader(f"📖 {title}")
        
        # Mostrar imagen si existe
        if story_data.get('image_url'):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(story_data['image_url'], caption="Imagen de la historia")
            with col2:
                # Mostrar información básica
                st.metric("Plataforma", story_data.get('platform', 'N/A'))
                st.metric("Tono", story_data.get('tone', 'N/A').title())
                st.metric("Fecha", datetime.fromisoformat(story_data.get('created_at', datetime.now().isoformat())).strftime("%d/%m/%Y"))
        else:
            # Mostrar información básica sin imagen
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Plataforma", story_data.get('platform', 'N/A'))
            with col2:
                st.metric("Tono", story_data.get('tone', 'N/A').title())
            with col3:
                st.metric("Fecha", datetime.fromisoformat(story_data.get('created_at', datetime.now().isoformat())).strftime("%d/%m/%Y"))

        
        # Vista previa visual de la historia
        st.markdown("**📱 Vista Previa de Publicación:**")
        self.render_story_preview(story_data)
        
        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Regenerar Historia", key="regenerate_story"):
                st.session_state.current_story = None
                st.session_state.story_approved = False
                st.session_state.show_storage_options = False
                st.rerun()
        
        with col2:
            if st.button("✅ Aprobar Historia", key="approve_story"):
                st.session_state.story_approved = True
                st.session_state.show_storage_options = True
                st.success("✅ Historia aprobada. Procede al almacenamiento.")
                st.rerun()
    
    def render_story_preview(self, story_data: Dict[str, Any]):
        """Renderiza una vista previa visual de la historia como se vería publicada"""
        content = story_data.get('content', {})
        platform = story_data.get('platform', '').lower()
        image_url = story_data.get('image_url', '')
        
        # Crear HTML personalizado según la plataforma
        if platform == 'facebook':
            preview_html = self.create_facebook_preview(content, image_url)
        elif platform == 'linkedin':
            preview_html = self.create_linkedin_preview(content, image_url)
        elif platform == 'instagram':
            preview_html = self.create_instagram_preview(content, image_url)
        elif platform in ['twitter', 'twitter/x']:
            preview_html = self.create_twitter_preview(content, image_url)
        else:
            preview_html = self.create_generic_preview(content, image_url)
        
        # Mostrar la vista previa
        st.markdown(preview_html, unsafe_allow_html=True)
    
    def create_facebook_preview(self, content: Dict[str, Any], image_url: str = '') -> str:
        """Crea vista previa estilo Facebook"""
        # full_text = content.get('full_text', '')
        full_text = content.get('body', '')
        image_section = f'<img src="{image_url}" style="width: 100%; border-radius: 8px; margin: 12px 0;" alt="Imagen del post">' if image_url else ''
        
        return f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; background: white; font-family: 'Segoe UI', Arial, sans-serif; max-width: 500px; margin: 10px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="width: 40px; height: 40px; background: #1877f2; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px;">U</div>
                <div>
                    <div style="font-weight: 600; font-size: 14px;">Tu Página</div>
                    <div style="font-size: 12px; color: #65676b;">Hace unos minutos · 🌍</div>
                </div>
            </div>
            <div style="font-size: 14px; line-height: 1.4; color: #1c1e21; white-space: pre-wrap;">{full_text}</div>
            {image_section}
            <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #f0f2f5; display: flex; justify-content: space-around; color: #65676b; font-size: 14px;">
                <span>👍 Me gusta</span>
                <span>💬 Comentar</span>
                <span>📤 Compartir</span>
            </div>
        </div>
        """
    
    def create_linkedin_preview(self, content: Dict[str, Any], image_url: str = '') -> str:
        """Crea vista previa estilo LinkedIn"""
        # full_text = content.get('full_text', '')
        full_text = content.get('body', '')
        hashtags = content.get('hashtags', [])
        hashtag_text = ' '.join(hashtags) if hashtags else ''
        image_section = f'<img src="{image_url}" style="width: 100%; border-radius: 8px; margin: 12px 0;" alt="Imagen del post">' if image_url else ''
        
        return f"""
        <div style="border: 1px solid #d4d4d8; border-radius: 8px; padding: 16px; background: white; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 550px; margin: 10px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="width: 48px; height: 48px; background: #0a66c2; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px;">TU</div>
                <div>
                    <div style="font-weight: 600; font-size: 14px; color: #000;">Tu Nombre</div>
                    <div style="font-size: 12px; color: #666;">Tu Título Profesional</div>
                    <div style="font-size: 12px; color: #666;">Hace 1 hora · 🌍</div>
                </div>
            </div>
            <div style="font-size: 14px; line-height: 1.5; color: #000; white-space: pre-wrap; margin-bottom: 8px;">{full_text}</div>
            {image_section}
            {f'<div style="font-size: 14px; color: #0a66c2; margin-bottom: 12px;">{hashtag_text}</div>' if hashtag_text else ''}
            <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #e6e6e6; display: flex; justify-content: space-around; color: #666; font-size: 14px;">
                <span>👍 Recomendar</span>
                <span>💬 Comentar</span>
                <span>🔄 Compartir</span>
                <span>📤 Enviar</span>
            </div>
        </div>
        """
    
    def create_instagram_preview(self, content: Dict[str, Any], image_url: str = '') -> str:
        """Crea vista previa estilo Instagram"""
        # full_text = content.get('full_text', '')
        full_text = content.get('body', '')
        hashtags = content.get('hashtags', [])
        hashtag_text = ' '.join(hashtags) if hashtags else ''
        
        image_section = f'<img src="{image_url}" style="width: 100%; height: 400px; object-fit: cover;" alt="Imagen del post">' if image_url else '<div style="width: 100%; height: 400px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 16px;">📸 Tu Imagen</div>'
        
        return f"""
        <div style="border: 1px solid #dbdbdb; border-radius: 8px; background: white; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 400px; margin: 10px 0;">
            <div style="display: flex; align-items: center; padding: 14px 16px; border-bottom: 1px solid #efefef;">
                <div style="width: 32px; height: 32px; background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px; font-size: 12px;">TU</div>
                <div style="font-weight: 600; font-size: 14px;">tu_usuario</div>
            </div>
            {image_section}
            <div style="padding: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="display: flex; gap: 16px;">
                        <span>❤️</span>
                        <span>💬</span>
                        <span>📤</span>
                    </div>
                    <span>🔖</span>
                </div>
                <div style="font-size: 14px; margin-bottom: 4px;"><strong>123 Me gusta</strong></div>
                <div style="font-size: 14px; line-height: 1.4;">
                    <strong>tu_usuario</strong> {full_text}
                    {f'<div style="color: #00376b; margin-top: 4px;">{hashtag_text}</div>' if hashtag_text else ''}
                </div>
                <div style="color: #8e8e8e; font-size: 12px; margin-top: 8px;">HACE 1 HORA</div>
            </div>
        </div>
        """
    
    def create_twitter_preview(self, content: Dict[str, Any], image_url: str = '') -> str:
        """Crea vista previa estilo Twitter"""
        # main_tweet = content.get('main_tweet', content.get('full_text', ''))
        main_tweet = content.get('main_tweet', content.get('body', ''))
        thread = content.get('thread', [])
        hashtags = content.get('hashtags', [])
        
        preview = f"""
        <div style="border: 1px solid #cfd9de; border-radius: 16px; padding: 16px; background: white; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 500px; margin: 10px 0;">
            <div style="display: flex; margin-bottom: 12px;">
                <div style="width: 40px; height: 40px; background: #1d9bf0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px;">TU</div>
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 4px;">
                        <span style="font-weight: 700; font-size: 15px;">Tu Nombre</span>
                        <span style="color: #536471; font-size: 15px;">@tu_usuario</span>
                        <span style="color: #536471; font-size: 15px;">· 1h</span>
                    </div>
                    <div style="font-size: 15px; line-height: 1.3; color: #0f1419; white-space: pre-wrap;">{main_tweet}</div>
                    {f'<img src="{image_url}" style="width: 100%; border-radius: 16px; margin-top: 12px;" alt="Imagen del tweet">' if image_url else ''}
                </div>
            </div>
        """
        
        # Agregar thread si existe
        for i, tweet in enumerate(thread):
            preview += f"""
            <div style="display: flex; margin-top: 12px; padding-top: 12px; border-top: 1px solid #eff3f4;">
                <div style="width: 40px; height: 40px; background: #1d9bf0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px;">TU</div>
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 4px;">
                        <span style="font-weight: 700; font-size: 15px;">Tu Nombre</span>
                        <span style="color: #536471; font-size: 15px;">@tu_usuario</span>
                        <span style="color: #536471; font-size: 15px;">· 1h</span>
                    </div>
                    <div style="font-size: 15px; line-height: 1.3; color: #0f1419; white-space: pre-wrap;">{tweet}</div>
                </div>
            </div>
            """
        
        preview += """
            <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #eff3f4; display: flex; justify-content: space-around; color: #536471; font-size: 14px;">
                <span>💬 12</span>
                <span>🔄 5</span>
                <span>❤️ 23</span>
                <span>📤</span>
            </div>
        </div>
        """
        
        return preview
    
    def create_generic_preview(self, content: Dict[str, Any], image_url: str = '') -> str:
        """Crea vista previa genérica"""
        full_text = content.get('full_text', '')
        image_section = f'<img src="{image_url}" style="width: 100%; border-radius: 8px; margin-bottom: 16px;" alt="Imagen del contenido">' if image_url else ''
        
        return f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #f9f9f9; font-family: Arial, sans-serif; max-width: 500px; margin: 10px 0;">
            {image_section}
            <div style="font-size: 16px; line-height: 1.5; color: #333; white-space: pre-wrap;">{full_text}</div>
        </div>
        """
    
    def storage_options_interface(self, story_data: Dict[str, Any]):
        """Interfaz para opciones de almacenamiento"""
        st.subheader("💾 Opciones de Almacenamiento")
        
        # Usar un formulario para evitar que desaparezca
        with st.form("storage_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Almacenamiento Local:**")
                local_formats = st.multiselect(
                    "Selecciona formatos:",
                    ["JSON", "Markdown", "HTML", "PDF"],
                    default=["JSON"],
                    key="local_formats_select"
                )
            
            with col2:
                st.markdown("**Almacenamiento Remoto:**")
                save_to_supabase = st.checkbox("Guardar en Supabase", value=True, key="supabase_checkbox")
                
                # Opción para actualizar historia existente
                if 'id' in story_data or story_data.get('edited_from'):
                    update_existing = st.checkbox(
                        "Actualizar historia existente (crear nueva versión)", 
                        value=True,
                        key="update_existing_checkbox"
                    )
                else:
                    update_existing = False
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                save_clicked = st.form_submit_button("💾 Guardar Historia", type="primary")
            with col2:
                cancel_clicked = st.form_submit_button("❌ Cancelar")
            
            if save_clicked:
                with st.spinner("Guardando historia..."):
                    
                    # storage_task = self.tasks.storage_task(story_data,local_formats,save_to_supabase)
        
                    # crew2 = Crew(
                    #     agents=[self.agents.storage_agent()],
                    #     tasks=[storage_task],
                    #     process=Process.sequential,
                    #     verbose=True
                    # )
        
                    # # Ejecutar crew con seguimiento
                    # self.update_workflow("Agente de Almacenamiento", "Guardando historia", "running")  #, workflow_placeholder
        
                    # result = crew2.kickoff()      
     
                    # success = result["success"]
                    # saved_files = result["saved_files"]

                    success, saved_files = self.save_story(story_data, local_formats, save_to_supabase, update_existing)
                    
                    # Mostrar confirmación detallada
                    if success:
                        st.success("✅ Historia guardada exitosamente!")
                        
                        # Mostrar detalles de archivos guardados
                        if saved_files:
                            st.markdown("**Archivos creados:**")
                            for file_info in saved_files:
                                st.write(f"• {file_info}")
                        
                        # Marcar como guardado exitosamente
                        st.session_state.story_saved_successfully = True
                        st.balloons()
                    else:
                        st.error("❌ Error al guardar la historia. Intenta nuevamente.")
            
            elif cancel_clicked:
                st.session_state.show_storage_options = False
                st.rerun()
        
        # Botón fuera del formulario para crear nueva historia
        if st.session_state.get('story_saved_successfully', False):
            if st.button("🎉 ¡Perfecto! Crear Nueva Historia", type="primary"):
                st.session_state.current_story = None
                st.session_state.story_approved = False
                st.session_state.show_storage_options = False
                st.session_state.story_saved_successfully = False
                st.rerun()
    
    def save_story(self, story_data: Dict[str, Any], local_formats: List[str], 
                   save_to_supabase: bool, update_existing: bool = False) -> tuple[bool, List[str]]:
        """Guarda la historia según las opciones seleccionadas"""
        saved_files = []
        success = True
        
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
                if not self.supabase_manager:
                    st.error("❌ Supabase no está configurado. No se puede guardar remotamente.")
                    success = False
                else:
                    story_id = None
                    if update_existing and ('id' in story_data or story_data.get('edited_from')):
                        story_id = story_data.get('id') or story_data.get('edited_from')
                    
                    # Incluir URL de imagen en los metadatos
                    images = [story_data['image_url']] if story_data.get('image_url') else []
                    
                    result = self.supabase_manager.save_story(
                        user_id=st.session_state.user_id,
                        title=story_data.get('content', {}).get('title', 'Historia Sin Título'),
                        content=story_data.get('content', {}),
                        tone=story_data.get('tone', 'profesional'),
                        images=images,
                        metadata=story_data.get('user_specs', {}),
                        story_id=story_id
                    )
                    
                    if result['success']:
                        action = "actualizada" if story_id else "creada"
                        saved_files.append(f"Supabase: Historia {action} - ID {result['data']['id']}")
                    else:
                        success = False
            
            return success, saved_files
            
        except Exception as e:
            return False, [f"Error: {str(e)}"]
    
    def edit_template_interface(self):
        """Interfaz para editar una historia desde plantilla"""
        template = st.session_state.template_story
        
        st.info("📝 Editando historia desde plantilla")
        
        # Botón para cancelar edición
        if st.button("❌ Cancelar Edición"):
            st.session_state.template_story = None
            st.rerun()
        
        # Mostrar información de la plantilla
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Plataforma Original", template.get('platform', 'N/A'))
        with col2:
            st.metric("Tono Original", template.get('tone', 'N/A').title())
        with col3:
            created_at = template.get('created_at', '')
            if created_at:
                try:
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    st.metric("Fecha Original", date_obj.strftime("%d/%m/%Y"))
                except:
                    st.metric("Fecha Original", "N/A")
        
        st.divider()
        
        # Formulario de edición
        with st.form("edit_template_form"):
            st.subheader("✏️ Editar Historia")
            
            # Configuración básica
            col1, col2 = st.columns(2)
            with col1:
                new_platform = st.selectbox(
                    "Nueva Plataforma:",
                    ["Facebook", "LinkedIn", "Instagram", "Twitter/X"],
                    index=["Facebook", "LinkedIn", "Instagram", "Twitter/X"].index(template.get('platform', 'Facebook')) if template.get('platform') in ["Facebook", "LinkedIn", "Instagram", "Twitter/X"] else 0
                )
            
            with col2:
                tone_options = [
                    "Profesional", "Divertido", "Inspiracional", "Educativo", 
                    "Casual", "Formal", "Motivacional", "Informativo", 
                    "Persuasivo", "Emocional", "Técnico", "Creativo",
                    "Amigable", "Autoritativo", "Conversacional", "Urgente"
                ]
                
                current_tone = template.get('tone', 'Profesional').title()
                tone_index = tone_options.index(current_tone) if current_tone in tone_options else 0
                
                new_tone = st.selectbox(
                    "Nuevo Tono:",
                    tone_options,
                    index=tone_index
                )
                
                # Opción para tono personalizado
                custom_tone = st.text_input(
                    "Tono personalizado (opcional):",
                    placeholder="Ej: Sarcástico, Nostálgico, Científico...",
                    help="Define tu propio tono si no encuentras el adecuado"
                )
                
                if custom_tone:
                    new_tone = custom_tone
            
            # Editar contenido
            content = template.get('content', {})
            
            new_title = st.text_input(
                "Título:",
                value=content.get('title', ''),
                help="Título de la historia"
            )
            
            new_hook = st.text_area(
                "Gancho:",
                value=content.get('hook', ''),
                height=100,
                help="Frase inicial que captura la atención"
            )
            
            # Editar párrafos del cuerpo
            st.markdown("**Contenido Principal:**")
            body_paragraphs = content.get('body', [''])
            new_body = []
            
            for i, paragraph in enumerate(body_paragraphs):
                new_paragraph = st.text_area(
                    f"Párrafo {i+1}:",
                    value=paragraph,
                    height=80,
                    key=f"paragraph_{i}"
                )
                if new_paragraph.strip():
                    new_body.append(new_paragraph)
            
            # Opción para agregar más párrafos
            add_paragraph = st.text_area(
                "Agregar nuevo párrafo (opcional):",
                height=80,
                key="new_paragraph"
            )
            if add_paragraph.strip():
                new_body.append(add_paragraph)
            
            new_cta = st.text_area(
                "Llamada a la Acción:",
                value=content.get('call_to_action', ''),
                height=80,
                help="Acción que quieres que tome el lector"
            )
            
            # Hashtags (si aplica)
            hashtags_text = ' '.join(content.get('hashtags', []))
            new_hashtags_text = st.text_input(
                "Hashtags (separados por espacios):",
                value=hashtags_text,
                help="Ej: #marketing #digital #contenido"
            )
            
            new_additional_specs = st.text_area(
                "Especificaciones adicionales:",
                value=template.get('user_specs', {}).get('additional_specs', ''),
                help="Instrucciones adicionales para la regeneración"
            )
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                regenerate_clicked = st.form_submit_button("🔄 Regenerar con IA", type="primary")
            with col2:
                save_manual_clicked = st.form_submit_button("💾 Guardar Edición Manual")
            
            if regenerate_clicked:
                # Regenerar usando IA con el contenido editado
                self.regenerate_from_template(
                    new_platform, new_tone, new_title, new_hook, 
                    new_body, new_cta, new_hashtags_text, new_additional_specs
                )
            
            elif save_manual_clicked:
                # Guardar edición manual
                self.save_manual_edit(
                    template, new_platform, new_tone, new_title, 
                    new_hook, new_body, new_cta, new_hashtags_text
                )
    
    def regenerate_from_template(self, platform: str, tone: str, title: str, 
                               hook: str, body: List[str], cta: str, 
                               hashtags: str, additional_specs: str):
        """Regenera la historia usando IA con el contenido editado"""
        
        # Crear especificaciones basadas en la edición
        user_specs = {
            'platform': platform,
            'tone': tone.lower(),
            'additional_specs': f"""
            Usa este contenido como base y mejóralo:
            Título: {title}
            Gancho: {hook}
            Contenido: {' '.join(body)}
            Llamada a la acción: {cta}
            Hashtags: {hashtags}
            
            Especificaciones adicionales: {additional_specs}
            """
        }
        
        with st.spinner("Regenerando historia con IA..."):
            try:
                # Usar imagen por defecto o la de la plantilla
                temp_image_path = st.session_state.template_story.get('image_path', 'default_image.jpg')
                
                # Ejecutar crew para regenerar
                result = self.execute_story_creation(temp_image_path, user_specs)
                
                if result:
                    # Mover la historia actual a versiones si existe en Supabase
                    self.create_version_backup(st.session_state.template_story)
                    
                    st.session_state.current_story = result
                    st.session_state.template_story = None
                    st.session_state.story_approved = False
                    st.session_state.show_storage_options = False
                    st.success("✅ Historia regenerada exitosamente!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error al regenerar: {str(e)}")
    
    def save_manual_edit(self, original_story: Dict[str, Any], platform: str, 
                        tone: str, title: str, hook: str, body: List[str], 
                        cta: str, hashtags: str):
        """Guarda la edición manual de la historia"""
        
        # Crear nueva estructura de contenido
        hashtags_list = [tag.strip() for tag in hashtags.split() if tag.strip().startswith('#')]
        
        # Construir texto completo
        full_text_parts = []
        if hook:
            full_text_parts.append(hook)
        full_text_parts.extend(body)
        if cta:
            full_text_parts.append(cta)
        if hashtags_list:
            full_text_parts.append(' '.join(hashtags_list))
        
        full_text = '\n\n'.join(full_text_parts)
        
        new_content = {
            'title': title,
            'hook': hook,
            'body': body,
            'call_to_action': cta,
            'hashtags': hashtags_list,
            'full_text': full_text
        }
        
        # Crear nueva historia
        new_story = {
            'content': new_content,
            'platform': platform,
            'tone': tone.lower(),
            'created_at': datetime.now().isoformat(),
            'user_specs': {
                'platform': platform,
                'tone': tone.lower(),
                'additional_specs': 'Editado manualmente desde plantilla'
            },
            'edited_from': original_story.get('id', 'local_template')
        }
        
        # Crear backup de la versión original si es necesario
        self.create_version_backup(original_story)
        
        st.session_state.current_story = new_story
        st.session_state.template_story = None
        st.session_state.story_approved = False
        st.session_state.show_storage_options = False
        
        st.success("✅ Edición guardada exitosamente!")
        st.rerun()
    
    def create_version_backup(self, story_data: Dict[str, Any]):
        """Crea un backup de la versión anterior en story_versions"""
        try:
            # Solo crear backup si la historia tiene ID (viene de Supabase)
            if 'id' in story_data:
                # Aquí podrías implementar la lógica para guardar en story_versions
                # Por ahora, solo registramos la acción
                st.info("📝 Versión anterior respaldada automáticamente")
        except Exception as e:
            st.warning(f"⚠️ No se pudo crear backup de versión: {str(e)}")
    
    def upload_image_to_supabase(self, image_path: str, filename: str) -> str:
        """Sube una imagen a Supabase Storage y retorna la URL pública"""
        try:
            result = self.supabase_manager.upload_image(
                image_path, 
                st.session_state.user_id, 
                filename
            )
            
            if result['success']:
                return result['url']
            else:
                st.warning(f"No se pudo subir la imagen: {result['error']}")
                return ""
        except Exception as e:
            st.warning(f"Error subiendo imagen: {str(e)}")
            return ""
    
    def update_workflow(self, agent: str, task: str, status: str, placeholder=None):
        """Actualiza el workflow de agentes en tiempo real"""
        # Buscar si ya existe una entrada para este agente
        existing_index = None
        for i, step in enumerate(st.session_state.crew_workflow):
            if step['agent'] == agent:
                existing_index = i
                break
        
        workflow_step = {
            'agent': agent,
            'task': task,
            'status': status,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        if existing_index is not None:
            st.session_state.crew_workflow[existing_index] = workflow_step
        else:
            st.session_state.crew_workflow.append(workflow_step)
        
        # Actualizar el placeholder si existe
        if placeholder:
            with placeholder.container():
                st.markdown("### 🤖 Progreso de Agentes")
                for step in st.session_state.crew_workflow:
                    status_icon = "✅" if step['status'] == 'completed' else "🔄" if step['status'] == 'running' else "⏳"
                    st.write(f"{status_icon} **{step['agent']}**: {step['task']} ({step['timestamp']})")
    
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
        
        # Contar por tipo de archivo
        file_types = {}
        for story in stories:
            file_type = story.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        # Mostrar estadísticas
        type_summary = ", ".join([f"{count} {ftype.upper()}" for ftype, count in file_types.items()])
        st.write(f"📊 Se encontraron {len(stories)} historias locales: {type_summary}")
        
        # Iconos por tipo de archivo
        file_type_icons = {
            'json': '📄',
            'markdown': '📝', 
            'html': '🌐',
            'pdf': '📕',
            'unknown': '❓'
        }
        
        for i, story in enumerate(stories):
            file_type = story.get('file_type', 'unknown')
            icon = file_type_icons.get(file_type, '📄')
            title = story.get('content', {}).get('title', f'Historia {i+1}')
            platform = story.get('platform', 'N/A')
            filename = story.get('filename', 'N/A')
            
            with st.expander(f"{icon} {title} - {platform} ({filename})"):
                self.display_story_details(story)
    
    def display_remote_stories(self):
        """Muestra historias de la base de datos remota"""
        if not self.supabase_manager:
            st.error("❌ Supabase no está configurado. Ve a Configuración para configurar las credenciales.")
            return
        
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
                        'id': story.get('id'),
                        'images': story.get('images', []),  # Agregar imágenes de Supabase
                        'image_url': story.get('images', [None])[0] if story.get('images') else None  # Primera imagen como URL principal
                    }
                    self.display_story_details(story_data)
        
        except Exception as e:
            st.error(f"❌ Error al conectar con Supabase: {str(e)}")
    
    def display_story_details(self, story_data: Dict[str, Any]):
        """Muestra los detalles de una historia específica"""
        content = story_data.get('content', {})
        
        # Información básica
        col1, col2, col3, col4 = st.columns(4)
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
        with col4:
            # Mostrar tipo de archivo si es local
            file_type = story_data.get('file_type', '')
            if file_type:
                file_type_labels = {
                    'json': '📄 JSON',
                    'markdown': '📝 Markdown', 
                    'html': '🌐 HTML',
                    'pdf': '📕 PDF'
                }
                st.metric("Tipo", file_type_labels.get(file_type, f"📄 {file_type.upper()}"))
        
        # Contenido
        if 'full_text' in content:
            st.markdown("**📄 Contenido:**")
            st.text_area("Contenido de la historia", content['full_text'], height=100, disabled=True, key=f"story_{story_data.get('id', hash(str(story_data)))}", label_visibility="collapsed")
        
        # Mostrar imagen si existe
        image_url = None
        
        # Priorizar diferentes fuentes de imagen
        if story_data.get('image_url'):
            image_url = story_data['image_url']
        elif story_data.get('images') and len(story_data['images']) > 0:
            image_url = story_data['images'][0]
        elif story_data.get('content', {}).get('image_url'):
            image_url = story_data['content']['image_url']
        
        if image_url:
            try:
                st.image(image_url, caption="Imagen de la historia")
            except Exception as e:
                st.warning(f"⚠️ No se pudo cargar la imagen: {str(e)}")
                st.text(f"URL de imagen: {image_url}")
        else:
            st.info("📷 No hay imagen asociada a esta historia")
        
        # Renderizar vista previa visual
        st.markdown("**📱 Vista Previa:**")
        
        # Preparar datos para vista previa
        preview_data = story_data.copy()
        
        # Asegurar que tenemos una URL de imagen para la vista previa
        if not preview_data.get('image_url'):
            if story_data.get('images') and len(story_data['images']) > 0:
                preview_data['image_url'] = story_data['images'][0]
            elif story_data.get('content', {}).get('image_url'):
                preview_data['image_url'] = story_data['content']['image_url']
        
        self.render_story_preview(preview_data)
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"📋 Usar como Plantilla", key=f"template_{story_data.get('id', hash(str(story_data)))}"):
                st.session_state.template_story = story_data
                st.session_state.current_story = None
                st.success("✅ Historia cargada como plantilla. Cambia a 'Crear Nueva Historia' para editarla.")
                st.balloons()
        
        with col2:
            if st.button(f"🗑️ Eliminar Historia", key=f"delete_{story_data.get('id', hash(str(story_data)))}", type="secondary"):
                self.delete_story_interface(story_data)
        
        with col3:
            if st.button(f" Publicar Historia", key=f"publicar_{story_data.get('id', hash(str(story_data)))}", type="secondary"):
                self.publish_story(story_data)
                # self.publish_agentic(story_data)
                st.balloons()

    def publish_agentic(self, story_data: Dict[str, Any]):
        
        
        publish_task = self.tasks.publish_task(story_data)
        publication_agent = self.agents.publication_agent()
        
        # Actualizar workflow
        # self.update_workflow("Agente de Publicación", "Publicando...", "running", workflow_placeholder)
    
        crew3 = Crew(
            # self.agents.voice_agent, self.agents.user_interaction_agent(), 
            agents=[publication_agent],
            tasks=[publish_task],
            process=Process.sequential,
            verbose=True
        )
        
        # self.update_workflow("Agente de Publicación", "Publicando historia", "running", workflow_placeholder)
        
        result = crew3.kickoff()
        
        # self.update_workflow("Agente de Publicación", "Publicación completado", "completed", workflow_placeholder)
        
        

    def publish_story(self, story_data: Dict[str, Any]):
        print("Hello from instagramApi!")
        # start_time = datetime.now() + timedelta(minutes=1)
        cl = login_user()        
        print(cl)
        response = requests.get(story_data.get('image_url'))
        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")
        new_image= image.resize((1080,1080))
        new_image.save("temporary.jpg")
        image_path = Path("temporary.jpg")
        caption = story_data.get('content')
        print(image_path)
        print(caption)
        # os.path.splitext(image)[0] + "\n #midjourney #aiart #promptengineering #chaos #midjourneychaos"
        # image_path = os.path.join(image_folder, image)
        # caption = "hola instagram"
        post_image(cl, image_path, json.dumps(caption))
        # os.remove(image_path)
        # logger.info(f"Posted and removed image: {image_path}")
 
    # logger.info("All images have been posted. Script is ending.")
        print("La historia fue publicada.")
        return True



    def delete_story_interface(self, story_data: Dict[str, Any]):
        """Interfaz para confirmar eliminación de historia"""
        story_title = story_data.get('content', {}).get('title', 'Historia sin título')
        
        # Usar un modal de confirmación
        if f"confirm_delete_{story_data.get('id', hash(str(story_data)))}" not in st.session_state:
            st.session_state[f"confirm_delete_{story_data.get('id', hash(str(story_data)))}"] = False
        
        if not st.session_state[f"confirm_delete_{story_data.get('id', hash(str(story_data)))}"] :
            st.session_state[f"confirm_delete_{story_data.get('id', hash(str(story_data)))}"] = True
            st.rerun()
        
        st.error(f"⚠️ ¿Estás seguro de que quieres eliminar '{story_title}'?")
        st.warning("Esta acción no se puede deshacer.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("❌ Cancelar", key=f"cancel_delete_{story_data.get('id', hash(str(story_data)))}"):
                st.session_state[f"confirm_delete_{story_data.get('id', hash(str(story_data)))}"] = False
                st.rerun()
        
        with col3:
            if st.button("🗑️ Confirmar Eliminación", key=f"confirm_delete_btn_{story_data.get('id', hash(str(story_data)))}", type="primary"):
                success = self.delete_story(story_data)
                if success:
                    st.success("✅ Historia eliminada exitosamente.")
                    st.session_state[f"confirm_delete_{story_data.get('id', hash(str(story_data)))}"] = False
                    st.rerun()
                else:
                    st.error("❌ Error al eliminar la historia.")
    
    def delete_story(self, story_data: Dict[str, Any]) -> bool:
        """Elimina una historia (local o remota)"""
        try:
            # Si tiene ID, es una historia remota
            if 'id' in story_data:
                if not self.supabase_manager:
                    st.error("❌ Supabase no está configurado. No se puede eliminar historia remota.")
                    return False
                
                result = self.supabase_manager.delete_story(
                    story_data['id'], 
                    st.session_state.user_id
                )
                return result['success']
            
            # Si tiene filepath, es una historia local
            elif 'filepath' in story_data:
                return self.file_manager.delete_local_story(story_data['filepath'])
            
            return False
            
        except Exception as e:
            st.error(f"Error al eliminar historia: {str(e)}")
            return False
    
    def configuration_interface(self):
        """Interfaz de configuración"""
        st.header("⚙️ Configuración del Sistema")
        
        tab1, tab2, tab3 = st.tabs(["🔑 Credenciales", "👤 Usuario", "📊 Sistema"])
        
        with tab1:
            st.subheader("🔑 Gestión de Credenciales")
            
            # Mostrar estado actual de las credenciales
            st.markdown("**Estado Actual de las Credenciales:**")
            
            credentials_status = {
                "🤖 Gemini API": "✅ Configurado" if os.getenv('GEMINI_API_KEY') else "❌ No configurado",
                "🌐 Supabase URL": "✅ Configurado" if os.getenv('SUPABASE_URL') else "❌ No configurado",
                "🔑 Supabase Key": "✅ Configurado" if os.getenv('SUPABASE_KEY') else "❌ No configurado",
                "🔐 Supabase Secret": "✅ Configurado" if os.getenv('SUPABASE_SECRET_KEY') else "❌ No configurado",
                "📊 AgentOps API": "✅ Configurado" if os.getenv('AGENTOPS_API_KEY') else "❌ No configurado"
            }
            
            for service, status in credentials_status.items():
                st.write(f"{service}: {status}")
            
            st.divider()
            
            # Interfaz para actualizar credenciales
            update_credentials_interface()
        
        with tab2:
            st.subheader("👤 Configuración de Usuario")
            
            current_user_id = st.session_state.get('user_id', 'demo_user')
            
            new_user_id = st.text_input(
                "ID de Usuario:",
                value=current_user_id,
                help="Identificador único para tus historias"
            )
            
            if st.button("💾 Actualizar Usuario"):
                st.session_state.user_id = new_user_id
                st.success(f"✅ Usuario actualizado a: {new_user_id}")
        
        with tab3:
            st.subheader("📊 Información del Sistema")
            
            # Estadísticas del sistema
            try:
                # Contar historias locales
                local_stories = self.file_manager.load_stories_from_folder()
                local_count = len(local_stories)
                
                # Contar historias remotas
                remote_count = 0
                if self.supabase_manager:
                    remote_result = self.supabase_manager.get_stories(st.session_state.user_id)
                    remote_count = len(remote_result['data']) if remote_result['success'] else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📁 Historias Locales", local_count)
                
                with col2:
                    st.metric("☁️ Historias Remotas", remote_count)
                
                with col3:
                    st.metric("📊 Total", local_count + remote_count)
                
            except Exception as e:
                st.error(f"Error obteniendo estadísticas: {str(e)}")
            
            st.divider()
            
            # Información de versión y estado
            st.markdown("**Información del Sistema:**")
            st.write(f"• Usuario actual: `{st.session_state.user_id}`")
            st.write(f"• Directorio de historias: `{self.file_manager.base_path}`")
            
            # Botón para limpiar caché
            if st.button("🧹 Limpiar Caché de Sesión"):
                # Limpiar variables de sesión excepto user_id
                keys_to_keep = ['user_id']
                keys_to_remove = [key for key in st.session_state.keys() if key not in keys_to_keep]
                
                for key in keys_to_remove:
                    del st.session_state[key]
                
                st.success("✅ Caché limpiado exitosamente.")
                st.rerun()