from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.mysql_connection import get_db
from app.models import TokenBlacklist, RefreshToken
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def jwt_encode(data : dict):
    encoded_data = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_data

def jwt_decode(token : str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
        return decoded_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token",
        )

def verify_access_token(request: Request, db: Session = Depends(get_db)) -> int:
    token = request.headers.get("Authorization")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    payload = jwt_decode(token)
    user_id = payload.get("uid")
    exp = payload.get("exp")

    if user_id is None or exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Check if the token is blacklisted
    blacklisted_token = db.query(TokenBlacklist).filter_by(token=token).first()
    if blacklisted_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session logged out! Please login again.",
        )

    # Check if the token has expired
    if datetime.utcnow() > datetime.utcfromtimestamp(exp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired! Please login again.",
        )

    return user_id
    
def verify_refresh_token(token: str, user_id: int, db: Session):
    token_data = db.query(RefreshToken).filter(token == token, user_id == user_id).first()
    if token_data and token_data.expires_at > datetime.utcnow():
        return token_data.user_id

    return None
