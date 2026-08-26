import uuid
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db import OutboxModel


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add(self, event_type: str, payload: str) -> None:
        model = OutboxModel(
            id=uuid.uuid4(),
            event_type=event_type,
            payload=payload,
            created_at=datetime.now(timezone.utc),
            processed=False,
        )
        self.session.add(model)
    
    async def get_unprocessed(self) -> list[OutboxModel]:
        result = await self.session.execute(
            select(OutboxModel).where(OutboxModel.processed == False)
        )
        return list(result.scalars().all())
    
    async def mark_processed(self, event_id: UUID) -> None:
        model = await self.session.get(OutboxModel, event_id)
        if model:
            model.processed = True