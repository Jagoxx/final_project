import json
from uuid import UUID
from app.domain import Order, OrderItem, OrderConfirmed
from app.application import OrderRepository, ProductRepository
from app.infrastructure.db import OutboxRepository


class CreateOrder:
    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository, outbox_repo: OutboxRepository):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.outbox_repo = outbox_repo
    
    async def execute(
        self,
        user_id: UUID,
        items: list[dict],
    ) -> Order:
        order_items = []
        products_to_update = []
        
        for item_data in items:
            product = await self.product_repo.get_by_id(item_data["product_id"])
            if product is None:
                raise ValueError(f"Товар {item_data['product_id']} не найден")
            
            if product.stock < item_data["quantity"]:
                raise ValueError(
                    f"Недостаточно товара '{product.name}' на складе: "
                    f"доступно {product.stock}, запрошено {item_data['quantity']}"
                )
            
            order_item = OrderItem(
                product_id=product.id,
                quantity=item_data["quantity"],
                price=product.price,
            )
            order_items.append(order_item)
            
            product.decrease_stock(item_data["quantity"])
            products_to_update.append(product)
        
        order = Order.create(user_id=user_id, items=order_items)
        
        await self.order_repo.save(order)
        
        for product in products_to_update:
            await self.product_repo.save(product)
        
        event = OrderConfirmed.create(
            order_id=order.id,
            user_id=user_id,
            total_amount=order.total_amount,
        )

        payload = json.dumps({
            "order_id": str(event.order_id),
            "user_id": str(event.user_id),
            "total_amount": event.total_amount,
        })
        await self.outbox_repo.add(event_type="OrderConfirmed", payload=payload)
        
        return order