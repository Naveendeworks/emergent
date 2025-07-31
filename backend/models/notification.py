from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from models.order import EASTERN_TZ
import uuid

class NotificationCreate(BaseModel):
    customerName: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=500)
    orderId: Optional[str] = None

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customerName: str
    message: str
    orderId: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(EASTERN_TZ))
    isRead: bool = Field(default=False)
    isActive: bool = Field(default=True)  # For display screen
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class NotificationUpdate(BaseModel):
    isRead: Optional[bool] = None
    isActive: Optional[bool] = None