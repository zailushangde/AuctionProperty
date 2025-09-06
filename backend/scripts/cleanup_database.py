#!/usr/bin/env python3
"""
Database cleanup script to remove test data or reset the database.
"""

import asyncio
import sys
import os
from typing import List, Optional

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models import (
    Publication, Auction, AuctionObject, Debtor, Contact, 
    UserSubscription, AuctionView
)
from sqlalchemy import text, delete
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseCleanup:
    """Database cleanup utility."""
    
    def __init__(self):
        self.cleaned_tables = []
        self.errors = []
    
    async def cleanup_table(self, db: AsyncSession, table_name: str, model_class) -> bool:
        """Clean a specific table."""
        try:
            # Get count before cleanup
            count_before = await db.scalar(text(f"SELECT COUNT(*) FROM {table_name}"))
            
            # Delete all records
            await db.execute(delete(model_class))
            await db.commit()
            
            # Get count after cleanup
            count_after = await db.scalar(text(f"SELECT COUNT(*) FROM {table_name}"))
            
            self.cleaned_tables.append({
                'table': table_name,
                'count_before': count_before,
                'count_after': count_after,
                'deleted': count_before - count_after
            })
            
            print(f"✅ Cleaned {table_name}: {count_before} → {count_after} records")
            return True
            
        except Exception as e:
            self.errors.append(f"Error cleaning {table_name}: {str(e)}")
            print(f"❌ Error cleaning {table_name}: {str(e)}")
            await db.rollback()
            return False
    
    async def cleanup_all_data(self) -> bool:
        """Clean all application data (but keep system tables)."""
        print("🧹 Starting database cleanup...")
        
        async with AsyncSessionLocal() as db:
            try:
                # Clean tables in reverse dependency order
                tables_to_clean = [
                    ('auction_views', AuctionView),
                    ('user_subscriptions', UserSubscription),
                    ('contacts', Contact),
                    ('debtors', Debtor),
                    ('auction_objects', AuctionObject),
                    ('auctions', Auction),
                    ('publications', Publication),
                ]
                
                for table_name, model_class in tables_to_clean:
                    await self.cleanup_table(db, table_name, model_class)
                
                # Reset sequences (auto-increment counters)
                await self.reset_sequences(db)
                
                print("\n🎉 Database cleanup completed!")
                self.print_summary()
                
                return len(self.errors) == 0
                
            except Exception as e:
                print(f"❌ Fatal error during cleanup: {str(e)}")
                await db.rollback()
                return False
    
    async def cleanup_test_data_only(self) -> bool:
        """Clean only test data (publications with specific IDs)."""
        print("🧹 Cleaning test data only...")
        
        test_publication_ids = [
            "6048b37e-2062-4bc6-a4d9-66d472f3cc2d",
            "c7948b44-cc3a-4496-bd1d-6e30b4df8e9e",
            "c42e67af-486d-44f4-8c6e-0ad03538770d",
            "bb0b8622-803e-413e-8d71-bb6da17f5b0c"
        ]
        
        async with AsyncSessionLocal() as db:
            try:
                for pub_id in test_publication_ids:
                    # Find and delete publication and all related data
                    pub = await db.scalar(
                        text("SELECT id FROM publications WHERE id = :pub_id"),
                        {"pub_id": pub_id}
                    )
                    
                    if pub:
                        # Delete in dependency order
                        await db.execute(
                            text("DELETE FROM auction_views WHERE auction_id IN (SELECT id FROM auctions WHERE publication_id = :pub_id)"),
                            {"pub_id": pub_id}
                        )
                        await db.execute(
                            text("DELETE FROM user_subscriptions WHERE auction_id IN (SELECT id FROM auctions WHERE publication_id = :pub_id)"),
                            {"pub_id": pub_id}
                        )
                        await db.execute(
                            text("DELETE FROM contacts WHERE publication_id = :pub_id"),
                            {"pub_id": pub_id}
                        )
                        await db.execute(
                            text("DELETE FROM debtors WHERE publication_id = :pub_id"),
                            {"pub_id": pub_id}
                        )
                        await db.execute(
                            text("DELETE FROM auction_objects WHERE auction_id IN (SELECT id FROM auctions WHERE publication_id = :pub_id)"),
                            {"pub_id": pub_id}
                        )
                        await db.execute(
                            text("DELETE FROM auctions WHERE publication_id = :pub_id"),
                            {"pub_id": pub_id}
                        )
                        await db.execute(
                            text("DELETE FROM publications WHERE id = :pub_id"),
                            {"pub_id": pub_id}
                        )
                        
                        print(f"✅ Cleaned test publication: {pub_id}")
                    else:
                        print(f"⚠️  Test publication not found: {pub_id}")
                
                await db.commit()
                print("🎉 Test data cleanup completed!")
                return True
                
            except Exception as e:
                print(f"❌ Error cleaning test data: {str(e)}")
                await db.rollback()
                return False
    
    async def reset_sequences(self, db: AsyncSession):
        """Reset auto-increment sequences."""
        try:
            # Note: PostgreSQL doesn't use sequences for UUID primary keys
            # But we can reset any sequences if they exist
            sequences = await db.execute(text("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
            """))
            
            sequence_list = sequences.fetchall()
            if sequence_list:
                print("🔄 Resetting sequences...")
                for (seq_name,) in sequence_list:
                    await db.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
                print("✅ Sequences reset")
            else:
                print("ℹ️  No sequences to reset (using UUIDs)")
                
        except Exception as e:
            print(f"⚠️  Could not reset sequences: {str(e)}")
    
    def print_summary(self):
        """Print cleanup summary."""
        if self.cleaned_tables:
            print("\n📊 Cleanup Summary:")
            print("=" * 60)
            total_deleted = 0
            for table_info in self.cleaned_tables:
                deleted = table_info['deleted']
                total_deleted += deleted
                print(f"  {table_info['table']:20} | {deleted:6} records deleted")
            print("=" * 60)
            print(f"  {'TOTAL':20} | {total_deleted:6} records deleted")
            print("=" * 60)
        
        if self.errors:
            print(f"\n❌ Errors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
    
    async def show_database_stats(self):
        """Show current database statistics."""
        print("📊 Current Database Statistics:")
        print("=" * 50)
        
        async with AsyncSessionLocal() as db:
            tables = [
                'publications', 'auctions', 'auction_objects', 
                'debtors', 'contacts', 'user_subscriptions', 'auction_views'
            ]
            
            for table in tables:
                try:
                    count = await db.scalar(text(f"SELECT COUNT(*) FROM {table}"))
                    print(f"  {table:20} | {count:6} records")
                except Exception as e:
                    print(f"  {table:20} | ERROR: {str(e)}")


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database cleanup utility')
    parser.add_argument('--mode', choices=['all', 'test', 'stats'], default='test',
                       help='Cleanup mode: all (all data), test (test data only), stats (show statistics)')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    cleanup = DatabaseCleanup()
    
    if args.mode == 'stats':
        await cleanup.show_database_stats()
        return
    
    # Show current stats
    await cleanup.show_database_stats()
    
    if args.mode == 'all':
        if not args.confirm:
            print("\n⚠️  WARNING: This will delete ALL data in the database!")
            response = input("Are you sure? Type 'yes' to continue: ")
            if response.lower() != 'yes':
                print("❌ Cleanup cancelled")
                return
        
        success = await cleanup.cleanup_all_data()
    else:  # test mode
        success = await cleanup.cleanup_test_data_only()
    
    if success:
        print("\n✅ Cleanup completed successfully!")
        await cleanup.show_database_stats()
    else:
        print("\n❌ Cleanup completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
