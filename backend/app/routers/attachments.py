from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, Header, Request, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.attachment import AttachmentResponse
from app.schemas.auth import MessageResponse
from app.services import attachment_service
from app.config import UPLOAD_PATH
from app.utils.security import decode_access_token

router = APIRouter(tags=["附件"])


def _resolve_user(db: Session, token_query: Optional[str], authorization: Optional[str]) -> User:
    """从 query 参数或 Authorization header 解析用户"""
    token = token_query
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少认证凭据")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")
    jti = payload.get("jti")
    if jti and db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")
    return user


@router.post("/api/tasks/{task_id}/attachments", response_model=AttachmentResponse)
def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return attachment_service.upload_attachment(db, task_id, user.id, file)


@router.get("/api/tasks/{task_id}/attachments", response_model=list[AttachmentResponse])
def list_attachments(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return attachment_service.list_attachments(db, task_id, user.id)


@router.get("/api/attachments/{attachment_id}/download")
def download_attachment(
    request: Request,
    attachment_id: int,
    preview: bool = Query(False),
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user = _resolve_user(db, token, authorization)

    attachment = attachment_service.get_attachment(db, attachment_id, user.id)
    file_path = UPLOAD_PATH / attachment.file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    file_size = os.path.getsize(file_path)

    # 强制下载（非预览）
    if not preview:
        return FileResponse(
            path=str(file_path),
            media_type=attachment.mime_type,
            filename=attachment.file_name,
            headers={"Content-Disposition": f'attachment; filename="{attachment.file_name}"'},
        )

    # 预览模式：统一用流式响应，支持 Range 请求（视频播放必需）
    range_header = request.headers.get("range")
    start = 0
    end = file_size - 1

    if range_header:
        range_spec = range_header.strip()
        if range_spec.lower().startswith("bytes="):
            range_val = range_spec[6:]
            parts = range_val.split("-", 1)
            if parts[0]:
                start = int(parts[0])
            if parts[1]:
                end = int(parts[1])
            end = min(end, file_size - 1)

    content_length = end - start + 1

    def iter_file():
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = content_length
            while remaining > 0:
                chunk_size = min(65536, remaining)
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    response_headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Disposition": f'inline; filename="{attachment.file_name}"',
    }

    if range_header:
        response_headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        return StreamingResponse(
            iter_file(),
            status_code=206,
            media_type=attachment.mime_type,
            headers=response_headers,
        )

    return StreamingResponse(
        iter_file(),
        status_code=200,
        media_type=attachment.mime_type,
        headers=response_headers,
    )


@router.delete("/api/attachments/{attachment_id}", response_model=MessageResponse)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    attachment_service.delete_attachment(db, attachment_id, user.id)
    return {"message": "附件已删除"}
