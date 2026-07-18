from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderOut(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: Optional[datetime] = None
    items: list[OrderItemOut] = []

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(PENDING|PROCESSING|SHIPPED|DELIVERED|CANCELLED)$")
