from uuid import uuid4
import pytest
from app.domain import Product
from app.application import CreateOrder
from tests.in_memory_repositories import (
    InMemoryOrderRepository,
    InMemoryProductRepository,
)


@pytest.fixture
def product_repo():
    """Фикстура: репозиторий товаров."""
    return InMemoryProductRepository()


@pytest.fixture
def order_repo():
    """Фикстура: репозиторий заказов."""
    return InMemoryOrderRepository()


async def test_create_order_success(product_repo, order_repo):
    """Успешное создание заказа."""
    #создаём товар и кладём в репозиторий
    product = Product.create(name="iPhone", price=999.0, stock=10)
    await product_repo.save(product)
    
    use_case = CreateOrder(order_repo=order_repo, product_repo=product_repo)
    
    # выполняем use-case
    order = await use_case.execute(
        user_id=uuid4(),
        items=[{"product_id": product.id, "quantity": 2}],
    )
    
    assert order.total_amount == 1998.0 
    assert order.status.value == "confirmed" 
    
    # Проверяем, что stock уменьшился
    updated_product = await product_repo.get_by_id(product.id)
    assert updated_product.stock == 8


async def test_create_order_insufficient_stock(product_repo, order_repo):
    """Ошибка при нехватке товара."""
    #товар с stock=1
    product = Product.create(name="iPhone", price=999.0, stock=1)
    await product_repo.save(product)
    
    use_case = CreateOrder(order_repo=order_repo, product_repo=product_repo)
    
    #ожидаем ошибку
    with pytest.raises(ValueError):
        await use_case.execute(
            user_id=uuid4(),
            items=[{"product_id": product.id, "quantity": 5}],
        )


async def test_create_order_product_not_found(product_repo, order_repo):
    """Ошибка при несуществующем товаре."""
    use_case = CreateOrder(order_repo=order_repo, product_repo=product_repo)
    
    #товара нет в репозитории
    with pytest.raises(ValueError):
        await use_case.execute(
            user_id=uuid4(),
            items=[{"product_id": uuid4(), "quantity": 1}],
        )


async def test_create_order_empty_items(product_repo, order_repo):
    """Ошибка при пустом списке позиций."""
    use_case = CreateOrder(order_repo=order_repo, product_repo=product_repo)
    
    # пустой список
    with pytest.raises(ValueError):
        await use_case.execute(user_id=uuid4(), items=[])


async def test_create_order_multiple_items(product_repo, order_repo):
    """Создание заказа с несколькими позициями."""
    # два товара
    iphone = Product.create(name="iPhone", price=999.0, stock=10)
    case = Product.create(name="Case", price=49.0, stock=20)
    await product_repo.save(iphone)
    await product_repo.save(case)
    
    use_case = CreateOrder(order_repo=order_repo, product_repo=product_repo)
    
    order = await use_case.execute(
        user_id=uuid4(),
        items=[
            {"product_id": iphone.id, "quantity": 1},
            {"product_id": case.id, "quantity": 2},
        ],
    )
    
    assert order.total_amount == 1097.0
    assert len(order.items) == 2
    
    # Проверяем stock обоих товаров
    updated_iphone = await product_repo.get_by_id(iphone.id)
    updated_case = await product_repo.get_by_id(case.id)
    assert updated_iphone.stock == 9
    assert updated_case.stock == 18