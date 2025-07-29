from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import uuid

class OrderItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=100)

class OrderCreate(BaseModel):
    customerName: str = Field(..., min_length=1, max_length=100)
    items: List[OrderItem] = Field(..., min_items=1)
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern='^(pending|completed)$')

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customerName: str
    items: List[OrderItem]
    status: str = Field(default='pending', regex='^(pending|completed)$')
    orderTime: datetime = Field(default_factory=datetime.utcnow)
    totalItems: int = Field(default=0)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('totalItems', always=True)
    def calculate_total_items(cls, v, values):
        if 'items' in values:
            return sum(item.quantity for item in values['items'])
        return v

class OrderStats(BaseModel):
    pending: int = 0
    completed: int = 0
    total: int = 0