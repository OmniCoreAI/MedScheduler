#!/usr/bin/env python3
"""
Streamlit frontend for the Medical Appointment Booking System.
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import uuid
import time

# Configure Streamlit page
st.set_page_config(
    page_title="MediBook - AI Medical Appointment Booking",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
import os
from dotenv import load_dotenv
load_dotenv()

API_PORT = os.getenv("PORT", "8000")
API_BASE_URL = f"http://localhost:{API_PORT}"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #F1F8E9;
        margin-right: 2rem;
    }
    .session-info {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF9800;
    }
    .success-message {
        background-color: #E8F5E8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
    .error-message {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #F44336;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'patient_info' not in st.session_state:
        st.session_state.patient_info = {}
    if 'current_step' not in st.session_state:
        st.session_state.current_step = "greeting"

def create_booking_session(patient_email):
    """Create a new booking session via API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/sessions",
            json={"patient_email": patient_email},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to create session: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def send_chat_message(session_id, message):
    """Send a chat message via API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"session_id": session_id, "message": message},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to send message: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def get_chat_history(session_id):
    """Get chat history via API."""
    try:
        response = requests.get(f"{API_BASE_URL}/chat-history/{session_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

def display_chat_message(message_type, content, timestamp=None):
    """Display a chat message with proper styling."""
    if message_type == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {content}
            {f'<small style="color: #666;">{timestamp}</small>' if timestamp else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🏥 MediBook Assistant:</strong> {content}
            {f'<small style="color: #666;">{timestamp}</small>' if timestamp else ''}
        </div>
        """, unsafe_allow_html=True)

def display_patient_info(patient_info):
    """Display current patient information."""
    if patient_info:
        st.markdown("### 📋 Current Information")
        col1, col2 = st.columns(2)
        
        with col1:
            if patient_info.get('name'):
                st.write(f"**Name:** {patient_info['name']}")
            if patient_info.get('phone'):
                st.write(f"**Phone:** {patient_info['phone']}")
            if patient_info.get('email'):
                st.write(f"**Email:** {patient_info['email']}")
        
        with col2:
            if patient_info.get('symptoms'):
                st.write(f"**Symptoms:** {patient_info['symptoms']}")
            if patient_info.get('preferred_doctor'):
                st.write(f"**Preferred Doctor:** {patient_info['preferred_doctor']}")
            if patient_info.get('preferred_date'):
                st.write(f"**Preferred Date:** {patient_info['preferred_date']}")

def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏥 MediBook</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Medical Appointment Booking</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Session Control")
        
        # Session creation
        if not st.session_state.session_id:
            st.subheader("Start New Session")
            patient_email = st.text_input("Your Email Address", placeholder="patient@example.com")
            
            if st.button("🚀 Start Booking Session", type="primary"):
                if patient_email:
                    with st.spinner("Creating session..."):
                        session_data = create_booking_session(patient_email)
                        if session_data:
                            st.session_state.session_id = session_data['session_id']
                            st.session_state.chat_history = []
                            st.success("Session created successfully!")
                            st.rerun()
                else:
                    st.error("Please enter your email address")
        else:
            # Session info
            st.success(f"✅ Session Active")
            st.write(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
            st.write(f"**Current Step:** {st.session_state.current_step}")
            
            if st.button("🔄 New Session"):
                st.session_state.session_id = None
                st.session_state.chat_history = []
                st.session_state.patient_info = {}
                st.session_state.current_step = "greeting"
                st.rerun()
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("📋 View All Sessions"):
            try:
                response = requests.get(f"{API_BASE_URL}/sessions")
                if response.status_code == 200:
                    sessions = response.json()
                    st.json(sessions)
            except:
                st.error("Failed to fetch sessions")
        
        if st.button("🧹 Cleanup Expired"):
            try:
                response = requests.post(f"{API_BASE_URL}/cleanup")
                if response.status_code == 200:
                    result = response.json()
                    st.success(result['message'])
            except:
                st.error("Failed to cleanup sessions")
    
    # Main content
    if not st.session_state.session_id:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="session-info">
                <h3>🎯 Welcome to MediBook!</h3>
                <p>Your AI-powered medical appointment booking assistant.</p>
                <ul>
                    <li>💬 Natural conversation interface</li>
                    <li>🤖 AI-powered assistance</li>
                    <li>📅 Smart appointment scheduling</li>
                    <li>👨‍⚕️ Multiple doctor specialties</li>
                </ul>
                <p><strong>Get started by entering your email in the sidebar!</strong></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Chat interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("💬 Chat with MediBook Assistant")
            
            # Chat history
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.chat_history:
                    display_chat_message(
                        message['type'], 
                        message['content'], 
                        message.get('timestamp')
                    )
            
            # Chat input
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_input(
                    "Type your message here...", 
                    placeholder="Hi, I'd like to book an appointment",
                    key="user_input"
                )
                col_send, col_clear = st.columns([1, 4])
                
                with col_send:
                    send_button = st.form_submit_button("📤 Send", type="primary")
                
                if send_button and user_input:
                    # Add user message to history
                    st.session_state.chat_history.append({
                        'type': 'user',
                        'content': user_input,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Send to API
                    with st.spinner("🤖 Assistant is thinking..."):
                        response = send_chat_message(st.session_state.session_id, user_input)
                        
                        if response:
                            # Add assistant response to history
                            st.session_state.chat_history.append({
                                'type': 'assistant',
                                'content': response['assistant_response'],
                                'timestamp': datetime.now().strftime("%H:%M:%S")
                            })
                            
                            # Update session state
                            st.session_state.current_step = response['current_step']
                            st.session_state.patient_info = response['patient_info']
                    
                    st.rerun()
        
        with col2:
            # Patient information panel
            display_patient_info(st.session_state.patient_info)
            
            st.divider()
            
            # Available doctors info
            st.markdown("### 👨‍⚕️ Available Doctors")
            doctors_info = """
            **Dr. Smith** - General Medicine  
            **Dr. Johnson** - Cardiology  
            **Dr. Brown** - Dermatology  
            """
            st.markdown(doctors_info)
            
            st.divider()
            
            # Booking progress
            st.markdown("### 📊 Booking Progress")
            steps = [
                "Greeting",
                "Name Collection", 
                "Phone Collection",
                "Symptoms Collection",
                "Doctor Preference",
                "Slot Selection",
                "Confirmation",
                "Completed"
            ]
            
            current_step_index = 0
            step_mapping = {
                "greeting": 0,
                "name_collection": 1,
                "phone_collection": 2,
                "symptoms_collection": 3,
                "doctor_preference": 4,
                "slot_selection": 5,
                "confirmation": 6,
                "completed": 7
            }
            
            current_step_index = step_mapping.get(st.session_state.current_step, 0)
            
            for i, step in enumerate(steps):
                if i <= current_step_index:
                    st.markdown(f"✅ {step}")
                else:
                    st.markdown(f"⏳ {step}")

if __name__ == "__main__":
    main() 