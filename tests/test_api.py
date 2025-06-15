"""
Professional test suite for the Medical Appointment Booking API.
"""

import requests
import json
import time
from typing import Dict, Optional
from datetime import datetime

class MedicalBookingAPIClient:
    """Professional API client for testing the medical booking system."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def create_session(self, patient_email: Optional[str] = None) -> Dict:
        """Create a new booking session."""
        url = f"{self.base_url}/sessions"
        payload = {}
        if patient_email:
            payload["patient_email"] = patient_email
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            self.session_id = data["session_id"]
            return data
        else:
            raise Exception(f"Failed to create session: {response.text}")
    
    def send_message(self, message: str, session_id: Optional[str] = None) -> Dict:
        """Send a chat message."""
        if not session_id and not self.session_id:
            raise Exception("No session ID available")
        
        url = f"{self.base_url}/chat"
        payload = {
            "session_id": session_id or self.session_id,
            "message": message
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send message: {response.text}")
    
    def get_chat_history(self, session_id: Optional[str] = None) -> Dict:
        """Get chat history for a session."""
        if not session_id and not self.session_id:
            raise Exception("No session ID available")
        
        url = f"{self.base_url}/chat-history/{session_id or self.session_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get chat history: {response.text}")
    
    def get_session_info(self, session_id: Optional[str] = None) -> Dict:
        """Get session information."""
        if not session_id and not self.session_id:
            raise Exception("No session ID available")
        
        url = f"{self.base_url}/sessions/{session_id or self.session_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get session info: {response.text}")
    
    def list_sessions(self, status: Optional[str] = None) -> Dict:
        """List all sessions."""
        url = f"{self.base_url}/sessions"
        params = {}
        if status:
            params["status"] = status
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to list sessions: {response.text}")
    
    def cleanup_sessions(self) -> Dict:
        """Clean up expired sessions."""
        url = f"{self.base_url}/cleanup"
        response = requests.post(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to cleanup sessions: {response.text}")
    
    def health_check(self) -> Dict:
        """Check API health."""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Health check failed: {response.text}")

def test_complete_booking_flow():
    """Test complete appointment booking flow."""
    print("🏥 Testing Complete Medical Appointment Booking Flow")
    print("=" * 60)
    
    client = MedicalBookingAPIClient()
    
    try:
        # 1. Health Check
        print("1. Checking API health...")
        health = client.health_check()
        print(f"   ✅ API Status: {health['status']}")
        
        # 2. Create Session
        print("\n2. Creating new session...")
        session = client.create_session(patient_email="test@example.com")
        print(f"   ✅ Session created: {session['session_id']}")
        print(f"   📅 Expires at: {session['expires_at']}")
        
        # 3. Start conversation
        print("\n3. Starting conversation...")
        messages = [
            "Hello, I'd like to book an appointment",
            "John Doe",
            "555-123-4567", 
            "I have been having headaches and feeling dizzy",
            "I'd prefer Dr. Smith",
            "I'll take the 9:00 AM slot on January 15th",
            "Yes, please confirm the appointment"
        ]
        
        for i, message in enumerate(messages, 1):
            print(f"\n   Step {i}: Sending '{message}'")
            response = client.send_message(message)
            print(f"   🤖 Assistant: {response['assistant_response'][:100]}...")
            print(f"   📍 Current step: {response['current_step']}")
            
            # Show patient info progress
            patient_info = response['patient_info']
            if patient_info['name']:
                print(f"   👤 Name: {patient_info['name']}")
            if patient_info['phone']:
                print(f"   📞 Phone: {patient_info['phone']}")
            if patient_info['symptoms']:
                print(f"   🩺 Symptoms: {patient_info['symptoms'][:50]}...")
            
            time.sleep(1)  # Simulate natural conversation pace
        
        # 4. Get final session info
        print("\n4. Getting final session information...")
        session_info = client.get_session_info()
        print(f"   ✅ Final status: {session_info['status']}")
        print(f"   📍 Final step: {session_info['current_step']}")
        
        # 5. Get chat history
        print("\n5. Retrieving chat history...")
        history = client.get_chat_history()
        print(f"   💬 Total messages: {history['total_messages']}")
        print(f"   👤 Patient: {history['patient_info']['name']}")
        print(f"   📞 Phone: {history['patient_info']['phone']}")
        
        print("\n✅ Complete booking flow test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

def test_session_management():
    """Test session management features."""
    print("\n🔧 Testing Session Management Features")
    print("=" * 60)
    
    client = MedicalBookingAPIClient()
    
    try:
        # Create multiple sessions
        print("1. Creating multiple sessions...")
        sessions = []
        for i in range(3):
            session = client.create_session(f"user{i}@example.com")
            sessions.append(session['session_id'])
            print(f"   ✅ Session {i+1}: {session['session_id']}")
        
        # List all sessions
        print("\n2. Listing all sessions...")
        all_sessions = client.list_sessions()
        print(f"   📊 Total sessions: {all_sessions['total']}")
        
        # Test cleanup
        print("\n3. Testing cleanup...")
        cleanup_result = client.cleanup_sessions()
        print(f"   🧹 {cleanup_result['message']}")
        
        print("\n✅ Session management test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Session management test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling scenarios."""
    print("\n⚠️  Testing Error Handling")
    print("=" * 60)
    
    client = MedicalBookingAPIClient()
    
    try:
        # Test invalid session
        print("1. Testing invalid session ID...")
        try:
            client.send_message("Hello", session_id="invalid-session-id")
            print("   ❌ Should have failed!")
            return False
        except Exception as e:
            print(f"   ✅ Correctly handled invalid session: {str(e)[:50]}...")
        
        # Test missing session
        print("\n2. Testing missing session...")
        try:
            client.get_session_info("nonexistent-session")
            print("   ❌ Should have failed!")
            return False
        except Exception as e:
            print(f"   ✅ Correctly handled missing session: {str(e)[:50]}...")
        
        print("\n✅ Error handling test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error handling test failed: {str(e)}")
        return False

def interactive_test():
    """Interactive test mode for manual testing."""
    print("\n🎮 Interactive Test Mode")
    print("=" * 60)
    
    client = MedicalBookingAPIClient()
    
    try:
        # Create session
        session = client.create_session()
        print(f"✅ Session created: {session['session_id']}")
        print("\nYou can now chat with the AI assistant!")
        print("Type 'quit' to exit, 'history' to see chat history, 'info' for session info")
        print("-" * 60)
        
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'history':
                history = client.get_chat_history()
                print(f"\n💬 Chat History ({history['total_messages']} messages):")
                for msg in history['messages'][-5:]:  # Show last 5 messages
                    icon = "👤" if msg['message_type'] == 'user' else "🤖"
                    print(f"   {icon} {msg['content'][:80]}...")
                continue
            elif user_input.lower() == 'info':
                info = client.get_session_info()
                print(f"\n📊 Session Info:")
                print(f"   Status: {info['status']}")
                print(f"   Step: {info['current_step']}")
                print(f"   Patient: {info['patient_info']['name'] or 'Not provided'}")
                continue
            elif not user_input:
                continue
            
            # Send message
            response = client.send_message(user_input)
            print(f"\n🤖 Assistant: {response['assistant_response']}")
            print(f"📍 Current step: {response['current_step']}")
        
        print("\n👋 Interactive session ended!")
        return True
        
    except Exception as e:
        print(f"\n❌ Interactive test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all automated tests."""
    print("🧪 Medical Appointment Booking API Test Suite")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Complete Booking Flow", test_complete_booking_flow),
        ("Session Management", test_session_management),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! System is working correctly.")
    else:
        print("⚠️  Some tests FAILED. Please check the system.")
    
    return passed == total

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        run_all_tests() 