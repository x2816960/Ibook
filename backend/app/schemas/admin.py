from pydantic import BaseModel


class UserToggleRequest(BaseModel):
    is_active: bool | None = None
    unlock: bool | None = None


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str | None
    nickname: str | None
    is_admin: bool
    is_active: bool
    failed_login_attempts: int
    locked_until: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SystemStatsResponse(BaseModel):
    total_users: int
    total_tasks: int
    tasks_by_status: dict


class ConfigItem(BaseModel):
    key: str
    value: str
    description: str | None


class ConfigUpdateRequest(BaseModel):
    configs: list[ConfigItem]
