from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import uuid
import re

class LoginRequest(BaseModel):
    email: str = Field(..., max_length=100, description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Please enter a valid email address')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., max_length=100, description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Confirm password")
    terms: bool = Field(..., description="Terms agreement")
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be no more than 50 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Please enter a valid email address')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('terms')
    def validate_terms(cls, v):
        if not v:
            raise ValueError('You must agree to the terms and conditions')
        return v

class UserResponse(BaseModel):
    id_user: str
    username: str
    email: str
    admin: bool

class SessionResponse(BaseModel):
    id_session: int
    id_user: str
    ip: str
    device_details: Optional[str]
    logged_at: datetime

    class Config:
        from_attributes = True
