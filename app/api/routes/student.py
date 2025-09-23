from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.database import get_db
from app.db import crud, models
from app.schemas.token import BLETokenSubmission, BiometricVerification
from app.schemas import session as session_schemas
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/student", tags=["student"])

async def get_current_student(current_user: models.User = Depends(get_current_user)):
    if current_user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a student account",
        )
    return current_user

@router.post("/token/submit")
async def submit_token(
    submission: BLETokenSubmission,
    db: Session = Depends(get_db),
    current_student: models.User = Depends(get_current_student)
):
    # Record token submission
    attendance_record, message = crud.submit_ble_token(
        db, 
        current_student.id, 
        submission
    )
    
    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    
    # Count token submissions
    token_count = db.query(models.TokenSubmission).filter(
        models.TokenSubmission.attendance_record_id == attendance_record.id
    ).count()
    
    return {
        "status": "success", 
        "message": message,
        "token_count": token_count,
        "biometric_verified": attendance_record.biometric_verified,
        "final_status": attendance_record.final_status
    }

@router.post("/biometric/verify")
async def verify_biometric(
    verification: BiometricVerification,
    db: Session = Depends(get_db),
    current_student: models.User = Depends(get_current_student)
):
    attendance_record, message = crud.verify_biometric_and_finalize(
        db,
        current_student.id,
        verification.session_id,
        verification.biometric_data
    )
    
    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    
    # Count token submissions
    token_count = db.query(models.TokenSubmission).filter(
        models.TokenSubmission.attendance_record_id == attendance_record.id
    ).count()
    
    return {
        "status": "success", 
        "verified": attendance_record.biometric_verified, 
        "token_count": token_count,
        "final_status": attendance_record.final_status
    }


