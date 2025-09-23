import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Attendance System"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_attendance.db")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    
    # BLE Token settings
    TOKEN_ROTATION_MINUTES: int = 5
    BLE_TOKEN_LENGTH: int = 16  # Length of BLE tokens in bytes (will be base64 encoded)
    BLE_SERVICE_UUID: str = "0000FEE0-0000-1000-8000-00805F9B34FB"  # Example service UUID
    
settings = Settings()
