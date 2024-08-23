from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils.helper import *
from app.services.user_service import *
from app.core.mysql_connection import get_db
from app.requests.signup_request import SignupRequest
from app.requests.signin_request import SigninRequest

router = APIRouter()

@router.post("/signup")
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
    return {"message": "Registration successful", "user": user}


@router.post("/signin")
def signin(signin_request: SigninRequest, db: Session = Depends(get_db)):
    user = get_user_by_email_or_username(db, signin_request.username, signin_request.username, 'password')
    if not user or not verify_password(signin_request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email, "uid": user.id})
    refresh_token = create_refresh_token()
    
    store_jwt_session(db=db, user_id=user.id, access_token=access_token['token'], expiry=access_token['expiry'])
    store_refresh_token(db=db, user_id=user.id, refresh_token=refresh_token)
    response = JSONResponse(content={"access_token": access_token['token']})
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=86400)  # 7 days expiry
    return response

@router.post("/logout")
def logout(request: Request, response: Response, type: str, db: Session = Depends(get_db), current_user_id: int = Depends(verify_access_token)):
    # Implementation for blacklisting the token
    access_token = request.headers.get('Authorization')
    if type == 'all':
        # Logout from all sessions
        logout_all_sessions(current_user_id, db)
    else:
        blacklist_token(access_token, db)
        refresh_token = request.cookies.get('refresh_token')
        if refresh_token:
            delete_refresh_token(refresh_token, current_user_id, db)
    
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

@router.post("/refresh-token")
def refresh_token(access_token: str, db: Session = Depends(get_db)):
    # Verify the refresh token
    refresh_token = Request.cookies.get('refresh_token')
    if refresh_token:
        payload = jwt_decode(access_token)
        user_id = verify_refresh_token(refresh_token, payload.get('uid'), db)
        response = JSONResponse()
        if not user_id:
            response.delete_cookie('refresh_token')
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        # Generate a new access token
        new_access_token = create_access_token(data={"sub": payload.get('sub'), "uid": user_id})
        store_jwt_session(db=db, user_id=user_id, access_token=new_access_token['token'], expiry=new_access_token['expiry'])
        return {"access_token": new_access_token['token']}
    
    raise HTTPException(status_code=400, detail="Refresh token not found") 
