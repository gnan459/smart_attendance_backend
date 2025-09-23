from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud, models
from app.schemas import session as session_schemas
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/session", tags=["session"])

@router.get("/{session_id}", response_model=session_schemas.SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get session
    db_session = crud.get_session_by_id(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Students can only see sessions they've attended
    if not current_user.is_teacher:
        has_attendance = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.session_id == db_session.id,
            models.AttendanceRecord.student_id == current_user.id
        ).first()
        
        if not has_attendance and db_session.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    return db_session
