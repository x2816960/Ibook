from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskSortUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatsResponse,
)
from app.schemas.auth import MessageResponse
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["任务"])


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.get_tasks(db, user.id, status, priority, keyword, page, page_size)


@router.post("", response_model=TaskResponse)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.create_task(db, user.id, data)


@router.get("/stats", response_model=TaskStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.get_task_stats(db, user.id)


@router.get("/trash", response_model=list[TaskResponse])
def list_trash(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.get_trash_tasks(db, user.id)


@router.get("/sort", response_model=MessageResponse)
def get_sort_info(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取排序信息"""
    return {"message": "ok"}


@router.put("/sort", response_model=MessageResponse)
def update_sort(
    data: TaskSortUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task_service.update_sort_order(db, user.id, data.task_ids)
    return {"message": "排序已更新"}


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.get_task(db, task_id, user.id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.update_task(db, task_id, user.id, data)


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task_service.delete_task(db, task_id, user.id)
    return {"message": "任务已删除"}


@router.patch("/{task_id}/status", response_model=TaskResponse)
def change_status(
    task_id: int,
    data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.change_task_status(db, task_id, user.id, data.status)


@router.post("/{task_id}/restore", response_model=TaskResponse)
def restore_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.restore_task(db, task_id, user.id)


@router.delete("/{task_id}/permanent", response_model=MessageResponse)
def permanent_delete(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task_service.permanent_delete_task(db, task_id, user.id)
    return {"message": "任务已永久删除"}
