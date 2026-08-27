import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import CreateOrder
from app.domain import Product, User
from app.infrastructure.db import IdempotencyRepository, SqlOrderRepository, SqlProductRepository, SqlUserRepository
from app.infrastructure.db.config import settings
from app.interfaces.api.dependencies import get_create_order_use_case, get_current_user, get_session
from app.interfaces.api.schemas import CreateOrderRequest, OrderResponse, ProductCreateRequest, ProductResponse, UserCreateRequest, UserResponse

router = APIRouter()


# AUTH

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    """Регистрация пользователя."""
    repo = SqlUserRepository(session)
    
    existing = await repo.get_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email занят")
    
    user = User.create(email=request.email, hashed_password=request.password)
    await repo.save(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at,
        is_active=user.is_active,
    )


@router.post("/login")
async def login(request: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    """Логин: выдаёт JWT-токен."""
    repo = SqlUserRepository(session)
    user = await repo.get_by_email(request.email)
    
    if user is None or user.hashed_password != request.password:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    token = jwt.encode(
        {
            "sub": str(user.id),
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )
    
    return {"access_token": token, "token_type": "bearer"}


# PRODUCTS

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(request: ProductCreateRequest, session: AsyncSession = Depends(get_session)):
    repo = SqlProductRepository(session)
    product = Product.create(name=request.name, price=request.price, stock=request.stock)
    await repo.save(product)
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        stock=product.stock,
        is_active=product.is_active,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = SqlProductRepository(session)
    product = await repo.get_by_id(product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        stock=product.stock,
        is_active=product.is_active,
    )


#ORDERS

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    use_case: CreateOrder = Depends(get_create_order_use_case),
    current_user: User = Depends(get_current_user),
    idempotency_key: str = Header(...),
    session: AsyncSession = Depends(get_session),
):
    # Проверяем идемпотентный ключ
    idem_repo = IdempotencyRepository(session)
    existing_order_id = await idem_repo.get_order_id(idempotency_key)
    
    if existing_order_id:
        order_repo = SqlOrderRepository(session)
        order = await order_repo.get_by_id(existing_order_id)
        if order:
            return OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status.value,
                created_at=order.created_at,
                total_amount=order.total_amount,
                items=[{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in order.items],
            )
    
    try:
        order = await use_case.execute(
            user_id=current_user.id,
            items=[item.model_dump() for item in request.items],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    await idem_repo.save(idempotency_key, order.id)
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status.value,
        created_at=order.created_at,
        total_amount=order.total_amount,
        items=[{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in order.items],
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = SqlOrderRepository(session)
    order = await repo.get_by_id(order_id)
    
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status.value,
        created_at=order.created_at,
        total_amount=order.total_amount,
        items=[{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in order.items],
    )