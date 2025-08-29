#!/usr/bin/env python3
"""
Basic test for StudyMate core functionality without heavy dependencies
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test basic Python imports"""
    print("🧪 Testing basic imports...")
    try:
        import streamlit
        print("✅ Streamlit import successful")
        
        import requests
        print("✅ Requests import successful")
        
        import numpy
        print("✅ NumPy import successful")
        
        import pandas
        print("✅ Pandas import successful")
        
        return True
    except Exception as e:
        print(f"❌ Basic imports test failed: {e}")
        return False

def test_app_structure():
    """Test that app.py can be imported"""
    print("\n🧪 Testing app structure...")
    try:
        # Check if app.py exists and is readable
        app_path = "/workspace/app.py"
        if os.path.exists(app_path):
            print("✅ app.py exists")
            
            with open(app_path, 'r') as f:
                content = f.read()
                if 'streamlit' in content and 'StudyMate' in content:
                    print("✅ app.py contains expected content")
                else:
                    print("⚠️ app.py may be missing expected content")
            
            return True
        else:
            print("❌ app.py not found")
            return False
            
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

def test_directory_structure():
    """Test project directory structure"""
    print("\n🧪 Testing directory structure...")
    try:
        required_dirs = ['/workspace/src', '/workspace/data', '/workspace/uploads']
        all_exist = True
        
        for directory in required_dirs:
            if os.path.exists(directory):
                print(f"✅ {directory} exists")
            else:
                print(f"❌ {directory} missing")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"❌ Directory structure test failed: {e}")
        return False

def test_requirements():
    """Test requirements file"""
    print("\n🧪 Testing requirements...")
    try:
        req_path = "/workspace/requirements.txt"
        if os.path.exists(req_path):
            print("✅ requirements.txt exists")
            
            with open(req_path, 'r') as f:
                content = f.read()
                if 'streamlit' in content:
                    print("✅ requirements.txt contains streamlit")
                else:
                    print("⚠️ requirements.txt may be missing streamlit")
            
            return True
        else:
            print("❌ requirements.txt not found")
            return False
            
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🚀 StudyMate Basic System Tests")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_app_structure,
        test_directory_structure,
        test_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! Core system structure is ready.")
        print("\n📝 Next steps:")
        print("   1. Install additional dependencies (PyMuPDF, FAISS, etc.)")
        print("   2. Run the full system tests")
        print("   3. Launch the Streamlit app")
        return 0
    else:
        print("⚠️ Some basic tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())