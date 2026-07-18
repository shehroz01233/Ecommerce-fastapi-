from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user_schema import UserCreate
from ..core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, user: UserCreate):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return {"error": "User already exists"}

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
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "Invalid credentials"}

    if not verify_password(password, user.password):
        return {"error": "Invalid credentials"}

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
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


def update_user_profile(db: Session, user: User, name: str = None, email: str = None, password: str = None):
    if name:
        user.name = name
    if email:
        existing = db.query(User).filter(User.email == email, User.id != user.id).first()
        if existing:
            return {"error": "Email already in use"}
        user.email = email
    if password:
        user.password = hash_password(password)

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
