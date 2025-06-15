"""
Base models and enums for the medical appointment booking system.
"""

from enum import Enum

class MessageType(str, Enum):
    """Types of messages in the chat system."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class SessionStatus(str, Enum):
    """Status of a booking session."""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class BookingStep(str, Enum):
    """Steps in the appointment booking process."""
    GREETING = "greeting"
    NAME_COLLECTION = "name_collection"
    PHONE_COLLECTION = "phone_collection"
    SYMPTOMS_COLLECTION = "symptoms_collection"
    DOCTOR_PREFERENCE = "doctor_preference"
    SLOT_SELECTION = "slot_selection"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed" 