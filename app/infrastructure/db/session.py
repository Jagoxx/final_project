from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.infrastructure.db import Base
from typing import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/mini_marketplace"

engine = create_async_engine(DATABASE_URL, echo=True)

session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)