from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import Base, engine
from .core.rate_limit import RateLimitMiddleware

from .routes import auth, product, cart, order, admin, user, review, wishlist, notifications, sse


app = FastAPI(
    title="E-Commerce API",
    description="Full Stack E-Commerce Backend with Real-Time Features",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"message": "E-Commerce API v2.0 is running successfully"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected",
        "service": "running",
        "version": "2.0.0",
        "features": [
            "real-time-notifications",
            "redis-caching",
            "rate-limiting",
            "background-tasks",
            "websocket",
            "sse"
        ]
    }
