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


#  For PATCH Requests (All fields optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    city: Optional[str] = None
    interests:Optional[List[str]]=None



class MatchPreferences(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    preferred_cities: Optional[List[str]] = None  
    interests: Optional[List[str]] = None
    strict_interest_match: bool = False  # Default is False,
    gender_preference: Optional[str] = "any"  # Default "any" if not provided


# Response Model (Includes ID)
class User(UserBase):
    id: int

    class Config:
        orm_mode = True
