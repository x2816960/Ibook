from datetime import datetime, timezone, timedelta

from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.task import Task

ALLOWED_TRANSITIONS = {
    "待办": ["进行中", "已取消"],
    "进行中": ["已完成", "待办"],
    "已完成": ["进行中"],
    "已取消": ["待办"],
}


def get_tasks(
    db: Session,
    user_id: int,
    status: str | None = None,
    priority: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(Task).filter(Task.user_id == user_id, Task.is_deleted == False)

    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == priority)
    if keyword:
        q = q.filter(
            (Task.title.contains(keyword)) | (Task.description.contains(keyword))
        )

    total = q.count()
    items = (
        q.order_by(Task.sort_order.asc(), Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = []
    for t in items:
        resp = _task_to_response(t)
        result.append(resp)

    return {"items": result, "total": total, "page": page, "page_size": page_size}


def create_task(db: Session, user_id: int, data) -> dict:
    max_order = (
        db.query(func.max(Task.sort_order))
        .filter(Task.user_id == user_id, Task.is_deleted == False)
        .scalar()
    )
    task = Task(
        title=data.title,
        description=data.description,
        detail_content=data.detail_content,
        priority=data.priority,
        due_date=data.due_date if not data.is_indefinite else None,
        is_indefinite=data.is_indefinite,
        sort_order=(max_order or 0) + 1,
        user_id=user_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_response(task)


def get_task(db: Session, task_id: int, user_id: int) -> dict:
    task = _get_user_task(db, task_id, user_id)
    return _task_to_response(task)


def update_task(db: Session, task_id: int, user_id: int, data) -> dict:
    task = _get_user_task(db, task_id, user_id)
    for field in ["title", "description", "detail_content", "priority", "due_date", "is_indefinite"]:
        value = getattr(data, field, None)
        if value is not None:
            if field == "due_date" and (data.is_indefinite if data.is_indefinite is not None else task.is_indefinite):
                setattr(task, field, None)
            else:
                setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return _task_to_response(task)


def delete_task(db: Session, task_id: int, user_id: int):
    task = _get_user_task(db, task_id, user_id)
    task.is_deleted = True
    task.deleted_at = datetime.now(timezone.utc)
    db.commit()


def change_task_status(db: Session, task_id: int, user_id: int, new_status: str) -> dict:
    task = _get_user_task(db, task_id, user_id)
    allowed = ALLOWED_TRANSITIONS.get(task.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"不允许从 '{task.status}' 切换到 '{new_status}'",
        )
    task.status = new_status
    db.commit()
    db.refresh(task)
    return _task_to_response(task)


def update_sort_order(db: Session, user_id: int, task_ids: list[int]):
    for order, tid in enumerate(task_ids):
        task = db.query(Task).filter(
            Task.id == tid, Task.user_id == user_id, Task.is_deleted == False
        ).first()
        if task:
            task.sort_order = order
    db.commit()


def get_task_stats(db: Session, user_id: int) -> dict:
    base = db.query(Task).filter(Task.user_id == user_id, Task.is_deleted == False)
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    total = base.count()
    todo = base.filter(Task.status == "待办").count()
    in_progress = base.filter(Task.status == "进行中").count()
    done = base.filter(Task.status == "已完成").count()
    cancelled = base.filter(Task.status == "已取消").count()
    today_due = base.filter(
        Task.due_date >= today_start,
        Task.due_date < today_end,
        Task.status.in_(["待办", "进行中"]),
    ).count()
    overdue = base.filter(
        Task.due_date < now,
        Task.is_indefinite == False,
        Task.due_date.isnot(None),
        Task.status.in_(["待办", "进行中"]),
    ).count()

    return {
        "total": total,
        "todo": todo,
        "in_progress": in_progress,
        "done": done,
        "cancelled": cancelled,
        "today_due": today_due,
        "overdue": overdue,
    }


def get_trash_tasks(db: Session, user_id: int):
    tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.is_deleted == True)
        .order_by(Task.deleted_at.desc())
        .all()
    )
    return [_task_to_response(t) for t in tasks]


def restore_task(db: Session, task_id: int, user_id: int) -> dict:
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user_id, Task.is_deleted == True
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    task.is_deleted = False
    task.deleted_at = None
    task.status = "待办"
    db.commit()
    db.refresh(task)
    return _task_to_response(task)


def permanent_delete_task(db: Session, task_id: int, user_id: int):
    from app.services.attachment_service import delete_task_attachments
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user_id, Task.is_deleted == True
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    delete_task_attachments(db, task_id)
    db.delete(task)
    db.commit()


def _get_user_task(db: Session, task_id: int, user_id: int) -> Task:
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user_id, Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


def _task_to_response(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "detail_content": task.detail_content,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "is_indefinite": task.is_indefinite,
        "sort_order": task.sort_order,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "user_id": task.user_id,
        "attachment_count": len(task.attachments) if task.attachments else 0,
    }
