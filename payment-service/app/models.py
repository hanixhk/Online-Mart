from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(index=True, unique=True)
    user_id: int
    amount: float
    currency: str
    payment_method: str  # e.g., "PayFast" or "Stripe"
    status: str = "pending"  # e.g., "pending", "completed", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
