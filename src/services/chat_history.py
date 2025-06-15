"""
Chat history management service.
"""

from typing import List
import json
import os

from ..models import ChatMessage

class ChatHistoryService:
    """Professional service for managing chat history with persistence."""
    
    def __init__(self, storage_path: str = "data/chat_history"):
        self.storage_path = storage_path
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _get_session_file_path(self, session_id: str) -> str:
        """Get file path for session chat history."""
        return os.path.join(self.storage_path, f"{session_id}.json")
    
    def save_message(self, message: ChatMessage) -> bool:
        """Save a chat message to persistent storage."""
        try:
            file_path = self._get_session_file_path(message.session_id)
            
            # Load existing messages
            messages = self.get_session_messages(message.session_id)
            
            # Add new message
            messages.append(message)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump([msg.dict() for msg in messages], f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session."""
        try:
            file_path = self._get_session_file_path(session_id)
            
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return [ChatMessage(**msg) for msg in data]
        except Exception as e:
            print(f"Error loading messages: {e}")
            return []
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent messages for context."""
        messages = self.get_session_messages(session_id)
        return messages[-limit:] if messages else []
    
    def delete_session_history(self, session_id: str) -> bool:
        """Delete chat history for a session."""
        try:
            file_path = self._get_session_file_path(session_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting session history: {e}")
            return False 