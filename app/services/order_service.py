from sqlalchemy.orm import Session
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..schemas.order_schema import OrderCreate


def create_order(db: Session, user_id: int, order_data: OrderCreate):
    total_price = 0

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            return {"error": f"Product {item.product_id} not found"}

        if product.stock < item.quantity:
            return {"error": f"Not enough stock for {product.name}"}

        total_price += product.price * item.quantity
        product.stock -= item.quantity

    order = Order(
        user_id=user_id,
        total_price=total_price,
        status="PENDING"
    )

    db.add(order)
    db.flush()

    for item in order_data.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
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
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return None

    order.status = status
    db.commit()
    db.refresh(order)

    return order
