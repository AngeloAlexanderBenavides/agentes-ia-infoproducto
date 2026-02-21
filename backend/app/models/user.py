"""
User Model
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """
    User model representing a customer
    """
    phone_number: str
    name: Optional[str] = None
    country: Optional[str] = None
    level: Optional[str] = None  # beginner, intermediate, advanced
    created_at: datetime = datetime.now()

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """
    Schema for creating a new user
    """
    phone_number: str
    name: str
    country: str


class UserUpdate(BaseModel):
    """
    Schema for updating user information
    """
    name: Optional[str] = None
    country: Optional[str] = None
    level: Optional[str] = None
