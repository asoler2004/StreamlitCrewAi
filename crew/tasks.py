from crewai import Task
from typing import Dict, Any

class StoryTasks:
    def __init__(self, agents):
        self.agents = agents
    
    def analyze_image_task(self, image_path: str) -> Task:
        return Task(
            description=f"""
            Analiza la imagen ubicada en: {image_path}
            
            Tu trabajo es:
            1. Usar la herramienta de análisis de imagen para obtener una descripción básica
            2. Expandir esa descripción con detalles adicionales sobre:
               - Elementos visuales principales
               - Colores dominantes
               - Emociones que transmite
               - Contexto o situación mostrada
               - Posibles interpretaciones o mensajes
            
            Proporciona una descripción rica y detallada que sirva como base para crear contenido compelling.
            """,
            agent=self.agents.vision_agent(),
            expected_output="Una descripción detallada y rica de la imagen que incluya elementos visuales, emociones, contexto y posibles interpretaciones para crear contenido."
        )
    
    def create_facebook_content_task(self, image_description: str, user_specs: Dict[str, Any]) -> Task:
        return Task(
            description=f"""
            Crea contenido optimizado para Facebook basado en:
            
            Descripción de la imagen: {image_description}
            Especificaciones del usuario: {user_specs}
            Tono deseado: {user_specs.get('tone', 'profesional')}
            Especificaciones adicionales: {user_specs.get('additional_specs', 'Ninguna')}
            
            Crea un post de Facebook que incluya:
            1. Un hook atractivo que capture la atención en los primeros segundos
            2. Contenido principal dividido en párrafos cortos y fáciles de leer
            3. Una llamada a la acción clara y específica
            4. Uso estratégico de emojis
            5. El texto completo optimizado para Facebook
            
            El contenido debe ser engaging, apropiado para el tono especificado, y diseñado para generar interacción.
            """,
            agent=self.agents.facebook_agent(),
            expected_output="""Un objeto JSON con la estructura:
            {
                "title": "Título del post",
                "hook": "Gancho inicial atractivo",
                "body": ["párrafo 1", "párrafo 2", "párrafo 3"],
                "call_to_action": "Llamada a la acción específica",
                "full_text": "Texto completo del post optimizado para Facebook"
            }"""
        )
    
    def create_linkedin_content_task(self, image_description: str, user_specs: Dict[str, Any]) -> Task:
        return Task(
            description=f"""
            Crea contenido profesional optimizado para LinkedIn basado en:
            
            Descripción de la imagen: {image_description}
            Especificaciones del usuario: {user_specs}
            Tono deseado: {user_specs.get('tone', 'profesional')}
            Especificaciones adicionales: {user_specs.get('additional_specs', 'Ninguna')}
            
            Crea un post de LinkedIn que incluya:
            1. Un hook profesional que genere curiosidad
            2. Contenido que aporte valor profesional o insights
            3. Storytelling personal o profesional relevante
            4. Una llamada a la acción que fomente networking o conversación profesional
            5. Hashtags relevantes y estratégicos
            6. Tono profesional pero accesible
            
            El contenido debe posicionar al autor como experto y generar conversación profesional.
            """,
            agent=self.agents.linkedin_agent(),
            expected_output="""Un objeto JSON con la estructura:
            {
                "title": "Título del post",
                "hook": "Gancho profesional inicial",
                "body": ["párrafo 1", "párrafo 2", "párrafo 3"],
                "call_to_action": "Llamada a la acción profesional",
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
                "full_text": "Texto completo del post optimizado para LinkedIn"
            }"""
        )
    
    def create_instagram_content_task(self, image_description: str, user_specs: Dict[str, Any]) -> Task:
        return Task(
            description=f"""
            Crea contenido visual optimizado para Instagram basado en:
            
            Descripción de la imagen: {image_description}
            Especificaciones del usuario: {user_specs}
            Tono deseado: {user_specs.get('tone', 'profesional')}
            Especificaciones adicionales: {user_specs.get('additional_specs', 'Ninguna')}
            
            Crea un post de Instagram que incluya:
            1. Un caption que complemente perfectamente la imagen
            2. Hook visual que funcione en los primeros segundos
            3. Contenido estructurado con line breaks para fácil lectura
            4. Emojis estratégicamente ubicados
            5. Hashtags relevantes y populares (mezcla de grandes y nicho)
            6. Llamada a la acción que fomente engagement
            
            El contenido debe ser visualmente atractivo y optimizado para el algoritmo de Instagram.
            """,
            agent=self.agents.instagram_agent(),
            expected_output="""Un objeto JSON con la estructura:
            {
                "title": "Título del post",
                "hook": "Gancho visual inicial",
                "body": ["párrafo 1", "párrafo 2", "párrafo 3"],
                "call_to_action": "Llamada a la acción para engagement",
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
                "full_text": "Caption completo optimizado para Instagram"
            }"""
        )
    
    def create_twitter_content_task(self, image_description: str, user_specs: Dict[str, Any]) -> Task:
        return Task(
            description=f"""
            Crea contenido conciso optimizado para Twitter/X basado en:
            
            Descripción de la imagen: {image_description}
            Especificaciones del usuario: {user_specs}
            Tono deseado: {user_specs.get('tone', 'profesional')}
            Especificaciones adicionales: {user_specs.get('additional_specs', 'Ninguna')}
            
            Crea contenido para Twitter que incluya:
            1. Un tweet principal impactante y conciso
            2. Si es necesario, un hilo (thread) de 2-3 tweets adicionales
            3. Uso estratégico de hashtags (máximo 2-3)
            4. Llamada a la acción clara y directa
            5. Tono apropiado para la cultura de Twitter
            
            El contenido debe ser punchy, generar conversación y estar optimizado para retweets.
            """,
            agent=self.agents.twitter_agent(),
            expected_output="""Un objeto JSON con la estructura:
            {
                "title": "Título del contenido",
                "main_tweet": "Tweet principal",
                "thread": ["tweet 2", "tweet 3"] (si aplica),
                "hashtags": ["#hashtag1", "#hashtag2"],
                "call_to_action": "Llamada a la acción",
                "full_text": "Contenido completo para Twitter"
            }"""
        )
    
    def storage_task(self, content: Dict[str, Any], storage_options: Dict[str, Any]) -> Task:
        return Task(
            description=f"""
            Gestiona el almacenamiento del contenido creado según las opciones especificadas:
            
            Contenido a almacenar: {content}
            Opciones de almacenamiento: {storage_options}
            
            Tu trabajo es:
            1. Si se solicita almacenamiento local, guardar en los formatos especificados (JSON, MD, HTML, PDF)
            2. Si se solicita almacenamiento remoto, guardar en la base de datos Supabase
            3. Si hay imágenes, subirlas al storage correspondiente
            4. Asegurar que todos los metadatos estén completos
            5. Proporcionar confirmación de que el almacenamiento fue exitoso
            
            Mantén la integridad de los datos y asegúrate de que el contenido esté correctamente estructurado.
            """,
            agent=self.agents.storage_agent(),
            expected_output="Confirmación detallada del almacenamiento realizado, incluyendo rutas de archivos creados y/o IDs de base de datos."
        )