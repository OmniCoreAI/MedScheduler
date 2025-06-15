"""
Appointment-related data models.
"""

from pydantic import BaseModel
from typing import Optional

class AppointmentRequest(BaseModel):
    """Request model for booking an appointment."""
    patient_name: str
    preferred_date: str
    preferred_time: str
    symptoms: str
    preferred_doctor: Optional[str] = None

class AppointmentResponse(BaseModel):
    """Response model for appointment booking."""
    appointment_id: str
    status: str
    message: str
    suggested_date: Optional[str] = None
    suggested_time: Optional[str] = None 