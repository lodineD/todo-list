from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import TodoNotFoundError, TodoTitleEmptyError
from app.models.todo import Todo
from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import (
    TodoCreate,
    TodoOrderUpdate,
    TodoResponse,
    TodoUpdate,
)


class TodoService:
    """业务逻辑层：校验规则在此处处理，并调用 Repository 完成数据操作。"""

    def __init__(self, session: AsyncSession):
        self.repository = TodoRepository()
        self.session = session

    async def get_all_todos(self, filter_value: str = "all") -> list[TodoResponse]:
        todos = await self.repository.get_all(self.session, filter_value)
        return [TodoResponse.model_validate(todo) for todo in todos]

    async def create_todo(self, todo_data: TodoCreate) -> TodoResponse:
        title = todo_data.title.strip()
        if not title:
            raise TodoTitleEmptyError()
        order_index = await self.repository.get_max_order_index(self.session) + 1
        todo = Todo(
            title=title,
            due_date=todo_data.due_date,
            priority=todo_data.priority,
            category=todo_data.category,
            description=todo_data.description,
            order_index=order_index,
        )
        todo = await self.repository.create(self.session, todo)
        return TodoResponse.model_validate(todo)

    async def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> TodoResponse:
        if todo_data.title is not None and not todo_data.title.strip():
            raise TodoTitleEmptyError()
        if todo_data.title is not None:
            todo_data = todo_data.model_copy(
                update={"title": todo_data.title.strip()}
            )
        todo = await self.repository.update(self.session, todo_id, todo_data)
        if todo is None:
            raise TodoNotFoundError()
        return TodoResponse.model_validate(todo)

    async def reorder_todos(self, order_updates: list[TodoOrderUpdate]) -> list[TodoResponse]:
        await self.repository.update_orders(self.session, order_updates)
        todos = await self.repository.get_all(self.session, "all")
        return [TodoResponse.model_validate(todo) for todo in todos]

    async def delete_todo(self, todo_id: int) -> None:
        deleted = await self.repository.delete(self.session, todo_id)
        if not deleted:
            raise TodoNotFoundError()

    async def clear_completed(self) -> int:
        return await self.repository.delete_completed(self.session)