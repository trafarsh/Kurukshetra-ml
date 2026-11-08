"""
Application configuration for Kurukshetra Kart backend.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Kurukshetra Kart Telemetry & Digital Twin Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    WS_V1_STR: str = "/ws/v1"
    
    # Environment & Security
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "kurukshetra-kart-insecure-development-secret-key-change-in-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    # Default to SQLite for lightweight pit-wall edge deployment
    DATABASE_URL: str = "sqlite:///./kurukshetra_kart.db"
    
    # Telemetry ingestion configuration
    UDP_HOST: str = "0.0.0.0"
    UDP_PORT: int = 8888
    SERIAL_PORT: str = "COM3"
    SERIAL_BAUDRATE: int = 115200
    
    # File Storage
    RAW_STORAGE_DIR: str = "./data/raw"
    REPORTS_STORAGE_DIR: str = "./reports"
    ML_MODELS_DIR: str = "./machine-learning/registry"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
