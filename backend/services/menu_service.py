from typing import List
from models.menu import MenuItem, MenuResponse

class MenuService:
    def __init__(self):
        # Updated menu items based on station list with correct categories and prices
        self.menu_items = [
            # Soup Station
            MenuItem(id="paya", name="Paya", category="Soup", price=10.00),
            
            # Non-veg Appetizer Station
            MenuItem(id="chicken_65_boneless", name="Chicken 65 (Boneless)", category="Non-veg Appetizer", price=10.00),
            
            # South Indian Delicacies Station
            MenuItem(id="idly_3", name="Idly (3)", category="South Indian Delicacies", price=7.00),
            MenuItem(id="guntur_ghee_podi_idly", name="Guntur Ghee Podi Idly", category="South Indian Delicacies", price=8.00),
            MenuItem(id="idly_natukodi_curry", name="Idly with Natukodi curry", category="South Indian Delicacies", price=10.00),
            MenuItem(id="idly_mutton_curry", name="Idly with Mutton curry", category="South Indian Delicacies", price=10.00),
            MenuItem(id="ragi_sangati_natukodi_curry", name="Ragi Sangati with Natukodi curry", category="South Indian Delicacies", price=10.00),
            MenuItem(id="ragi_sangati_mutton_curry", name="Ragi Sangati with Mutton curry", category="South Indian Delicacies", price=10.00),
            
            # Dosas Station
            MenuItem(id="keema_dosa", name="Keema Dosa", category="Dosas", price=15.00),
            MenuItem(id="mutton_curry_dosa", name="Mutton curry Dosa", category="Dosas", price=16.00),
            MenuItem(id="pesarattu_upma_dosa", name="Pesarattu Upma Dosa", category="Dosas", price=12.00),
            MenuItem(id="nellore_kaaram_dosa", name="Nellore Kaaram Dosa", category="Dosas", price=12.00),
            MenuItem(id="ghee_massala_dosa", name="Ghee Massala Dosa", category="Dosas", price=12.00),
            MenuItem(id="ghee_roast", name="Ghee Roast", category="Dosas", price=10.00),
            MenuItem(id="plain_roast", name="Plain Roast", category="Dosas", price=10.00),
            MenuItem(id="chocolate_dosa", name="Chocolate Dosa", category="Dosas", price=8.00),
            
            # Biryani's Station
            MenuItem(id="thalapakatti_goat_biryani", name="Thalapakatti Goat Biryani", category="Biryani's", price=15.00),
            MenuItem(id="hyderabad_chicken_dum_biryani", name="Hyderabad Chicken Dum Biryani", category="Biryani's", price=12.00),
            
            # Snacks Station
            MenuItem(id="punugulu", name="Punugulu", category="Snacks", price=8.00),
            MenuItem(id="mirchi_bajji", name="Mirchi Bajji", category="Snacks", price=8.00),
            MenuItem(id="veg_puff", name="Veg Puff", category="Snacks", price=3.00),
            MenuItem(id="egg_puff", name="Egg Puff", category="Snacks", price=4.00),
            MenuItem(id="chicken_puff", name="Chicken Puff", category="Snacks", price=5.00),
            MenuItem(id="veg_samosa_2", name="Veg Samosa (2)", category="Snacks", price=5.00),
            
            # Chaat Station
            MenuItem(id="pani_puri", name="Pani Puri", category="Chaat", price=6.00),
            MenuItem(id="bhel_puri", name="Bhel Puri", category="Chaat", price=7.00),
            MenuItem(id="dahi_puri", name="Dahi Puri", category="Chaat", price=7.00),
            MenuItem(id="sev_puri", name="Sev Puri", category="Chaat", price=7.00),
            MenuItem(id="batani_chaat", name="Batani Chaat", category="Chaat", price=7.00),
            
            # Hot Beverages Station
            MenuItem(id="arakku_filter_coffee", name="Arakku Filter Coffee", category="Hot Beverages", price=3.00),
            MenuItem(id="masala_chai", name="Masala Chai", category="Hot Beverages", price=1.00),
            
            # Fresh Fruit Juices Station
            MenuItem(id="abc_detox_juice", name="ABC Detox Juice", category="Fresh Fruit Juices", price=8.00),
            MenuItem(id="orange_juice", name="Orange Juice", category="Fresh Fruit Juices", price=6.00),
            MenuItem(id="watermelon_juice", name="Watermelon Juice", category="Fresh Fruit Juices", price=6.00),
            MenuItem(id="strawberry_banana_shake", name="Strawberry Banana Shake", category="Fresh Fruit Juices", price=8.00),
            
            # Cold Beverages Station
            MenuItem(id="mango_milk_shake", name="Mango Milk Shake", category="Cold Beverages", price=6.00),
            MenuItem(id="rose_milk", name="Rose Milk", category="Cold Beverages", price=5.00),
            MenuItem(id="thumbs_up", name="Thumbs up", category="Cold Beverages", price=3.00),
            MenuItem(id="coke", name="Coke", category="Cold Beverages", price=2.00),
            MenuItem(id="water_bottle", name="Water Bottle", category="Cold Beverages", price=1.00),
        ]
    
    async def get_menu(self) -> MenuResponse:
        """Get the complete menu with categories"""
        categories = list(set([item.category for item in self.menu_items]))
        categories.sort()
        
        return MenuResponse(
            items=[item for item in self.menu_items if item.available],
            categories=categories
        )
    
    async def get_menu_item(self, item_id: str) -> MenuItem:
        """Get a specific menu item by ID"""
        for item in self.menu_items:
            if item.id == item_id:
                return item
        return None
    
    async def get_items_by_category(self, category: str) -> List[MenuItem]:
        """Get menu items by category"""
        return [item for item in self.menu_items if item.category == category and item.available]
    
    async def search_menu_items(self, query: str) -> List[MenuItem]:
        """Search menu items by name"""
        query_lower = query.lower()
        return [
            item for item in self.menu_items 
            if query_lower in item.name.lower() and item.available
        ]