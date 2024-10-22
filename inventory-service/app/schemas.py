from typing import Optional
from datetime import datetime
from pydantic import BaseModel, PositiveInt, NonNegativeInt

class InventoryCreate(BaseModel):
    product_id: int
    quantity: NonNegativeInt

class InventoryRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class InventoryUpdate(BaseModel):
    quantity: Optional[NonNegativeInt] = None
    is_available: Optional[bool] = None
