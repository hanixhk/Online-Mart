from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class NotificationCreate(BaseModel):
    user_id: int
    notification_type: str  # "email" or "sms"
    message: str

class NotificationRead(BaseModel):
    id: int
    user_id: int
    notification_type: str
    message: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NotificationUpdate(BaseModel):
    status: Optional[str] = None  # "sent" or "failed"
    message: Optional[str] = None
