#!/usr/bin/env python3
"""
Script to clean up partially created database tables.
Run this if a migration fails partway through.
"""

import asyncio
import asyncpg
from app.config import settings


async def cleanup_database():
    """Clean up partially created tables."""
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
        
        # List of tables to drop (in reverse dependency order)
        tables_to_drop = [
            'user_subscriptions',
            'auction_views', 
            'auction_objects',
            'contacts',
            'debtors',
            'auctions',
            'publications'
        ]
        
        print("Dropping existing tables...")
        for table in tables_to_drop:
            try:
                await conn.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                print(f"✅ Dropped table: {table}")
            except Exception as e:
                print(f"⚠️  Could not drop table {table}: {e}")
        
        # Drop any existing indexes
        indexes_to_drop = [
            'idx_auction_objects_coordinates',
            'idx_auction_objects_auction_id',
            'idx_auctions_publication_id',
            'idx_debtors_publication_id',
            'idx_contacts_publication_id',
            'idx_user_subscriptions_user_id',
            'idx_user_subscriptions_auction_id',
            'idx_auction_views_auction_id',
            'idx_auction_views_user_id'
        ]
        
        print("Dropping existing indexes...")
        for index in indexes_to_drop:
            try:
                await conn.execute(f'DROP INDEX IF EXISTS "{index}"')
                print(f"✅ Dropped index: {index}")
            except Exception as e:
                print(f"⚠️  Could not drop index {index}: {e}")
        
        print("✅ Database cleanup completed!")
        print("You can now run: alembic upgrade head")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error cleaning up database: {e}")


if __name__ == "__main__":
    asyncio.run(cleanup_database())
