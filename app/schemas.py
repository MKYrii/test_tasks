from pydantic import BaseModel
from typing import Optional
from app.models import TaskStatus

class TaskCreateResponse(BaseModel):
    task_id: int

class TaskStatusResponse(BaseModel):
    status: TaskStatus
    create_time: Optional[str]
    start_time: Optional[str]
    time_to_execute: Optional[int]

class ErrorResponse(BaseModel):
    detail: str