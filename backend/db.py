import os
import asyncpg
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Global connection pool
_pool = None

async def get_pg_pool():
    global _pool
    
    if _pool is None:
        try:
            # Construct connection URL with proper SSL mode for Supabase
            connection_url = DATABASE_URL
            if "?sslmode=" not in connection_url:
                connection_url += "?sslmode=require"
            
            logger.info("Creating new database connection pool")
            _pool = await asyncpg.create_pool(
                connection_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={'timezone': 'UTC'}
            )
        except Exception as e:
            logger.error(f"Failed to create connection pool: {str(e)}")
            raise
    
    return _pool

async def close_pg_pool():
    global _pool
    if _pool:
        logger.info("Closing database connection pool")
        await _pool.close()
        _pool = None
