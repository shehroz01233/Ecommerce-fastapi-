from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user, require_admin
from ..models.user import User
from ..schemas.order_schema import OrderCreate, OrderOut, StatusUpdate
from ..services import order_service
from ..services.notification_service import notification_service
from ..services.background_tasks import process_order_background
from ..services.cache_service import cache_service

router = APIRouter(prefix="/orders", tags=["Orders"])


def serialize_order(order) -> dict:
    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price
            }
            for item in (order.items or [])
        ]
    }


@router.post("/")
def create_order(order: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = order_service.create_order(db, current_user.id, order)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    order_obj = result["order"]
    items_data = [{"product_id": i.product_id, "quantity": i.quantity, "price": i.price} for i in order_obj.items]

    background_tasks.add_task(
        process_order_background,
        order_obj.id, current_user.id, current_user.email,
        result["total_price"], items_data
    )

    cache_service.invalidate_products()

    return {
        "message": result["message"],
        "order": serialize_order(order_obj),
        "total_price": result["total_price"]
    }


@router.get("/user/me", response_model=List[OrderOut])
def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return order_service.get_user_orders(db, current_user.id)


@router.get("/user/{user_id}", response_model=List[OrderOut])
def get_user_orders(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    return order_service.get_user_orders(db, user_id)


@router.get("/", response_model=List[OrderOut])
def get_all_orders(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return order_service.get_all_orders(db)


@router.put("/{order_id}", response_model=OrderOut)
def update_status(order_id: int, data: StatusUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    updated = order_service.update_order_status(db, order_id, data.status)

    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")

    background_tasks.add_task(
        notification_service.notify_order_status,
        updated.user_id, order_id, data.status
    )

    return updated
