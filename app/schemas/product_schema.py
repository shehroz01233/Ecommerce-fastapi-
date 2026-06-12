from pydantic import BaseModel


# ========================
# CREATE PRODUCT (REQUEST)
# ========================
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int


# ========================
# UPDATE PRODUCT (OPTIONAL BUT PROFESSIONAL)
# ========================
class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None


# ========================
# PRODUCT RESPONSE (SAFE OUTPUT)
# ========================
class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

    class Config:
        from_attributes = True