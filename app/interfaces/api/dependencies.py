from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import CreateOrder
from app.infrastructure.db import session_factory, SqlOrderRepository, SqlProductRepository


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_create_order_use_case(session: AsyncSession = Depends(get_session)) -> CreateOrder:
    order_repo = SqlOrderRepository(session)
    product_repo = SqlProductRepository(session)
    return CreateOrder(order_repo=order_repo, product_repo=product_repo)