from typing import List
import logging
from models.menu import MenuItem, MenuResponse
from asyncpg import Pool

logger = logging.getLogger(__name__)

class MenuService:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MenuService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            self.initialized = True
    
    @classmethod
    def set_pool(cls, pool: Pool):
        """Set the database pool for all instances"""
        cls._pool = pool
    
    @property
    def pool(self) -> Pool:
        """Get the database pool"""
        if self._pool is None:
            raise RuntimeError("Database pool not set. Call MenuService.set_pool() first.")
        return self._pool
        
    async def initialize_menu_items(self):
        """Initialize menu items in the database if they don't exist"""
        try:
            # Create menu_items table if it doesn't exist
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS menu_items (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        chef TEXT,
                        sous_chef TEXT,
                        category TEXT NOT NULL,
                        price DECIMAL(10,2) NOT NULL,
                        available BOOLEAN DEFAULT true
                    )
                """)
                
                # Default menu items
                default_items = [
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
                
                # Insert items if they don't exist
                for item in default_items:
                    await conn.execute("""
                        INSERT INTO menu_items (id, name, chef, sous_chef, category, price, available)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (id) DO NOTHING
                    """, 
                    item.id,
                    item.name,
                    item.chef,
                    item.sousChef,
                    item.category,
                    item.price,
                    True
                    )
                
                logger.info("Menu items initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing menu items: {str(e)}")
            raise e
    
    async def get_menu(self) -> MenuResponse:
        """Get the complete menu with categories"""
        try:
            async with self.pool.acquire() as conn:
                # Get all menu items
                rows = await conn.fetch("""
                    SELECT * FROM menu_items 
                    WHERE available = true 
                    ORDER BY category, name
                """)
                
                # Get unique categories
                categories = await conn.fetch("""
                    SELECT DISTINCT category 
                    FROM menu_items 
                    WHERE available = true 
                    ORDER BY category
                """)
                
                menu_items = [MenuItem(**dict(row)) for row in rows]
                category_list = [row['category'] for row in categories]
                
                return MenuResponse(
                    items=menu_items,
                    categories=category_list
                )
        except Exception as e:
            logger.error(f"Error getting menu: {str(e)}")
            return MenuResponse(items=[], categories=[])
    
    async def get_menu_item(self, item_id: str) -> MenuItem:
        """Get a specific menu item by ID"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM menu_items 
                    WHERE id = $1 AND available = true
                """, item_id)
                
                if row:
                    return MenuItem(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error getting menu item: {str(e)}")
            return None
    
    async def get_items_by_category(self, category: str) -> List[MenuItem]:
        """Get menu items by category"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM menu_items 
                    WHERE category = $1 AND available = true 
                    ORDER BY name
                """, category)
                
                return [MenuItem(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting items by category: {str(e)}")
            return []
    
    async def search_menu_items(self, query: str) -> List[MenuItem]:
        """Search menu items by name"""
        try:
            query_lower = query.lower()
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM menu_items 
                    WHERE lower(name) LIKE $1 AND available = true 
                    ORDER BY category, name
                """, f"%{query_lower}%")
                
                return [MenuItem(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error searching menu items: {str(e)}")
            return []