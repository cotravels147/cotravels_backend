from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.mysql_connection import get_db
from app.utils.helper import verify_access_token
from app.models.notification import Notification
from app.services.notification_service import *

router = APIRouter()

@router.get("/")
async def get_notifications(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    notifications = get_user_notifications(db, current_user_id)
    return {"notifications" : notifications} 

@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(verify_access_token)
):
    notification = mark_notification_as_read(db, notification_id, current_user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}