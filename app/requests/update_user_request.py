from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import date
import re
import json

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    travel_preferences: Optional[List[str]] = None
    languages_spoken: Optional[List[str]] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not re.match(r"^[a-zA-Z\s]+$", v):
                raise ValueError('Name must contain only letters and spaces')
            if len(v) < 2 or len(v) > 50:
                raise ValueError('Name must be between 2 and 50 characters long')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        if v is not None:
            valid_genders = ['male', 'female', 'other']
            if v.lower() not in valid_genders:
                raise ValueError('Invalid gender. Choose from: male, female, other')
            return v.lower()
        return v

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            if not re.match(r'^\+?1?\d{9,15}$', v):
                raise ValueError('Invalid phone number format')
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v is not None:
            if v > date.today():
                raise ValueError('Date of birth cannot be in the future')
        return v

    @validator('bio')
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio must not exceed 500 characters')
        return v
    
    @validator('travel_preferences')
    def validate_travel_preferences(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('You can specify up to 10 travel preferences')
            for pref in v:
                if len(pref) > 50:
                    raise ValueError('Each travel preference must not exceed 50 characters')
            return json.dumps(v)
        return None

    @validator('languages_spoken')
    def validate_languages_spoken(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('You can specify up to 10 languages')
            for lang in v:
                if len(lang) > 50:
                    raise ValueError('Each language must not exceed 50 characters')
            return json.dumps(v)
        return None
    
    @validator('country', 'state', 'city')
    def blank_string_as_none(cls, v):
        if v == "":
            raise ValueError('Value of this field is required')
        return v

    class Config:
        extra = 'forbid'