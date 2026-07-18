from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""


class ReviewOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: str
    created_at: Optional[datetime] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
