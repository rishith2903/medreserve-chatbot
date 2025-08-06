"""
Configuration settings for MedReserve AI Chatbot System
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "MedReserve AI Chatbot"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8001, env="PORT")
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/medreserve",
        env="DATABASE_URL"
    )
    
    # Spring Boot Backend Integration
    spring_boot_base_url: str = Field(
        default="http://localhost:8080/api",
        env="SPRING_BOOT_BASE_URL"
    )
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Redis Configuration (for caching and sessions)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # WebSocket Configuration
    websocket_ping_interval: int = Field(default=20, env="WEBSOCKET_PING_INTERVAL")
    websocket_ping_timeout: int = Field(default=10, env="WEBSOCKET_PING_TIMEOUT")
    
    # File Upload
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    upload_directory: str = Field(default="uploads", env="UPLOAD_DIRECTORY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # CORS
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Chatbot Configuration
    max_message_length: int = Field(default=1000, env="MAX_MESSAGE_LENGTH")
    max_conversation_history: int = Field(default=50, env="MAX_CONVERSATION_HISTORY")
    
    # NLP Configuration (Optional)
    enable_nlp: bool = Field(default=False, env="ENABLE_NLP")
    nlp_model_path: Optional[str] = Field(default=None, env="NLP_MODEL_PATH")
    
    # Emergency Keywords
    emergency_keywords: list = Field(
        default=[
            "emergency", "urgent", "critical", "severe pain", "chest pain",
            "difficulty breathing", "unconscious", "bleeding", "heart attack",
            "stroke", "allergic reaction", "overdose", "suicide"
        ],
        env="EMERGENCY_KEYWORDS"
    )
    
    # Medical Specializations
    medical_specializations: list = Field(
        default=[
            "Cardiology", "Dermatology", "Endocrinology", "Gastroenterology",
            "Neurology", "Oncology", "Orthopedics", "Pediatrics", "Psychiatry",
            "Pulmonology", "Radiology", "Urology", "Gynecology", "ENT",
            "Ophthalmology", "Internal Medicine", "General Practice"
        ],
        env="MEDICAL_SPECIALIZATIONS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings"""
    debug: bool = False
    log_level: str = "WARNING"


class TestingSettings(Settings):
    """Testing environment settings"""
    debug: bool = True
    database_url: str = "sqlite:///./test.db"
    redis_url: str = "redis://localhost:6379/1"


def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export the appropriate settings
settings = get_settings()
