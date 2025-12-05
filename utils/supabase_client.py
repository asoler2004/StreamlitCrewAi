import os
from supabase import create_client, Client
from typing import Dict, List, Optional
import json
from datetime import datetime

class SupabaseManager:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.secret_key = os.getenv("SUPABASE_SECRET_KEY")
        self.client: Client = create_client(self.url, self.secret_key)
    
    def save_story(self, user_id: str, title: str, content: Dict, tone: str, 
                   images: List[str] = None, metadata: Dict = None, story_id: str = None) -> Dict:
        """Guarda una historia en la base de datos o actualiza una existente"""
        try:
            story_data = {
                "user_id": user_id,
                "title": title,
                "content": content,
                "tone": tone,
                "images": images or [],
                "metadata": metadata or {},
                "status": "published"
            }
            
            if story_id:
                # Actualizar historia existente
                # Primero, crear backup de la versión anterior
                self.create_story_version(story_id)
                
                # Incrementar versión
                current_story = self.client.table("stories").select("version").eq("id", story_id).execute()
                if current_story.data:
                    current_version = current_story.data[0].get("version", 1)
                    story_data["version"] = current_version + 1
                
                result = self.client.table("stories").update(story_data).eq("id", story_id).execute()
            else:
                # Crear nueva historia
                story_data["version"] = 1
                result = self.client.table("stories").insert(story_data).execute()
            
            return {"success": True, "data": result.data[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_story_version(self, story_id: str) -> Dict:
        """Crea una versión backup de una historia antes de actualizarla"""
        try:
            # Obtener la historia actual
            current_story = self.client.table("stories").select("*").eq("id", story_id).execute()
            
            if not current_story.data:
                return {"success": False, "error": "Historia no encontrada"}
            
            story = current_story.data[0]
            
            # Crear entrada en story_versions
            version_data = {
                "story_id": story_id,
                "content": story["content"],
                "version_number": story.get("version", 1),
                "version_notes": f"Backup automático antes de actualización"
            }
            
            result = self.client.table("story_versions").insert(version_data).execute()
            return {"success": True, "data": result.data[0]}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stories(self, user_id: str, limit: int = 50) -> Dict:
        """Obtiene las historias de un usuario"""
        try:
            result = self.client.table("stories")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_story_by_id(self, story_id: str, user_id: str) -> Dict:
        """Obtiene una historia específica por ID"""
        try:
            result = self.client.table("stories")\
                .select("*")\
                .eq("id", story_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Historia no encontrada"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_image(self, file_path: str, user_id: str, file_name: str) -> Dict:
        """Sube una imagen al storage de Supabase"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Generar nombre único para evitar conflictos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            storage_path = f"{user_id}/{timestamp}_{file_name}"
            
            # Intentar subir la imagen
            try:
                result = self.client.storage.from_("story-images").upload(
                    storage_path, file_data
                )
            except Exception as upload_error:
                # Si falla, intentar con upsert (sobrescribir)
                result = self.client.storage.from_("story-images").upload(
                    storage_path, file_data, {"upsert": "true"}
                )
            
            # Obtener URL pública
            public_url = self.client.storage.from_("story-images").get_public_url(storage_path)
            
            return {"success": True, "url": public_url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_image_url(self, image_path: str) -> str:
        """Obtiene la URL pública de una imagen en Supabase Storage"""
        try:
            public_url = self.client.storage.from_("story-images").get_public_url(image_path)
            return public_url
        except Exception as e:
            return ""
    
    def delete_story(self, story_id: str, user_id: str) -> Dict:
        """Elimina una historia y sus versiones asociadas"""
        try:
            # Primero eliminar las versiones asociadas
            self.client.table("story_versions")\
                .delete()\
                .eq("story_id", story_id)\
                .execute()
            
            # Luego eliminar la historia principal
            result = self.client.table("stories")\
                .delete()\
                .eq("id", story_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_image(self, image_path: str) -> Dict:
        """Elimina una imagen del storage de Supabase"""
        try:
            result = self.client.storage.from_("story-images").remove([image_path])
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}