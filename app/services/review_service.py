from sqlalchemy.orm import Session
from ..models.review import Review
from ..schemas.review_schema import ReviewCreate


def create_review(db: Session, user_id: int, data: ReviewCreate):
    existing = db.query(Review).filter(
        Review.user_id == user_id,
        Review.product_id == data.product_id
    ).first()

    if existing:
        return {"error": "You already reviewed this product"}

    review = Review(
        user_id=user_id,
        product_id=data.product_id,
        rating=data.rating,
        comment=data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def get_product_reviews(db: Session, product_id: int):
    return db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()


def get_user_reviews(db: Session, user_id: int):
    return db.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).all()


def delete_review(db: Session, review_id: int, user_id: int):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).first()

    if not review:
        return None

    db.delete(review)
    db.commit()

    return {"message": "Review deleted"}


def get_product_rating(db: Session, product_id: int):
    reviews = db.query(Review).filter(Review.product_id == product_id).all()

    if not reviews:
        return {"average": 0, "count": 0}

    total = sum(r.rating for r in reviews)
    return {
        "average": round(total / len(reviews), 1),
        "count": len(reviews)
    }
