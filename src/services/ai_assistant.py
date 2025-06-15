"""
AI Assistant service for medical appointment booking.
"""

from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

from ..models import SessionData, BookingStep, MessageType
from .session_manager import SessionManager

class AIAssistantService:
    """AI Assistant service for handling conversational appointment booking."""
    
    def __init__(self, openai_api_key: str, session_manager: SessionManager):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        self.session_manager = session_manager
        self.available_slots = self._load_available_slots()
    
    def _load_available_slots(self) -> Dict:
        """Load available appointment slots."""
        slots_file = "data/available_slots.json"
        if os.path.exists(slots_file):
            with open(slots_file, 'r') as f:
                return json.load(f)
        
        # Default slots if file doesn't exist
        default_slots = {
            "dr_smith": {
                "name": "Dr. Smith",
                "specialty": "General Medicine",
                "available_slots": [
                    {"date": "2024-01-15", "time": "09:00", "available": True},
                    {"date": "2024-01-15", "time": "10:00", "available": True},
                    {"date": "2024-01-16", "time": "14:00", "available": True}
                ]
            },
            "dr_johnson": {
                "name": "Dr. Johnson", 
                "specialty": "Cardiology",
                "available_slots": [
                    {"date": "2024-01-15", "time": "11:00", "available": True},
                    {"date": "2024-01-16", "time": "15:00", "available": True}
                ]
            },
            "dr_brown": {
                "name": "Dr. Brown",
                "specialty": "Dermatology", 
                "available_slots": [
                    {"date": "2024-01-15", "time": "13:00", "available": True},
                    {"date": "2024-01-17", "time": "10:00", "available": True}
                ]
            }
        }
        
        # Save default slots
        os.makedirs("data", exist_ok=True)
        with open(slots_file, 'w') as f:
            json.dump(default_slots, f, indent=2)
        
        return default_slots
    
    def get_system_prompt(self, session: SessionData) -> str:
        """Get system prompt based on current session state."""
        base_prompt = """You are a professional medical appointment booking assistant. 
        Your role is to help patients book medical appointments through a conversational interface.
        
        Current session information:
        - Current step: {current_step}
        - Patient name: {patient_name}
        - Patient phone: {patient_phone}
        - Symptoms: {symptoms}
        - Preferred doctor: {preferred_doctor}
        
        Available doctors:
        - Dr. Smith (General Medicine)
        - Dr. Johnson (Cardiology)
        - Dr. Brown (Dermatology)
        
        Guidelines:
        1. Be professional, empathetic, and helpful
        2. Collect information step by step
        3. Ask only one question at a time
        4. Validate information before proceeding
        5. Provide clear next steps
        6. If symptoms suggest urgency, recommend immediate medical attention
        
        Current step instructions:
        {step_instructions}
        """
        
        step_instructions = self._get_step_instructions(session.current_step)
        
        return base_prompt.format(
            current_step=session.current_step.value,
            patient_name=session.patient_info.name or "Not provided",
            patient_phone=session.patient_info.phone or "Not provided", 
            symptoms=session.patient_info.symptoms or "Not provided",
            preferred_doctor=session.patient_info.preferred_doctor or "Not specified",
            step_instructions=step_instructions
        )
    
    def _get_step_instructions(self, step: BookingStep) -> str:
        """Get specific instructions for each booking step."""
        instructions = {
            BookingStep.GREETING: "Greet the patient warmly and ask for their name.",
            BookingStep.NAME_COLLECTION: "Collect the patient's full name and confirm it's correct.",
            BookingStep.PHONE_COLLECTION: "Ask for the patient's phone number for appointment confirmation.",
            BookingStep.SYMPTOMS_COLLECTION: "Ask about their symptoms or reason for the visit. Be empathetic.",
            BookingStep.DOCTOR_PREFERENCE: "Based on symptoms, suggest appropriate doctors and ask for preference.",
            BookingStep.SLOT_SELECTION: "Show available slots for the preferred doctor and ask them to choose.",
            BookingStep.CONFIRMATION: "Confirm all appointment details and finalize the booking.",
            BookingStep.COMPLETED: "Provide appointment confirmation and next steps."
        }
        return instructions.get(step, "Continue with the booking process.")
    
    def process_message(self, session_id: str, user_message: str) -> str:
        """Process user message and generate appropriate response."""
        session = self.session_manager.get_session(session_id)
        if not session:
            return "I'm sorry, I couldn't find your session. Please start a new booking session."
        
        # Get recent chat history for context
        recent_messages = self.session_manager.chat_history_service.get_recent_messages(session_id, limit=5)
        
        # Build conversation context
        messages = [SystemMessage(content=self.get_system_prompt(session))]
        
        # Add recent conversation history
        for msg in recent_messages:
            if msg.message_type == MessageType.USER:
                messages.append(HumanMessage(content=msg.content))
            elif msg.message_type == MessageType.ASSISTANT:
                messages.append(SystemMessage(content=f"Assistant previously said: {msg.content}"))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Generate response
        try:
            response = self.llm.invoke(messages)
            assistant_response = response.content
            
            # Update session based on response and user input
            self._update_session_state(session, user_message, assistant_response)
            
            return assistant_response
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    def _update_session_state(self, session: SessionData, user_message: str, assistant_response: str):
        """Update session state based on conversation."""
        user_lower = user_message.lower()
        
        # Update patient info based on current step
        if session.current_step == BookingStep.GREETING:
            if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good']):
                session.current_step = BookingStep.NAME_COLLECTION
        
        elif session.current_step == BookingStep.NAME_COLLECTION:
            # Extract name from user message (simple extraction)
            if not session.patient_info.name and len(user_message.strip()) > 0:
                # Simple name extraction - in production, use NLP
                potential_name = user_message.strip()
                if len(potential_name.split()) <= 3 and potential_name.replace(' ', '').isalpha():
                    session.patient_info.name = potential_name
                    session.current_step = BookingStep.PHONE_COLLECTION
        
        elif session.current_step == BookingStep.PHONE_COLLECTION:
            # Extract phone number
            import re
            phone_pattern = r'[\d\-\(\)\+\s]+'
            phone_match = re.search(phone_pattern, user_message)
            if phone_match and len(re.sub(r'[^\d]', '', phone_match.group())) >= 10:
                session.patient_info.phone = phone_match.group().strip()
                session.current_step = BookingStep.SYMPTOMS_COLLECTION
        
        elif session.current_step == BookingStep.SYMPTOMS_COLLECTION:
            if not session.patient_info.symptoms:
                session.patient_info.symptoms = user_message
                session.current_step = BookingStep.DOCTOR_PREFERENCE
        
        elif session.current_step == BookingStep.DOCTOR_PREFERENCE:
            # Check if user mentioned a doctor
            if 'smith' in user_lower:
                session.patient_info.preferred_doctor = 'dr_smith'
                session.current_step = BookingStep.SLOT_SELECTION
            elif 'johnson' in user_lower:
                session.patient_info.preferred_doctor = 'dr_johnson'
                session.current_step = BookingStep.SLOT_SELECTION
            elif 'brown' in user_lower:
                session.patient_info.preferred_doctor = 'dr_brown'
                session.current_step = BookingStep.SLOT_SELECTION
        
        elif session.current_step == BookingStep.SLOT_SELECTION:
            # Check if user selected a time slot
            if any(time in user_lower for time in ['9', '10', '11', '12', '13', '14', '15', '16']):
                session.current_step = BookingStep.CONFIRMATION
        
        elif session.current_step == BookingStep.CONFIRMATION:
            if any(word in user_lower for word in ['yes', 'confirm', 'book', 'schedule']):
                session.current_step = BookingStep.COMPLETED
        
        # Save updated session
        self.session_manager.update_session(session)
    
    def get_available_slots_for_doctor(self, doctor_key: str) -> List[Dict]:
        """Get available slots for a specific doctor."""
        if doctor_key in self.available_slots:
            return [slot for slot in self.available_slots[doctor_key]["available_slots"] if slot["available"]]
        return []
    
    def reserve_slot(self, doctor_key: str, date: str, time: str) -> bool:
        """Reserve a specific time slot."""
        if doctor_key in self.available_slots:
            for slot in self.available_slots[doctor_key]["available_slots"]:
                if slot["date"] == date and slot["time"] == time and slot["available"]:
                    slot["available"] = False
                    # Save updated slots
                    with open("data/available_slots.json", 'w') as f:
                        json.dump(self.available_slots, f, indent=2)
                    return True
        return False 