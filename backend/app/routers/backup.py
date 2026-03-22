from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_admin
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.services import backup_service

router = APIRouter(prefix="/api/admin/backup", tags=["备份恢复"])


@router.post("/export")
def export_backup(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    filename = backup_service.export_backup(db)
    return {"filename": filename, "message": "备份已创建"}


@router.get("/download/{filename}")
def download_backup(
    filename: str,
    _: User = Depends(get_current_admin),
):
    path = backup_service.get_backup_path(filename)
    return FileResponse(
        path=str(path),
        media_type="application/gzip",
        filename=filename,
    )


@router.post("/import", response_model=MessageResponse)
async def import_backup(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    content = await file.read()
    return backup_service.import_backup(db, content, file.filename)


@router.get("/list")
def list_backups(
    _: User = Depends(get_current_admin),
):
    return backup_service.list_backups()


@router.delete("/delete/{filename}", response_model=MessageResponse)
def delete_backup(
    filename: str,
    _: User = Depends(get_current_admin),
):
    return backup_service.delete_backup(filename)


@router.delete("/delete-all", response_model=MessageResponse)
def delete_all_backups(
    _: User = Depends(get_current_admin),
):
    return backup_service.delete_all_backups()
