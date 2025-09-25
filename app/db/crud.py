from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from . import models
from app.schemas import user as user_schemas
from app.schemas import session as session_schemas
from app.schemas import token as token_schemas
from app.core.security import get_password_hash, verify_password
from app.services import biometric, ble_service
from app.core.config import settings
from .logger import logger

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: user_schemas.UserCreate):
    logger.info(f"Creating new user with email: {user.email}")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_teacher=user.is_teacher,
        biometric_reference=user.biometric_reference
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created successfully: ID={db_user.id}, Email={db_user.email}")
    return db_user

# Session operations
def create_class_session(db: Session, teacher_id: int, course_name: str, classroom_location: str = None):
    logger.info(f"Creating new class session: Teacher ID={teacher_id}, Course={course_name}")
    session_id = str(uuid.uuid4())
    db_session = models.ClassSession(
        session_id=session_id,
        teacher_id=teacher_id,
        course_name=course_name,
        classroom_location=classroom_location,
        start_time=datetime.utcnow(),
        is_active=True
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    logger.info(f"Class session created: ID={db_session.id}, Session ID={session_id}")
    return db_session

def end_class_session(db: Session, session_id: str):
    logger.info(f"Ending class session: Session ID={session_id}")
    db_session = get_session_by_id(db, session_id)
    
    if db_session and db_session.is_active:
        db_session.is_active = False
        db_session.end_time = datetime.utcnow()
        
        # Deactivate all active tokens
        for token in db_session.tokens:
            if token.is_active:
                token.is_active = False
        
        db.commit()
        db.refresh(db_session)
        logger.info(f"Class session ended: ID={db_session.id}, Session ID={session_id}")
    else:
        logger.warning(f"Failed to end session: Session ID={session_id} not found or not active")
    return db_session

def get_session_by_id(db: Session, session_id: str):
    return db.query(models.ClassSession).filter(
        models.ClassSession.session_id == session_id
    ).first()

# BLE Token operations
def get_active_ble_token(db: Session, session_id: str):
    session = get_session_by_id(db, session_id)
    if not session:
        return None
        
    return db.query(models.BLEToken).filter(
        models.BLEToken.session_id == session.id,
        models.BLEToken.is_active == True
    ).first()

# Attendance operations
def submit_ble_token(db: Session, student_id: int, submission: token_schemas.BLETokenSubmission):
    session = get_session_by_id(db, submission.session_id)
    if not session:
        return None, "Session not found"
    
    # Validate the token
    is_valid, message = ble_service.validate_ble_token(
        db, 
        submission.session_id, 
        submission.token_value, 
        submission.timestamp
    )
    
    if not is_valid:
        return None, message
    
    # Get the token
    token = db.query(models.BLEToken).filter(
        models.BLEToken.session_id == session.id,
        models.BLEToken.token_value == submission.token_value
    ).first()
    
    # Get or create attendance record
    attendance_record = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.session_id == session.id,
        models.AttendanceRecord.student_id == student_id
    ).first()
    
    if not attendance_record:
        attendance_record = models.AttendanceRecord(
            session_id=session.id,
            student_id=student_id,
            check_in_time=submission.timestamp,
            final_status="pending"
        )
        db.add(attendance_record)
        db.commit()
        db.refresh(attendance_record)
    
    # Record token submission
    token_submission = models.TokenSubmission(
        token_id=token.id,
        student_id=student_id,
        attendance_record_id=attendance_record.id,
        timestamp=submission.timestamp,
        rssi=submission.rssi
    )
    
    db.add(token_submission)
    
    # Check if this is a biometric verification (end of class)
    if submission.biometric_data:
        student = get_user(db, student_id)
        is_verified = biometric.verify_biometric(
            submission.biometric_data, 
            student.biometric_reference
        )
        
        attendance_record.biometric_verified = is_verified
        attendance_record.check_out_time = submission.timestamp
        
        # Update final status
        if not session.is_active:  # Session has ended
            _update_attendance_status(db, attendance_record)
    
    db.commit()
    db.refresh(attendance_record)
    return attendance_record, "Token submission recorded"

def verify_biometric_and_finalize(db: Session, student_id: int, session_id: str, biometric_data: str):
    session = get_session_by_id(db, session_id)
    if not session:
        return None, "Session not found"
    
    # Get attendance record
    attendance_record = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.session_id == session.id,
        models.AttendanceRecord.student_id == student_id
    ).first()
    
    if not attendance_record:
        return None, "No attendance record found"
    
    # Get student
    student = get_user(db, student_id)
    if not student:
        return None, "Student not found"
    
    # Verify biometric
    is_verified = biometric.verify_biometric(biometric_data, student.biometric_reference)
    
    attendance_record.biometric_verified = is_verified
    attendance_record.check_out_time = datetime.utcnow()
    
    # Always update final status after biometric verification
    _update_attendance_status(db, attendance_record)
    
    db.commit()
    db.refresh(attendance_record)
    
    return attendance_record, "Biometric verification completed"

def _update_attendance_status(db: Session, attendance_record):
    """Update the final attendance status based on token submissions and biometric verification"""
    # Count token submissions
    token_count = db.query(models.TokenSubmission).filter(
        models.TokenSubmission.attendance_record_id == attendance_record.id
    ).count()
    
    # Get session details
    session = db.query(models.ClassSession).filter(
        models.ClassSession.id == attendance_record.session_id
    ).first()
    
    # Calculate expected submissions
    expected_submissions = 1  # Minimum expected
    if session.end_time and session.start_time:
        duration_minutes = (session.end_time - session.start_time).total_seconds() / 60
        expected_submissions = max(1, int(duration_minutes / settings.TOKEN_ROTATION_MINUTES))
    
    # Determine final status
    if attendance_record.biometric_verified:
        if token_count >= expected_submissions * 0.8:
            attendance_record.final_status = "present"
        elif token_count >= expected_submissions * 0.5:
            attendance_record.final_status = "partial"
        else:
            attendance_record.final_status = "absent"
    else:
        attendance_record.final_status = "absent"  # Biometric verification failed
    
    return attendance_record
