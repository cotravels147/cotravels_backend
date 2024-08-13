# app/services/user_service.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from app.models.user import User
from app.requests.signup_request import SignupRequest
from app.utils.helper import get_password_hash

def get_user_by_email_or_username(db: Session, email: str = None, username: str = None):
    # Retrieve a user by email.
    return db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).first()

def create_user(db: Session, user_data: SignupRequest) -> SignupRequest:
    """Create a new user in the database."""

    # Create a new user instance from the user_data
    user_data = user_data.model_dump()
    user = User(**user_data)

    # Hash the user's password
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    """Retrieve a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: dict):
    """Update an existing user."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    """Delete a user."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
