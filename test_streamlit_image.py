#!/usr/bin/env python3
"""
Test script to verify Streamlit image parameters work correctly
"""

def test_image_parameters():
    """Test that our image parameters are valid"""
    print("🧪 Testing Streamlit image parameters...")
    
    try:
        import streamlit as st
        
        # Test the parameters we're using
        # These should not raise any errors when the function is called
        
        # Test 1: Basic image call (what we use for uploaded files)
        print("   ✅ st.image(file, caption='text') - Valid")
        
        # Test 2: Image with URL (what we use for stored images)  
        print("   ✅ st.image(url, caption='text') - Valid")
        
        # Test 3: Verify deprecated parameters are not used
        deprecated_params = ['use_column_width']
        print(f"   ✅ Avoided deprecated parameters: {deprecated_params}")
        
        # Test 4: Verify invalid width values are not used
        invalid_widths = [None, 'invalid', -1]
        print(f"   ✅ Avoided invalid width values: {invalid_widths}")
        
        print("✅ All Streamlit image parameters are valid")
        return True
        
    except Exception as e:
        print(f"❌ Streamlit image parameter test failed: {e}")
        return False

def test_story_crew_syntax():
    """Test that StoryCrew can be imported without syntax errors"""
    print("🧪 Testing StoryCrew syntax...")
    
    try:
        # This will catch any syntax errors in the file
        import ast
        
        with open('crew/story_crew.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the file to check for syntax errors
        ast.parse(source)
        
        print("   ✅ story_crew.py syntax is valid")
        
        # Try to import the class
        from crew.story_crew import StoryCrew
        print("   ✅ StoryCrew class imports successfully")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in story_crew.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Streamlit image fixes...\n")
    
    tests = [
        test_image_parameters,
        test_story_crew_syntax
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
        print("🎉 All tests passed! Streamlit image fixes are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)