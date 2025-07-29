from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.notification import Notification, NotificationCreate, NotificationUpdate
from services.notification_service import NotificationService
from routers.auth import get_current_user
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter(prefix="/notifications", tags=["notifications"])

def get_notification_service() -> NotificationService:
    return NotificationService(db)

@router.post("/", response_model=Notification, status_code=201)
async def create_notification(
    notification_data: NotificationCreate,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: str = Depends(get_current_user)
):
    """Create a new notification (requires authentication)"""
    try:
        notification = await notification_service.create_notification(notification_data)
        return notification
    except Exception as e:
        logger.error(f"Error in create_notification endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create notification")

@router.get("/active", response_model=List[Notification])
async def get_active_notifications(
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get active notifications for display (public endpoint)"""
    try:
        notifications = await notification_service.get_active_notifications()
        return notifications
    except Exception as e:
        logger.error(f"Error in get_active_notifications endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch active notifications")

@router.get("/", response_model=List[Notification])
async def get_all_notifications(
    limit: int = 100,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: str = Depends(get_current_user)
):
    """Get all notifications (requires authentication)"""
    try:
        notifications = await notification_service.get_all_notifications(limit)
        return notifications
    except Exception as e:
        logger.error(f"Error in get_all_notifications endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch notifications")

@router.put("/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: str = Depends(get_current_user)
):
    """Update notification (requires authentication)"""
    try:
        notification = await notification_service.update_notification(notification_id, update_data)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_notification endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update notification")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: str = Depends(get_current_user)
):
    """Delete notification (requires authentication)"""
    try:
        deleted = await notification_service.delete_notification(notification_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"message": "Notification deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_notification endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")

@router.post("/clear-old")
async def clear_old_notifications(
    hours_old: int = 24,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: str = Depends(get_current_user)
):
    """Clear old notifications (requires authentication)"""
    try:
        count = await notification_service.clear_old_notifications(hours_old)
        return {"message": f"Cleared {count} old notifications"}
    except Exception as e:
        logger.error(f"Error in clear_old_notifications endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear old notifications")