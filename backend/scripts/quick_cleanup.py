#!/usr/bin/env python3
"""
Quick database cleanup script for common testing scenarios.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def quick_cleanup():
    """Quick cleanup of test data."""
    print("🧹 Quick database cleanup...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Clean test publications and all related data
            test_ids = [
                '6048b37e-2062-4bc6-a4d9-66d472f3cc2d', 'c7948b44-cc3a-4496-bd1d-6e30b4df8e9e'
            ]
            
            for pub_id in test_ids:
                # Delete all related data in one go
                await db.execute(text("""
                    WITH deleted_auctions AS (
                        DELETE FROM auctions WHERE publication_id = :pub_id RETURNING id
                    ),
                    deleted_auction_objects AS (
                        DELETE FROM auction_objects WHERE auction_id IN (SELECT id FROM deleted_auctions)
                    ),
                    deleted_contacts AS (
                        DELETE FROM contacts WHERE publication_id = :pub_id
                    ),
                    deleted_debtors AS (
                        DELETE FROM debtors WHERE publication_id = :pub_id
                    ),
                    deleted_publications AS (
                        DELETE FROM publications WHERE id = :pub_id
                    )
                    SELECT 1
                """), {"pub_id": pub_id})
            
            await db.commit()
            print("✅ Test data cleaned successfully!")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            await db.rollback()


async def show_stats():
    """Show database statistics."""
    async with AsyncSessionLocal() as db:
        tables = ['publications', 'auctions', 'auction_objects', 'debtors', 'contacts']
        
        print("📊 Database Statistics:")
        for table in tables:
            count = await db.scalar(text(f"SELECT COUNT(*) FROM {table}"))
            print(f"  {table}: {count} records")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        asyncio.run(show_stats())
    else:
        asyncio.run(quick_cleanup())
