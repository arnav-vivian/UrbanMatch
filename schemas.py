from pydantic import BaseModel,EmailStr
from typing import List, Optional


# Base Model with required fields
class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: EmailStr
    city: str
    interests: List[str]


# For Creating Users (All fields required)
class UserCreate(UserBase):
    pass


# ✅ For PATCH Requests (All fields optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    city: Optional[str] = None

# Response Model (Includes ID)
class User(UserBase):
    id: int

    class Config:
        orm_mode = True

