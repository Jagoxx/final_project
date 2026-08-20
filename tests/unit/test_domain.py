from uuid import uuid4
import pytest
from app.domain import User, UserRole, Product, Order, OrderItem, OrderStatus


# ТЕСТЫ USER

def test_create_user():
    user = User.create(email="John@Example.com", hashed_password="hash123")
    
    assert user.email == "john@example.com"
    assert user.hashed_password == "hash123"
    assert user.role == UserRole.BUYER  
    assert user.is_active is True


def test_deactivate_user():
    user = User.create(email="john@example.com", hashed_password="hash123")
    
    user.deactivate()
    
    assert user.is_active is False


def test_activate_user():
    """Активация пользователя."""
    user = User.create(email="john@example.com", hashed_password="hash123")
    user.deactivate()
    user.activate()
    
    assert user.is_active is True


def test_change_email():
    user = User.create(email="john@example.com", hashed_password="hash123")
    
    user.change_email("NEW@Example.com")
    
    assert user.email == "new@example.com" 


# ТЕСТЫ PRODUCT

def test_create_product():
    product = Product.create(name="iPhone", price=999.0, stock=10)
    
    assert product.name == "iPhone"
    assert product.price == 999.0
    assert product.stock == 10
    assert product.is_active is True


def test_decrease_stock():
    product = Product.create(name="iPhone", price=999.0, stock=10)
    
    product.decrease_stock(3)
    
    assert product.stock == 7


def test_decrease_stock_insufficient():
    product = Product.create(name="iPhone", price=999.0, stock=5)
    
    with pytest.raises(ValueError):
        product.decrease_stock(10)


def test_increase_stock():
    product = Product.create(name="iPhone", price=999.0, stock=5)
    
    product.increase_stock(10)
    
    assert product.stock == 15


def test_increase_stock_negative():
    product = Product.create(name="iPhone", price=999.0, stock=5)
    
    with pytest.raises(ValueError):
        product.increase_stock(-5)


# ТЕСТЫ ORDER

def _create_order_item(price: float = 100.0, quantity: int = 2) -> OrderItem:
    return OrderItem(product_id=uuid4(), quantity=quantity, price=price)


def test_create_order():
    items = [_create_order_item(price=100.0, quantity=2)]
    
    order = Order.create(user_id=uuid4(), items=items)
    
    assert order.status == OrderStatus.CONFIRMED
    assert order.total_amount == 200.0 
    assert len(order.items) == 1


def test_create_order_empty():
    with pytest.raises(ValueError):
        Order.create(user_id=uuid4(), items=[])


def test_order_pay():
    order = Order.create(user_id=uuid4(), items=[_create_order_item()])
    
    order.pay()
    
    assert order.status == OrderStatus.PAID


def test_order_cannot_pay_twice():
    order = Order.create(user_id=uuid4(), items=[_create_order_item()])
    order.pay()
    
    with pytest.raises(ValueError):
        order.pay()


def test_order_ship():
    order = Order.create(user_id=uuid4(), items=[_create_order_item()])
    order.pay()  
    
    order.ship()
    
    assert order.status == OrderStatus.SHIPPED


def test_order_cannot_ship_unpaid():
    order = Order.create(user_id=uuid4(), items=[_create_order_item()])
    
    with pytest.raises(ValueError):
        order.ship()


def test_order_deliver():
    order = Order.create(user_id=uuid4(), items=[_create_order_item()])
    order.pay()
    order.ship()
    
    order.deliver()
    
    assert order.status == OrderStatus.DELIVERED


def test_order_cancel():
    order = Order.create(user_id=uuid4(), items=[_create_order_item()])
    
    order.cancel()
    
    assert order.status == OrderStatus.CANCELLED


def test_order_cannot_cancel_shipped():
    order = Order.create(user_id=uuid4(), items=[_create_order_item()])
    order.pay()
    order.ship()
    
    with pytest.raises(ValueError):
        order.cancel()


def test_order_add_item():
    order = Order.create(user_id=uuid4(), items=[_create_order_item(price=100.0, quantity=1)])
    
    order.add_item(_create_order_item(price=50.0, quantity=1))
    
    assert order.total_amount == 150.0
    assert len(order.items) == 2