#!/usr/bin/env python3
"""
Simple test script to verify MediBook setup and functionality.
"""

import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv

def test_environment():
    """Test environment setup."""
    print("🔧 Testing environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        print("❌ OpenAI API key not configured")
        return False
    else:
        print(f"✅ OpenAI API key configured: {api_key[:10]}...")
    
    # Check required files
    required_files = [
        "main.py",
        "streamlit_app.py", 
        "requirements.txt",
        "src/services/ai_assistant.py",
        "src/api/routes.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def test_imports():
    """Test if all required packages can be imported."""
    print("\n📦 Testing package imports...")
    
    packages = [
        "fastapi",
        "uvicorn", 
        "streamlit",
        "langchain",
        "langchain_openai",
        "openai",
        "pydantic",
        "requests"
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} import failed: {e}")
            return False
    
    return True

def test_ai_service():
    """Test AI service directly."""
    print("\n🤖 Testing AI service...")
    
    try:
        # Add src to path
        sys.path.append('src')
        
        from src.services.session_manager import SessionManager
        from src.services.ai_assistant import AIAssistantService
        
        # Initialize services
        session_manager = SessionManager()
        ai_assistant = AIAssistantService(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            session_manager=session_manager
        )
        
        # Create test session
        session = session_manager.create_session(patient_email="test@example.com")
        print(f"✅ Test session created: {session.session_id}")
        
        # Test AI response
        response = ai_assistant.process_message(session.session_id, "Hello")
        print(f"✅ AI response received: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False

def test_fastapi_server():
    """Test FastAPI server startup."""
    print("\n🚀 Testing FastAPI server...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print("✅ FastAPI server started successfully")
                    print(f"✅ Health check response: {response.json()}")
                    
                    # Test session creation
                    session_response = requests.post(
                        "http://localhost:8000/sessions",
                        json={"patient_email": "test@example.com"}
                    )
                    if session_response.status_code == 200:
                        print("✅ Session creation works")
                        session_data = session_response.json()
                        
                        # Test chat
                        chat_response = requests.post(
                            "http://localhost:8000/chat",
                            json={
                                "session_id": session_data["session_id"],
                                "message": "Hello"
                            }
                        )
                        if chat_response.status_code == 200:
                            print("✅ Chat functionality works")
                        else:
                            print(f"❌ Chat test failed: {chat_response.status_code}")
                    else:
                        print(f"❌ Session creation failed: {session_response.status_code}")
                    
                    # Stop server
                    process.terminate()
                    process.wait()
                    return True
                    
            except requests.exceptions.RequestException:
                time.sleep(1)
        
        print("❌ FastAPI server failed to start within 30 seconds")
        process.terminate()
        process.wait()
        return False
        
    except Exception as e:
        print(f"❌ FastAPI server test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🏥 MediBook Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Package Imports", test_imports),
        ("AI Service", test_ai_service),
        ("FastAPI Server", test_fastapi_server)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MediBook is ready to use.")
        print("\n🚀 To start the application:")
        print("   ./run_servers.sh start")
        print("\n📍 Access points:")
        print("   🎨 Web Interface: http://localhost:8501")
        print("   🔧 API Backend: http://localhost:8000")
        print("   📚 API Docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 