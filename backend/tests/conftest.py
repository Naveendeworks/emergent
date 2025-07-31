import pytest
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
async def pool():
    """Create a test database pool"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Create the connection pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    yield pool
    
    # Close the pool after tests
    await pool.close()
