from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import Base, engine

# routes
from .routes import auth, product, cart, order, admin


# =========================
# APP INIT
# =========================
app = FastAPI(
    title="E-Commerce API",
    description="Full Stack E-Commerce Backend using FastAPI",
    version="1.0.0"
)


# =========================
# CORS (for Next.js frontend)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later change to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# CREATE DATABASE TABLES
# =========================
Base.metadata.create_all(bind=engine)


# =========================
# REGISTER ROUTES
# =========================
app.include_router(auth.router, prefix="/api")
app.include_router(product.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(order.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


# =========================
# HEALTH CHECK ROUTE
# =========================
@app.get("/")
def home():
    return {
        "message": "E-Commerce API is running successfully 🚀"
    }


# =========================
# TEST ROUTE
# =========================
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected",
        "service": "running"
    }