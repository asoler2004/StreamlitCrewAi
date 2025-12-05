#!/usr/bin/env python3
"""
Test script to verify the fixes work correctly
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append('.')

def test_config_functions():
    """Test configuration functions"""
    print("🧪 Testing configuration functions...")
    
    try:
        from utils.config import check_environment_variables, get_config
        
        # Test environment check
        env_check = check_environment_variables()
        print(f"   Environment check result: {env_check}")
        
        # Test config retrieval
        config = get_config()
        print(f"   Config keys available: {list(config.keys())}")
        
        print("✅ Configuration functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_file_manager():
    """Test file manager functions"""
    print("🧪 Testing file manager...")
    
    try:
        from utils.file_manager import FileManager
        
        fm = FileManager()
        
        # Test loading stories
        stories = fm.load_stories_from_folder()
        print(f"   Found {len(stories)} local stories")
        
        # Test creating a sample story
        sample_story = {
            'content': {
                'title': 'Test Story',
                'full_text': 'This is a test story content.',
                'hook': 'Test hook',
                'body': ['Test paragraph 1', 'Test paragraph 2'],
                'call_to_action': 'Test CTA'
            },
            'platform': 'Facebook',
            'tone': 'professional',
            'created_at': datetime.now().isoformat()
        }
        
        # Test JSON save
        json_path = fm.save_as_json(sample_story, 'test_story.json')
        print(f"   JSON saved to: {json_path}")
        
        # Clean up test file
        if os.path.exists(json_path):
            os.remove(json_path)
            print("   Test file cleaned up")
        
        print("✅ File manager works correctly")
        return True
        
    except Exception as e:
        print(f"❌ File manager test failed: {e}")
        return False

def test_supabase_manager():
    """Test Supabase manager (without actual connection)"""
    print("🧪 Testing Supabase manager initialization...")
    
    try:
        from utils.supabase_client import SupabaseManager
        
        # This will fail if credentials are missing, but that's expected
        try:
            sm = SupabaseManager()
            print("   Supabase manager initialized (credentials available)")
        except Exception as e:
            print(f"   Supabase manager failed to initialize (expected if no credentials): {type(e).__name__}")
        
        print("✅ Supabase manager class loads correctly")
        return True
        
    except Exception as e:
        print(f"❌ Supabase manager test failed: {e}")
        return False

def test_story_crew_import():
    """Test StoryCrew import"""
    print("🧪 Testing StoryCrew import...")
    
    try:
        from crew.story_crew import StoryCrew
        
        print("   StoryCrew class imported successfully")
        
        # Test initialization (may fail due to missing credentials, but class should load)
        try:
            crew = StoryCrew()
            print("   StoryCrew initialized successfully")
        except Exception as e:
            print(f"   StoryCrew initialization failed (expected if no credentials): {type(e).__name__}")
        
        print("✅ StoryCrew class loads correctly")
        return True
        
    except Exception as e:
        print(f"❌ StoryCrew import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running fix verification tests...\n")
    
    tests = [
        test_config_functions,
        test_file_manager,
        test_supabase_manager,
        test_story_crew_import
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)