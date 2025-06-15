"""
Data models for the medical appointment booking system.
"""

from .base import (
    MessageType,
    SessionStatus,
    BookingStep
)

from .session import (
    SessionData,
    PatientInfo,
    SessionCreateRequest,
    SessionCreateResponse
)

from .chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse
)

from .appointment import (
    AppointmentRequest,
    AppointmentResponse
)

__all__ = [
    # Enums
    "MessageType",
    "SessionStatus", 
    "BookingStep",
    
    # Session models
    "SessionData",
    "PatientInfo",
    "SessionCreateRequest",
    "SessionCreateResponse",
    
    # Chat models
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatHistoryResponse",
    
    # Appointment models
    "AppointmentRequest",
    "AppointmentResponse"
] 