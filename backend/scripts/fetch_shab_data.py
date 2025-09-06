#!/usr/bin/env python3
"""Script to manually fetch SHAB data."""

import asyncio
import sys
from pathlib import Path
from datetime import date, timedelta

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parsers import SHABParser
from app.tasks.shab_tasks import _process_publication_data


async def fetch_and_process_data(days_back: int = 7):
    """Fetch and process SHAB data."""
    
    print(f"Fetching SHAB data for the last {days_back} days...")
    
    # Create parser
    parser = SHABParser()
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    try:
        # Fetch XML data
        print(f"Fetching XML data from {start_date} to {end_date}...")
        xml_content = parser.fetch_xml_data(start_date, end_date)
        
        # Parse XML
        print("Parsing XML data...")
        publications_data = parser.parse_xml(xml_content)
        
        print(f"Found {len(publications_data)} publications to process")
        
        # Process each publication
        processed_count = 0
        for i, pub_data in enumerate(publications_data, 1):
            try:
                print(f"Processing publication {i}/{len(publications_data)}: {pub_data['title'][:50]}...")
                await _process_publication_data(pub_data)
                processed_count += 1
            except Exception as e:
                print(f"Error processing publication {i}: {e}")
                continue
        
        print(f"Successfully processed {processed_count}/{len(publications_data)} publications")
        
    except Exception as e:
        print(f"Error fetching or processing data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch SHAB data")
    parser.add_argument(
        "--days", 
        type=int, 
        default=7, 
        help="Number of days back to fetch data (default: 7)"
    )
    
    args = parser.parse_args()
    asyncio.run(fetch_and_process_data(args.days))
