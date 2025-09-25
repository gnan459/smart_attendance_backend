import asyncio
import base64
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import models
from app.core.config import settings

# Store active background tasks
active_token_tasks = {}

async def token_rotation_task(db: Session, session_id: str):
    """Background task to rotate BLE tokens every X minutes"""
    while True:
        # Check if session is still active
        session = db.query(models.ClassSession).filter(
            models.ClassSession.session_id == session_id,
            models.ClassSession.is_active == True
        ).first()
        
        if not session:
            break
            
        # Create new token
        generate_ble_token(db, session_id)
        
        # Wait for the token rotation interval
        await asyncio.sleep(settings.TOKEN_ROTATION_MINUTES * 60)
    
    # Clean up
    if session_id in active_token_tasks:
        del active_token_tasks[session_id]

def start_token_rotation(db: Session, session_id: str):
    """Start the token rotation background task"""
    if session_id in active_token_tasks:
        return False
    
    # Create initial token
    initial_token = generate_ble_token(db, session_id)
    if not initial_token:
        return False
    
    # Start background task (only if we're in an async context)
    try:
        task = asyncio.create_task(token_rotation_task(db, session_id))
        active_token_tasks[session_id] = task
    except RuntimeError:
        # No event loop running, skip background task for now
        # The initial token is still created
        pass
    
    return True

def stop_token_rotation(session_id: str):
    """Stop the token rotation background task"""
    if session_id in active_token_tasks:
        active_token_tasks[session_id].cancel()
        del active_token_tasks[session_id]
        return True
    return False

def generate_ble_token(db: Session, session_id: str):
    """Generate a new BLE token for a class session"""
    session = db.query(models.ClassSession).filter(
        models.ClassSession.session_id == session_id,
        models.ClassSession.is_active == True
    ).first()
    
    if not session:
        return None
        
    # Generate a secure random token
    token_bytes = os.urandom(settings.BLE_TOKEN_LENGTH)
    token_value = base64.urlsafe_b64encode(token_bytes).decode('utf-8')
    
    # Calculate expiration time
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=settings.TOKEN_ROTATION_MINUTES)
    
    # Deactivate previous tokens for this session
    previous_tokens = db.query(models.BLEToken).filter(
        models.BLEToken.session_id == session.id,
        models.BLEToken.is_active == True
    ).all()
    
    for token in previous_tokens:
        token.is_active = False
    
    # Create new token
    new_token = models.BLEToken(
        session_id=session.id,
        token_value=token_value,
        created_at=created_at,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    
    return new_token

def validate_ble_token(db: Session, session_id: str, token_value: str, timestamp: datetime):
    """Validate a submitted BLE token"""
    session = db.query(models.ClassSession).filter(
        models.ClassSession.session_id == session_id
    ).first()
    
    if not session:
        return False, "Session not found"
    
    # Find the token
    token = db.query(models.BLEToken).filter(
        models.BLEToken.session_id == session.id,
        models.BLEToken.token_value == token_value,
        models.BLEToken.created_at <= timestamp,
        models.BLEToken.expires_at >= timestamp
    ).first()
    
    if not token:
        # Check if this was a recent token that just expired
        recent_token = db.query(models.BLEToken).filter(
            models.BLEToken.session_id == session.id,
            models.BLEToken.token_value == token_value,
            models.BLEToken.expires_at < timestamp,
            models.BLEToken.expires_at >= timestamp - timedelta(minutes=2)  # Grace period
        ).first()
        
        if recent_token:
            return True, "Token accepted (grace period)"
        return False, "Invalid or expired token"
    
    return True, "Token valid"