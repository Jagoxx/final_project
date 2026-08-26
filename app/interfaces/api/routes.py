from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import CreateOrder
from app.domain import User, Product
from app.infrastructure.db import SqlProductRepository, SqlUserRepository, SqlOrderRepository
from app.interfaces.api.dependencies import get_create_order_use_case, get_session
from app.interfaces.api.schemas import (
    CreateOrderRequest,
    OrderResponse,
    ProductCreateRequest,
    ProductResponse,
    UserCreateRequest,
    UserResponse,
)

router = APIRouter()

# USERS

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreateRequest, session: AsyncSession = Depends(get_session)):
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

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreateRequest,
    session: AsyncSession = Depends(get_session),
):
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
async def get_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session),
):
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


# ORDERS 

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    use_case: CreateOrder = Depends(get_create_order_use_case),
):
    try:
        order = await use_case.execute(
            user_id=request.user_id,
            items=[item.model_dump() for item in request.items],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status.value,
        created_at=order.created_at,
        total_amount=order.total_amount,
        items=[{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in order.items],
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
):
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
