from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.order import PaymentReport, ItemReport
from services.order_service import OrderService
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

router = APIRouter(prefix="/reports", tags=["reports"])

def get_order_service() -> OrderService:
    return OrderService(db)

@router.get("/payment", response_model=List[PaymentReport])
async def get_payment_reports(
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Get payment method reports (requires authentication)"""
    try:
        reports = await order_service.get_payment_reports()
        return reports
    except Exception as e:
        logger.error(f"Error in get_payment_reports endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment reports")

@router.get("/items", response_model=List[ItemReport])
async def get_item_reports(
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Get item-based reports (requires authentication)"""
    try:
        reports = await order_service.get_item_reports()
        return reports
    except Exception as e:
        logger.error(f"Error in get_item_reports endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch item reports")