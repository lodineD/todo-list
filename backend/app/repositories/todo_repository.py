from datetime import date, datetime, timezone

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoOrderUpdate


class TodoRepository:
    """封装所有数据库 CRUD 操作，不含业务逻辑判断。"""

    def _build_filter_condition(self, filter_value: str = "all"):
        """根据筛选值构造 where 条件。"""
        today = date.today()
        if filter_value == "today":
            return Todo.due_date == today
        if filter_value == "overdue":
            return (Todo.due_date < today) & (Todo.completed == False)  # noqa: E712
        if filter_value == "completed":
            return Todo.completed == True  # noqa: E712
        return None

    async def get_all(self, session: AsyncSession, filter_value: str = "all") -> list[Todo]:
        condition = self._build_filter_condition(filter_value)
        statement = select(Todo).order_by(Todo.order_index.asc())
        if condition is not None:
            statement = statement.where(condition)
        result = await session.exec(statement)
        return result.all()

    async def get_by_id(self, session: AsyncSession, todo_id: int) -> Todo | None:
        statement = select(Todo).where(Todo.id == todo_id)
        result = await session.exec(statement)
        return result.one_or_none()

    async def get_max_order_index(self, session: AsyncSession) -> int:
        statement = select(func.max(Todo.order_index))
        result = await session.exec(statement)
        max_order = result.one()
        return max_order if max_order is not None else 0

    async def create(self, session: AsyncSession, todo: Todo) -> Todo:
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

        # completed_at 处理：完成状态转变时自动记录/清除已完成时间
        if "completed" in update_data:
            if update_data["completed"] and not todo.completed:
                update_data["completed_at"] = datetime.now(timezone.utc)
            elif not update_data["completed"]:
                update_data["completed_at"] = None

        update_data["updated_at"] = datetime.now(timezone.utc)
        for field, value in update_data.items():
            setattr(todo, field, value)
        session.add(todo)
        await session.commit()
        await session.refresh(todo)
        return todo

    async def update_orders(
        self, session: AsyncSession, order_updates: list[TodoOrderUpdate]
    ) -> None:
        for order in order_updates:
            statement = select(Todo).where(Todo.id == order.id)
            result = await session.exec(statement)
            todo = result.one_or_none()
            if todo is None:
                continue
            todo.order_index = order.order_index
            todo.updated_at = datetime.now(timezone.utc)
            session.add(todo)
        await session.commit()

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