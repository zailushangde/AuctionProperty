#!/usr/bin/env python3
"""
Script to enable PostGIS extension in Supabase database.
Run this before running Alembic migrations.
"""

import asyncio
import asyncpg
from app.config import settings


async def enable_postgis():
    """Enable PostGIS extension in the database."""
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
        
        # Enable PostGIS extension
        print("Enabling PostGIS extension...")
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "postgis"')
        
        # Check if PostGIS is enabled
        result = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')"
        )
        
        if result:
            print("✅ PostGIS extension enabled successfully!")
        else:
            print("❌ Failed to enable PostGIS extension")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error enabling PostGIS: {e}")
        print("\n💡 Manual steps:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to Database > Extensions")
        print("3. Enable the 'postgis' extension")
        print("4. Then run: alembic upgrade head")


if __name__ == "__main__":
    asyncio.run(enable_postgis())
