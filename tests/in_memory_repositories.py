from uuid import UUID
from app.domain import Order, Product, User
from app.application.ports import OrderRepository, ProductRepository, UserRepository


class InMemoryUserRepository(UserRepository):
    """Хранит пользователей в словаре."""
    
    def __init__(self):
        self._users: dict[UUID, User] = {}
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)
    
    async def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    async def save(self, user: User) -> None:
        self._users[user.id] = user


class InMemoryProductRepository(ProductRepository):
    """Хранит товары в словаре."""
    
    def __init__(self):
        self._products: dict[UUID, Product] = {}
    
    async def get_by_id(self, product_id: UUID) -> Product | None:
        return self._products.get(product_id)
    
    async def save(self, product: Product) -> None:
        self._products[product.id] = product


class InMemoryOrderRepository(OrderRepository):
    """Хранит заказы в словаре."""
    
    def __init__(self):
        self._orders: dict[UUID, Order] = {}
    
    async def get_by_id(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)
    
    async def save(self, order: Order) -> None:
        self._orders[order.id] = order