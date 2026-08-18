from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.todo import Priority


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    due_date: date | None = None
    priority: Priority = Priority.medium
    category: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)


class TodoUpdate(BaseModel):
    """全部字段可选：前端会传全量数据，后端用 exclude_unset 只应用提供的字段。"""

    title: str | None = Field(None, min_length=1, max_length=100)
    completed: bool | None = None
    due_date: date | None = None
    priority: Priority | None = None
    category: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)


class TodoOrderUpdate(BaseModel):
    id: int
    order_index: int


class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    due_date: date | None
    priority: Priority
    category: str | None
    description: str | None
    order_index: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}