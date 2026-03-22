from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


DEFAULT_CONFIG = {
    "max_image_size_mb": ("10", "图片最大文件大小(MB)"),
    "max_video_size_mb": ("200", "视频最大文件大小(MB)"),
    "max_other_size_mb": ("50", "其他附件最大文件大小(MB)"),
    "max_attachments_per_task": ("10", "每个任务最大附件数量"),
}


def init_system_config(db):
    for key, (value, desc) in DEFAULT_CONFIG.items():
        if not db.query(SystemConfig).filter(SystemConfig.key == key).first():
            db.add(SystemConfig(key=key, value=value, description=desc))
    db.commit()
