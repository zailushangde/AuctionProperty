"""Background tasks for SHAB data processing."""

import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from celery import current_task

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import Publication, Auction, Debtor, AuctionObject, Contact, DebtorType
from app.parsers import SHABParser


@celery_app.task(bind=True)
def fetch_shab_data(self, days_back: int = 7):
    """Fetch and process SHAB data from the last N days."""
    
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'status': 'Starting SHAB data fetch'})
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        # Create parser instance
        parser = SHABParser()
        
        # Fetch XML data
        self.update_state(state='PROGRESS', meta={'status': 'Fetching XML data from SHAB API'})
        xml_content = parser.fetch_xml_data(start_date, end_date)
        
        # Parse XML
        self.update_state(state='PROGRESS', meta={'status': 'Parsing XML data'})
        publications_data = parser.parse_xml(xml_content)
        
        # Process publications
        processed_count = 0
        for pub_data in publications_data:
            try:
                # Process publication in async context
                import asyncio
                asyncio.run(_process_publication_data(pub_data))
                processed_count += 1
                
                # Update progress
                progress = (processed_count / len(publications_data)) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Processing publications: {processed_count}/{len(publications_data)}',
                        'progress': progress
                    }
                )
                
            except Exception as e:
                print(f"Error processing publication {pub_data.get('id', 'unknown')}: {e}")
                continue
        
        return {
            'status': 'completed',
            'processed_publications': processed_count,
            'total_publications': len(publications_data),
            'date_range': f"{start_date} to {end_date}"
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'status': f'Task failed: {str(e)}'}
        )
        raise


async def _process_publication_data(pub_data: Dict[str, Any]):
    """Process a single publication's data and save to database."""
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if publication already exists
            existing_pub = await db.execute(
                select(Publication).where(
                    and_(
                        Publication.title == pub_data['title'],
                        Publication.publication_date == pub_data['publication_date']
                    )
                )
            )
            
            if existing_pub.scalar_one_or_none():
                return  # Skip if already exists
            
            # Create publication
            publication = Publication(
                id=pub_data['id'],
                publication_date=pub_data['publication_date'],
                expiration_date=pub_data.get('expiration_date'),
                title=pub_data['title'],  # Now JSONB for multilingual titles
                language=pub_data['language'],
                canton=pub_data['canton'],
                content=pub_data.get('content')
            )
            
            db.add(publication)
            await db.flush()  # Get the ID
            
            # Create auctions
            for auction_data in pub_data.get('auctions', []):
                auction = Auction(
                    id=auction_data['id'],
                    date=auction_data['date'],
                    time=auction_data.get('time'),
                    location=auction_data['location'],
                    circulation_entry_deadline=auction_data.get('circulation', {}).get('entry_deadline'),
                    circulation_comment_deadline=auction_data.get('circulation', {}).get('comment_entry_deadline'),
                    registration_entry_deadline=auction_data.get('registration', {}).get('entry_deadline'),
                    registration_comment_deadline=auction_data.get('registration', {}).get('comment_entry_deadline'),
                    publication_id=publication.id
                )
                
                db.add(auction)
                await db.flush()
                
                # Create auction objects
                for obj_data in auction_data.get('auction_objects', []):
                    auction_object = AuctionObject(
                        id=obj_data.get('id', str(uuid.uuid4())),
                        parcel_number=obj_data.get('parcel_number'),
                        property_number=obj_data.get('property_number'),
                        surface_area=obj_data.get('surface_area'),
                        estimated_value=obj_data.get('estimated_value'),
                        description=obj_data.get('description'),
                        property_type=obj_data.get('property_type'),
                        address=obj_data.get('address'),
                        municipality=obj_data.get('municipality'),
                        canton=obj_data.get('canton'),
                        remarks=obj_data.get('remarks'),
                        latitude=obj_data.get('latitude'),
                        longitude=obj_data.get('longitude'),
                        auction_id=auction.id
                    )
                    
                    db.add(auction_object)
            
            # Create debtors
            for debtor_data in pub_data.get('debtors', []):
                # Handle address - convert dict to string if needed
                address = debtor_data.get('address')
                if isinstance(address, dict):
                    # Convert address dict to string
                    address_parts = []
                    if address.get('street'):
                        address_parts.append(address['street'])
                    if address.get('house_number'):
                        address_parts.append(address['house_number'])
                    address = ' '.join(address_parts) if address_parts else None
                
                debtor = Debtor(
                    id=debtor_data['id'],
                    debtor_type=DebtorType(debtor_data.get('debtor_type', 'person')),
                    name=debtor_data['name'],
                    prename=debtor_data.get('prename'),
                    date_of_birth=debtor_data.get('date_of_birth'),
                    country_of_origin=debtor_data.get('country_of_origin'),
                    residence_type=debtor_data.get('residence', {}).get('select_type'),
                    address=address,
                    city=debtor_data.get('city'),
                    postal_code=debtor_data.get('postal_code'),
                    legal_form=debtor_data.get('legal_form'),
                    publication_id=publication.id
                )
                
                db.add(debtor)
            
            # Create contacts
            for contact_data in pub_data.get('contacts', []):
                contact = Contact(
                    id=contact_data['id'],
                    name=contact_data['name'],
                    phone=contact_data.get('phone'),
                    email=contact_data.get('email'),
                    address=contact_data.get('address'),
                    city=contact_data.get('city'),
                    postal_code=contact_data.get('postal_code'),
                    contact_type=contact_data.get('contact_type'),
                    office_id=contact_data.get('office_id'),
                    contains_post_office_box=contact_data.get('contains_post_office_box'),
                    post_office_box=contact_data.get('post_office_box'),
                    publication_id=publication.id
                )
                
                db.add(contact)
            
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            raise e


@celery_app.task
def cleanup_expired_data():
    """Clean up expired auction data (auctions older than 1 year)."""
    
    try:
        import asyncio
        return asyncio.run(_cleanup_expired_data())
    except Exception as e:
        print(f"Error in cleanup task: {e}")
        raise


async def _cleanup_expired_data():
    """Clean up expired data."""
    
    cutoff_date = date.today() - timedelta(days=365)
    
    async with AsyncSessionLocal() as db:
        try:
            # Find expired auctions
            expired_auctions = await db.execute(
                select(Auction).where(Auction.date < cutoff_date)
            )
            auctions_to_delete = expired_auctions.scalars().all()
            
            # Delete expired auctions (cascade will handle related objects)
            for auction in auctions_to_delete:
                await db.delete(auction)
            
            await db.commit()
            
            return {
                'status': 'completed',
                'deleted_auctions': len(auctions_to_delete),
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            await db.rollback()
            raise e


@celery_app.task
def geocode_auction_locations():
    """Geocode auction locations for map integration."""
    
    try:
        import asyncio
        return asyncio.run(_geocode_auction_locations())
    except Exception as e:
        print(f"Error in geocoding task: {e}")
        raise


async def _geocode_auction_locations():
    """Geocode auction locations that don't have coordinates."""
    
    async with AsyncSessionLocal() as db:
        try:
            # Find auction objects without coordinates
            query = select(AuctionObject).where(
                and_(
                    AuctionObject.latitude.is_(None),
                    AuctionObject.longitude.is_(None),
                    AuctionObject.address.isnot(None)
                )
            ).limit(100)  # Process in batches
            
            result = await db.execute(query)
            objects_to_geocode = result.scalars().all()
            
            geocoded_count = 0
            for obj in objects_to_geocode:
                try:
                    # Simple geocoding - in production, use a proper geocoding service
                    coordinates = await _geocode_address(obj.address, obj.municipality, obj.canton)
                    if coordinates:
                        obj.latitude = coordinates['lat']
                        obj.longitude = coordinates['lng']
                        geocoded_count += 1
                except Exception as e:
                    print(f"Error geocoding {obj.address}: {e}")
                    continue
            
            await db.commit()
            
            return {
                'status': 'completed',
                'geocoded_objects': geocoded_count,
                'total_processed': len(objects_to_geocode)
            }
            
        except Exception as e:
            await db.rollback()
            raise e


async def _geocode_address(address: str, municipality: str, canton: str) -> dict:
    """Geocode an address (placeholder implementation)."""
    
    # This is a placeholder - in production, you would use:
    # - Google Geocoding API
    # - OpenStreetMap Nominatim
    # - Swiss Federal Office of Topography API
    
    # For now, return None to indicate no geocoding
    return None


@celery_app.task
def generate_daily_report():
    """Generate daily statistics report."""
    
    try:
        import asyncio
        return asyncio.run(_generate_daily_report())
    except Exception as e:
        print(f"Error in report generation: {e}")
        raise


async def _generate_daily_report():
    """Generate daily report."""
    
    async with AsyncSessionLocal() as db:
        try:
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Count new publications
            new_pubs = await db.execute(
                select(Publication).where(
                    and_(
                        Publication.publication_date >= yesterday,
                        Publication.publication_date < today
                    )
                )
            )
            new_publications_count = len(new_pubs.scalars().all())
            
            # Count new auctions
            new_auctions = await db.execute(
                select(Auction).where(
                    and_(
                        Auction.date >= yesterday,
                        Auction.date < today
                    )
                )
            )
            new_auctions_count = len(new_auctions.scalars().all())
            
            # Count upcoming auctions (next 7 days)
            upcoming_date = today + timedelta(days=7)
            upcoming_auctions = await db.execute(
                select(Auction).where(
                    and_(
                        Auction.date >= today,
                        Auction.date <= upcoming_date
                    )
                )
            )
            upcoming_auctions_count = len(upcoming_auctions.scalars().all())
            
            report = {
                'date': today.isoformat(),
                'new_publications': new_publications_count,
                'new_auctions': new_auctions_count,
                'upcoming_auctions': upcoming_auctions_count,
                'status': 'completed'
            }
            
            # Here you could save the report to a file or send it via email
            print(f"Daily report generated: {report}")
            
            return report
            
        except Exception as e:
            raise e
