import secrets
import string

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.task import Task
from app.models.system_config import SystemConfig
from app.utils.security import hash_password


def list_users(db: Session, page: int = 1, page_size: int = 20):
    q = db.query(User)
    total = q.count()
    users = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": users, "total": total, "page": page, "page_size": page_size}


def toggle_user(db: Session, user_id: int, is_active: bool | None = None, unlock: bool | None = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="不能修改管理员账户")
    if is_active is not None:
        user.is_active = is_active
    if unlock:
        user.failed_login_attempts = 0
        user.locked_until = None
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, user_id: int) -> str:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    chars = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(chars) for _ in range(12))
    user.password_hash = hash_password(new_password)
    db.commit()
    return new_password


def get_system_stats(db: Session) -> dict:
    total_users = db.query(User).count()
    total_tasks = db.query(Task).filter(Task.is_deleted == False).count()
    statuses = db.query(Task.status, func.count()).filter(
        Task.is_deleted == False
    ).group_by(Task.status).all()
    tasks_by_status = {s: c for s, c in statuses}
    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "tasks_by_status": tasks_by_status,
    }


def get_system_config(db: Session) -> list[dict]:
    configs = db.query(SystemConfig).all()
    return [{"key": c.key, "value": c.value, "description": c.description} for c in configs]


def update_system_config(db: Session, configs: list):
    for item in configs:
        c = db.query(SystemConfig).filter(SystemConfig.key == item.key).first()
        if c:
            c.value = item.value
    db.commit()
