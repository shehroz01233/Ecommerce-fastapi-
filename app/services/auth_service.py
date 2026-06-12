from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user_schema import UserCreate
from ..core.security import hash_password, verify_password, create_access_token


# =========================
# REGISTER USER
# =========================
def register_user(db: Session, user: UserCreate):
    # check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return {"error": "User already exists"}

    # create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role="USER"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": new_user
    }


# =========================
# LOGIN USER
# =========================
def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    # user not found
    if not user:
        return {"error": "Invalid credentials"}

    # password check
    if not verify_password(password, user.password):
        return {"error": "Invalid credentials"}

    # create JWT token
    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }