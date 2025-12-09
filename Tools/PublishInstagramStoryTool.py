from crewai.tools import BaseTool
from utils.publicar import login_user,post_image, generate_daily_schedule, schedule_and_post
from typing import Dict, Any, List
import requests
from io import BytesIO
from PIL import Image
from pathlib import Path
import sys
sys.path.append('../')

class PublishInstagramStoryTool(BaseTool):
    name: str = "Story Publishing Tool"
    description: str = (
        "Publica la historia seleccionada en Instagram."
    )
    
    def _run(self, story_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Publica la historia en la red social seleccionada"""
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

publish_instagram_story_tool = PublishInstagramStoryTool()