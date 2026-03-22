from datetime import datetime

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    created_at: datetime
    url: str = ""

    class Config:
        from_attributes = True
