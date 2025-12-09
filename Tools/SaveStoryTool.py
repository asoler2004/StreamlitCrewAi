from crewai.tools import BaseTool
from typing import Dict, List, Any
import sys
sys.path.append('../')

from utils.supabase_client import SupabaseManager
from utils.file_manager import FileManager

class SaveStoryTool(BaseTool):
    name: str = "Story Saving Tool"
    description: str = (
        "Guarda la historia generada en forma local o remota"
    )
    
    def _run(self, story_data: Dict[str, Any], local_formats: List[str], 
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

save_story_tool = SaveStoryTool()