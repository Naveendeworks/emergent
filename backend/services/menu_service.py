from typing import List
from models.menu import MenuItem, MenuResponse

class MenuService:
    def __init__(self):
        # Static menu items based on the provided menu table (excluding removed items)
        self.menu_items = [
            MenuItem(id="dosa", name="Dosa", chef="Sunoj", sousChef="Rakesh", category="South Indian"),
            MenuItem(id="chicken_biryani", name="Chicken Biryani", chef="Nachu", sousChef="Sreedhar", category="Biryani"),
            MenuItem(id="goat_biryani", name="Goat Biryani", chef="Mario", sousChef="Rakesh", category="Biryani"),
            MenuItem(id="goat_curry", name="Goat Curry", chef="Mario", category="Curry"),
            MenuItem(id="fish_pulusu", name="Fish Pulusu", chef="Sunoj", category="Fish"),
            MenuItem(id="chicken_65", name="Chicken 65", chef="Sunoj", sousChef="Jnet", category="Starters"),
            MenuItem(id="idly", name="Idly", chef="Jose", sousChef="Ranjitha Mom", category="South Indian"),
            MenuItem(id="coffee", name="Coffee", chef="Ravi Mom", category="Beverages"),
            MenuItem(id="chaat_items", name="Chaat Items", chef="Bhavana", sousChef="Abhiram", category="Chaat"),
            MenuItem(id="bajji", name="Bajji", chef="Gupta", sousChef="Akula", category="Snacks"),
            MenuItem(id="punugulu", name="Punugulu", chef="Akula", sousChef="Bhavana(Batter)", category="Snacks"),
            MenuItem(id="nellore_kaaram", name="Nellore Kaaram", chef="Mridula", sousChef="Sravani", category="Spicy"),
            MenuItem(id="paya_soup", name="Paya Soup", chef="Sreedhar", sousChef="Jnet", category="Soup"),
            MenuItem(id="keema", name="Keema", chef="Sreedhar", sousChef="Jnet", category="Meat"),
            MenuItem(id="tea", name="Tea", chef="Dera", category="Beverages"),
            MenuItem(id="aloo_masala", name="Aloo Masala", chef="Anusha Allu", category="Vegetarian"),
            MenuItem(id="fruits_cutting", name="Fruits Cutting", chef="", category="Dessert")
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