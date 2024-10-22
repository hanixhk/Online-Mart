from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(index=True, unique=True)
    quantity: int
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
