from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import TodoNotFoundError, TodoTitleEmptyError
from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate


class TodoService:
    """业务逻辑层：校验规则在此处处理，并调用 Repository 完成数据操作。"""

    def __init__(self, session: AsyncSession):
        self.repository = TodoRepository()
        self.session = session

    async def get_all_todos(self) -> list[TodoResponse]:
        todos = await self.repository.get_all(self.session)
        return [TodoResponse.model_validate(todo) for todo in todos]

    async def create_todo(self, todo_data: TodoCreate) -> TodoResponse:
        title = todo_data.title.strip()
        if not title:
            raise TodoTitleEmptyError()
        todo_data = todo_data.model_copy(update={"title": title})
        todo = await self.repository.create(self.session, todo_data)
        return TodoResponse.model_validate(todo)

    async def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> TodoResponse:
        if todo_data.title is not None and not todo_data.title.strip():
            raise TodoTitleEmptyError()
        todo = await self.repository.update(self.session, todo_id, todo_data)
        if todo is None:
            raise TodoNotFoundError()
        return TodoResponse.model_validate(todo)

    async def delete_todo(self, todo_id: int) -> None:
        deleted = await self.repository.delete(self.session, todo_id)
        if not deleted:
            raise TodoNotFoundError()

    async def clear_completed(self) -> int:
        return await self.repository.delete_completed(self.session)