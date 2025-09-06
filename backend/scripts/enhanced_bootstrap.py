#!/usr/bin/env python3
"""
Enhanced database bootstrap script that can handle different publication types.
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any
import logging

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.parsers.shab_parser import SHABParser
from app.tasks.shab_tasks import _process_publication_data
from app.models import Publication
from sqlalchemy import select
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedDatabaseBootstrap:
    """Enhanced bootstrap that handles different publication types."""
    
    def __init__(self):
        self.parser = SHABParser()
        self.processed_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.non_auction_count = 0
    
    def detect_publication_type(self, xml_content: str) -> str:
        """Detect the publication type from XML content."""
        if 'SB01' in xml_content:
            return 'SB01'  # Auction/Debt Collection
        elif 'HR02' in xml_content:
            return 'HR02'  # Commercial Register
        elif 'HR01' in xml_content:
            return 'HR01'  # Commercial Register (different version)
        else:
            return 'UNKNOWN'
    
    def construct_urls(self, publication_ids: List[str]) -> List[Dict[str, str]]:
        """Construct URLs for publication IDs."""
        urls = []
        xml_base_url = "https://www.shab.ch/api/v1/publications/"
        html_base_url = "https://www.shab.ch/#!/search/publications/detail/"
        
        for pub_id in publication_ids:
            clean_id = pub_id.strip().lstrip('@')
            
            xml_url = f"{xml_base_url}{clean_id}/xml"
            html_url = f"{html_base_url}{clean_id}"
            
            urls.append({
                'id': clean_id,
                'xml_url': xml_url,
                'html_url': html_url
            })
        
        return urls
    
    async def check_existing_publication(self, publication_id: str) -> bool:
        """Check if a publication already exists in the database."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Publication).where(Publication.id == publication_id)
            )
            return result.scalar_one_or_none() is not None
    
    async def fetch_and_analyze_publication(self, url_info: Dict[str, str]) -> Dict[str, Any]:
        """Fetch and analyze a publication to determine its type and content."""
        try:
            logger.info(f"Analyzing publication: {url_info['id']}")
            
            # Check if already exists
            if await self.check_existing_publication(url_info['id']):
                logger.info(f"Publication {url_info['id']} already exists, skipping")
                self.skipped_count += 1
                return None
            
            # Fetch XML data
            logger.info(f"Fetching XML from: {url_info['xml_url']}")
            xml_content = self.parser.fetch_url_data(url_info['xml_url'])
            
            if not xml_content:
                logger.error(f"Failed to fetch XML for {url_info['id']}")
                self.error_count += 1
                return None
            
            # Detect publication type
            pub_type = self.detect_publication_type(xml_content)
            logger.info(f"Publication type detected: {pub_type}")
            
            if pub_type != 'SB01':
                logger.info(f"Skipping non-auction publication {url_info['id']} (type: {pub_type})")
                self.non_auction_count += 1
                return {
                    'id': url_info['id'],
                    'type': pub_type,
                    'skip_reason': f'Non-auction publication (type: {pub_type})'
                }
            
            # Parse XML with HTML URL for contact extraction
            logger.info(f"Parsing auction publication: {url_info['id']}")
            publications = self.parser.parse_xml(xml_content, url_info['html_url'])
            
            if not publications:
                logger.error(f"No publications found in XML for {url_info['id']}")
                self.error_count += 1
                return None
            
            publication_data = publications[0]
            
            # Ensure the ID matches
            if publication_data.get('id') != url_info['id']:
                logger.warning(f"ID mismatch: expected {url_info['id']}, got {publication_data.get('id')}")
                publication_data['id'] = url_info['id']
            
            # Add publication type info
            publication_data['publication_type'] = pub_type
            
            logger.info(f"Successfully parsed auction publication: {url_info['id']}")
            return publication_data
            
        except Exception as e:
            logger.error(f"Error analyzing publication {url_info['id']}: {str(e)}")
            self.error_count += 1
            return None
    
    async def store_publication_data(self, publication_data: Dict[str, Any]) -> bool:
        """Store publication data in the database."""
        try:
            logger.info(f"Storing auction publication: {publication_data['id']}")
            
            # Use the existing task function to process and store data
            await _process_publication_data(publication_data)
            
            logger.info(f"Successfully stored auction publication: {publication_data['id']}")
            self.processed_count += 1
            return True
            
        except Exception as e:
            logger.error(f"Error storing publication {publication_data['id']}: {str(e)}")
            self.error_count += 1
            return False
    
    async def process_publication(self, url_info: Dict[str, str]) -> Dict[str, Any]:
        """Process a single publication (analyze, parse if auction, store)."""
        try:
            # Analyze publication
            result = await self.fetch_and_analyze_publication(url_info)
            
            if not result:
                return {'status': 'error', 'id': url_info['id']}
            
            # Check if it's a non-auction publication
            if 'skip_reason' in result:
                return {'status': 'skipped', 'id': url_info['id'], 'reason': result['skip_reason']}
            
            # Store auction publication
            success = await self.store_publication_data(result)
            
            if success:
                return {'status': 'processed', 'id': url_info['id']}
            else:
                return {'status': 'error', 'id': url_info['id']}
            
        except Exception as e:
            logger.error(f"Error processing publication {url_info['id']}: {str(e)}")
            self.error_count += 1
            return {'status': 'error', 'id': url_info['id']}
    
    async def bootstrap_database(self, publication_ids: List[str], batch_size: int = 5) -> Dict[str, int]:
        """Bootstrap the database with publication data."""
        logger.info(f"Starting enhanced database bootstrap with {len(publication_ids)} publications")
        
        # Construct URLs
        urls = self.construct_urls(publication_ids)
        logger.info(f"Constructed {len(urls)} URLs")
        
        # Process in batches
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
            
            # Process batch concurrently
            tasks = [self.process_publication(url_info) for url_info in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log batch results
            processed = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'processed')
            skipped = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'skipped')
            errors = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'error')
            
            logger.info(f"Batch completed: {processed} processed, {skipped} skipped, {errors} errors")
            
            # Small delay between batches
            if i + batch_size < len(urls):
                await asyncio.sleep(1)
        
        # Final statistics
        stats = {
            'total': len(publication_ids),
            'processed': self.processed_count,
            'skipped': self.skipped_count,
            'non_auction': self.non_auction_count,
            'errors': self.error_count
        }
        
        logger.info("Enhanced bootstrap completed!")
        logger.info(f"Total: {stats['total']}")
        logger.info(f"Processed (auctions): {stats['processed']}")
        logger.info(f"Skipped (already exist): {stats['skipped']}")
        logger.info(f"Skipped (non-auction): {stats['non_auction']}")
        logger.info(f"Errors: {stats['errors']}")
        
        return stats


async def main():
    """Main function to run the enhanced bootstrap script."""
    
    # Example publication IDs - replace with your actual list
    publication_ids = [
        '6048b37e-2062-4bc6-a4d9-66d472f3cc2d', 'c7948b44-cc3a-4496-bd1d-6e30b4df8e9e', '3142634e-cc4e-4696-9f1e-ad674ae784e8', 'b343804b-027d-44db-918e-86e66e1ce470', '324cace7-cca2-4656-8cac-6aad6a6147d6', '851ee2be-e8f5-4c09-bd92-20932f6a960c', 'd2854126-9ccf-45dd-b3e6-f4c00133d4d7', 'f2b72834-7f4c-4700-9d62-d30b2cbf1fb2', '3895b51f-a7a1-4a23-91e2-19c43c001bb4', '70c8b157-ea90-4ce5-812f-6da632b1f206', '451fbddf-c6cb-4352-8b3d-1218d086898a', '35dd5059-4599-4c5f-b95c-762189c50460', 'c5986112-3923-4389-aebe-799dfa4670b2', '107d4bca-df4d-428c-8825-7290e3d23487', '8eced93a-682d-42f8-8c45-cf0fc1a6048e',
    ]
    
    # You can also read from a file
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as f:
                publication_ids = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(publication_ids)} publication IDs from {file_path}")
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return
    
    if not publication_ids:
        logger.error("No publication IDs provided")
        return
    
    # Create bootstrap instance and run
    bootstrap = EnhancedDatabaseBootstrap()
    stats = await bootstrap.bootstrap_database(publication_ids)
    
    # Print final results
    print("\n" + "="*60)
    print("🎉 ENHANCED DATABASE BOOTSTRAP COMPLETED!")
    print("="*60)
    print(f"📊 Total publications: {stats['total']}")
    print(f"✅ Successfully processed (auctions): {stats['processed']}")
    print(f"⏭️  Skipped (already exist): {stats['skipped']}")
    print(f"🚫 Skipped (non-auction): {stats['non_auction']}")
    print(f"❌ Errors: {stats['errors']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
