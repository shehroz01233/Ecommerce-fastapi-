from sqlalchemy.orm import Session
from ..models.wishlist import Wishlist
from ..schemas.wishlist_schema import WishlistCreate


def add_to_wishlist(db: Session, user_id: int, data: WishlistCreate):
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == data.product_id
    ).first()

    if existing:
        return {"error": "Already in wishlist"}

    item = Wishlist(
        user_id=user_id,
        product_id=data.product_id
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def get_user_wishlist(db: Session, user_id: int):
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).order_by(Wishlist.created_at.desc()).all()


def remove_from_wishlist(db: Session, user_id: int, product_id: int):
    item = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first()

    if not item:
        return None

    db.delete(item)
    db.commit()

    return {"message": "Removed from wishlist"}
