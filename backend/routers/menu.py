from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.menu import MenuItem, MenuResponse
from services.menu_service import MenuService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/menu", tags=["menu"])

def get_menu_service() -> MenuService:
    return MenuService()

@router.get("/", response_model=MenuResponse)
async def get_menu(
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get the complete menu"""
    try:
        menu = await menu_service.get_menu()
        return menu
    except Exception as e:
        logger.error(f"Error in get_menu endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch menu")

@router.get("/item/{item_id}", response_model=MenuItem)
async def get_menu_item(
    item_id: str,
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get a specific menu item"""
    try:
        item = await menu_service.get_menu_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_menu_item endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch menu item")

@router.get("/category/{category}", response_model=List[MenuItem])
async def get_items_by_category(
    category: str,
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get menu items by category"""
    try:
        items = await menu_service.get_items_by_category(category)
        return items
    except Exception as e:
        logger.error(f"Error in get_items_by_category endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch menu items by category")

@router.get("/search/{query}", response_model=List[MenuItem])
async def search_menu_items(
    query: str,
    menu_service: MenuService = Depends(get_menu_service)
):
    """Search menu items"""
    try:
        items = await menu_service.search_menu_items(query)
        return items
    except Exception as e:
        logger.error(f"Error in search_menu_items endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search menu items")