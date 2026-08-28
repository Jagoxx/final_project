from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    event_id: UUID
    event_type: str
    occurred_at: datetime


@dataclass
class OrderConfirmed(DomainEvent):
    order_id: UUID
    user_id: UUID
    total_amount: float
    
    @classmethod
    def create(cls, order_id: UUID, user_id: UUID, total_amount: float) -> "OrderConfirmed":
        return cls(
            event_id=uuid4(),
            event_type="OrderConfirmed",
            occurred_at=datetime.now(timezone.utc),
            order_id=order_id,
            user_id=user_id,
            total_amount=total_amount,
        )


@dataclass
class OrderEvent(DomainEvent):
    order_id: UUID
    user_id: UUID
    
    @classmethod
    def create(cls, event_type: str, order_id: UUID, user_id: UUID) -> "OrderEvent":
        return cls(
            event_id=uuid4(),
            event_type=event_type,
            occurred_at=datetime.now(timezone.utc),
            order_id=order_id,
            user_id=user_id,
        )