from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.services.auth_service import (
    register_user,
    login_user,
    logout_user,
    change_password,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=MessageResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    register_user(db, data)
    return {"message": "注册成功"}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, data)


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else ""
    logout_user(db, token)
    return {"message": "已退出登录"}


@router.put("/password", response_model=MessageResponse)
def update_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    change_password(db, user, data.old_password, data.new_password)
    return {"message": "密码修改成功"}


@router.get("/profile", response_model=UserResponse)
def get_profile(user: User = Depends(get_current_user)):
    return user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if data.nickname is not None:
        user.nickname = data.nickname
    db.commit()
    db.refresh(user)
    return user
