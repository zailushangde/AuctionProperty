#!/usr/bin/env python3
"""
Simple script to run the database bootstrap with your publication IDs.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.bootstrap_database import DatabaseBootstrap


async def run_bootstrap_with_ids(publication_ids):
    """Run bootstrap with a list of publication IDs."""
    bootstrap = DatabaseBootstrap()
    stats = await bootstrap.bootstrap_database(publication_ids, batch_size=3)
    return stats


async def main():
    """Main function."""
    
    # Your list of publication IDs
    publication_ids = [
        '6048b37e-2062-4bc6-a4d9-66d472f3cc2d', 
        'c7948b44-cc3a-4496-bd1d-6e30b4df8e9e'
        # Add more IDs here as needed
    ]
    
    print("🚀 Starting database bootstrap...")
    print(f"📋 Processing {len(publication_ids)} publication IDs")
    
    # Run the bootstrap
    stats = await run_bootstrap_with_ids(publication_ids)
    
    # Print results
    print("\n" + "="*60)
    print("🎉 BOOTSTRAP COMPLETED!")
    print("="*60)
    print(f"📊 Total: {stats['total']}")
    print(f"✅ Processed: {stats['processed']}")
    print(f"⏭️  Skipped: {stats['skipped']}")
    print(f"❌ Errors: {stats['errors']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
