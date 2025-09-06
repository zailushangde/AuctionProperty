"""Background tasks for SHAB data processing."""

import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from celery import current_task

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import Publication, Auction, Debtor, AuctionObject, Contact
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
                title=pub_data['title'],
                language=pub_data['language'],
                canton=pub_data['canton'],
                registration_office=pub_data['registration_office'],
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
                    auction_type=auction_data.get('auction_type'),
                    court=auction_data.get('court'),
                    publication_id=publication.id
                )
                
                db.add(auction)
                await db.flush()
                
                # Create auction objects
                for obj_data in auction_data.get('auction_objects', []):
                    auction_object = AuctionObject(
                        id=obj_data['id'],
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
                        auction_id=auction.id
                    )
                    
                    db.add(auction_object)
            
            # Create debtors
            for debtor_data in pub_data.get('debtors', []):
                debtor = Debtor(
                    id=debtor_data['id'],
                    name=debtor_data['name'],
                    prename=debtor_data.get('prename'),
                    date_of_birth=debtor_data.get('date_of_birth'),
                    address=debtor_data.get('address'),
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
                    title=contact_data.get('title'),
                    phone=contact_data.get('phone'),
                    email=contact_data.get('email'),
                    fax=contact_data.get('fax'),
                    organization=contact_data.get('organization'),
                    department=contact_data.get('department'),
                    address=contact_data.get('address'),
                    city=contact_data.get('city'),
                    postal_code=contact_data.get('postal_code'),
                    contact_type=contact_data.get('contact_type'),
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
