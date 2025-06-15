"""
Chat-related data models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from .base import MessageType, BookingStep, SessionStatus
from .session import PatientInfo

class ChatMessage(BaseModel):
    """Individual chat message model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    message_type: MessageType
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    session_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    session_id: str
    message_id: str
    user_message: str
    assistant_response: str
    current_step: BookingStep
    patient_info: PatientInfo
    timestamp: datetime
    session_status: SessionStatus

class ChatHistoryResponse(BaseModel):
    """Response model for chat history retrieval."""
    session_id: str
    messages: List[ChatMessage]
    total_messages: int
    patient_info: PatientInfo
    current_step: BookingStep
    session_status: SessionStatus
    created_at: datetime
    updated_at: datetime 