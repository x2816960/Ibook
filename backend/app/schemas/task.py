from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    detail_content: str | None = None
    priority: Literal["高", "中", "低"] = "中"
    due_date: datetime | None = None
    is_indefinite: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    detail_content: str | None = None
    priority: Literal["高", "中", "低"] | None = None
    due_date: datetime | None = None
    is_indefinite: bool | None = None


class TaskStatusUpdate(BaseModel):
    status: Literal["待办", "进行中", "已完成", "已取消"]


class TaskSortUpdate(BaseModel):
    task_ids: list[int]


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    detail_content: str | None
    priority: str
    status: str
    due_date: datetime | None
    is_indefinite: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    attachment_count: int = 0

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskStatsResponse(BaseModel):
    total: int
    todo: int
    in_progress: int
    done: int
    cancelled: int
    today_due: int
    overdue: int
