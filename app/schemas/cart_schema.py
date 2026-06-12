from pydantic import BaseModel


# ========================
# ADD TO CART (REQUEST)
# ========================
class CartCreate(BaseModel):
    product_id: int
    quantity: int


# ========================
# UPDATE CART ITEM (OPTIONAL)
# ========================
class CartUpdate(BaseModel):
    quantity: int


# ========================
# CART RESPONSE (SAFE OUTPUT)
# ========================
class CartOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True