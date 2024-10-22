from typing import Optional
from datetime import datetime
from pydantic import BaseModel, condecimal

class TransactionCreate(BaseModel):
    order_id: int
    user_id: int
    amount: condecimal(max_digits=10, decimal_places=2)
    currency: str
    payment_method: str  # "PayFast" or "Stripe"

class TransactionRead(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: float
    currency: str
    payment_method: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TransactionUpdate(BaseModel):
    status: Optional[str] = None  # "pending", "completed", "failed"
