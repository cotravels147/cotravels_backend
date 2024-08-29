from fastapi import APIRouter, Request, Response, Cookie, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils.helper import *
from app.services.user_service import *
from app.core.mysql_connection import get_db
from app.requests.signup_request import SignupRequest
from app.requests.signin_request import SigninRequest
from app.requests.refresh_token_request import TokenRequest
import shutil
from uuid import uuid4

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
def logout(request: Request, response: Response, db: Session = Depends(get_db), current_user_id: int = Depends(verify_access_token)):
    # Implementation for blacklisting the token
    access_token = request.headers.get('Authorization')
    type = request.query_params.get('type')
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

@router.get("/refresh-token")
def refresh_token(response: Response, token_request: TokenRequest, refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    # Verify the refresh token
    access_token = token_request.access_token
    if refresh_token:
        payload = jwt_decode(access_token, {"verify_exp": False})
        user_id = verify_refresh_token(refresh_token, payload.get('uid'), db)
        if not user_id:
            response.delete_cookie(key="refresh_token")
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        # Generate a new access token
        new_access_token = create_access_token(data={"sub": payload.get('sub'), "uid": user_id})
        store_jwt_session(db=db, user_id=user_id, access_token=new_access_token['token'], expiry=new_access_token['expiry'])
        return {"access_token": new_access_token['token']}
    
    raise HTTPException(status_code=401, detail="Invalid or expired refresh token") 

@router.post("/upload-profile-picture")
async def upload_profile_picture(file: UploadFile = File(...), user_id: int = Depends(verify_access_token), db: Session = Depends(get_db)):    
    # Validate the file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    # Define the path to save the profile picture
    profile_picture_dir = "static/profile_pictures"
    os.makedirs(profile_picture_dir, exist_ok=True)  # Create directory if it doesn't exist   
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the existing profile picture if it exists
    if user.profile_picture:
        existing_file_path = os.path.join(profile_picture_dir, user.profile_picture)
        print(existing_file_path)
        if os.path.exists(existing_file_path):
            print('here')
            os.remove(existing_file_path)

    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid4()}_{user_id}.{file_extension}"
    profile_picture_path = f"{profile_picture_dir}/{file_name}"

    # Save the file
    with open(profile_picture_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    user.profile_picture = file_name
    db.commit()
    
    return JSONResponse(content={"message": "Profile picture uploaded successfully.", "profile_picture_url": file_name})
