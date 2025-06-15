"""
Session-related data models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from .base import SessionStatus, BookingStep

class PatientInfo(BaseModel):
    """Patient information collected during the booking process."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    symptoms: Optional[str] = None
    preferred_doctor: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    additional_notes: Optional[str] = None

class SessionData(BaseModel):
    """Complete session data structure."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: SessionStatus = SessionStatus.ACTIVE
    current_step: BookingStep = BookingStep.GREETING
    patient_info: PatientInfo = Field(default_factory=PatientInfo)
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

class SessionCreateRequest(BaseModel):
    """Request model for creating a new session."""
    patient_email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionCreateResponse(BaseModel):
    """Response model for session creation."""
    session_id: str
    status: SessionStatus
    created_at: datetime
    expires_at: Optional[datetime]
    message: str 