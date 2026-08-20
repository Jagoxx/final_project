from abc import ABC, abstractmethod
from uuid import UUID
from app.domain import Order, Product, User


class UserRepository(ABC):
    """Интерфейс репозитория пользователей."""
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по id."""
        ...
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        ...
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """Сохранить пользователя."""
        ...


class ProductRepository(ABC):
    """Интерфейс репозитория товаров."""
    
    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Получить товар по id."""
        ...
    
    @abstractmethod
    async def save(self, product: Product) -> None:
        """Сохранить товар."""
        ...


class OrderRepository(ABC):
    """Интерфейс репозитория заказов."""
    
    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Получить заказ по id."""
        ...
    
    @abstractmethod
    async def save(self, order: Order) -> None:
        """Сохранить заказ."""
        ...