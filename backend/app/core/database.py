from collections.abc import AsyncIterator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：提供一个异步会话，并在请求结束后关闭。"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """创建所有尚未存在的表。"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)