import uuid
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import IdempotencyKeyModel


class IdempotencyRepository:
    """Репозиторий для идемпотентных ключей."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_order_id(self, key: str) -> UUID | None:
        result = await self.session.execute(
            select(IdempotencyKeyModel).where(IdempotencyKeyModel.key == key)
        )
        model = result.scalar_one_or_none()
        return model.order_id if model else None
    
    async def save(self, key: str, order_id: UUID) -> None:
        model = IdempotencyKeyModel(
            id=uuid.uuid4(),
            key=key,
            order_id=order_id,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(model)