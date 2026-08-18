from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class Todo(SQLModel, table=True):
    """待办事项数据表模型"""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=100)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))