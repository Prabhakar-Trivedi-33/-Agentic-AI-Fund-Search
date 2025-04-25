from pydantic import BaseSettings, Field
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Keys
    openai_api_key: str = Field(default=os.getenv("OPENAI_API_KEY", ""))
    
    # Application Settings
    app_env: str = Field(default=os.getenv("APP_ENV", "development"))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    
    # MFAPI Configuration
    mfapi_base_url: str = "https://api.mfapi.in/mf"
    mfapi_timeout: int = 30
    
    # Cache Settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()