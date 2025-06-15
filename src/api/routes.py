"""
API routes for the medical appointment booking system.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict, List
import os

from ..models import (
    SessionCreateRequest, SessionCreateResponse, ChatRequest, ChatResponse,
    ChatHistoryResponse, MessageType, SessionStatus
)
from ..services import SessionManager, AIAssistantService
from dotenv import load_dotenv

load_dotenv()

# Initialize services
session_manager = SessionManager()
ai_assistant = AIAssistantService(
    openai_api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
    session_manager=session_manager
)

# Create router
router = APIRouter()

# Session Management Endpoints
@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new booking session."""
    try:
        session = session_manager.create_session(
            patient_email=request.patient_email,
            metadata=request.metadata
        )
        
        return SessionCreateResponse(
            session_id=session.session_id,
            status=session.status,
            created_at=session.created_at,
            expires_at=session.expires_at,
            message="Session created successfully. You can now start chatting to book your appointment."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "status": session.status,
        "current_step": session.current_step,
        "patient_info": session.patient_info,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "expires_at": session.expires_at
    }

@router.get("/sessions")
async def list_sessions(status: SessionStatus = None):
    """List all sessions with optional status filter."""
    sessions = session_manager.get_all_sessions(status_filter=status)
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "status": s.status,
                "current_step": s.current_step,
                "patient_name": s.patient_info.name,
                "created_at": s.created_at,
                "updated_at": s.updated_at
            }
            for s in sessions
        ],
        "total": len(sessions)
    }

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its chat history."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete chat history
    session_manager.chat_history_service.delete_session_history(session_id)
    
    # Delete session file
    session_file = session_manager._get_session_file_path(session_id)
    if os.path.exists(session_file):
        os.remove(session_file)
    
    return {"message": "Session deleted successfully"}

# Chat Endpoints
@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send a chat message and get AI response."""
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Session is {session.status.value}")
    
    try:
        # Save user message
        user_message = session_manager.save_chat_message(
            session_id=request.session_id,
            message_type=MessageType.USER,
            content=request.message,
            metadata=request.metadata
        )
        
        # Generate AI response
        ai_response_text = ai_assistant.process_message(request.session_id, request.message)
        
        # Save AI response
        ai_message = session_manager.save_chat_message(
            session_id=request.session_id,
            message_type=MessageType.ASSISTANT,
            content=ai_response_text
        )
        
        # Get updated session
        updated_session = session_manager.get_session(request.session_id)
        
        return ChatResponse(
            session_id=request.session_id,
            message_id=ai_message.id if ai_message else "unknown",
            user_message=request.message,
            assistant_response=ai_response_text,
            current_step=updated_session.current_step,
            patient_info=updated_session.patient_info,
            timestamp=ai_message.timestamp if ai_message else None,
            session_status=updated_session.status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/chat-history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    history = session_manager.get_chat_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return history

# Utility Endpoints
@router.post("/cleanup")
async def cleanup_expired_sessions():
    """Clean up expired sessions."""
    cleaned_count = session_manager.cleanup_expired_sessions()
    return {"message": f"Cleaned up {cleaned_count} expired sessions"}

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Medical Appointment Booking API"}

# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    # Verify session exists
    session = session_manager.get_session(session_id)
    if not session:
        await websocket.send_json({"error": "Session not found"})
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            
            if not user_message:
                continue
            
            # Save user message
            session_manager.save_chat_message(
                session_id=session_id,
                message_type=MessageType.USER,
                content=user_message
            )
            
            # Generate AI response
            ai_response = ai_assistant.process_message(session_id, user_message)
            
            # Save AI response
            session_manager.save_chat_message(
                session_id=session_id,
                message_type=MessageType.ASSISTANT,
                content=ai_response
            )
            
            # Get updated session
            updated_session = session_manager.get_session(session_id)
            
            # Send response to client
            await websocket.send_json({
                "type": "assistant_response",
                "message": ai_response,
                "current_step": updated_session.current_step.value,
                "patient_info": updated_session.patient_info.dict(),
                "session_status": updated_session.status.value
            })
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})

# Static file serving
@router.get("/", response_class=HTMLResponse)
async def serve_chat_interface():
    """Serve the chat interface."""
    html_file = "static/index.html"
    if os.path.exists(html_file):
        with open(html_file, 'r') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>Medical Appointment Booking</title></head>
            <body>
                <h1>Medical Appointment Booking System</h1>
                <p>Chat interface not found. Please ensure static/index.html exists.</p>
                <p>API is running at <a href="/docs">/docs</a></p>
            </body>
        </html>
        """) 