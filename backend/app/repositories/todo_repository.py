from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoRepository:
    """封装所有数据库 CRUD 操作，不含业务逻辑判断。"""

    async def get_all(self, session: AsyncSession) -> list[Todo]:
        statement = select(Todo).order_by(Todo.created_at.desc())
        result = await session.exec(statement)
        return result.all()

    async def get_by_id(self, session: AsyncSession, todo_id: int) -> Todo | None:
        statement = select(Todo).where(Todo.id == todo_id)
        result = await session.exec(statement)
        return result.one_or_none()

    async def create(self, session: AsyncSession, todo_data: TodoCreate) -> Todo:
        todo = Todo(title=todo_data.title)
        session.add(todo)
        await session.commit()
        await session.refresh(todo)
        return todo

    async def update(
        self, session: AsyncSession, todo_id: int, todo_data: TodoUpdate
    ) -> Todo | None:
        statement = select(Todo).where(Todo.id == todo_id)
        result = await session.exec(statement)
        todo = result.one_or_none()
        if todo is None:
            return None

        update_data = todo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        session.add(todo)
        await session.commit()
        await session.refresh(todo)
        return todo

    async def delete(self, session: AsyncSession, todo_id: int) -> bool:
        statement = select(Todo).where(Todo.id == todo_id)
        result = await session.exec(statement)
        todo = result.one_or_none()
        if todo is None:
            return False
        await session.delete(todo)
        await session.commit()
        return True

    async def delete_completed(self, session: AsyncSession) -> int:
        statement = select(Todo).where(Todo.completed == True)  # noqa: E712
        result = await session.exec(statement)
        todos = result.all()
        count = len(todos)
        for todo in todos:
            await session.delete(todo)
        await session.commit()
        return count