from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import date
import re
import json

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    date_of_birth: date
    gender: str
    phone_number: str
    city: str
    state: str
    country: str
    bio: Optional[str] = None
    travel_preferences: Optional[List[str]] = None
    languages_spoken: Optional[List[str]] = None

    @validator('username')
    def validate_username(cls, v):
        if not re.match("^[a-zA-Z0-9_.-]+$", v):
            raise ValueError('Username must contain only letters, numbers, underscores, dots, or dashes')
        if len(v) < 3 or len(v) > 30:
            raise ValueError('Username must be between 3 and 30 characters long')
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
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError('Name must contain only letters and spaces')
        if len(v) < 2 or len(v) > 50:
            raise ValueError('Name must be between 2 and 50 characters long')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        valid_genders = ['male', 'female', 'other']
        if v.lower() not in valid_genders:
            raise ValueError('Invalid gender. Choose from: male, female, other')
        return v.lower()

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v

    @validator('bio')
    def validate_bio(cls, v):
        if v and len(v) > 500:
            raise ValueError('Bio must not exceed 500 characters')
        return v
    
    @validator('travel_preferences')
    def validate_travel_preferences(cls, v):
        if v:
            if len(v) > 10:
                raise ValueError('You can specify up to 10 travel preferences')
            for pref in v:
                if len(pref) > 50:
                    raise ValueError('Each travel preference must not exceed 50 characters')
        return json.dumps(v) if v else None

    @validator('languages_spoken')
    def validate_languages_spoken(cls, v):
        if v:
            if len(v) > 10:
                raise ValueError('You can specify up to 10 languages')
            for lang in v:
                if len(lang) > 50:
                    raise ValueError('Each language must not exceed 50 characters')
        return json.dumps(v) if v else None
    
    @validator('country', 'state', 'city')
    def blank_string_as_none(cls, v):
        # Convert blank strings to None
        if v == "":
            raise ValueError('Value of this field is required')
        return v