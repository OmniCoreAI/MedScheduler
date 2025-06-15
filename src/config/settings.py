"""
Application settings and configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional, Union, List
from pydantic import field_validator
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    app_name: str = "Medical Appointment Booking System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    
    # Session Configuration
    session_timeout_hours: int = 24
    max_sessions_per_user: int = 5
    
    # Storage Configuration
    data_directory: str = "data"
    sessions_directory: str = "data/sessions"
    chat_history_directory: str = "data/chat_history"
    appointments_directory: str = "data/appointments"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001
    streamlit_port: int = 8501
    reload: bool = False
    
    # CORS Configuration
    cors_origins: Union[str, List[str]] = "*"
    cors_methods: Union[str, List[str]] = "*"
    cors_headers: Union[str, List[str]] = "*"
    
    @field_validator('cors_origins', 'cors_methods', 'cors_headers', mode='before')
    @classmethod
    def parse_cors_values(cls, v):
        """Parse CORS values from string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            # Split comma-separated values
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 