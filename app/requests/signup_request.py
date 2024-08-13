from pydantic import BaseModel, EmailStr, validator
import re

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str

    @validator('username')
    def validate_username(cls, v):
        # Check if username has special characters
        if not re.match("^[a-zA-Z0-9_.-]+$", v):
            raise ValueError('Username must contain only letters, numbers, underscores, dots, or dashes')
        return v

    @validator('password')
    def validate_password(cls, v):
        # Check password security requirements
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('name')
    def validate_name(cls, v):
        # Check if name has special characters
        if not re.match("^[a-zA-Z\s]+$", v):
            raise ValueError('Name must contain only letters and spaces')
        return v