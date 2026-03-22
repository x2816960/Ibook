import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException

from app.config import UPLOAD_PATH, BACKUP_PATH, DATA_PATH
from app.database import engine, recreate_engine


def export_backup(db: Session) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"ibook_backup_{timestamp}"
    backup_file = BACKUP_PATH / f"{backup_name}.tar.gz"

    # 确保 WAL 文件中的更改写入主数据库文件
    with engine.connect() as conn:
        conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
        conn.commit()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        db_source = DATA_PATH / "ibook.db"
        if db_source.exists():
            shutil.copy2(db_source, tmpdir / "ibook.db")

        uploads_dest = tmpdir / "uploads"
        if UPLOAD_PATH.exists():
            shutil.copytree(UPLOAD_PATH, uploads_dest)

        with tarfile.open(backup_file, "w:gz") as tar:
            for item in tmpdir.iterdir():
                tar.add(item, arcname=item.name)

    return f"{backup_name}.tar.gz"


def list_backups() -> list[dict]:
    if not BACKUP_PATH.exists():
        return []
    backups = []
    for f in sorted(BACKUP_PATH.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.name.endswith(".tar.gz"):
            stat = f.stat()
            backups.append({
                "filename": f.name,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    return backups


def get_backup_path(filename: str) -> Path:
    path = BACKUP_PATH / filename
    if not path.exists() or not path.name.endswith(".tar.gz"):
        raise HTTPException(status_code=404, detail="备份文件不存在")
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")
    return path


def import_backup(db: Session, file_content: bytes, filename: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        archive = tmpdir / "backup.tar.gz"
        archive.write_bytes(file_content)

        try:
            with tarfile.open(archive, "r:gz") as tar:
                # Security: check for path traversal
                for member in tar.getmembers():
                    if member.name.startswith("/") or ".." in member.name:
                        raise HTTPException(status_code=400, detail="备份文件包含不安全的路径")
                tar.extractall(tmpdir / "extracted")
        except tarfile.TarError:
            raise HTTPException(status_code=400, detail="无效的备份文件格式")

        extracted = tmpdir / "extracted"

        db_file = extracted / "ibook.db"
        if not db_file.exists():
            raise HTTPException(status_code=400, detail="备份文件中未找到数据库")

        db.close()

        target_db = DATA_PATH / "ibook.db"

        # 重新创建引擎并关闭所有连接池，确保没有进程持有旧数据库文件的连接
        recreate_engine()

        # 删除旧的 WAL 和 SHM 文件，避免 SQLite 读取时应用旧数据
        for suffix in ["-wal", "-shm", "-journal"]:
            old_file = target_db.parent / (target_db.name + suffix)
            if old_file.exists():
                old_file.unlink()
        shutil.copy2(db_file, target_db)

        uploads_dir = extracted / "uploads"
        if uploads_dir.exists():
            if UPLOAD_PATH.exists():
                shutil.rmtree(UPLOAD_PATH)
            shutil.copytree(uploads_dir, UPLOAD_PATH)

    # 重新创建数据库引擎，刷新连接
    recreate_engine()

    return {"message": "数据恢复成功"}


def delete_backup(filename: str):
    path = get_backup_path(filename)
    path.unlink()
    return {"message": f"备份 {filename} 已删除"}


def delete_all_backups():
    if not BACKUP_PATH.exists():
        return {"message": "没有备份文件"}
    count = 0
    for f in BACKUP_PATH.iterdir():
        if f.name.endswith(".tar.gz"):
            f.unlink()
            count += 1
    return {"message": f"已删除 {count} 个备份文件"}
