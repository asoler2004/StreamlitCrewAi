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
                   images: List[str] = None, metadata: Dict = None) -> Dict:
        """Guarda una historia en la base de datos"""
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
            
            result = self.client.table("stories").insert(story_data).execute()
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
            
            storage_path = f"{user_id}/{file_name}"
            
            result = self.client.storage.from_("story-images").upload(
                storage_path, file_data
            )
            
            # Obtener URL pública
            public_url = self.client.storage.from_("story-images").get_public_url(storage_path)
            
            return {"success": True, "url": public_url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_story(self, story_id: str, user_id: str) -> Dict:
        """Elimina una historia"""
        try:
            result = self.client.table("stories")\
                .delete()\
                .eq("id", story_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}