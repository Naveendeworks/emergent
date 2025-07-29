from typing import List
from models.menu import MenuItem, MenuResponse

class MenuService:
    def __init__(self):
        # Static menu items with prices based on the provided pricing list
        self.menu_items = [
            MenuItem(id="dosa", name="Dosa", chef="Sunoj", sousChef="Rakesh", category="South Indian", price=10.99),
            MenuItem(id="chicken_biryani", name="Chicken Biryani", chef="Nachu", sousChef="Sreedhar", category="Biryani", price=12.99),
            MenuItem(id="goat_biryani", name="Goat Biryani", chef="Mario", sousChef="Rakesh", category="Biryani", price=12.99),
            MenuItem(id="goat_curry", name="Goat Curry", chef="Mario", category="Curry", price=14.99),
            MenuItem(id="fish_pulusu", name="Fish Pulusu", chef="Sunoj", category="Fish", price=12.99),
            MenuItem(id="chicken_65", name="Chicken 65", chef="Sunoj", sousChef="Jnet", category="Starters", price=9.99),
            MenuItem(id="idly", name="Idly", chef="Jose", sousChef="Ranjitha Mom", category="South Indian", price=9.99),
            MenuItem(id="coffee", name="Coffee", chef="Ravi Mom", category="Beverages", price=3.00),
            MenuItem(id="chaat_items", name="Chaat Items", chef="Bhavana", sousChef="Abhiram", category="Chaat", price=5.99),
            MenuItem(id="bajji", name="Bajji", chef="Gupta", sousChef="Akula", category="Snacks", price=6.99),
            MenuItem(id="punugulu", name="Punugulu", chef="Akula", sousChef="Bhavana(Batter)", category="Snacks", price=5.99),
            MenuItem(id="nellore_kaaram", name="Nellore Kaaram", chef="Mridula", sousChef="Sravani", category="Spicy", price=10.99),
            MenuItem(id="paya_soup", name="Paya Soup", chef="Sreedhar", sousChef="Jnet", category="Soup", price=8.99),
            MenuItem(id="keema", name="Keema", chef="Sreedhar", sousChef="Jnet", category="Meat", price=15.99),
            MenuItem(id="tea", name="Tea", chef="Dera", category="Beverages", price=2.00),
            MenuItem(id="aloo_masala", name="Aloo Masala", chef="Anusha Allu", category="Vegetarian", price=6.99),
            MenuItem(id="fruits_cutting", name="Fruits Cutting", chef="Kitchen Staff", category="Dessert", price=5.99)
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