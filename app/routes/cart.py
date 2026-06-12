from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.cart_schema import CartCreate
from ..models.cart import Cart

router = APIRouter(prefix="/cart", tags=["Cart"])


# =========================
# ADD TO CART
# =========================
@router.post("/")
def add_to_cart(cart: CartCreate, user_id: int, db: Session = Depends(get_db)):

    new_item = Cart(
        user_id=user_id,
        product_id=cart.product_id,
        quantity=cart.quantity
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# =========================
# GET USER CART
# =========================
@router.get("/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):

    items = db.query(Cart).filter(Cart.user_id == user_id).all()
    return items


# =========================
# REMOVE ITEM FROM CART
# =========================
@router.delete("/{cart_id}")
def remove_item(cart_id: int, db: Session = Depends(get_db)):

    item = db.query(Cart).filter(Cart.id == cart_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()

    return {"message": "Item removed from cart"}