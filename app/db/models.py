from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_teacher = Column(Boolean, default=False)
    biometric_reference = Column(Text, nullable=True)
    
    # Relationships
    sessions = relationship("ClassSession", back_populates="teacher", foreign_keys="ClassSession.teacher_id")
    attendance_records = relationship("AttendanceRecord", back_populates="student")

class ClassSession(Base):
    __tablename__ = "class_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    course_name = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    classroom_location = Column(String, nullable=True)  # Optional classroom location
    
    # Relationships
    teacher = relationship("User", back_populates="sessions", foreign_keys=[teacher_id])
    tokens = relationship("BLEToken", back_populates="session")
    attendance_records = relationship("AttendanceRecord", back_populates="session")

class BLEToken(Base):
    __tablename__ = "ble_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"))
    token_value = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    session = relationship("ClassSession", back_populates="tokens")
    token_submissions = relationship("TokenSubmission", back_populates="token")

class TokenSubmission(Base):
    __tablename__ = "token_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("ble_tokens.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    attendance_record_id = Column(Integer, ForeignKey("attendance_records.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    rssi = Column(Integer, nullable=True)  # Signal strength for proximity estimation
    
    # Relationships
    token = relationship("BLEToken", back_populates="token_submissions")
    student = relationship("User")
    attendance_record = relationship("AttendanceRecord", back_populates="token_submissions")
    
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    biometric_verified = Column(Boolean, default=False)
    final_status = Column(String, default="pending")  # pending, present, absent, partial
    
    # Relationships
    session = relationship("ClassSession", back_populates="attendance_records")
    student = relationship("User", back_populates="attendance_records")
    token_submissions = relationship("TokenSubmission", back_populates="attendance_record")
