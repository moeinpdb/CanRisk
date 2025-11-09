"""
Configuration Management
مدیریت تنظیمات با Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """تنظیمات اصلی برنامه"""
    
    # Application
    APP_NAME: str = "Breast Cancer Risk Assessment API"
    VERSION: str = "1.4.2"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """تبدیل CORS origins به لیست"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()