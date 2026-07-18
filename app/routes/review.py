from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.review_schema import ReviewCreate, ReviewOut
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..services import review_service
from ..services.notification_service import notification_service
from ..services.cache_service import cache_service
from ..services.background_tasks import process_review_notification

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewOut)
def create_review(data: ReviewCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = review_service.create_review(db, current_user.id, data)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    cache_service.invalidate_product_rating(data.product_id)

    background_tasks.add_task(process_review_notification, data.product_id, current_user.name, data.rating)

    return ReviewOut(
        id=result.id, user_id=result.user_id, product_id=result.product_id,
        rating=result.rating, comment=result.comment, created_at=result.created_at,
        user_name=current_user.name
    )


@router.get("/product/{product_id}", response_model=PaginatedResponse[ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db), pagination: PaginationParams = Depends()):
    reviews = review_service.get_product_reviews(db, product_id)
    total = len(reviews)
    start = pagination.offset
    end = start + pagination.limit
    pages = max(1, (total + pagination.limit - 1) // pagination.limit)
    items = [
        ReviewOut(
            id=r.id, user_id=r.user_id, product_id=r.product_id,
            rating=r.rating, comment=r.comment, created_at=r.created_at,
            user_name=r.user.name if r.user else None
        )
        for r in reviews[start:end]
    ]
    return PaginatedResponse(
        items=items, total=total, page=pagination.page,
        limit=pagination.limit, pages=pages,
        has_next=pagination.page < pages, has_prev=pagination.page > 1,
    )


@router.get("/user/me", response_model=PaginatedResponse[ReviewOut])
def get_my_reviews(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), pagination: PaginationParams = Depends()):
    reviews = review_service.get_user_reviews(db, current_user.id)
    total = len(reviews)
    start = pagination.offset
    end = start + pagination.limit
    pages = max(1, (total + pagination.limit - 1) // pagination.limit)
    items = [
        ReviewOut(
            id=r.id, user_id=r.user_id, product_id=r.product_id,
            rating=r.rating, comment=r.comment, created_at=r.created_at,
            user_name=current_user.name
        )
        for r in reviews[start:end]
    ]
    return PaginatedResponse(
        items=items, total=total, page=pagination.page,
        limit=pagination.limit, pages=pages,
        has_next=pagination.page < pages, has_prev=pagination.page > 1,
    )


@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = review_service.delete_review(db, review_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Review not found")
    return result
