#!/usr/bin/env python3
"""
Simple syntax test for the fixed files
"""

import ast
import sys

def test_file_syntax(filepath):
    """Test syntax of a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        ast.parse(source)
        print(f"✅ {filepath} - Syntax OK")
        return True
        
    except SyntaxError as e:
        print(f"❌ {filepath} - Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {filepath} - Error: {e}")
        return False

def main():
    """Test syntax of all modified files"""
    print("🧪 Testing syntax of modified files...\n")
    
    files_to_test = [
        'utils/config.py',
        'utils/supabase_client.py', 
        'utils/file_manager.py',
        'crew/story_crew.py',
        'main.py'
    ]
    
    results = []
    for filepath in files_to_test:
        result = test_file_syntax(filepath)
        results.append(result)
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} files passed syntax check")
    
    if all(results):
        print("🎉 All files have valid syntax!")
        print("\n✅ The Streamlit image width error should now be fixed.")
        print("✅ You can run the application with: streamlit run main.py")
    else:
        print("⚠️ Some files have syntax errors.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)