from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.review_schema import ReviewCreate, ReviewOut
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


@router.get("/product/{product_id}", response_model=List[ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = review_service.get_product_reviews(db, product_id)
    return [
        ReviewOut(
            id=r.id, user_id=r.user_id, product_id=r.product_id,
            rating=r.rating, comment=r.comment, created_at=r.created_at,
            user_name=r.user.name if r.user else None
        )
        for r in reviews
    ]


@router.get("/user/me", response_model=List[ReviewOut])
def get_my_reviews(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reviews = review_service.get_user_reviews(db, current_user.id)
    return [
        ReviewOut(
            id=r.id, user_id=r.user_id, product_id=r.product_id,
            rating=r.rating, comment=r.comment, created_at=r.created_at,
            user_name=current_user.name
        )
        for r in reviews
    ]


@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = review_service.delete_review(db, review_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Review not found")
    return result
