from datetime import datetime, timezone
from datetime import date
from enum import Enum

from sqlmodel import SQLModel, Field


class Priority(str, Enum):
    """任务优先级。"""

    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Todo(SQLModel, table=True):
    """待办事项数据表模型"""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=100)
    completed: bool = Field(default=False)
    due_date: date | None = Field(default=None)
    priority: Priority = Field(default=Priority.medium)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    order_index: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = Field(default=None)