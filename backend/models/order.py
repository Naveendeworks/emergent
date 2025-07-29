from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import uuid
import pytz
import random
import string

# Eastern Time timezone
EASTERN_TZ = pytz.timezone('US/Eastern')

def generate_order_number() -> str:
    """Generate a unique order number like ORD-ABC123"""
    # Generate 3 random uppercase letters + 3 random numbers
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=3))
    return f"ORD-{letters}{numbers}"

class OrderItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=100)
    price: float = Field(..., gt=0, description="Price per item in USD")
    subtotal: float = Field(..., gt=0, description="Total for this item (price * quantity)")
    cooking_status: str = Field(default="not started", pattern='^(not started|cooking|finished)$')

class OrderItemCreate(BaseModel):
    """Simplified order item for frontend - backend will calculate prices"""
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=100)

class OrderCreate(BaseModel):
    customerName: str = Field(..., min_length=1, max_length=100)
    items: List[OrderItemCreate] = Field(..., min_items=1)
    paymentMethod: str = Field(..., pattern='^(zelle|cashapp|cash)$')
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

class OrderItemCookingUpdate(BaseModel):
    """Model for updating cooking status of an order item"""
    order_id: str = Field(..., min_length=1)
    item_name: str = Field(..., min_length=1, max_length=100)
    cooking_status: str = Field(..., pattern='^(not started|cooking|finished)$')

class ItemOrderSummary(BaseModel):
    """Summary of orders for a specific menu item"""
    item_name: str
    total_quantity: int
    orders: List[dict]  # List of orders containing this item

class CookingStatusSummary(BaseModel):
    """Summary of cooking status across all orders"""
    not_started: int = 0
    cooking: int = 0
    finished: int = 0

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    orderNumber: str
    customerName: str
    items: List[OrderItem]
    paymentMethod: str = Field(default='cash', pattern='^(zelle|cashapp|cash)$')
    status: str = Field(default='pending', pattern='^(pending|completed)$')
    orderTime: datetime = Field(default_factory=lambda: datetime.now(EASTERN_TZ))
    completedTime: Optional[datetime] = None
    estimatedDeliveryTime: Optional[datetime] = None
    actualDeliveryTime: Optional[datetime] = None
    deliveryMinutes: Optional[int] = Field(default=30)  # Default 30 min delivery
    totalItems: int = Field(default=0)
    totalAmount: float = Field(default=0.0, description="Total order amount in USD")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('totalItems', always=True)
    def calculate_total_items(cls, v, values):
        if 'items' in values:
            return sum(item.quantity for item in values['items'])
        return v

    @validator('estimatedDeliveryTime', always=True)
    def calculate_estimated_delivery(cls, v, values):
        if 'orderTime' in values and 'deliveryMinutes' in values:
            order_time = values['orderTime']
            if isinstance(order_time, str):
                order_time = datetime.fromisoformat(order_time.replace('Z', '+00:00'))
            
            # Ensure order_time is timezone aware
            if order_time.tzinfo is None:
                order_time = EASTERN_TZ.localize(order_time)
            
            delivery_minutes = values.get('deliveryMinutes', 30)
            return order_time + timedelta(minutes=delivery_minutes)
        return v

class OrderStats(BaseModel):
    pending: int = 0
    completed: int = 0
    total: int = 0
    averageDeliveryTime: Optional[float] = None  # in minutes

class PaymentReport(BaseModel):
    paymentMethod: str
    orderCount: int
    totalItems: int
    pendingOrders: int
    completedOrders: int
    averageDeliveryTime: Optional[float] = None

class ItemReport(BaseModel):
    itemName: str
    totalOrdered: int
    orderCount: int
    averageQuantityPerOrder: float
    popularPaymentMethod: str
    recentOrders: List[str]  # Customer names