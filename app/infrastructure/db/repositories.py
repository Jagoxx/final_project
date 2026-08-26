import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain import Order, OrderItem, OrderStatus, Product, User, UserRole
from app.application.ports import OrderRepository, ProductRepository, UserRepository
from app.infrastructure.db import OrderItemModel, OrderModel, ProductModel, UserModel


class SqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self.session.get(UserModel, user_id)
        if model is None:
            return None
        return self._to_domain(model)
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)
    
    async def save(self, user: User) -> None:
        model = await self.session.get(UserModel, user.id)
        
        if model is None:
            model = UserModel(
                id=user.id,
                email=user.email,
                hashed_password=user.hashed_password,
                role=user.role.value,
                created_at=user.created_at,
                is_active=user.is_active,
            )
            self.session.add(model)
        else:
            model.email = user.email
            model.hashed_password = user.hashed_password
            model.role = user.role.value
            model.is_active = user.is_active
    
    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            created_at=model.created_at,
            is_active=model.is_active,
        )

class SqlProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, product_id: UUID) -> Product | None:
        model = await self.session.get(ProductModel, product_id)
        if model is None:
            return None
        return self._to_domain(model)
    
    async def save(self, product: Product) -> None:
        model = await self.session.get(ProductModel, product.id)
        
        if model is None:
            model = ProductModel(
                id=product.id,
                name=product.name,
                price=product.price,
                stock=product.stock,
                is_active=product.is_active,
            )
            self.session.add(model)
        else:
            model.name = product.name
            model.price = product.price
            model.stock = product.stock
            model.is_active = product.is_active
    
    @staticmethod
    def _to_domain(model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            price=model.price,
            stock=model.stock,
            is_active=model.is_active,
        )

class SqlOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items))
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)
    
    async def save(self, order: Order) -> None:
        model = await self.session.get(OrderModel, order.id)
        
        if model is None:
            model = OrderModel(
                id=order.id,
                user_id=order.user_id,
                status=order.status.value,
                created_at=order.created_at,
                total_amount=order.total_amount,
            )
            self.session.add(model)
            
            for item in order.items:
                item_model = OrderItemModel(
                    id=uuid.uuid4(),
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                )
                self.session.add(item_model)
        else:
            model.status = order.status.value
            model.total_amount = order.total_amount
                
    @staticmethod
    def _to_domain(model: OrderModel) -> Order:
        items = [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in model.items
        ]
        
        return Order(
            id=model.id,
            user_id=model.user_id,
            items=items,
            status=OrderStatus(model.status),
            created_at=model.created_at,
            total_amount=model.total_amount,
        )