from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    notification_type: str  # e.g., "email", "sms"
    message: str
    status: str = "sent"  # e.g., "sent", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
