from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    is_teacher: bool = False
    biometric_reference: Optional[str] = None

class User(UserBase):
    id: int
    is_teacher: bool
    
    class Config:
        orm_mode = True
