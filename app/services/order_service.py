from sqlalchemy import text
from sqlalchemy.orm import Session
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..schemas.order_schema import OrderCreate


def create_order(db: Session, user_id: int, order_data: OrderCreate):
    total_price = 0
    product_cache = {}

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            return {"error": f"Product {item.product_id} not found"}

        result = db.execute(
            text("UPDATE products SET stock = stock - :qty WHERE id = :id AND stock >= :qty"),
            {"qty": item.quantity, "id": item.product_id}
        )
        db.flush()

        if result.rowcount == 0:
            db.rollback()
            return {"error": f"Not enough stock for {product.name}"}

        db.refresh(product)
        total_price += product.price * item.quantity
        product_cache[item.product_id] = product

    order = Order(
        user_id=user_id,
        total_price=total_price,
        status="PENDING"
    )

    db.add(order)
    db.flush()

    for item in order_data.items:
        product = product_cache[item.product_id]
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)

    return {
        "message": "Order created successfully",
        "order": order,
        "total_price": total_price
    }


def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()


def get_all_orders(db: Session):
    return db.query(Order).order_by(Order.created_at.desc()).all()


def update_order_status(db: Session, order_id: int, status: str):
    valid_statuses = {"PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"}
    if status not in valid_statuses:
        return None

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return None

    order.status = status
    db.commit()
    db.refresh(order)

    return order
