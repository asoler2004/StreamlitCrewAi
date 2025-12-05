import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

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
    
    def parse_markdown_file(self, filepath: str) -> Optional[Dict]:
        """Parsea un archivo Markdown y extrae la información de la historia"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer título (primera línea con #)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else 'Historia Sin Título'
            
            # Extraer metadatos
            tone_match = re.search(r'\*\*Tono:\*\*\s*(.+)', content)
            tone = tone_match.group(1) if tone_match else 'No especificado'
            
            date_match = re.search(r'\*\*Fecha:\*\*\s*(.+)', content)
            date_str = date_match.group(1) if date_match else ''
            
            # Extraer secciones
            hook_match = re.search(r'##\s+Gancho\s*\n(.+?)(?=\n##|\n---|\Z)', content, re.DOTALL)
            hook = hook_match.group(1).strip() if hook_match else ''
            
            cta_match = re.search(r'##\s+Llamada a la Acción\s*\n(.+?)(?=\n##|\n---|\Z)', content, re.DOTALL)
            cta = cta_match.group(1).strip() if cta_match else ''
            
            # Extraer texto completo
            full_text_match = re.search(r'###\s+Texto Completo\s*\n(.+)', content, re.DOTALL)
            full_text = full_text_match.group(1).strip() if full_text_match else content
            
            # Extraer contenido del cuerpo
            body_match = re.search(r'##\s+Contenido\s*\n(.+?)(?=\n##|\n---|\Z)', content, re.DOTALL)
            body_text = body_match.group(1).strip() if body_match else ''
            body = [p.strip() for p in body_text.split('\n\n') if p.strip()]
            
            return {
                'content': {
                    'title': title,
                    'hook': hook,
                    'body': body,
                    'call_to_action': cta,
                    'full_text': full_text
                },
                'tone': tone,
                'platform': 'Markdown',
                'created_at': self._extract_date_from_filename(os.path.basename(filepath)),
                'file_type': 'markdown'
            }
            
        except Exception as e:
            print(f"Error parseando archivo Markdown {filepath}: {e}")
            return None
    
    def parse_html_file(self, filepath: str) -> Optional[Dict]:
        """Parsea un archivo HTML y extrae la información de la historia"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not BEAUTIFULSOUP_AVAILABLE:
                # Fallback: usar regex básico si BeautifulSoup no está disponible
                return self._parse_html_with_regex(content, filepath)
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extraer título
            title_elem = soup.find('h1', class_='title') or soup.find('title') or soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else 'Historia Sin Título'
            
            # Extraer metadatos
            meta_elem = soup.find('div', class_='meta')
            tone = 'No especificado'
            if meta_elem:
                tone_match = re.search(r'Tono:\s*(.+?)(?:\s*\||\s*$)', meta_elem.get_text())
                tone = tone_match.group(1).strip() if tone_match else tone
            
            # Extraer secciones
            hook_elem = soup.find('div', class_='hook')
            hook = hook_elem.get_text().strip() if hook_elem else ''
            
            cta_elem = soup.find('div', class_='cta')
            cta = cta_elem.get_text().strip() if cta_elem else ''
            
            # Extraer texto completo
            full_text_elem = soup.find('div', class_='full-text')
            full_text = full_text_elem.get_text().strip() if full_text_elem else ''
            
            # Extraer párrafos del cuerpo
            body_paragraphs = soup.find_all('div', class_='body-paragraph')
            body = [p.get_text().strip() for p in body_paragraphs if p.get_text().strip()]
            
            # Si no hay texto completo, construirlo
            if not full_text:
                full_text = '\n\n'.join([hook] + body + [cta])
            
            return {
                'content': {
                    'title': title,
                    'hook': hook,
                    'body': body,
                    'call_to_action': cta,
                    'full_text': full_text
                },
                'tone': tone,
                'platform': 'HTML',
                'created_at': self._extract_date_from_filename(os.path.basename(filepath)),
                'file_type': 'html'
            }
            
        except Exception as e:
            print(f"Error parseando archivo HTML {filepath}: {e}")
            return None
    
    def _parse_html_with_regex(self, content: str, filepath: str) -> Optional[Dict]:
        """Fallback para parsear HTML usando regex cuando BeautifulSoup no está disponible"""
        try:
            # Extraer título
            title_match = re.search(r'<h1[^>]*class=["\']title["\'][^>]*>(.+?)</h1>', content, re.DOTALL | re.IGNORECASE)
            if not title_match:
                title_match = re.search(r'<title>(.+?)</title>', content, re.IGNORECASE)
            if not title_match:
                title_match = re.search(r'<h1[^>]*>(.+?)</h1>', content, re.DOTALL | re.IGNORECASE)
            
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else 'Historia Sin Título'
            
            # Extraer texto de elementos con clases específicas
            hook_match = re.search(r'<div[^>]*class=["\']hook["\'][^>]*>(.+?)</div>', content, re.DOTALL | re.IGNORECASE)
            hook = re.sub(r'<[^>]+>', '', hook_match.group(1)).strip() if hook_match else ''
            
            cta_match = re.search(r'<div[^>]*class=["\']cta["\'][^>]*>(.+?)</div>', content, re.DOTALL | re.IGNORECASE)
            cta = re.sub(r'<[^>]+>', '', cta_match.group(1)).strip() if cta_match else ''
            
            full_text_match = re.search(r'<div[^>]*class=["\']full-text["\'][^>]*>(.+?)</div>', content, re.DOTALL | re.IGNORECASE)
            full_text = re.sub(r'<[^>]+>', '', full_text_match.group(1)).strip() if full_text_match else ''
            
            # Extraer párrafos del cuerpo
            body_matches = re.findall(r'<div[^>]*class=["\']body-paragraph["\'][^>]*>(.+?)</div>', content, re.DOTALL | re.IGNORECASE)
            body = [re.sub(r'<[^>]+>', '', p).strip() for p in body_matches if p.strip()]
            
            return {
                'content': {
                    'title': title,
                    'hook': hook,
                    'body': body,
                    'call_to_action': cta,
                    'full_text': full_text or '\n\n'.join([hook] + body + [cta])
                },
                'tone': 'No especificado',
                'platform': 'HTML',
                'created_at': self._extract_date_from_filename(os.path.basename(filepath)),
                'file_type': 'html'
            }
            
        except Exception as e:
            print(f"Error parseando HTML con regex {filepath}: {e}")
            return None
    
    def parse_pdf_file(self, filepath: str) -> Optional[Dict]:
        """Parsea un archivo PDF y extrae la información de la historia"""
        try:
            if not PYPDF2_AVAILABLE:
                # Si PyPDF2 no está disponible, crear entrada básica
                return {
                    'content': {
                        'title': f'Historia PDF - {os.path.basename(filepath)}',
                        'hook': '',
                        'body': ['Contenido PDF no disponible para lectura automática'],
                        'call_to_action': '',
                        'full_text': 'Archivo PDF - Contenido no extraíble sin PyPDF2'
                    },
                    'tone': 'No especificado',
                    'platform': 'PDF',
                    'created_at': self._extract_date_from_filename(os.path.basename(filepath)),
                    'file_type': 'pdf'
                }
            
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text_content = ''
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + '\n'
            
            # Intentar extraer estructura básica del texto
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            # El primer texto grande probablemente sea el título
            title = lines[0] if lines else 'Historia PDF Sin Título'
            
            # Buscar patrones conocidos
            tone = 'No especificado'
            hook = ''
            cta = ''
            body = []
            
            for i, line in enumerate(lines):
                if 'Tono:' in line:
                    tone = line.split('Tono:')[-1].strip()
                elif 'Gancho' in line and i + 1 < len(lines):
                    hook = lines[i + 1]
                elif 'Llamada a la Acción' in line and i + 1 < len(lines):
                    cta = lines[i + 1]
                elif len(line) > 50 and not any(keyword in line for keyword in ['Tono:', 'Gancho', 'Llamada']):
                    body.append(line)
            
            return {
                'content': {
                    'title': title,
                    'hook': hook,
                    'body': body[:5],  # Limitar a 5 párrafos para evitar sobrecarga
                    'call_to_action': cta,
                    'full_text': text_content[:1000] + '...' if len(text_content) > 1000 else text_content
                },
                'tone': tone,
                'platform': 'PDF',
                'created_at': self._extract_date_from_filename(os.path.basename(filepath)),
                'file_type': 'pdf'
            }
            
        except Exception as e:
            print(f"Error parseando archivo PDF {filepath}: {e}")
            return None
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """Extrae la fecha del nombre del archivo si sigue el patrón historia_YYYYMMDD_HHMMSS"""
        try:
            # Buscar patrón de fecha en el nombre del archivo
            date_match = re.search(r'(\d{8}_\d{6})', filename)
            if date_match:
                date_str = date_match.group(1)
                # Convertir YYYYMMDD_HHMMSS a formato ISO
                dt = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                return dt.isoformat()
            else:
                # Usar fecha de modificación del archivo
                filepath = os.path.join(self.base_path, filename)
                if os.path.exists(filepath):
                    mtime = os.path.getmtime(filepath)
                    return datetime.fromtimestamp(mtime).isoformat()
        except Exception:
            pass
        
        # Fallback: fecha actual
        return datetime.now().isoformat()
    
    def load_stories_from_folder(self) -> List[Dict]:
        """Carga todas las historias guardadas localmente (JSON, MD, HTML, PDF)"""
        stories = []
        
        if not os.path.exists(self.base_path):
            return stories
        
        supported_extensions = {'.json', '.md', '.html', '.htm', '.pdf'}
        
        for filename in os.listdir(self.base_path):
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in supported_extensions:
                continue
                
            filepath = os.path.join(self.base_path, filename)
            story_data = None
            
            try:
                if file_ext == '.json':
                    with open(filepath, 'r', encoding='utf-8') as f:
                        story_data = json.load(f)
                        story_data['file_type'] = 'json'
                
                elif file_ext == '.md':
                    story_data = self.parse_markdown_file(filepath)
                
                elif file_ext in ['.html', '.htm']:
                    story_data = self.parse_html_file(filepath)
                
                elif file_ext == '.pdf':
                    story_data = self.parse_pdf_file(filepath)
                
                if story_data:
                    story_data['filename'] = filename
                    story_data['filepath'] = filepath
                    stories.append(story_data)
                    
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
        
        return sorted(stories, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def delete_local_story(self, filepath: str) -> bool:
        """Elimina una historia local"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error eliminando archivo {filepath}: {e}")
            return False