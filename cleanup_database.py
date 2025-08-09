#!/usr/bin/env python3
"""
Database Cleanup Script for Mem Famous Stall 2025
Clears all order data while preserving admin credentials and menu items
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def cleanup_database():
    """Clean up database - remove all order data, reset counters"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        logger.info(f"Connecting to MongoDB at {mongo_url}")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # List all collections to see what we're working with
        collections = await db.list_collection_names()
        logger.info(f"Found collections: {collections}")
        
        # Clean up orders collection
        if 'orders' in collections:
            orders_count = await db.orders.count_documents({})
            logger.info(f"Found {orders_count} orders to delete")
            
            if orders_count > 0:
                result = await db.orders.delete_many({})
                logger.info(f"Deleted {result.deleted_count} orders")
            else:
                logger.info("No orders to delete")
        else:
            logger.info("Orders collection not found")
        
        # Reset counters collection
        if 'counters' in collections:
            counters_count = await db.counters.count_documents({})
            logger.info(f"Found {counters_count} counter documents")
            
            if counters_count > 0:
                result = await db.counters.delete_many({})
                logger.info(f"Deleted {result.deleted_count} counter documents")
            else:
                logger.info("No counter documents to delete")
        else:
            logger.info("Counters collection not found")
        
        # Clean up notifications collection if it exists
        if 'notifications' in collections:
            notifications_count = await db.notifications.count_documents({})
            logger.info(f"Found {notifications_count} notifications to delete")
            
            if notifications_count > 0:
                result = await db.notifications.delete_many({})
                logger.info(f"Deleted {result.deleted_count} notifications")
            else:
                logger.info("No notifications to delete")
        else:
            logger.info("Notifications collection not found")
        
        # Verify cleanup
        logger.info("\n=== VERIFICATION ===")
        final_orders_count = await db.orders.count_documents({})
        final_counters_count = await db.counters.count_documents({})
        final_notifications_count = await db.notifications.count_documents({}) if 'notifications' in collections else 0
        
        logger.info(f"Orders remaining: {final_orders_count}")
        logger.info(f"Counters remaining: {final_counters_count}")
        logger.info(f"Notifications remaining: {final_notifications_count}")
        
        if final_orders_count == 0 and final_counters_count == 0 and final_notifications_count == 0:
            logger.info("✅ Database cleanup completed successfully!")
            logger.info("✅ Admin credentials preserved (hardcoded)")
            logger.info("✅ Menu items preserved (hardcoded)")
        else:
            logger.warning("⚠️  Some data may still remain in the database")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"Error during database cleanup: {str(e)}")
        raise e

async def main():
    """Main function"""
    logger.info("Starting database cleanup for Mem Famous Stall 2025...")
    
    try:
        await cleanup_database()
        logger.info("Database cleanup completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)