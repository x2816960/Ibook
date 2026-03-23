import uuid
import mimetypes
import subprocess
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from app.models.attachment import Attachment
from app.models.task import Task
from app.models.system_config import SystemConfig
from app.utils.file_utils import get_file_type, is_allowed_file
from app.config import UPLOAD_PATH

logger = logging.getLogger(__name__)


def get_upload_limits(db: Session) -> dict:
    configs = db.query(SystemConfig).all()
    limits = {}
    for c in configs:
        limits[c.key] = c.value
    return {
        "max_image_size": int(limits.get("max_image_size_mb", 10)) * 1024 * 1024,
        "max_video_size": int(limits.get("max_video_size_mb", 200)) * 1024 * 1024,
        "max_other_size": int(limits.get("max_other_size_mb", 50)) * 1024 * 1024,
        "max_attachments": int(limits.get("max_attachments_per_task", 10)),
    }


def upload_attachment(
    db: Session, task_id: int, user_id: int, file: UploadFile
) -> dict:
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user_id, Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if not file.filename or not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    file_type = get_file_type(file.filename)
    limits = get_upload_limits(db)

    current_count = db.query(Attachment).filter(Attachment.task_id == task_id).count()
    if current_count >= limits["max_attachments"]:
        raise HTTPException(status_code=400, detail="附件数量已达上限")

    content = file.file.read()
    file_size = len(content)

    max_size_key = f"max_{file_type}_size"
    if file_size > limits[max_size_key]:
        max_mb = limits[max_size_key] / (1024 * 1024)
        raise HTTPException(status_code=400, detail=f"文件大小超过限制({max_mb:.0f}MB)")

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    stored_name = f"{date_prefix}_{uuid.uuid4().hex}.{ext}"
    rel_path = f"{user_id}/{task_id}/{stored_name}"
    abs_path = UPLOAD_PATH / str(user_id) / str(task_id)
    abs_path.mkdir(parents=True, exist_ok=True)

    with open(abs_path / stored_name, "wb") as f:
        f.write(content)

    # 视频文件：检测编码并转码为 H.264（浏览器兼容格式）
    saved_file = abs_path / stored_name
    if file_type == "video":
        saved_file, stored_name, rel_path, file_size = _transcode_video_if_needed(
            saved_file, stored_name, user_id, task_id
        )

    mime = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    attachment = Attachment(
        task_id=task_id,
        file_name=file.filename,
        file_path=rel_path,
        file_size=file_size,
        file_type=file_type,
        mime_type=mime,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return _attachment_to_response(attachment)


def list_attachments(db: Session, task_id: int, user_id: int) -> list[dict]:
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    attachments = db.query(Attachment).filter(Attachment.task_id == task_id).all()
    return [_attachment_to_response(a) for a in attachments]


def get_attachment(db: Session, attachment_id: int, user_id: int | None = None):
    query = db.query(Attachment).join(Task)
    if user_id is not None:
        query = query.filter(Attachment.id == attachment_id, Task.user_id == user_id)
    else:
        query = query.filter(Attachment.id == attachment_id)
    attachment = query.first()
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    return attachment


def delete_attachment(db: Session, attachment_id: int, user_id: int):
    attachment = get_attachment(db, attachment_id, user_id)
    file_path = UPLOAD_PATH / attachment.file_path
    if file_path.exists():
        file_path.unlink()
    db.delete(attachment)
    db.commit()


def delete_task_attachments(db: Session, task_id: int):
    attachments = db.query(Attachment).filter(Attachment.task_id == task_id).all()
    for a in attachments:
        file_path = UPLOAD_PATH / a.file_path
        if file_path.exists():
            file_path.unlink()
        db.delete(a)
    db.commit()


def _attachment_to_response(a: Attachment) -> dict:
    return {
        "id": a.id,
        "task_id": a.task_id,
        "file_name": a.file_name,
        "file_path": a.file_path,
        "file_size": a.file_size,
        "file_type": a.file_type,
        "mime_type": a.mime_type,
        "created_at": a.created_at,
        "url": f"/api/attachments/{a.id}/download",
    }


def _get_video_codec(file_path: Path) -> str | None:
    """用 ffprobe 获取视频编码格式"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip().lower() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _transcode_video_if_needed(
    saved_file: Path, stored_name: str, user_id: int, task_id: int
) -> tuple:
    """如果视频不是 H.264 编码，转码为 H.264"""
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    codec = _get_video_codec(saved_file)
    if codec is None or codec == "h264":
        # 无法检测或已经是 H.264，直接返回
        file_size = saved_file.stat().st_size
        rel_path = f"{user_id}/{task_id}/{stored_name}"
        return saved_file, stored_name, rel_path, file_size

    logger.info(f"视频编码为 {codec}，开始转码为 H.264: {saved_file}")
    out_name = f"{date_prefix}_{uuid.uuid4().hex}.mp4"
    out_path = saved_file.parent / out_name

    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", str(saved_file),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                "-y", str(out_path),
            ],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            logger.warning(f"转码失败: {result.stderr}")
            file_size = saved_file.stat().st_size
            rel_path = f"{user_id}/{task_id}/{stored_name}"
            return saved_file, stored_name, rel_path, file_size

        # 转码成功，删除原文件
        saved_file.unlink()
        file_size = out_path.stat().st_size
        rel_path = f"{user_id}/{task_id}/{out_name}"
        logger.info(f"转码完成: {out_path} ({file_size} bytes)")
        return out_path, out_name, rel_path, file_size

    except (subprocess.TimeoutExpired, Exception) as e:
        logger.warning(f"转码异常: {e}")
        if out_path.exists():
            out_path.unlink()
        file_size = saved_file.stat().st_size
        rel_path = f"{user_id}/{task_id}/{stored_name}"
        return saved_file, stored_name, rel_path, file_size
