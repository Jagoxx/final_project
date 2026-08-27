import asyncio

from app.infrastructure.db import OutboxRepository, session_factory
from app.infrastructure.queue.publisher import RabbitMQPublisher


async def process_outbox() -> None:
    """Читает необработанные события из outbox и отправляет в RabbitMQ."""
    publisher = RabbitMQPublisher()
    
    while True:
        async with session_factory() as session:
            outbox_repo = OutboxRepository(session)
            events = await outbox_repo.get_unprocessed()
            
            for event in events:
                try:
                    await publisher.publish(event.event_type, event.payload)
                    await outbox_repo.mark_processed(event.id)
                    await session.commit()
                    print(f"Обработано событие: {event.event_type} ({event.id})")
                except Exception as e:
                    print(f"Ошибка обработки события {event.id}: {e}")
                            
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(process_outbox())