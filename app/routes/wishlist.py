from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.wishlist_schema import WishlistCreate, WishlistOut
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..services import wishlist_service

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.post("/", response_model=WishlistOut)
def add_to_wishlist(data: WishlistCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = wishlist_service.add_to_wishlist(db, current_user.id, data)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return WishlistOut(
        id=result.id, user_id=result.user_id, product_id=result.product_id,
        product_name=result.product.name if result.product else None,
        product_price=result.product.price if result.product else None,
        product_image=result.product.image_url if result.product else None
    )


@router.get("/", response_model=PaginatedResponse[WishlistOut])
def get_wishlist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), pagination: PaginationParams = Depends()):
    items = wishlist_service.get_user_wishlist(db, current_user.id)
    total = len(items)
    start = pagination.offset
    end = start + pagination.limit
    pages = max(1, (total + pagination.limit - 1) // pagination.limit)
    page_items = [
        WishlistOut(
            id=item.id, user_id=item.user_id, product_id=item.product_id,
            product_name=item.product.name if item.product else None,
            product_price=item.product.price if item.product else None,
            product_image=item.product.image_url if item.product else None
        )
        for item in items[start:end]
    ]
    return PaginatedResponse(
        items=page_items, total=total, page=pagination.page,
        limit=pagination.limit, pages=pages,
        has_next=pagination.page < pages, has_prev=pagination.page > 1,
    )


@router.delete("/{product_id}")
def remove_from_wishlist(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = wishlist_service.remove_from_wishlist(db, current_user.id, product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    return result
