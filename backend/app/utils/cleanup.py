from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.task import Task
from app.models.token_blacklist import TokenBlacklist
from app.models.attachment import Attachment
from app.config import settings, UPLOAD_PATH


def cleanup_trash():
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.TRASH_AUTO_PURGE_DAYS)
        tasks = db.query(Task).filter(
            Task.is_deleted == True,
            Task.deleted_at <= cutoff,
        ).all()
        for task in tasks:
            for att in task.attachments:
                fp = UPLOAD_PATH / att.file_path
                if fp.exists():
                    fp.unlink()
            db.delete(task)
        db.commit()
    finally:
        db.close()


def cleanup_token_blacklist():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        db.query(TokenBlacklist).filter(TokenBlacklist.expires_at < now).delete()
        db.commit()
    finally:
        db.close()
