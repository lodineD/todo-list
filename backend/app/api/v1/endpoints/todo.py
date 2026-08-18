from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_db
from app.core.exceptions import TodoNotFoundError, TodoTitleEmptyError
from app.dependencies import get_todo_service
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[TodoResponse])
async def list_todos(service: TodoService = Depends(get_todo_service)):
    return await service.get_all_todos()


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate, service: TodoService = Depends(get_todo_service)
):
    try:
        return await service.create_todo(todo_data)
    except TodoTitleEmptyError:
        raise HTTPException(status_code=400, detail="待办标题不能为空")


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
):
    try:
        return await service.update_todo(todo_id, todo_data)
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="待办不存在")
    except TodoTitleEmptyError:
        raise HTTPException(status_code=400, detail="待办标题不能为空")


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int, service: TodoService = Depends(get_todo_service)
):
    try:
        await service.delete_todo(todo_id)
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="待办不存在")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_completed(service: TodoService = Depends(get_todo_service)):
    await service.clear_completed()