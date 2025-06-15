"""
Main application entry point for the Medical Appointment Booking System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging

from src.api import router
from src.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Professional AI-powered medical appointment booking system with session management",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Mount static files if directory exists
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Include API routes
    app.include_router(router, prefix="/api/v1")
    app.include_router(router)  # Also include without prefix for backward compatibility
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Application startup tasks."""
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")
        
        # Ensure data directories exist
        os.makedirs(settings.data_directory, exist_ok=True)
        os.makedirs(settings.sessions_directory, exist_ok=True)
        os.makedirs(settings.chat_history_directory, exist_ok=True)
        os.makedirs(settings.appointments_directory, exist_ok=True)
        
        logger.info("Application startup complete")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown tasks."""
        logger.info("Application shutting down")
    
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    ) 