from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class BLETokenCreate(BaseModel):
    session_id: str

class BLETokenResponse(BaseModel):
    token_value: str
    created_at: datetime
    expires_at: datetime
    
    class Config:
        orm_mode = True

class BLETokenSubmission(BaseModel):
    session_id: str
    token_value: str
    timestamp: datetime = datetime.utcnow()
    rssi: Optional[int] = None  # Signal strength (Received Signal Strength Indicator)
    biometric_data: Optional[str] = None  # For final check

class BiometricVerification(BaseModel):
    session_id: str
    biometric_data: str
