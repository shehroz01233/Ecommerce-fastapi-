from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WishlistCreate(BaseModel):
    product_id: int


class WishlistOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: Optional[datetime] = None
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    product_image: Optional[str] = None

    class Config:
        from_attributes = True
