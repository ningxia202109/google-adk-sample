from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserBase(BaseModel):
    name: str
    email: EmailStr
    habits: Optional[List[str]] = []


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    habits: Optional[List[str]] = None


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class Team(BaseModel):
    name: str
    members: List[int] = []  # List of user IDs
