from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.mysql_connection import get_db
from app.utils.helper import verify_access_token
from app.services.friend_service import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    get_friends_list,
    get_friend_suggestions,
    remove_friend,
    block_user,
    unblock_user,
    update_privacy_settings
)
from app.requests.friend_request import FriendRequestCreate, PrivacySettingsUpdate

router = APIRouter()

@router.post("/send-request")
async def create_friend_request(
    request: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await send_friend_request(db, current_user_id, request.receiver_id)

@router.post("/accept-request/{request_id}")
async def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await accept_friend_request(db, current_user_id, request_id)

@router.post("/reject-request/{request_id}")
async def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await reject_friend_request(db, current_user_id, request_id)

@router.get("/list/{user_id}")
async def list_friends(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await get_friends_list(db, user_id, current_user_id)

@router.get("/suggestions")
async def get_suggestions(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await get_friend_suggestions(db, current_user_id)

@router.delete("/remove/{friend_id}")
async def remove_friend_connection(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await remove_friend(db, current_user_id, friend_id)

@router.post("/block/{user_id}")
async def block_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await block_user(db, current_user_id, user_id)

@router.post("/unblock/{user_id}")
async def unblock_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await unblock_user(db, current_user_id, user_id)

@router.put("/privacy-settings")
async def update_privacy_settings_endpoint(
    settings: PrivacySettingsUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    return await update_privacy_settings(db, current_user_id, settings.friends_list_privacy, settings.friend_requests_privacy)