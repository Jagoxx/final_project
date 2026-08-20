from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class OrderStatus(str, Enum):
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Product:
    id: UUID
    name: str
    price: float
    stock: int
    is_active: bool = True
    
    @classmethod
    def create(cls, name: str, price: float, stock: int) -> "Product":
        return cls(
            id=uuid4(),
            name=name,
            price=price,
            stock=stock,
        )
    
    def decrease_stock(self, quantity: int) -> None:
        if quantity > self.stock:
            raise ValueError(f"Недостаточно товара '{self.name}' на складе")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Количество для пополнения должно быть положительным")
        self.stock += quantity

    def deactivate(self) -> None:
        self.is_active = False

@dataclass
class OrderItem:
    product_id: UUID
    quantity: int
    price: float
    
    @property
    def total(self) -> float:
        return self.price * self.quantity

@dataclass
class Order:
    id: UUID
    user_id: UUID
    items: list[OrderItem]
    status: OrderStatus
    created_at: datetime
    total_amount: float
    
    @classmethod
    def create(cls, user_id: UUID, items: list[OrderItem]) -> "Order":
        if not items:
            raise ValueError("Заказ должен содержать хотя бы одну позицию")
        
        total = sum(item.total for item in items)
        
        return cls(
            id=uuid4(),
            user_id=user_id,
            items=items,
            status=OrderStatus.CONFIRMED,
            created_at=datetime.now(timezone.utc),
            total_amount=total,
        )
    
    def pay(self) -> None:
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Нельзя оплатить заказ в статусе {self.status}")
        self.status = OrderStatus.PAID
    
    def ship(self) -> None:
        if self.status != OrderStatus.PAID:
            raise ValueError(f"Нельзя отправить заказ в статусе {self.status}")
        self.status = OrderStatus.SHIPPED
    
    def deliver(self) -> None:
        if self.status != OrderStatus.SHIPPED:
            raise ValueError(f"Нельзя доставить заказ в статусе {self.status}")
        self.status = OrderStatus.DELIVERED
    
    def cancel(self) -> None:
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError(f"Нельзя отменить заказ в статусе {self.status}")
        self.status = OrderStatus.CANCELLED
    
    def add_item(self, item: OrderItem) -> None:
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError("Можно добавлять товары только в подтверждённый заказ")
        self.items.append(item)
        self._recalculate_total()
    
    def _recalculate_total(self) -> None:
        self.total_amount = sum(item.total for item in self.items)