#!/usr/bin/env python3
"""
Debug script to test AI Assistant service directly.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from src.services.session_manager import SessionManager
from src.services.ai_assistant import AIAssistantService

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize services
    session_manager = SessionManager()
    ai_assistant = AIAssistantService(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        session_manager=session_manager
    )
    
    # Create a test session
    session = session_manager.create_session(patient_email="test@example.com")
    print(f"Created session: {session.session_id}")
    print(f"Current step: {session.current_step}")
    
    # Test AI assistant
    print("\n--- Testing AI Assistant ---")
    try:
        response = ai_assistant.process_message(session.session_id, "hi")
        print(f"AI Response: {response}")
        
        # Check updated session
        updated_session = session_manager.get_session(session.session_id)
        print(f"Updated step: {updated_session.current_step}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 