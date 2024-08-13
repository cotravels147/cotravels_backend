from jose import jwt, JWTError
from datetime import datetime, timedelta
import bcrypt

SECRET_KEY = "your-secret-key"  
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT token for the given data."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode a JWT token and return the data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError("Invalid token") from e

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