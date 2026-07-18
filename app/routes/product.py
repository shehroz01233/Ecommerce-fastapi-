from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.security import require_admin
from ..models.user import User
from ..schemas.product_schema import ProductCreate, ProductUpdate, ProductOut
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..services import product_service
from ..services.cache_service import cache_service
from ..services.notification_service import notification_service
from ..services.background_tasks import process_stock_alert

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductOut)
def create(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    new_product = product_service.create_product(db, product)
    cache_service.invalidate_products()
    cache_service.invalidate_categories()
    notification_service.notify_admin_alert(
        f"New product added: {new_product.name}", "product"
    )
    return new_product


@router.get("/", response_model=PaginatedResponse[ProductOut])
def get_all(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    pagination: PaginationParams = Depends(),
):
    products = product_service.get_all_products(db, search=search, category=category)
    total = len(products)
    start = pagination.offset
    end = start + pagination.limit
    page_items = products[start:end]
    pages = max(1, (total + pagination.limit - 1) // pagination.limit)

    return PaginatedResponse(
        items=[
            {
                "id": p.id, "name": p.name, "description": p.description,
                "price": p.price, "stock": p.stock, "category": p.category,
                "image_url": p.image_url
            }
            for p in page_items
        ],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        pages=pages,
        has_next=pagination.page < pages,
        has_prev=pagination.page > 1,
    )


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cached = cache_service.get_categories()
    if cached:
        return cached

    categories = product_service.get_categories(db)
    cache_service.set_categories(categories)
    return categories


@router.get("/{product_id}", response_model=ProductOut)
def get_one(product_id: int, db: Session = Depends(get_db)):
    cached = cache_service.get_product(product_id)
    if cached:
        return cached

    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = {
        "id": product.id, "name": product.name, "description": product.description,
        "price": product.price, "stock": product.stock, "category": product.category,
        "image_url": product.image_url
    }
    cache_service.set_product(product_id, result)
    return result


@router.get("/{product_id}/rating")
def get_product_rating(product_id: int, db: Session = Depends(get_db)):
    cached = cache_service.get_product_rating(product_id)
    if cached:
        return cached

    from ..models.review import Review
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    if not reviews:
        return {"average": 0, "count": 0}

    total = sum(r.rating for r in reviews)
    result = {"average": round(total / len(reviews), 1), "count": len(reviews)}
    cache_service.set_product_rating(product_id, result)
    return result


@router.put("/{product_id}", response_model=ProductOut)
def update(product_id: int, updated_data: ProductUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    old_product = product_service.get_product_by_id(db, product_id)
    if not old_product:
        raise HTTPException(status_code=404, detail="Product not found")

    old_price = old_product.price
    updated = product_service.update_product(db, product_id, updated_data)

    cache_service.invalidate_product(product_id)

    if updated_data.price is not None and updated_data.price < old_price:
        background_tasks.add_task(
            notification_service.notify_price_drop,
            product_id, updated.name, old_price, updated.price
        )

    if updated_data.stock is not None:
        background_tasks.add_task(process_stock_alert, product_id, updated.name, updated.stock)

    return updated


@router.delete("/{product_id}")
def delete(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = product_service.delete_product(db, product_id)
    cache_service.invalidate_product(product_id)
    notification_service.notify_admin_alert(f"Product deleted: {product.name}", "product")
    return result
