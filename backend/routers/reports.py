from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
from models.order import PaymentReport, ItemReport
from services.order_service import OrderService
from services.excel_service import ExcelService
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

def get_excel_service() -> ExcelService:
    return ExcelService()

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

@router.get("/payment/export")
async def export_payment_reports(
    order_service: OrderService = Depends(get_order_service),
    excel_service: ExcelService = Depends(get_excel_service),
    current_user: str = Depends(get_current_user)
):
    """Export payment method reports as Excel file (requires authentication)"""
    try:
        # Get payment reports data
        reports = await order_service.get_payment_reports()
        
        # Generate Excel file
        excel_file = excel_service.create_payment_report_excel(reports)
        filename = excel_service.get_filename("payment_methods")
        
        # Return as streaming response
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error in export_payment_reports endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export payment reports")

@router.get("/items/export")
async def export_item_reports(
    order_service: OrderService = Depends(get_order_service),
    excel_service: ExcelService = Depends(get_excel_service),
    current_user: str = Depends(get_current_user)
):
    """Export item reports as Excel file (requires authentication)"""
    try:
        # Get item reports data
        reports = await order_service.get_item_reports()
        
        # Generate Excel file
        excel_file = excel_service.create_item_report_excel(reports)
        filename = excel_service.get_filename("menu_items")
        
        # Return as streaming response
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error in export_item_reports endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export item reports")