from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from models import User
from routers.auth import oauth2_scheme

router = APIRouter()

class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool
    is_admin: bool

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    for key, value in user.dict(exclude_unset=True).items():
        if key == "password":
            setattr(db_user, "hashed_password", get_password_hash(value))
        else:
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(db_user)
    db.commit()
    return {"message": "用户已删除"} 