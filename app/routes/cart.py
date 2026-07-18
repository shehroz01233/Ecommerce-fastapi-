from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.cart_schema import CartCreate, CartUpdate, CartOut
from ..models.cart import Cart
from ..models.product import Product
from ..services.cache_service import cache_service
from datetime import datetime

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/", response_model=CartOut)
def add_to_cart(cart: CartCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == cart.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == cart.product_id
    ).first()

    if existing:
        existing.quantity += cart.quantity
        db.commit()
        db.refresh(existing)
        cache_service.invalidate_user_cart(current_user.id)
        return CartOut(
            id=existing.id, user_id=existing.user_id, product_id=existing.product_id,
            quantity=existing.quantity, created_at=existing.created_at,
            product_name=product.name, product_price=product.price,
            product_image=product.image_url
        )

    new_item = Cart(
        user_id=current_user.id,
        product_id=cart.product_id,
        quantity=cart.quantity
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    cache_service.invalidate_user_cart(current_user.id)

    return CartOut(
        id=new_item.id, user_id=new_item.user_id, product_id=new_item.product_id,
        quantity=new_item.quantity, created_at=new_item.created_at,
        product_name=product.name, product_price=product.price,
        product_image=product.image_url
    )


@router.get("/", response_model=List[CartOut])
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cached = cache_service.get_user_cart(current_user.id)
    if cached:
        return cached

    items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    result = []
    for item in items:
        result.append({
            "id": item.id, "user_id": item.user_id, "product_id": item.product_id,
            "quantity": item.quantity, "created_at": item.created_at.isoformat() if item.created_at else None,
            "product_name": item.product.name if item.product else None,
            "product_price": item.product.price if item.product else None,
            "product_image": item.product.image_url if item.product else None
        })

    cache_service.set_user_cart(current_user.id, result)
    return result


@router.put("/{cart_id}", response_model=CartOut)
def update_cart_item(cart_id: int, data: CartUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    cache_service.invalidate_user_cart(current_user.id)

    return CartOut(
        id=item.id, user_id=item.user_id, product_id=item.product_id,
        quantity=item.quantity, created_at=item.created_at,
        product_name=item.product.name if item.product else None,
        product_price=item.product.price if item.product else None,
        product_image=item.product.image_url if item.product else None
    )


@router.delete("/{cart_id}")
def remove_item(cart_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    cache_service.invalidate_user_cart(current_user.id)
    return {"message": "Item removed from cart"}


@router.delete("/")
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    for item in items:
        db.delete(item)
    db.commit()
    cache_service.invalidate_user_cart(current_user.id)
    return {"message": "Cart cleared"}
