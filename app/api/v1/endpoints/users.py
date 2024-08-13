from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.utils.helper import *
from app.services.user_service import *
from app.core.mysql_connection import get_db
from app.requests.signup_request import SignupRequest

print('here')
router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/signup/")
def signup(signup_request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_email_or_username(db, signup_request.email, signup_request.username)
    if existing_user:
        if existing_user.email == signup_request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif existing_user.username == signup_request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # Create new user
    user = create_user(db, signup_request)
    return {"message": "User registered successfully", "user": user}


@router.post("/signin")
def signin(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email_or_username(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    # Implementation for blacklisting the token
    pass
