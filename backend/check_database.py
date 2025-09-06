#!/usr/bin/env python3
"""
Script to check what's currently in the database.
"""

import asyncio
import asyncpg
from app.config import settings


async def check_database():
    """Check what's currently in the database."""
    try:
        # Parse the database URL
        db_url = settings.database_url
        # Convert SQLAlchemy URL to asyncpg format
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        elif db_url.startswith('postgresql://'):
            pass  # Already correct format
        else:
            raise ValueError(f"Unsupported database URL format: {db_url}")
            
        print(f"Connecting to database...")
        
        # Connect to the database
        conn = await asyncpg.connect(db_url)
        
        # Check what tables exist
        print("\n📋 Existing tables:")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Check what indexes exist
        print("\n🔍 Existing indexes:")
        indexes = await conn.fetch("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            ORDER BY indexname
        """)
        for index in indexes:
            print(f"  - {index['indexname']}")
        
        # Check what extensions are enabled
        print("\n🔧 Enabled extensions:")
        extensions = await conn.fetch("""
            SELECT extname 
            FROM pg_extension 
            ORDER BY extname
        """)
        for ext in extensions:
            print(f"  - {ext['extname']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")


if __name__ == "__main__":
    asyncio.run(check_database())
