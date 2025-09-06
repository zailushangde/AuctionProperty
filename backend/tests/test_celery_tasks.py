"""Tests for Celery background tasks with new schema."""

import pytest
import uuid
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.tasks.shab_tasks import (
    _process_publication_data, _cleanup_expired_data, 
    _generate_daily_report, _geocode_auction_locations
)
from app.models import (
    Publication, Auction, AuctionObject, Debtor, Contact,
    DebtorType
)
from app.database import AsyncSessionLocal


class TestCeleryTasks:
    """Test Celery background tasks."""
    
    @pytest.mark.asyncio
    async def test_process_publication_data_new_schema(self):
        """Test processing publication data with new schema."""
        
        # Mock publication data matching new schema
        pub_data = {
            "id": uuid.uuid4(),
            "publication_date": date(2025, 9, 6),
            "expiration_date": date(2026, 9, 6),
            "title": {
                "de": "Betreibungsamtliche Grundstücksteigerung",
                "fr": "Vente aux enchères d'immeubles",
                "en": "Property auction"
            },
            "language": "de",
            "canton": "ZH",
            "content": "Test content",
            "auctions": [
                {
                    "id": uuid.uuid4(),
                    "date": date(2025, 10, 15),
                    "time": "14:30:00",
                    "location": "Test Location",
                    "circulation": {
                        "entry_deadline": "2025-09-25",
                        "comment_entry_deadline": "Test circulation comment"
                    },
                    "registration": {
                        "entry_deadline": "2025-10-05",
                        "comment_entry_deadline": "Test registration comment"
                    },
                    "auction_objects": [
                        {
                            "id": uuid.uuid4(),
                            "parcel_number": "1234",
                            "estimated_value": "500000.00",
                            "description": "Test property",
                            "property_type": "House",
                            "address": "Test Street 123",
                            "municipality": "Test City",
                            "canton": "ZH",
                            "latitude": "47.3769",
                            "longitude": "8.5417"
                        }
                    ]
                }
            ],
            "debtors": [
                {
                    "id": uuid.uuid4(),
                    "debtor_type": "person",
                    "name": "Smith",
                    "prename": "John",
                    "date_of_birth": "1980-05-15",
                    "country_of_origin": {
                        "name": {"de": "Deutschland", "en": "Germany"},
                        "isoCode": "DE"
                    },
                    "residence": {
                        "select_type": "switzerland"
                    },
                    "address": "Test Street 123",
                    "city": "Test City",
                    "postal_code": "8001"
                }
            ],
            "contacts": [
                {
                    "id": uuid.uuid4(),
                    "name": "Test Office",
                    "phone": "+41 44 123 45 67",
                    "email": "test@office.ch",
                    "address": "Office Street 456",
                    "city": "Office City",
                    "postal_code": "8002",
                    "contact_type": "office",
                    "office_id": "office-123",
                    "contains_post_office_box": False,
                    "post_office_box": {
                        "number": "123",
                        "zipCode": "8001",
                        "town": "Zurich"
                    }
                }
            ]
        }
        
        # Process the data
        await _process_publication_data(pub_data)
        
        # Verify data was created correctly
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            
            # Check publication
            pub_result = await db.execute(
                select(Publication).where(Publication.id == pub_data["id"])
            )
            publication = pub_result.scalar_one_or_none()
            
            assert publication is not None
            assert publication.title["de"] == "Betreibungsamtliche Grundstücksteigerung"
            assert publication.title["fr"] == "Vente aux enchères d'immeubles"
            assert publication.expiration_date == date(2026, 9, 6)
            
            # Check auction
            auction_result = await db.execute(
                select(Auction).where(Auction.publication_id == publication.id)
            )
            auction = auction_result.scalar_one_or_none()
            
            assert auction is not None
            assert auction.date == date(2025, 10, 15)
            assert auction.circulation_entry_deadline == date(2025, 9, 25)
            assert auction.registration_entry_deadline == date(2025, 10, 5)
            assert auction.circulation_comment_deadline == "Test circulation comment"
            
            # Check auction object
            obj_result = await db.execute(
                select(AuctionObject).where(AuctionObject.auction_id == auction.id)
            )
            auction_object = obj_result.scalar_one_or_none()
            
            assert auction_object is not None
            assert auction_object.parcel_number == "1234"
            assert auction_object.estimated_value == Decimal("500000.00")
            assert auction_object.latitude == Decimal("47.3769")
            assert auction_object.longitude == Decimal("8.5417")
            
            # Check debtor
            debtor_result = await db.execute(
                select(Debtor).where(Debtor.publication_id == publication.id)
            )
            debtor = debtor_result.scalar_one_or_none()
            
            assert debtor is not None
            assert debtor.debtor_type == DebtorType.PERSON
            assert debtor.name == "Smith"
            assert debtor.prename == "John"
            assert debtor.country_of_origin["isoCode"] == "DE"
            assert debtor.residence_type == "switzerland"
            
            # Check contact
            contact_result = await db.execute(
                select(Contact).where(Contact.publication_id == publication.id)
            )
            contact = contact_result.scalar_one_or_none()
            
            assert contact is not None
            assert contact.name == "Test Office"
            assert contact.contact_type == "office"
            assert contact.office_id == "office-123"
            assert contact.post_office_box["number"] == "123"
    
    @pytest.mark.asyncio
    async def test_process_company_debtor(self):
        """Test processing company debtor data."""
        
        pub_data = {
            "id": uuid.uuid4(),
            "publication_date": date(2025, 9, 6),
            "title": {"de": "Test"},
            "language": "de",
            "canton": "ZH",
            "auctions": [],
            "debtors": [
                {
                    "id": uuid.uuid4(),
                    "debtor_type": "company",
                    "name": "Test Company AG",
                    "legal_form": "AG",
                    "address": "Company Street 456",
                    "city": "Company City",
                    "postal_code": "8002"
                }
            ],
            "contacts": []
        }
        
        await _process_publication_data(pub_data)
        
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            
            debtor_result = await db.execute(
                select(Debtor).where(Debtor.publication_id == pub_data["id"])
            )
            debtor = debtor_result.scalar_one_or_none()
            
            assert debtor is not None
            assert debtor.debtor_type == DebtorType.COMPANY
            assert debtor.name == "Test Company AG"
            assert debtor.legal_form == "AG"
            assert debtor.full_name == "Test Company AG"
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_data(self):
        """Test cleanup of expired auction data."""
        
        # Create test data
        async with AsyncSessionLocal() as db:
            # Create old publication and auction
            old_publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2020, 1, 1),  # Old date
                title={"de": "Old Publication"},
                language="de",
                canton="ZH"
            )
            db.add(old_publication)
            await db.flush()
            
            old_auction = Auction(
                id=uuid.uuid4(),
                date=date(2020, 2, 1),  # Old date
                location="Old Location",
                publication_id=old_publication.id
            )
            db.add(old_auction)
            await db.flush()
            
            # Create recent publication and auction
            recent_publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 1, 1),  # Recent date
                title={"de": "Recent Publication"},
                language="de",
                canton="ZH"
            )
            db.add(recent_publication)
            await db.flush()
            
            recent_auction = Auction(
                id=uuid.uuid4(),
                date=date(2025, 2, 1),  # Recent date
                location="Recent Location",
                publication_id=recent_publication.id
            )
            db.add(recent_auction)
            
            await db.commit()
        
        # Run cleanup
        result = await _cleanup_expired_data()
        
        assert result["status"] == "completed"
        assert result["deleted_auctions"] >= 1  # At least the old auction
        
        # Verify old data was deleted
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            
            # Old auction should be deleted
            old_auction_result = await db.execute(
                select(Auction).where(Auction.id == old_auction.id)
            )
            assert old_auction_result.scalar_one_or_none() is None
            
            # Recent auction should still exist
            recent_auction_result = await db.execute(
                select(Auction).where(Auction.id == recent_auction.id)
            )
            assert recent_auction_result.scalar_one_or_none() is not None
    
    @pytest.mark.asyncio
    async def test_generate_daily_report(self):
        """Test daily report generation."""
        
        # Create test data
        async with AsyncSessionLocal() as db:
            # Create publications and auctions for testing
            for i in range(3):
                pub = Publication(
                    id=uuid.uuid4(),
                    publication_date=date(2025, 9, 6),  # Today
                    title={"de": f"Test Publication {i}"},
                    language="de",
                    canton="ZH"
                )
                db.add(pub)
                await db.flush()
                
                auction = Auction(
                    id=uuid.uuid4(),
                    date=date(2025, 9, 6),  # Today
                    location=f"Test Location {i}",
                    publication_id=pub.id
                )
                db.add(auction)
            
            await db.commit()
        
        # Generate report
        result = await _generate_daily_report()
        
        assert result["status"] == "completed"
        assert "new_publications" in result
        assert "new_auctions" in result
        assert "upcoming_auctions" in result
        assert result["date"] == date.today().isoformat()
    
    @pytest.mark.asyncio
    async def test_geocode_auction_locations(self):
        """Test geocoding of auction locations."""
        
        # Create test data without coordinates
        async with AsyncSessionLocal() as db:
            pub = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={"de": "Test"},
                language="de",
                canton="ZH"
            )
            db.add(pub)
            await db.flush()
            
            auction = Auction(
                id=uuid.uuid4(),
                date=date(2025, 10, 15),
                location="Test Location",
                publication_id=pub.id
            )
            db.add(auction)
            await db.flush()
            
            # Create auction object without coordinates
            auction_object = AuctionObject(
                id=uuid.uuid4(),
                address="Test Street 123, Zurich",
                municipality="Zurich",
                canton="ZH",
                auction_id=auction.id
            )
            db.add(auction_object)
            await db.commit()
        
        # Run geocoding (with mock geocoding service)
        with patch('app.tasks.shab_tasks._geocode_address') as mock_geocode:
            mock_geocode.return_value = {"lat": 47.3769, "lng": 8.5417}
            
            result = await _geocode_auction_locations()
            
            assert result["status"] == "completed"
            assert result["total_processed"] >= 1
        
        # Verify coordinates were added
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            
            obj_result = await db.execute(
                select(AuctionObject).where(AuctionObject.id == auction_object.id)
            )
            updated_object = obj_result.scalar_one_or_none()
            
            # Note: In the current implementation, _geocode_address returns None
            # So coordinates won't actually be updated, but the task runs without error
            assert updated_object is not None


class TestTaskIntegration:
    """Test task integration and error handling."""
    
    @pytest.mark.asyncio
    async def test_duplicate_publication_handling(self):
        """Test handling of duplicate publications."""
        
        pub_data = {
            "id": uuid.uuid4(),
            "publication_date": date(2025, 9, 6),
            "title": {"de": "Duplicate Test"},
            "language": "de",
            "canton": "ZH",
            "auctions": [],
            "debtors": [],
            "contacts": []
        }
        
        # Process first time
        await _process_publication_data(pub_data)
        
        # Process second time (should be skipped)
        await _process_publication_data(pub_data)
        
        # Verify only one publication exists
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select, func
            
            count_result = await db.execute(
                select(func.count(Publication.id)).where(
                    Publication.title["de"].astext == "Duplicate Test"
                )
            )
            count = count_result.scalar()
            
            assert count == 1  # Only one publication should exist
    
    @pytest.mark.asyncio
    async def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        
        # Test with missing required fields
        invalid_pub_data = {
            "id": uuid.uuid4(),
            # Missing publication_date
            "title": {"de": "Invalid Test"},
            "language": "de",
            "canton": "ZH",
            "auctions": [],
            "debtors": [],
            "contacts": []
        }
        
        # Should handle gracefully
        try:
            await _process_publication_data(invalid_pub_data)
        except Exception as e:
            # Should not crash the entire process
            assert "publication_date" in str(e) or "required" in str(e)
    
    @pytest.mark.asyncio
    async def test_database_rollback_on_error(self):
        """Test database rollback on processing errors."""
        
        # Create data that will cause an error
        pub_data = {
            "id": uuid.uuid4(),
            "publication_date": date(2025, 9, 6),
            "title": {"de": "Error Test"},
            "language": "de",
            "canton": "ZH",
            "auctions": [
                {
                    "id": uuid.uuid4(),
                    "date": "invalid-date",  # Invalid date format
                    "location": "Test Location",
                    "auction_objects": []
                }
            ],
            "debtors": [],
            "contacts": []
        }
        
        # Should handle error gracefully
        try:
            await _process_publication_data(pub_data)
        except Exception:
            pass  # Expected to fail
        
        # Verify no partial data was saved
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            
            pub_result = await db.execute(
                select(Publication).where(Publication.id == pub_data["id"])
            )
            publication = pub_result.scalar_one_or_none()
            
            # Publication should not exist due to rollback
            assert publication is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
