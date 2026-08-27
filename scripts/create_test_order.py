# scripts/create_test_order.py
import asyncio
import time
import uuid
import httpx


async def main():
    email = f"test{int(time.time())}@example.com"
    idempotency_key = str(uuid.uuid4())  # уникальный ключ
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Регистрируем пользователя
        user_response = await client.post(
            "/register",
            json={"email": email, "password": "secret123"},
        )
        user_data = user_response.json()
        user_id = user_data["id"]
        print(f"✅ User: {user_id}")
        
        # 2. Логинимся
        login_response = await client.post(
            "/login",
            json={"email": email, "password": "secret123"},
        )
        token = login_response.json()["access_token"]
        print(f"✅ Token: {token[:30]}...")
        
        # 3. Создаём товар
        product_response = await client.post(
            "/products",
            json={"name": "iPhone", "price": 999.0, "stock": 10},
        )
        product_id = product_response.json()["id"]
        print(f"✅ Product: {product_id}")
        
        # 4. Создаём заказ (первый раз)
        order_response = await client.post(
            "/orders",
            json={
                "user_id": user_id,
                "items": [{"product_id": product_id, "quantity": 1}],
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": idempotency_key,
            },
        )
        order_data = order_response.json()
        print(f"✅ Order 1: {order_data['id']}")
        
        # 5. Повторяем тот же запрос (с тем же ключом)
        order_response2 = await client.post(
            "/orders",
            json={
                "user_id": user_id,
                "items": [{"product_id": product_id, "quantity": 1}],
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": idempotency_key,  # тот же ключ
            },
        )
        order_data2 = order_response2.json()
        print(f"✅ Order 2: {order_data2['id']}")
        print(f"   Это тот же заказ? {order_data['id'] == order_data2['id']}")


if __name__ == "__main__":
    asyncio.run(main())