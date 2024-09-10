from fastapi import APIRouter, Request, Response, Cookie, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils.helper import *
from app.services.user_service import *
from app.core.mysql_connection import get_db
from app.requests.signup_request import SignupRequest
from app.requests.signin_request import SigninRequest
from app.requests.update_user_request import UpdateUserRequest
from app.requests.change_password_request import ChangePasswordRequest

router = APIRouter()

@router.post("/signup")
def signup(signup_request: SignupRequest, db: Session = Depends(get_db)):
    # Create or restore user
    user = create_or_restore_user(db, signup_request)
    return {"message": "Registration successful", "user": user}


@router.post("/signin")
def signin(signin_request: SigninRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, signin_request)
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
def refresh_token(response: Response, request: Request, refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    # Verify the refresh token
    access_token = request.headers.get('authorization')
    if not access_token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
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

@router.get("/user-profile")
def get_user_profile(db: Session = Depends(get_db), user_id: int = Depends(verify_access_token)):
    user = get_user_by_id(db, user_id, 'profile_picture')
    return user

@router.put("/update-profile")
def update_user_profile(update_request: UpdateUserRequest, db: Session = Depends(get_db), current_user_id: int = Depends(verify_access_token)):
    updated_user = update_user(db, current_user_id, update_request.dict(exclude_unset=True))
    return {"message": "Profile updated successfully", "user": updated_user}

@router.post("/upload-profile-picture")
async def upload_profile_picture(file: UploadFile = File(...), current_user_id: int = Depends(verify_access_token), db: Session = Depends(get_db)):    
    profile_picture_url = await upload_user_profile_picture(file, current_user_id, db)
    return JSONResponse(content={"message": "Profile picture uploaded successfully.", "profile_picture_url": profile_picture_url})

@router.post("/change-password")
def change_password(change_password_request: ChangePasswordRequest, db: Session = Depends(get_db), current_user_id: int = Depends(verify_access_token)):
    change_user_password(db, current_user_id, change_password_request.old_password, change_password_request.new_password)
    return {"message": "Password changed successfully"}

@router.delete("/delete-account")
def delete_account(db: Session = Depends(get_db), current_user_id: int = Depends(verify_access_token)):
    delete_user(db, current_user_id)
    return {"message": "Account deleted successfully"}