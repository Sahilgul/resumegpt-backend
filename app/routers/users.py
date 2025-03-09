from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, auth
from .. database import get_db
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # db_user = await db.query(models.User).filter(models.User.username == user.username).first()

    result = await db.execute(models.User.__table__.select().where(models.User.username == user.username))
    db_user = result.scalar_one_or_none()  # ✅ Async-safe query
    
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Username already registered")
    
    # db_email = db.query(models.User).filter(models.User.email == user.email).first()
    
    
    result = await db.execute(models.User.__table__.select().where(models.User.email == user.email))
    db_email = result.scalar_one_or_none()  # ✅ Async-safe query


    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/me", response_model=User)
async def read_users_me(current_user = Depends(auth.get_current_active_user)):
    return current_user