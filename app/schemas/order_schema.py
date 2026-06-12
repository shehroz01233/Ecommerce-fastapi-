from pydantic import BaseModel
from typing import List


# ========================
# ORDER ITEM (SUB STRUCTURE)
# ========================
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


# ========================
# CREATE ORDER (REQUEST)
# ========================
class OrderCreate(BaseModel):
    items: List[OrderItem]


# ========================
# ORDER RESPONSE (SAFE OUTPUT)
# ========================
class OrderOut(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str

    class Config:
        from_attributes = True