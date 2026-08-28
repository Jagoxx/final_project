# tests/integration/test_api.py
import asyncio
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text

from app.infrastructure.db import engine
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Один event loop на всю сессию."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE order_items, orders, products, users CASCADE"))
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_create_product(client):
    response = await client.post("/products", json={"name": "iPhone", "price": 999.0, "stock": 10})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "iPhone"


async def test_get_product(client):
    create_response = await client.post("/products", json={"name": "iPhone", "price": 999.0, "stock": 10})
    product_id = create_response.json()["id"]
    get_response = await client.get(f"/products/{product_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == product_id


async def test_create_order(client):
    # Регистрируем и логинимся
    user_response = await client.post("/register", json={"email": "john@example.com", "password": "secret123"})
    user_id = user_response.json()["id"]
    login_response = await client.post("/login", json={"email": "john@example.com", "password": "secret123"})
    token = login_response.json()["access_token"]
    
    # Создаём товар
    product_response = await client.post("/products", json={"name": "iPhone", "price": 999.0, "stock": 10})
    product_id = product_response.json()["id"]
    
    # Создаём заказ с токеном
    order_response = await client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 2}]},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid4())},
    )
    assert order_response.status_code == 201
    
    product_after = await client.get(f"/products/{product_id}")
    assert product_after.json()["stock"] == 8


async def test_create_order_insufficient_stock(client):
    # Регистрируем и логинимся
    user_response = await client.post("/register", json={"email": "john@example.com", "password": "secret123"})
    user_id = user_response.json()["id"]
    login_response = await client.post("/login", json={"email": "john@example.com", "password": "secret123"})
    token = login_response.json()["access_token"]
    
    product_response = await client.post("/products", json={"name": "iPhone", "price": 999.0, "stock": 1})
    product_id = product_response.json()["id"]
    
    order_response = await client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 5}]},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid4())},
    )
    assert order_response.status_code == 400


async def test_get_order(client):
    # Регистрируем и логинимся
    user_response = await client.post("/register", json={"email": "john@example.com", "password": "secret123"})
    user_id = user_response.json()["id"]
    login_response = await client.post("/login", json={"email": "john@example.com", "password": "secret123"})
    token = login_response.json()["access_token"]
    
    product_response = await client.post("/products", json={"name": "iPhone", "price": 999.0, "stock": 10})
    product_id = product_response.json()["id"]
    
    order_response = await client.post(
        "/orders",
        json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid4())},
    )
    order_id = order_response.json()["id"]
    
    get_response = await client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == order_id