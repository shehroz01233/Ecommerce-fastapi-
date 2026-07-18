from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("idx_reviews_product_id", "product_id"),
        Index("idx_reviews_user_id", "user_id"),
        Index("idx_reviews_rating", "rating"),
        UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", lazy="joined")
    product = relationship("Product", lazy="joined")
