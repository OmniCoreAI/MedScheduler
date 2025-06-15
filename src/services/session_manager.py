"""
Session management service.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os

from ..models import (
    SessionData, MessageType, SessionStatus, BookingStep, ChatHistoryResponse
)
from .chat_history import ChatHistoryService

class SessionManager:
    """Professional session management service."""
    
    def __init__(self, storage_path: str = "data/sessions", session_timeout_hours: int = 24):
        self.storage_path = storage_path
        self.session_timeout_hours = session_timeout_hours
        self.chat_history_service = ChatHistoryService()
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _get_session_file_path(self, session_id: str) -> str:
        """Get file path for session data."""
        return os.path.join(self.storage_path, f"{session_id}.json")
    
    def create_session(self, patient_email: Optional[str] = None, metadata: Optional[Dict] = None) -> SessionData:
        """Create a new session with professional structure."""
        session = SessionData(
            expires_at=datetime.now() + timedelta(hours=self.session_timeout_hours),
            metadata=metadata or {}
        )
        
        if patient_email:
            session.patient_info.email = patient_email
        
        # Save session to persistent storage
        self._save_session(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data with expiration check."""
        try:
            file_path = self._get_session_file_path(session_id)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            session = SessionData(**data)
            
            # Check if session is expired
            if session.expires_at and datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                self._save_session(session)
            
            return session
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def update_session(self, session: SessionData) -> bool:
        """Update session data."""
        try:
            session.updated_at = datetime.now()
            return self._save_session(session)
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def _save_session(self, session: SessionData) -> bool:
        """Save session to persistent storage."""
        try:
            file_path = self._get_session_file_path(session.session_id)
            
            with open(file_path, 'w') as f:
                json.dump(session.dict(), f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def update_patient_info(self, session_id: str, field: str, value: str) -> bool:
        """Update specific patient information field."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Update the field
        setattr(session.patient_info, field, value)
        
        return self.update_session(session)
    
    def update_booking_step(self, session_id: str, step: BookingStep) -> bool:
        """Update the current booking step."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.current_step = step
        return self.update_session(session)
    
    def get_chat_history(self, session_id: str) -> Optional[ChatHistoryResponse]:
        """Get complete chat history for a session."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        messages = self.chat_history_service.get_session_messages(session_id)
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=messages,
            total_messages=len(messages),
            patient_info=session.patient_info,
            current_step=session.current_step,
            session_status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
    
    def save_chat_message(self, session_id: str, message_type: MessageType, content: str, metadata: Optional[Dict] = None):
        """Save a chat message."""
        from ..models import ChatMessage
        
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            metadata=metadata
        )
        
        if self.chat_history_service.save_message(message):
            return message
        return None
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        cleaned_count = 0
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # Remove .json extension
                    session = self.get_session(session_id)
                    
                    if session and session.status == SessionStatus.EXPIRED:
                        # Delete session and chat history
                        os.remove(self._get_session_file_path(session_id))
                        self.chat_history_service.delete_session_history(session_id)
                        cleaned_count += 1
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        return cleaned_count
    
    def get_all_sessions(self, status_filter: Optional[SessionStatus] = None) -> List[SessionData]:
        """Get all sessions with optional status filter."""
        sessions = []
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    session_id = filename[:-5]
                    session = self.get_session(session_id)
                    
                    if session and (not status_filter or session.status == status_filter):
                        sessions.append(session)
        except Exception as e:
            print(f"Error loading sessions: {e}")
        
        return sessions 