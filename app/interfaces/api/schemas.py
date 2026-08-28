from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime
    is_active: bool


class ProductCreateRequest(BaseModel):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):
    id: UUID
    name: str
    price: float
    stock: int
    is_active: bool


class OrderItemRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class CreateOrderRequest(BaseModel):
    user_id: UUID
    items: list[OrderItemRequest]


class OrderItemResponse(BaseModel):
    product_id: UUID
    quantity: int
    price: float


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    total_amount: float
    items: list[OrderItemResponse]