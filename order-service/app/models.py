from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Order(SQLModel, table=True):
    __tablename__ = "orders" 
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    product_id: int
    quantity: int
    price: float
    total: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None