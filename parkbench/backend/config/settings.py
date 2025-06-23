from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "ParkBench API"
    api_version: str = "0.1.0"
    api_debug: bool = False
    
    # Database Settings
    database_url: str = "postgresql://parkbenchuser:parkbenchpassword@localhost:5432/parkbenchdb"
    database_echo: bool = False
    
    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Certificate Settings
    ca_cert_path: Optional[str] = None
    verify_certificates: bool = True
    
    # Agent Settings
    max_agents_per_search: int = 100
    default_session_timeout_minutes: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
