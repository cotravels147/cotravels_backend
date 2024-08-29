# app/services/user_service.py

from sqlalchemy.orm import Session, undefer
from sqlalchemy import or_
from sqlalchemy.dialects.mysql import insert
from fastapi import HTTPException, status
from app.models import User, JwtSession, RefreshToken, TokenBlacklist
from app.requests.signup_request import SignupRequest
from app.utils.helper import jwt_encode
from datetime import datetime, timedelta
import bcrypt
import secrets
import uuid

ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 1440

def get_user_by_email_or_username(db: Session, email: str = None, username: str = None, columnToUndefer: str = None):
    # Retrieve a user by email or username.
    query = db.query(User)

    if columnToUndefer and hasattr(User, columnToUndefer):
        columnToUndefer = getattr(User, columnToUndefer)
        query = query.options(undefer(columnToUndefer))

    return query.filter(
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

def store_jwt_session(db: Session, user_id: int, access_token: str, expiry: datetime):
    jwt_session = JwtSession(
        user_id=user_id,
        token=access_token,
        issued_at=datetime.utcnow(),
        expires_at=expiry
    )
    db.add(jwt_session)
    db.commit()

def store_refresh_token(db: Session, user_id: int, refresh_token: str):
    expires_delta = timedelta(minutes=1440)
    refresh_token_entry = RefreshToken(
        user_id=user_id,   
        token=refresh_token,
        issued_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + expires_delta
    )
    db.add(refresh_token_entry)
    db.commit()

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

# Create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY)
    to_encode.update({"exp": expire})
    to_encode.update({"jti": str(uuid.uuid4())})
    encoded_jwt = jwt_encode(to_encode)
    return {"token": encoded_jwt, "expiry": expire}

# Create refresh token
def create_refresh_token() -> str:
    """Generate a secure random string to be used as a refresh token."""
    return secrets.token_urlsafe(64)  # Generate a random 64-character token

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt."""
    # Check the password against the hashed version
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def blacklist_token(token: str, db: Session):
    # Add the JWT to the blacklist
    blacklist_entry = TokenBlacklist(token=token, blacklisted_at=datetime.utcnow())
    db.add(blacklist_entry)
    db.commit()

def delete_refresh_token(refresh_token: str, user_id: int, db: Session):
    # Delete the specific refresh token for the current session
    db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.user_id == user_id
    ).delete()
    db.commit()

def logout_all_sessions(user_id: int, db: Session):
    # Blacklist all JWTs for the user
    jwt_sessions = db.query(JwtSession).filter(JwtSession.user_id == user_id).all()
    for session in jwt_sessions:
        # blacklist_entry = TokenBlacklist(token=session.token, blacklisted_at=datetime.utcnow())
        blacklist_entry = insert(TokenBlacklist).values(token=session.token, blacklisted_at=datetime.utcnow()).prefix_with('IGNORE')
        db.execute(blacklist_entry)
    
    # Delete all refresh tokens for the user
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.commit()