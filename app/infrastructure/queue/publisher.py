import json
import aio_pika


class RabbitMQPublisher:
    """Отправляет события в очередь RabbitMQ."""
    
    def __init__(self, url: str = "amqp://guest:guest@localhost/"):
        self.url = url
    
    async def publish(self, event_type: str, payload: str) -> None:
        """Отправить событие в очередь."""
        connection = await aio_pika.connect_robust(self.url)
        
        async with connection:
            channel = await connection.channel()
            
            queue = await channel.declare_queue("order_events", durable=True)
            
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({
                        "event_type": event_type,
                        "payload": json.loads(payload),
                    }).encode(),
                    content_type="application/json",
                ),
                routing_key=queue.name,
            )