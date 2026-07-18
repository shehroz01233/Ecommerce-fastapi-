from pydantic import BaseModel, Field
from typing import Optional


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str = "General"
    image_url: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: str

    class Config:
        from_attributes = True
