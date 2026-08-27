from typing import AsyncGenerator
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import CreateOrder
from app.domain import User
from app.infrastructure.db import session_factory, SqlOrderRepository, SqlProductRepository, SqlUserRepository, OutboxRepository
from app.infrastructure.db.config import settings

security = HTTPBearer()

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
    outbox_repo = OutboxRepository(session)
    return CreateOrder(order_repo=order_repo, product_repo=product_repo, outbox_repo=outbox_repo)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Проверяет JWT-токен и возвращает пользователя."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id = payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
    
    user_repo = SqlUserRepository(session)
    user = await user_repo.get_by_id(UUID(user_id))
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    
    return user