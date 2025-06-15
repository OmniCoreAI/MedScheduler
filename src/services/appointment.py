"""
Appointment management service.
"""

from typing import Optional, Dict
from datetime import datetime
import json
import os

class AppointmentService:
    """Service for managing appointments."""
    
    def __init__(self, storage_path: str = "data/appointments"):
        self.storage_path = storage_path
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def reserve_appointment(self, session_id: str, doctor_key: str, date: str, time: str) -> Optional[Dict]:
        """Reserve an appointment and link it to session."""
        # This would integrate with your existing appointment reservation logic
        # For now, return a mock appointment
        appointment = {
            "appointment_id": f"APT{int(datetime.now().timestamp())}",
            "session_id": session_id,
            "doctor_key": doctor_key,
            "date": date,
            "time": time,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Save appointment
        file_path = os.path.join(self.storage_path, f"{appointment['appointment_id']}.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(appointment, f, indent=2, default=str)
            return appointment
        except Exception as e:
            print(f"Error saving appointment: {e}")
            return None
    
    def get_appointment(self, appointment_id: str) -> Optional[Dict]:
        """Get appointment by ID."""
        file_path = os.path.join(self.storage_path, f"{appointment_id}.json")
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading appointment: {e}")
        return None
    
    def get_all_appointments(self) -> list:
        """Get all appointments."""
        appointments = []
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    with open(os.path.join(self.storage_path, filename), 'r') as f:
                        appointment = json.load(f)
                        appointments.append(appointment)
        except Exception as e:
            print(f"Error loading appointments: {e}")
        return appointments 