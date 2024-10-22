from sqlmodel import Session, select
from .models import Notification
from .schemas import NotificationCreate, NotificationUpdate
from typing import Optional
from datetime import datetime

def create_notification(session: Session, notification: NotificationCreate) -> Notification:
    db_notification = Notification(
        user_id=notification.user_id,
        notification_type=notification.notification_type,
        message=notification.message,
        status="sent"  # Assume notification is sent upon creation
    )
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification

def get_notification(session: Session, notification_id: int) -> Optional[Notification]:
    return session.get(Notification, notification_id)

def list_notifications(session: Session) -> list[Notification]:
    statement = select(Notification)
    results = session.exec(statement)
    return results.all()

def update_notification(session: Session, notification_id: int, notification_update: NotificationUpdate) -> Optional[Notification]:
    notification = session.get(Notification, notification_id)
    if notification:
        for key, value in notification_update.dict(exclude_unset=True).items():
            setattr(notification, key, value)
        notification.updated_at = datetime.utcnow()
        session.add(notification)
        session.commit()
        session.refresh(notification)
    return notification

def delete_notification(session: Session, notification_id: int) -> bool:
    notification = session.get(Notification, notification_id)
    if notification:
        session.delete(notification)
        session.commit()
        return True
    return False