import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    DATABASE_URL: str = "sqlite:///./data/ibook.db"
    UPLOAD_DIR: str = "./uploads"
    BACKUP_DIR: str = "./backups"
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REMEMBER_ME_EXPIRE_MINUTES: int = 10080  # 7 days

    ADMIN_PASSWORD: str | None = None

    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    TRASH_AUTO_PURGE_DAYS: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_PATH = BASE_DIR / settings.UPLOAD_DIR
BACKUP_PATH = BASE_DIR / settings.BACKUP_DIR
DATA_PATH = BASE_DIR / "data"

for p in [UPLOAD_PATH, BACKUP_PATH, DATA_PATH]:
    p.mkdir(parents=True, exist_ok=True)
