import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import CORS_ORIGINS
from .core.database import Base, engine
from .core.rate_limit import RateLimitMiddleware
from .core.middleware import (
    RequestIDMiddleware, LoggingMiddleware, SlowRequestMiddleware,
    SecurityHeadersMiddleware, BodySizeLimitMiddleware,
)
from .core.exceptions import register_exception_handlers

from .routes import auth, product, cart, order, admin, user, review, wishlist, notifications, sse

logger = logging.getLogger("ecommerce")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")
    engine.dispose()


app = FastAPI(
    title="E-Commerce API",
    description="Full Stack E-Commerce Backend with Real-Time Features",
    version="2.2.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)
app.add_middleware(SlowRequestMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, default_limit=100, default_window=60)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(product.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(order.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(wishlist.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(sse.router, prefix="/api")


@app.get("/")
def home():
    return {"message": "E-Commerce API v2.2 is running successfully"}


@app.get("/health")
def health_check():
    from .core.redis import redis_manager
    from sqlalchemy import text

    db_status = "ok"
    redis_status = "ok" if redis_manager.connected else "unavailable"

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "redis": redis_status,
        "service": "running",
        "version": "2.2.0",
        "features": [
            "real-time-notifications",
            "redis-caching",
            "rate-limiting",
            "background-tasks",
            "websocket",
            "sse",
            "connection-pooling",
            "request-logging",
            "global-error-handling",
            "security-headers",
            "body-size-limit",
        ]
    }
