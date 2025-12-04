import os
import json
import markdown
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class FileManager:
    def __init__(self, base_path: str = "stories"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save_as_json(self, story_data: Dict, filename: str = None) -> str:
        """Guarda la historia como archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historia_{timestamp}.json"
        
        filepath = os.path.join(self.base_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def save_as_markdown(self, story_data: Dict, filename: str = None) -> str:
        """Guarda la historia como archivo Markdown"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historia_{timestamp}.md"
        
        filepath = os.path.join(self.base_path, filename)
        
        content = story_data.get('content', {})
        
        md_content = f"""# {content.get('title', 'Historia Sin Título')}

**Tono:** {story_data.get('tone', 'No especificado')}
**Fecha:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

---

## Gancho
{content.get('hook', '')}

## Contenido
"""
        
        for paragraph in content.get('body', []):
            md_content += f"\n{paragraph}\n"
        
        md_content += f"""
## Llamada a la Acción
{content.get('call_to_action', '')}

---

### Texto Completo
{content.get('full_text', '')}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
    
    def save_as_html(self, story_data: Dict, filename: str = None) -> str:
        """Guarda la historia como archivo HTML"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historia_{timestamp}.html"
        
        filepath = os.path.join(self.base_path, filename)
        
        content = story_data.get('content', {})
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.get('title', 'Historia')}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            border-bottom: 2px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            color: #007acc;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .meta {{
            color: #666;
            font-style: italic;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            color: #007acc;
            font-size: 1.3em;
            border-left: 4px solid #007acc;
            padding-left: 15px;
            margin-bottom: 15px;
        }}
        .hook {{
            background: #f0f8ff;
            padding: 20px;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
        }}
        .body-paragraph {{
            margin: 15px 0;
            text-align: justify;
        }}
        .cta {{
            background: #007acc;
            color: white;
            padding: 20px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
        }}
        .full-text {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ccc;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{content.get('title', 'Historia Sin Título')}</h1>
        <div class="meta">
            <strong>Tono:</strong> {story_data.get('tone', 'No especificado')} | 
            <strong>Fecha:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Gancho</h2>
        <div class="hook">{content.get('hook', '')}</div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Contenido</h2>"""
        
        for paragraph in content.get('body', []):
            html_content += f'<div class="body-paragraph">{paragraph}</div>'
        
        html_content += f"""
    </div>
    
    <div class="section">
        <h2 class="section-title">Llamada a la Acción</h2>
        <div class="cta">{content.get('call_to_action', '')}</div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Texto Completo</h2>
        <div class="full-text">{content.get('full_text', '')}</div>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def save_as_pdf(self, story_data: Dict, filename: str = None) -> str:
        """Guarda la historia como archivo PDF"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historia_{timestamp}.pdf"
        
        filepath = os.path.join(self.base_path, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#007acc')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#007acc')
        )
        
        content = story_data.get('content', {})
        story = []
        
        # Título
        story.append(Paragraph(content.get('title', 'Historia Sin Título'), title_style))
        story.append(Spacer(1, 12))
        
        # Metadatos
        meta_text = f"<b>Tono:</b> {story_data.get('tone', 'No especificado')} | <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(meta_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Gancho
        story.append(Paragraph("Gancho", subtitle_style))
        story.append(Paragraph(content.get('hook', ''), styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Contenido
        story.append(Paragraph("Contenido", subtitle_style))
        for paragraph in content.get('body', []):
            story.append(Paragraph(paragraph, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Llamada a la acción
        story.append(Spacer(1, 20))
        story.append(Paragraph("Llamada a la Acción", subtitle_style))
        story.append(Paragraph(content.get('call_to_action', ''), styles['Normal']))
        
        doc.build(story)
        return filepath
    
    def load_stories_from_folder(self) -> List[Dict]:
        """Carga todas las historias guardadas localmente"""
        stories = []
        
        if not os.path.exists(self.base_path):
            return stories
        
        for filename in os.listdir(self.base_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.base_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        story_data = json.load(f)
                        story_data['filename'] = filename
                        story_data['filepath'] = filepath
                        stories.append(story_data)
                except Exception as e:
                    print(f"Error cargando {filename}: {e}")
        
        return sorted(stories, key=lambda x: x.get('created_at', ''), reverse=True)