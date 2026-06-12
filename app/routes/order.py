from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.order_schema import OrderCreate
from ..services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


# =========================
# CREATE ORDER (CHECKOUT)
# =========================
@router.post("/")
def create_order(user_id: int, order: OrderCreate, db: Session = Depends(get_db)):

    result = order_service.create_order(db, user_id, order)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# =========================
# GET USER ORDERS
# =========================
@router.get("/user/{user_id}")
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    return order_service.get_user_orders(db, user_id)


# =========================
# GET ALL ORDERS (ADMIN)
# =========================
@router.get("/")
def get_all_orders(db: Session = Depends(get_db)):
    return order_service.get_all_orders(db)


# =========================
# UPDATE ORDER STATUS (ADMIN)
# =========================
@router.put("/{order_id}")
def update_status(order_id: int, status: str, db: Session = Depends(get_db)):

    updated = order_service.update_order_status(db, order_id, status)

    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")

    return updated