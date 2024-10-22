from typing import Optional
from datetime import datetime
from pydantic import BaseModel, condecimal

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int
    price: condecimal(max_digits=10, decimal_places=2)

class ProductRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
        name: Optional[str] = None
        description: Optional[str] = None
        price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
        quantity: Optional[int] = None
        is_active: Optional[bool] = None

# class ProductCreate(BaseModel):
#     name: str
#     description: Optional[str] = None
#     quantity: int
#     price: condecimal(max_digits=10, decimal_places=2)
#     total_price: condecimal(max_digits=10, decimal_places=2)
# class ProductRead(BaseModel):
#     id: int
#     name: str
#     description: Optional[str] = None
#     price: float
#     total_price: float
#     quantity: int
#     is_active: bool
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

# class ProductUpdate(BaseModel):
#     name: Optional[str] = None
#     description: Optional[str] = None
#     price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
#     quantity: Optional[int] = None
#     is_active: Optional[bool] = None
