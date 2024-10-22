from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    price: int
    total: int

class OrderRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    status: str
    created_at: datetime
    updated_at: datetime
    price: int
    total: int


    class Config:
        from_attributes = True