from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud, models
from app.schemas import session as session_schemas
from app.schemas.token import BLETokenResponse
from app.api.routes.auth import get_current_user
from app.services import ble_service

router = APIRouter(prefix="/teacher", tags=["teacher"])

async def get_current_teacher(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a teacher account",
        )
    return current_user

@router.post("/session/start", response_model=session_schemas.SessionResponse)
async def start_class_session(
    session: session_schemas.SessionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher)
):
    # Create session
    db_session = crud.create_class_session(
        db, 
        current_teacher.id, 
        session.course_name,
        session.classroom_location
    )
    
    # Start token rotation in background
    ble_service.start_token_rotation(db, db_session.session_id)
    
    return db_session

@router.post("/session/{session_id}/end", response_model=session_schemas.SessionResponse)
async def end_class_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher)
):
    # Get session
    db_session = crud.get_session_by_id(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    if db_session.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not authorized to end this session")
    
    # Stop token rotation
    ble_service.stop_token_rotation(session_id)
    
    # End session
    db_session = crud.end_class_session(db, session_id)
    return db_session

@router.get("/session/{session_id}/token", response_model=BLETokenResponse)
async def get_current_token(
    session_id: str,
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher)
):
    # Get session
    db_session = crud.get_session_by_id(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    if db_session.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    # Get active token
    active_token = crud.get_active_ble_token(db, session_id)
    
    if not active_token:
        # Generate a new token if no active token exists
        active_token = ble_service.generate_ble_token(db, session_id)
        if not active_token:
            raise HTTPException(status_code=400, detail="Failed to generate token")
    
    return active_token

@router.get("/sessions", response_model=List[session_schemas.SessionResponse])
async def get_teacher_sessions(
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher)
):
    return db.query(models.ClassSession).filter(
        models.ClassSession.teacher_id == current_teacher.id
    ).all()

@router.get("/session/{session_id}/attendance", response_model=List[session_schemas.AttendanceStatus])
async def get_session_attendance(
    session_id: str,
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher)
):
    # Get session
    db_session = crud.get_session_by_id(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    if db_session.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    # Get attendance records with student info
    results = []
    for record in db_session.attendance_records:
        student = crud.get_user(db, record.student_id)
        
        # Count token submissions
        token_count = db.query(models.TokenSubmission).filter(
            models.TokenSubmission.attendance_record_id == record.id
        ).count()
        
        results.append(
            session_schemas.AttendanceStatus(
                student_id=student.id,
                student_name=student.full_name,
                check_in_time=record.check_in_time,
                check_out_time=record.check_out_time,
                biometric_verified=record.biometric_verified,
                final_status=record.final_status,
                token_count=token_count
            )
        )
    
    return results
