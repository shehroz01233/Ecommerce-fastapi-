from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CartCreate(BaseModel):
    product_id: int
    quantity: int


class CartUpdate(BaseModel):
    quantity: int


class CartOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: Optional[datetime] = None
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    product_image: Optional[str] = None

    class Config:
        from_attributes = True
