from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_admin
from app.models.user import User
from app.schemas.admin import (
    UserToggleRequest,
    SystemStatsResponse,
    ConfigItem,
    ConfigUpdateRequest,
)
from app.schemas.auth import MessageResponse, UserResponse
from app.services import admin_service

router = APIRouter(prefix="/api/admin", tags=["管理员"])


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return admin_service.list_users(db, page, page_size)


@router.patch("/users/{user_id}")
def toggle_user(
    user_id: int,
    data: UserToggleRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    user = admin_service.toggle_user(db, user_id, data.is_active, data.unlock)
    return UserResponse.model_validate(user)


@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    new_password = admin_service.reset_user_password(db, user_id)
    return {"message": f"密码已重置", "new_password": new_password}


@router.get("/stats", response_model=SystemStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return admin_service.get_system_stats(db)


@router.get("/config", response_model=list[ConfigItem])
def get_config(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return admin_service.get_system_config(db)


@router.put("/config", response_model=MessageResponse)
def update_config(
    data: ConfigUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    admin_service.update_system_config(db, data.configs)
    return {"message": "配置已更新"}
