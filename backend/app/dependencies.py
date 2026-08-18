from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi import Depends

from app.core.database import get_db
from app.services.todo_service import TodoService


async def get_todo_service(
    session: AsyncSession = Depends(get_db),
) -> TodoService:
    return TodoService(session=session)