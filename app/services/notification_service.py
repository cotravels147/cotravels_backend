# app/services/notification_service.py
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType

def create_notification(db: Session, user_id: int, notification_type: NotificationType, content: str):
    notification = Notification(user_id=user_id, type=notification_type, content=content)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        return True
    return False