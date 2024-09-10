# app/services/user_service.py

from sqlalchemy.orm import Session, undefer
from sqlalchemy import or_
from sqlalchemy.dialects.mysql import insert
from fastapi import HTTPException, status, UploadFile
from app.models import User, JwtSession, RefreshToken, TokenBlacklist
from app.requests.signup_request import SignupRequest
from app.requests.signin_request import SigninRequest
from app.utils.helper import jwt_encode
from datetime import datetime, timedelta
from uuid import uuid4
import bcrypt
import shutil
import os
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

def authenticate_user(db: Session, signin_request: SigninRequest):
    user = get_user_by_email_or_username(db, signin_request.username, signin_request.username, 'password')
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This account has been deleted")
    
    if not verify_password(signin_request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    return user

def create_or_restore_user(db: Session, user_data: SignupRequest) -> User:
    """Create a new user or restore a deleted user in the database."""
    existing_user = get_user_by_email_or_username(db, user_data.email, user_data.username)

    if existing_user:
        if existing_user.is_deleted:
            # Restore the deleted user
            existing_user.is_deleted = False
            existing_user.name = user_data.name
            existing_user.password = get_password_hash(user_data.password)
            existing_user.date_of_birth = user_data.date_of_birth
            existing_user.gender = user_data.gender
            existing_user.phone_number = user_data.phone_number
            existing_user.city = user_data.city
            existing_user.state = user_data.state
            existing_user.country = user_data.country
            existing_user.bio = user_data.bio
            existing_user.travel_preferences = user_data.travel_preferences
            existing_user.languages_spoken = user_data.languages_spoken
            existing_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            # User exists and is not deleted
            if existing_user.email == user_data.email:
                raise HTTPException(status_code=400, detail="Email already registered")
            else:
                raise HTTPException(status_code=400, detail="Username already exists")

    # Create a new user
    new_user = User(**user_data.dict(exclude={'password'}))
    new_user.password = get_password_hash(user_data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

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

def get_user_by_id(db: Session, user_id: int, columnToUndefer: str = None):
    """Retrieve a user by ID."""
    query = db.query(User)
    
    if columnToUndefer and hasattr(User, columnToUndefer):
        columnToUndefer = getattr(User, columnToUndefer)
        query = query.options(undefer(columnToUndefer))
    
    return query.filter(User.id == user_id).first()

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
    
    user.is_deleted = True
    db.commit()
    
    # remove all logged in sessions
    logout_all_sessions(user_id, db)

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

def change_user_password(db: Session, user_id: int, old_password: str, new_password: str):
    user = get_user_by_id(db, user_id, 'password')
    if not user or not verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    hashed_password = get_password_hash(new_password)
    user.password = hashed_password
    db.commit()

async def upload_user_profile_picture(file: UploadFile, user_id: int, db: Session):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    profile_picture_dir = "static/profile_pictures"
    os.makedirs(profile_picture_dir, exist_ok=True)
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.profile_picture:
        existing_file_path = os.path.join(profile_picture_dir, user.profile_picture)
        if os.path.exists(existing_file_path):
            os.remove(existing_file_path)

    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid4()}_{user_id}.{file_extension}"
    profile_picture_path = f"{profile_picture_dir}/{file_name}"

    with open(profile_picture_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    user.profile_picture = file_name
    db.commit()
    
    return file_name