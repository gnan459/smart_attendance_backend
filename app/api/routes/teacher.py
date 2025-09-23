from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.database import get_db
from app.db import crud, models
from app.schemas import session as session_schemas
from app.schemas.token import BLETokenResponse
from app.api.routes.auth import get_current_user
from app.services import ble_service
from datetime import datetime, timedelta

router = APIRouter(prefix="/teacher", tags=["teacher"])
@router.get("/analytics/attendance_percentage", response_model=List[Dict[str, Any]])
async def get_attendance_percentage(
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher),
    period: str = "month"  # "month" or "semester"
):
    """
    Returns each student's attendance percentage for the current month or semester.
    """
    now = datetime.now()
    if period == "month":
        start_date = now.replace(day=1)
    else:
        # For demo, assume semester starts 4 months ago
        start_date = now - timedelta(days=120)
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.teacher_id == current_teacher.id,
        models.ClassSession.start_time >= start_date
    ).all()
    student_attendance = {}
    total_classes = len(sessions)
    for session in sessions:
        for record in session.attendance_records:
            sid = record.student_id
            if sid not in student_attendance:
                student_attendance[sid] = {"present": 0, "student_name": crud.get_user(db, sid).full_name}
            if record.final_status == "present":
                student_attendance[sid]["present"] += 1
    results = []
    for sid, data in student_attendance.items():
        percent = (data["present"] / total_classes * 100) if total_classes > 0 else 0
        results.append({
            "student_id": sid,
            "student_name": data["student_name"],
            "attendance_percentage": round(percent, 2)
        })
    return results

@router.get("/analytics/daily_class_report", response_model=Dict[str, Any])
async def get_daily_class_report(
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher),
    date: str = None
):
    """
    Returns total present vs absent count for all classes on a given day.
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    start_dt = datetime.strptime(date, "%Y-%m-%d")
    end_dt = start_dt + timedelta(days=1)
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.teacher_id == current_teacher.id,
        models.ClassSession.start_time >= start_dt,
        models.ClassSession.start_time < end_dt
    ).all()
    present = 0
    absent = 0
    for session in sessions:
        for record in session.attendance_records:
            if record.final_status == "present":
                present += 1
            else:
                absent += 1
    return {"date": date, "present": present, "absent": absent}

@router.get("/analytics/attendance_trends", response_model=List[Dict[str, Any]])
async def get_attendance_trends(
    db: Session = Depends(get_db),
    current_teacher: models.User = Depends(get_current_teacher),
    days: int = 30
):
    """
    Returns attendance counts per day for the last N days (for charting).
    """
    now = datetime.now()
    start_date = now - timedelta(days=days)
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.teacher_id == current_teacher.id,
        models.ClassSession.start_time >= start_date
    ).all()
    trends = {}
    for session in sessions:
        day = session.start_time.strftime("%Y-%m-%d")
        if day not in trends:
            trends[day] = {"present": 0, "absent": 0}
        for record in session.attendance_records:
            if record.final_status == "present":
                trends[day]["present"] += 1
            else:
                trends[day]["absent"] += 1
    # Convert to list for charting
    results = []
    for day in sorted(trends.keys()):
        results.append({"date": day, "present": trends[day]["present"], "absent": trends[day]["absent"]})
    return results

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



