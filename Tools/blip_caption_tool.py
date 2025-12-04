from crewai.tools import BaseTool
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Cargamos BLIP una sola vez a nivel de módulo
_processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base",
    use_fast=True
)
_blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

class BlipCaptionTool(BaseTool):
    name: str = "Image Captioning Tool"
    description: str = (
        "Genera una descripción breve y precisa del contenido visual de una imagen "
        "a partir de su ruta en disco. Devuelve solo texto descriptivo."
    )

    def _run(self, image_path: str) -> str:
        """
        image_path → ruta al archivo de imagen
        Devuelve → caption en texto
        """
        print(image_path)
        image = Image.open(image_path).convert("RGB")

        inputs = _processor(images=image, return_tensors="pt")
        output = _blip_model.generate(
            **inputs,
            max_new_tokens=50,
            num_beams=3
        )

        caption = _processor.decode(output[0], skip_special_tokens=True)
        print(caption)
        return caption


# Instancia lista para usar en los agentes
blip_caption_tool = BlipCaptionTool()