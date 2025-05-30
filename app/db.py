import asyncpg
import os
from typing import Optional

class DatabaseConnection:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Initialize database connection pool"""
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clothcraft")
        self.pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            await self.connect()
        return self.pool.acquire()

# Global database instance
db = DatabaseConnection()
