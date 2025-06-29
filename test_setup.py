#!/usr/bin/env python3
"""
Test script for AI Email Agent
This script tests the basic functionality to ensure everything is working.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔄 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False
    
    try:
        import playwright
        print("✅ Playwright imported successfully")
    except ImportError as e:
        print(f"❌ Playwright import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        import cohere
        print("✅ Cohere imported successfully")
    except ImportError as e:
        print(f"⚠️  Cohere import failed (optional): {e}")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow (PIL) imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True

def test_ai_email_agent():
    """Test if the AI Email Agent can be imported and initialized"""
    print("\n🔄 Testing AI Email Agent...")
    
    try:
        from ai_email_agent import AIEmailAgent
        print("✅ AI Email Agent imported successfully")
        
        # Try to initialize the agent
        agent = AIEmailAgent()
        print("✅ AI Email Agent initialized successfully")
        
        # Test fallback content generation
        content = agent.generate_email_content("Test email prompt")
        if content and "subject" in content and "body" in content:
            print("✅ Email content generation working")
        else:
            print("❌ Email content generation failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ AI Email Agent test failed: {e}")
        return False

def test_main_app():
    """Test if the main FastAPI app can be imported"""
    print("\n🔄 Testing main application...")
    
    try:
        from main import app
        print("✅ Main FastAPI app imported successfully")
        
        # Test if the app has the expected endpoints
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/send-ai-email"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} found")
            else:
                print(f"⚠️  Route {route} not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Main app test failed: {e}")
        return False

def test_env_file():
    """Test if .env file exists and has proper format"""
    print("\n🔄 Testing .env file...")
    
    if not os.path.exists(".env"):
        print("⚠️  .env file not found (this is normal for first-time setup)")
        return True
    
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "OPENAI_API_KEY" in content or "COHERE_API_KEY" in content:
            print("✅ .env file has API key placeholders")
        else:
            print("⚠️  .env file doesn't contain expected API key variables")
        
        return True
        
    except Exception as e:
        print(f"❌ .env file test failed: {e}")
        return False

def main():
    print("🧪 AI Email Agent Setup Test")
    print("=" * 50)
    
    # Test Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Run all tests
    tests = [
        test_imports,
        test_ai_email_agent,
        test_main_app,
        test_env_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📋 Next steps:")
        print("1. Add your API keys to the .env file")
        print("2. Start the backend: python main.py")
        print("3. Start the frontend: cd frontend && npm run dev")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n💡 Try running: python setup.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 