from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.response import APIResponse
from app.services import user_service
from app.core.security import create_token, verify_password
from app.dependencies import get_current_user, set_user_cache, user_to_dict, delete_user_cache
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=APIResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    user = user_service.create_user(db, user_data)
    return APIResponse(code=200, message="注册成功", data=None)


@router.post("/login", response_model=APIResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    token = create_token({"sub": str(user.id), "role": user.role})
    user_service.update_last_login(db, user)
    
    # 登录时缓存用户信息
    user_dict = user_to_dict(user)
    set_user_cache(user.id, user_dict, expire=3600)
    
    return APIResponse(
        code=200,
        message="登录成功",
        data={
            "token": token,
            "role": user.role,
            "username": user.username
        }
    )


@router.post("/logout", response_model=APIResponse)
def logout(current_user: User = Depends(get_current_user)):
    # 退出时清除用户缓存
    delete_user_cache(current_user.id)
    return APIResponse(code=200, message="退出成功", data=None)


@router.get("/info", response_model=APIResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    def format_datetime(value):
        if isinstance(value, str):
            return value
        elif value:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return None
    
    return APIResponse(
        code=200,
        message="获取成功",
        data={
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "create_time": format_datetime(current_user.create_time),
            "last_login_time": format_datetime(current_user.last_login_time)
        }
    )
