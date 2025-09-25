from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SessionBase(BaseModel):
    course_name: str
    classroom_location: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    session_id: str
    teacher_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class AttendanceStatus(BaseModel):
    student_id: int
    student_name: str
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    biometric_verified: bool
    final_status: str
    token_count: Optional[int] = None
    
    class Config:
        from_attributes = True
