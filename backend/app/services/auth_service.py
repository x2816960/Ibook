from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
)
from app.config import settings


def register_user(db: Session, data: RegisterRequest) -> User:
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致")

    error = validate_password_strength(data.password)
    if error:
        raise HTTPException(status_code=400, detail=error)

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    if data.email:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        email=data.email or None,
        nickname=data.nickname or None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, data: LoginRequest) -> dict:
    user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.username)
    ).first()

    if user and user.locked_until:
        now = datetime.now(timezone.utc)
        if user.locked_until > now:
            remaining = int((user.locked_until - now).total_seconds() / 60) + 1
            raise HTTPException(
                status_code=403,
                detail=f"账户已锁定，请 {remaining} 分钟后重试",
            )
        else:
            user.locked_until = None
            user.failed_login_attempts = 0

    if not user or not verify_password(data.password, user.password_hash):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
            db.commit()
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    expires = timedelta(
        minutes=settings.REMEMBER_ME_EXPIRE_MINUTES
        if data.remember_me
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = create_access_token(data={"sub": user.username}, expires_delta=expires)

    return {
        "access_token": token,
        "token_type": "bearer",
        "must_change_password": user.must_change_password,
    }


def logout_user(db: Session, token: str):
    from app.utils.security import decode_access_token

    payload = decode_access_token(token)
    if payload:
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            blacklist_entry = TokenBlacklist(
                jti=jti,
                expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
            )
            db.add(blacklist_entry)
            db.commit()


def change_password(db: Session, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")

    error = validate_password_strength(new_password)
    if error:
        raise HTTPException(status_code=400, detail=error)

    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()


def init_admin(db: Session, password: str | None = None):
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        return

    admin_password = password or settings.ADMIN_PASSWORD
    if not admin_password:
        admin_password = "Admin123!"

    admin = User(
        username="admin",
        password_hash=hash_password(admin_password),
        nickname="管理员",
        is_admin=True,
        must_change_password=not password and not settings.ADMIN_PASSWORD,
    )
    db.add(admin)
    db.commit()
