"""
Web Bluetooth BLE Service - Real BLE without hardware
"""
import uuid
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import models
from app.core.config import settings

# BLE Service UUID for your attendance system
ATTENDANCE_SERVICE_UUID = "12345678-1234-5678-9abc-123456789abc"
TOKEN_CHARACTERISTIC_UUID = "87654321-4321-8765-cba9-987654321abc"

def generate_ble_advertisement_data(db: Session, session_id: str):
    """Generate real BLE advertisement data that devices can scan"""
    session = db.query(models.ClassSession).filter(
        models.ClassSession.session_id == session_id,
        models.ClassSession.is_active == True
    ).first()
    
    if not session:
        return None
    
    # Create BLE advertisement data structure
    advertisement_data = {
        "service_uuid": ATTENDANCE_SERVICE_UUID,
        "service_data": {
            "session_id": session_id,
            "course_name": session.course_name,
            "classroom": session.classroom_location,
            "timestamp": datetime.utcnow().isoformat(),
            "token_rotation_interval": settings.TOKEN_ROTATION_MINUTES
        },
        "characteristics": {
            "token_characteristic": TOKEN_CHARACTERISTIC_UUID,
            "current_token": generate_rotating_token(session_id)
        }
    }
    
    return advertisement_data

def generate_rotating_token(session_id: str):
    """Generate time-based rotating token that changes every interval"""
    import hashlib
    import time
    
    # Create time-based token that changes every TOKEN_ROTATION_MINUTES
    current_time_slot = int(time.time() // (settings.TOKEN_ROTATION_MINUTES * 60))
    
    # Combine session_id with time slot for unique, rotating token
    token_data = f"{session_id}:{current_time_slot}:{settings.SECRET_KEY}"
    token_hash = hashlib.sha256(token_data.encode()).hexdigest()[:16]
    
    return token_hash

def validate_time_based_token(session_id: str, submitted_token: str, submission_time: datetime):
    """Validate time-based token with grace period"""
    import time
    import hashlib
    
    submission_timestamp = submission_time.timestamp()
    current_time_slot = int(submission_timestamp // (settings.TOKEN_ROTATION_MINUTES * 60))
    
    # Check current time slot and previous time slot (grace period)
    for time_slot in [current_time_slot, current_time_slot - 1]:
        expected_token_data = f"{session_id}:{time_slot}:{settings.SECRET_KEY}"
        expected_token = hashlib.sha256(expected_token_data.encode()).hexdigest()[:16]
        
        if submitted_token == expected_token:
            return True, "Token valid"
    
    return False, "Invalid or expired token"