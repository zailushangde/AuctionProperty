#!/usr/bin/env python3
"""
Database bootstrap script to populate the database with SHAB publication data.
Takes a list of publication IDs, fetches and parses the XML data, then stores it in the database.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseBootstrap:
    """Bootstrap the database with SHAB publication data."""
    
    def __init__(self):
        self.parser = SHABParser()
        self.processed_count = 0
        self.error_count = 0
        self.skipped_count = 0
    
    def construct_urls(self, publication_ids: List[str]) -> List[Dict[str, str]]:
        """
        Construct URLs for publication IDs.
        
        Args:
            publication_ids: List of publication IDs
            
        Returns:
            List of dictionaries with 'id', 'xml_url', and 'html_url'
        """
        urls = []
        xml_base_url = "https://www.shab.ch/api/v1/publications/"
        html_base_url = "https://www.shab.ch/#!/search/publications/detail/"
        
        for pub_id in publication_ids:
            # Remove any existing @ symbol
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
        """
        Check if a publication already exists in the database.
        
        Args:
            publication_id: The publication ID to check
            
        Returns:
            True if publication exists, False otherwise
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Publication).where(Publication.id == publication_id)
            )
            return result.scalar_one_or_none() is not None
    
    async def fetch_and_parse_publication(self, url_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Fetch and parse a single publication.
        
        Args:
            url_info: Dictionary containing 'id', 'xml_url', and 'html_url'
            
        Returns:
            Parsed publication data or None if failed
        """
        try:
            logger.info(f"Processing publication: {url_info['id']}")
            
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
            
            # Parse XML with HTML URL for contact extraction
            logger.info(f"Parsing XML for: {url_info['id']}")
            publications = self.parser.parse_xml(xml_content, url_info['html_url'])
            
            if not publications:
                logger.error(f"No publications found in XML for {url_info['id']}")
                self.error_count += 1
                return None
            
            # Should be exactly one publication
            if len(publications) != 1:
                logger.warning(f"Expected 1 publication, got {len(publications)} for {url_info['id']}")
            
            publication_data = publications[0]
            
            # Ensure the ID matches
            if publication_data.get('id') != url_info['id']:
                logger.warning(f"ID mismatch: expected {url_info['id']}, got {publication_data.get('id')}")
                publication_data['id'] = url_info['id']
            
            logger.info(f"Successfully parsed publication: {url_info['id']}")
            return publication_data
            
        except Exception as e:
            logger.error(f"Error processing publication {url_info['id']}: {str(e)}")
            self.error_count += 1
            return None
    
    async def store_publication_data(self, publication_data: Dict[str, Any]) -> bool:
        """
        Store publication data in the database.
        
        Args:
            publication_data: Parsed publication data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Storing publication data for: {publication_data['id']}")
            
            # Use the existing task function to process and store data
            await _process_publication_data(publication_data)
            
            logger.info(f"Successfully stored publication: {publication_data['id']}")
            self.processed_count += 1
            return True
            
        except Exception as e:
            logger.error(f"Error storing publication {publication_data['id']}: {str(e)}")
            self.error_count += 1
            return False
    
    async def process_publication(self, url_info: Dict[str, str]) -> bool:
        """
        Process a single publication (fetch, parse, store).
        
        Args:
            url_info: Dictionary containing 'id', 'xml_url', and 'html_url'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch and parse
            publication_data = await self.fetch_and_parse_publication(url_info)
            
            if not publication_data:
                return False
            
            # Store in database
            return await self.store_publication_data(publication_data)
            
        except Exception as e:
            logger.error(f"Error processing publication {url_info['id']}: {str(e)}")
            self.error_count += 1
            return False
    
    async def bootstrap_database(self, publication_ids: List[str], batch_size: int = 5) -> Dict[str, int]:
        """
        Bootstrap the database with publication data.
        
        Args:
            publication_ids: List of publication IDs to process
            batch_size: Number of publications to process concurrently
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Starting database bootstrap with {len(publication_ids)} publications")
        
        # Construct URLs
        urls = self.construct_urls(publication_ids)
        logger.info(f"Constructed {len(urls)} URLs")
        
        # Process in batches to avoid overwhelming the server
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
            
            # Process batch concurrently
            tasks = [self.process_publication(url_info) for url_info in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log batch results
            successful = sum(1 for r in results if r is True)
            logger.info(f"Batch completed: {successful}/{len(batch)} successful")
            
            # Small delay between batches to be respectful to the server
            if i + batch_size < len(urls):
                await asyncio.sleep(1)
        
        # Final statistics
        stats = {
            'total': len(publication_ids),
            'processed': self.processed_count,
            'skipped': self.skipped_count,
            'errors': self.error_count
        }
        
        logger.info("Bootstrap completed!")
        logger.info(f"Total: {stats['total']}")
        logger.info(f"Processed: {stats['processed']}")
        logger.info(f"Skipped: {stats['skipped']}")
        logger.info(f"Errors: {stats['errors']}")
        
        return stats


async def main():
    """Main function to run the bootstrap script."""
    
    # Example publication IDs - replace with your actual list
    publication_ids = [
        "c42e67af-486d-44f4-8c6e-0ad03538770d",
        "bb0b8622-803e-413e-8d71-bb6da17f5b0c",
        # Add more publication IDs here
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
    bootstrap = DatabaseBootstrap()
    stats = await bootstrap.bootstrap_database(publication_ids)
    
    # Print final results
    print("\n" + "="*60)
    print("🎉 DATABASE BOOTSTRAP COMPLETED!")
    print("="*60)
    print(f"📊 Total publications: {stats['total']}")
    print(f"✅ Successfully processed: {stats['processed']}")
    print(f"⏭️  Skipped (already exist): {stats['skipped']}")
    print(f"❌ Errors: {stats['errors']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
