from pydantic import BaseModel, EmailStr


# ========================
# CREATE USER (REQUEST)
# ========================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# ========================
# LOGIN (REQUEST)
# ========================
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ========================
# RESPONSE MODEL (SAFE OUTPUT)
# ========================
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True