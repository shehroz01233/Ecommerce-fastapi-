from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.wishlist_schema import WishlistCreate, WishlistOut
from ..services import wishlist_service
from ..models.product import Product

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.post("/", response_model=WishlistOut)
def add_to_wishlist(data: WishlistCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = wishlist_service.add_to_wishlist(db, current_user.id, data)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    product = db.query(Product).filter(Product.id == data.product_id).first()
    return WishlistOut(
        id=result.id, user_id=result.user_id, product_id=result.product_id,
        product_name=product.name if product else None,
        product_price=product.price if product else None,
        product_image=product.image_url if product else None
    )


@router.get("/", response_model=List[WishlistOut])
def get_wishlist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = wishlist_service.get_user_wishlist(db, current_user.id)
    result = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        result.append(WishlistOut(
            id=item.id, user_id=item.user_id, product_id=item.product_id,
            product_name=product.name if product else None,
            product_price=product.price if product else None,
            product_image=product.image_url if product else None
        ))
    return result


@router.delete("/{product_id}")
def remove_from_wishlist(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = wishlist_service.remove_from_wishlist(db, current_user.id, product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    return result
