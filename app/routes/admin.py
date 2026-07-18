from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..core.security import require_admin
from ..models.user import User
from ..models.product import Product
from ..models.order import Order
from ..models.review import Review

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/")
def admin_dashboard(current_user: User = Depends(require_admin)):
    return {
        "message": "Admin Dashboard",
        "status": "active"
    }


@router.get("/stats")
def system_stats(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.sum(Order.total_price)).scalar() or 0
    total_reviews = db.query(Review).count()

    pending_orders = db.query(Order).filter(Order.status == "PENDING").count()
    delivered_orders = db.query(Order).filter(Order.status == "DELIVERED").count()

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": round(float(total_revenue), 2),
        "total_reviews": total_reviews,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders
    }
