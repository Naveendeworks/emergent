import pytest
from datetime import datetime, timedelta
import pytz
from models.order import (
    Order, OrderItem, OrderCreate, OrderItemCreate,
    OrderStats, PaymentReport, ItemReport, EASTERN_TZ
)
from services.order_service import OrderService

# Test data
test_order_item = {
    "name": "Dosa",
    "quantity": 2,
    "price": 10.99,
    "subtotal": 21.98,
    "cooking_status": "not started"
}

test_order = {
    "orderNumber": "1",
    "customerName": "Test Customer",
    "items": [test_order_item],
    "paymentMethod": "cash",
    "status": "pending",
    "orderTime": datetime.now(EASTERN_TZ),
    "deliveryMinutes": 30,
    "totalItems": 2,
    "totalAmount": 21.98
}

@pytest.fixture
async def order_service(pool):
    """Create order service with test database pool"""
    service = OrderService(pool)
    return service

@pytest.mark.asyncio
async def test_create_order():
    """Test creating an order"""
    # Test OrderItemCreate validation
    item_create = OrderItemCreate(
        name="Dosa",
        quantity=2
    )
    assert item_create.name == "Dosa"
    assert item_create.quantity == 2

    # Test OrderCreate validation
    order_create = OrderCreate(
        customerName="Test Customer",
        items=[item_create],
        paymentMethod="cash"
    )
    assert order_create.customerName == "Test Customer"
    assert len(order_create.items) == 1
    assert order_create.paymentMethod == "cash"

    # Test Order model
    order = Order(**test_order)
    assert order.customerName == "Test Customer"
    assert order.status == "pending"
    assert order.totalItems == 2  # Validated by calculate_total_items
    assert order.estimatedDeliveryTime is not None  # Validated by calculate_estimated_delivery

@pytest.mark.asyncio
async def test_order_validators():
    """Test Order model validators"""
    order = Order(**test_order)
    
    # Test total items calculation
    assert order.totalItems == sum(item.quantity for item in order.items)
    
    # Test estimated delivery calculation
    expected_delivery = order.orderTime + timedelta(minutes=order.deliveryMinutes)
    assert order.estimatedDeliveryTime == expected_delivery

@pytest.mark.asyncio
async def test_database_operations(order_service):
    """Test order database operations"""
    # Create order
    order_create = OrderCreate(
        customerName="Test Customer",
        items=[OrderItemCreate(name="Dosa", quantity=2)],
        paymentMethod="cash"
    )
    order = await order_service.create_order(order_create)
    assert order is not None
    assert order.id is not None
    assert order.status == "pending"

    # Get order by ID
    retrieved_order = await order_service.get_order_by_id(order.id)
    assert retrieved_order is not None
    assert retrieved_order.id == order.id
    assert retrieved_order.customerName == "Test Customer"

    # Get all orders
    orders = await order_service.get_all_orders()
    assert len(orders) > 0
    assert any(o.id == order.id for o in orders)

    # Update order status
    updated_order = await order_service.update_order(order.id, {"status": "completed"})
    assert updated_order is not None
    assert updated_order.status == "completed"

    # Get orders by status
    completed_orders = await order_service.get_orders_by_status("completed")
    assert len(completed_orders) > 0
    assert any(o.id == order.id for o in completed_orders)

@pytest.mark.asyncio
async def test_order_statistics(order_service):
    """Test order statistics and reports"""
    # Create test orders with different statuses and payment methods
    for i in range(3):
        order_create = OrderCreate(
            customerName=f"Customer {i}",
            items=[OrderItemCreate(name="Dosa", quantity=2)],
            paymentMethod="cash" if i % 2 == 0 else "zelle"
        )
        await order_service.create_order(order_create)

    # Test order stats
    stats = await order_service.get_order_stats()
    assert stats.total >= 3
    assert stats.pending > 0
    assert isinstance(stats.averageDeliveryTime, (float, type(None)))

    # Complete one order
    orders = await order_service.get_all_orders()
    test_order = orders[0]
    await order_service.complete_order(test_order.id)

    # Re-check stats
    new_stats = await order_service.get_order_stats()
    assert new_stats.completed > 0
    assert new_stats.pending < stats.pending

@pytest.mark.asyncio
async def test_invalid_orders():
    """Test order validation errors"""
    # Test invalid quantity
    with pytest.raises(ValueError):
        OrderItemCreate(name="Dosa", quantity=0)

    # Test invalid payment method
    with pytest.raises(ValueError):
        OrderCreate(
            customerName="Test",
            items=[OrderItemCreate(name="Dosa", quantity=1)],
            paymentMethod="invalid"
        )

    # Test empty items list
    with pytest.raises(ValueError):
        OrderCreate(
            customerName="Test",
            items=[],
            paymentMethod="cash"
        )
