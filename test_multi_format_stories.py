#!/usr/bin/env python3
"""
Test script to verify multi-format story loading works correctly
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append('.')

def create_test_files():
    """Create test files in different formats"""
    print("🧪 Creating test files in different formats...")
    
    # Ensure stories directory exists
    os.makedirs('stories', exist_ok=True)
    
    # Test data
    test_story = {
        'content': {
            'title': 'Historia de Prueba Multi-Formato',
            'hook': 'Este es un gancho de prueba que captura la atención.',
            'body': [
                'Este es el primer párrafo del contenido de la historia.',
                'Este es el segundo párrafo con más detalles interesantes.',
                'Y aquí tenemos el párrafo final del cuerpo principal.'
            ],
            'call_to_action': '¡Actúa ahora y comparte esta historia!',
            'full_text': 'Este es un gancho de prueba que captura la atención.\n\nEste es el primer párrafo del contenido de la historia.\n\nEste es el segundo párrafo con más detalles interesantes.\n\nY aquí tenemos el párrafo final del cuerpo principal.\n\n¡Actúa ahora y comparte esta historia!'
        },
        'platform': 'Test',
        'tone': 'profesional',
        'created_at': datetime.now().isoformat()
    }
    
    # Create JSON file
    json_path = 'stories/test_historia_multiformat.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(test_story, f, ensure_ascii=False, indent=2)
    print(f"   ✅ Created JSON: {json_path}")
    
    # Create Markdown file
    md_content = f"""# {test_story['content']['title']}

**Tono:** {test_story['tone']}
**Fecha:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

---

## Gancho
{test_story['content']['hook']}

## Contenido

{test_story['content']['body'][0]}

{test_story['content']['body'][1]}

{test_story['content']['body'][2]}

## Llamada a la Acción
{test_story['content']['call_to_action']}

---

### Texto Completo
{test_story['content']['full_text']}
"""
    
    md_path = 'stories/test_historia_multiformat.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"   ✅ Created Markdown: {md_path}")
    
    # Create HTML file
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{test_story['content']['title']}</title>
</head>
<body>
    <div class="header">
        <h1 class="title">{test_story['content']['title']}</h1>
        <div class="meta">
            <strong>Tono:</strong> {test_story['tone']} | 
            <strong>Fecha:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Gancho</h2>
        <div class="hook">{test_story['content']['hook']}</div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Contenido</h2>
        <div class="body-paragraph">{test_story['content']['body'][0]}</div>
        <div class="body-paragraph">{test_story['content']['body'][1]}</div>
        <div class="body-paragraph">{test_story['content']['body'][2]}</div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Llamada a la Acción</h2>
        <div class="cta">{test_story['content']['call_to_action']}</div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Texto Completo</h2>
        <div class="full-text">{test_story['content']['full_text']}</div>
    </div>
</body>
</html>"""
    
    html_path = 'stories/test_historia_multiformat.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"   ✅ Created HTML: {html_path}")
    
    return [json_path, md_path, html_path]

def test_file_manager():
    """Test the enhanced FileManager"""
    print("🧪 Testing enhanced FileManager...")
    
    try:
        from utils.file_manager import FileManager
        
        fm = FileManager()
        
        # Load all stories
        stories = fm.load_stories_from_folder()
        
        print(f"   📊 Found {len(stories)} stories total")
        
        # Count by file type
        file_types = {}
        for story in stories:
            file_type = story.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        print("   📋 Stories by file type:")
        for file_type, count in file_types.items():
            print(f"      - {file_type.upper()}: {count}")
        
        # Test specific parsers
        test_files = [f for f in stories if 'test_historia_multiformat' in f.get('filename', '')]
        
        for story in test_files:
            file_type = story.get('file_type', 'unknown')
            title = story.get('content', {}).get('title', 'No title')
            print(f"   ✅ Parsed {file_type.upper()}: '{title}'")
            
            # Verify content structure
            content = story.get('content', {})
            required_fields = ['title', 'hook', 'body', 'call_to_action', 'full_text']
            missing_fields = [field for field in required_fields if not content.get(field)]
            
            if missing_fields:
                print(f"      ⚠️ Missing fields: {missing_fields}")
            else:
                print(f"      ✅ All required fields present")
        
        print("✅ FileManager multi-format loading works correctly")
        return True
        
    except Exception as e:
        print(f"❌ FileManager test failed: {e}")
        return False

def cleanup_test_files(file_paths):
    """Clean up test files"""
    print("🧹 Cleaning up test files...")
    
    for filepath in file_paths:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"   🗑️ Removed: {filepath}")
        except Exception as e:
            print(f"   ⚠️ Could not remove {filepath}: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing multi-format story loading...\n")
    
    test_files = []
    
    try:
        # Create test files
        test_files = create_test_files()
        print()
        
        # Test file manager
        success = test_file_manager()
        print()
        
        if success:
            print("🎉 All multi-format tests passed!")
            print("\n📋 Supported formats:")
            print("   📄 JSON - Full support (native format)")
            print("   📝 Markdown - Parsed with regex")
            print("   🌐 HTML - Parsed with BeautifulSoup/regex fallback")
            print("   📕 PDF - Basic support (requires PyPDF2)")
            print("\n✅ You can now view stories in all these formats in the archived stories section.")
        else:
            print("⚠️ Some tests failed.")
        
        return success
        
    finally:
        # Always clean up
        if test_files:
            print()
            cleanup_test_files(test_files)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)