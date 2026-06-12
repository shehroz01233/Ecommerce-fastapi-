from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])


# =========================
# ADMIN DASHBOARD (BASIC)
# =========================
@router.get("/")
def admin_dashboard():
    return {
        "message": "Admin Dashboard",
        "status": "active"
    }


# =========================
# PLACEHOLDER (CAN EXTEND LATER)
# =========================
@router.get("/stats")
def system_stats():
    return {
        "users": "endpoint coming soon",
        "products": "endpoint coming soon",
        "orders": "endpoint coming soon"
    }