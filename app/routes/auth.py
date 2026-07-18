from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.user_schema import UserCreate, UserLogin
from ..services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    result = auth_service.register_user(db, user)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    result = auth_service.login_user(db, user.email, user.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result
