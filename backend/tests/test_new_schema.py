"""Comprehensive tests for the new database schema and API endpoints."""

import pytest
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.database import get_db, AsyncSessionLocal
from app.models import (
    Publication, Auction, AuctionObject, Debtor, Contact,
    UserSubscription, AuctionView, DebtorType, SubscriptionType, ViewType
)


class TestDatabaseModels:
    """Test database models and relationships."""
    
    @pytest.mark.asyncio
    async def test_create_publication_with_multilingual_title(self):
        """Test creating a publication with multilingual title."""
        async with AsyncSessionLocal() as db:
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                expiration_date=date(2026, 9, 6),
                title={
                    "de": "Betreibungsamtliche Grundstücksteigerung",
                    "fr": "Vente aux enchères d'immeubles",
                    "it": "Incanto immobiliare",
                    "en": "Property auction"
                },
                language="de",
                canton="ZH",
                content="Test content"
            )
            
            db.add(publication)
            await db.commit()
            await db.refresh(publication)
            
            assert publication.id is not None
            assert publication.title["de"] == "Betreibungsamtliche Grundstücksteigerung"
            assert publication.title["fr"] == "Vente aux enchères d'immeubles"
            assert publication.expiration_date == date(2026, 9, 6)
    
    @pytest.mark.asyncio
    async def test_create_auction_with_deadlines(self):
        """Test creating an auction with circulation and registration deadlines."""
        async with AsyncSessionLocal() as db:
            # Create publication first
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={"de": "Test Publication"},
                language="de",
                canton="ZH"
            )
            db.add(publication)
            await db.flush()
            
            # Create auction
            auction = Auction(
                id=uuid.uuid4(),
                date=date(2025, 10, 15),
                time=time(14, 30),
                location="Test Location",
                circulation_entry_deadline=date(2025, 9, 25),
                circulation_comment_deadline="Test circulation comment",
                registration_entry_deadline=date(2025, 10, 5),
                registration_comment_deadline="Test registration comment",
                publication_id=publication.id
            )
            
            db.add(auction)
            await db.commit()
            await db.refresh(auction)
            
            assert auction.id is not None
            assert auction.date == date(2025, 10, 15)
            assert auction.time == time(14, 30)
            assert auction.circulation_entry_deadline == date(2025, 9, 25)
            assert auction.registration_entry_deadline == date(2025, 10, 5)
    
    @pytest.mark.asyncio
    async def test_create_auction_object_with_spatial_data(self):
        """Test creating an auction object with spatial coordinates."""
        async with AsyncSessionLocal() as db:
            # Create publication and auction
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={"de": "Test"},
                language="de",
                canton="ZH"
            )
            db.add(publication)
            await db.flush()
            
            auction = Auction(
                id=uuid.uuid4(),
                date=date(2025, 10, 15),
                location="Test Location",
                publication_id=publication.id
            )
            db.add(auction)
            await db.flush()
            
            # Create auction object with spatial data
            auction_object = AuctionObject(
                id=uuid.uuid4(),
                parcel_number="1234",
                estimated_value=Decimal("500000.00"),
                description="Test property description",
                property_type="House",
                address="Test Street 123",
                municipality="Test City",
                canton="ZH",
                latitude=Decimal("47.3769"),
                longitude=Decimal("8.5417"),
                auction_id=auction.id
            )
            
            db.add(auction_object)
            await db.commit()
            await db.refresh(auction_object)
            
            assert auction_object.id is not None
            assert auction_object.parcel_number == "1234"
            assert auction_object.estimated_value == Decimal("500000.00")
            assert auction_object.latitude == Decimal("47.3769")
            assert auction_object.longitude == Decimal("8.5417")
    
    @pytest.mark.asyncio
    async def test_create_debtor_with_type(self):
        """Test creating a debtor with person/company type."""
        async with AsyncSessionLocal() as db:
            # Create publication
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={"de": "Test"},
                language="de",
                canton="ZH"
            )
            db.add(publication)
            await db.flush()
            
            # Test person debtor
            person_debtor = Debtor(
                id=uuid.uuid4(),
                debtor_type=DebtorType.PERSON,
                name="Smith",
                prename="John",
                date_of_birth=date(1980, 5, 15),
                country_of_origin={
                    "name": {"de": "Deutschland", "en": "Germany"},
                    "isoCode": "DE"
                },
                residence_type="switzerland",
                address="Test Street 123",
                city="Test City",
                postal_code="8001",
                publication_id=publication.id
            )
            
            db.add(person_debtor)
            await db.commit()
            await db.refresh(person_debtor)
            
            assert person_debtor.debtor_type == DebtorType.PERSON
            assert person_debtor.full_name == "John Smith"
            assert person_debtor.country_of_origin["isoCode"] == "DE"
            
            # Test company debtor
            company_debtor = Debtor(
                id=uuid.uuid4(),
                debtor_type=DebtorType.COMPANY,
                name="Test Company AG",
                legal_form="AG",
                address="Company Street 456",
                city="Company City",
                postal_code="8002",
                publication_id=publication.id
            )
            
            db.add(company_debtor)
            await db.commit()
            await db.refresh(company_debtor)
            
            assert company_debtor.debtor_type == DebtorType.COMPANY
            assert company_debtor.full_name == "Test Company AG"
    
    @pytest.mark.asyncio
    async def test_create_contact_with_office_details(self):
        """Test creating a contact with office details."""
        async with AsyncSessionLocal() as db:
            # Create publication
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={"de": "Test"},
                language="de",
                canton="ZH"
            )
            db.add(publication)
            await db.flush()
            
            # Create contact
            contact = Contact(
                id=uuid.uuid4(),
                name="Office des poursuites de Zurich",
                phone="+41 44 123 45 67",
                email="contact@zurich.ch",
                address="Bahnhofstrasse 1",
                city="Zurich",
                postal_code="8001",
                contact_type="office",
                office_id="office-123",
                contains_post_office_box=False,
                post_office_box={
                    "number": "123",
                    "zipCode": "8001",
                    "town": "Zurich"
                },
                publication_id=publication.id
            )
            
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            
            assert contact.contact_type == "office"
            assert contact.office_id == "office-123"
            assert contact.post_office_box["number"] == "123"
    
    @pytest.mark.asyncio
    async def test_create_user_subscription(self):
        """Test creating a user subscription."""
        async with AsyncSessionLocal() as db:
            # Create publication and auction
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={"de": "Test"},
                language="de",
                canton="ZH"
            )
            db.add(publication)
            await db.flush()
            
            auction = Auction(
                id=uuid.uuid4(),
                date=date(2025, 10, 15),
                location="Test Location",
                publication_id=publication.id
            )
            db.add(auction)
            await db.flush()
            
            # Create subscription
            subscription = UserSubscription(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                auction_id=auction.id,
                subscription_type=SubscriptionType.PREMIUM,
                payment_id="payment-123",
                amount_paid="15.00",
                is_active=True
            )
            
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
            
            assert subscription.subscription_type == SubscriptionType.PREMIUM
            assert subscription.amount_paid == "15.00"
            assert subscription.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_auction_view(self):
        """Test creating an auction view for analytics."""
        async with AsyncSessionLocal() as db:
            # Create publication and auction
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={"de": "Test"},
                language="de",
                canton="ZH"
            )
            db.add(publication)
            await db.flush()
            
            auction = Auction(
                id=uuid.uuid4(),
                date=date(2025, 10, 15),
                location="Test Location",
                publication_id=publication.id
            )
            db.add(auction)
            await db.flush()
            
            # Create view
            view = AuctionView(
                id=uuid.uuid4(),
                auction_id=auction.id,
                user_id=uuid.uuid4(),
                view_type=ViewType.DETAIL,
                ip_address="192.168.1.1",
                user_agent="Mozilla/5.0...",
                session_id="session-123"
            )
            
            db.add(view)
            await db.commit()
            await db.refresh(view)
            
            assert view.view_type == ViewType.DETAIL
            assert view.ip_address == "192.168.1.1"
            assert view.session_id == "session-123"


class TestAPIIntegration:
    """Test API endpoints with the new schema."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    async def sample_data(self):
        """Create sample data for testing."""
        async with AsyncSessionLocal() as db:
            # Create publication
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                expiration_date=date(2026, 9, 6),
                title={
                    "de": "Test Auction",
                    "fr": "Enchère Test",
                    "en": "Test Auction"
                },
                language="de",
                canton="ZH"
            )
            db.add(publication)
            await db.flush()
            
            # Create auction
            auction = Auction(
                id=uuid.uuid4(),
                date=date(2025, 10, 15),
                time=time(14, 30),
                location="Test Location, Zurich",
                circulation_entry_deadline=date(2025, 9, 25),
                registration_entry_deadline=date(2025, 10, 5),
                publication_id=publication.id
            )
            db.add(auction)
            await db.flush()
            
            # Create auction object
            auction_object = AuctionObject(
                id=uuid.uuid4(),
                parcel_number="1234",
                estimated_value=Decimal("500000.00"),
                description="Test property",
                property_type="House",
                municipality="Zurich",
                canton="ZH",
                latitude=Decimal("47.3769"),
                longitude=Decimal("8.5417"),
                auction_id=auction.id
            )
            db.add(auction_object)
            
            # Create debtor
            debtor = Debtor(
                id=uuid.uuid4(),
                debtor_type=DebtorType.PERSON,
                name="Smith",
                prename="John",
                publication_id=publication.id
            )
            db.add(debtor)
            
            # Create contact
            contact = Contact(
                id=uuid.uuid4(),
                name="Test Office",
                contact_type="office",
                publication_id=publication.id
            )
            db.add(contact)
            
            await db.commit()
            
            return {
                "publication_id": publication.id,
                "auction_id": auction.id,
                "auction_object_id": auction_object.id,
                "debtor_id": debtor.id,
                "contact_id": contact.id
            }
    
    def test_list_auctions_basic(self, client, sample_data):
        """Test listing auctions with basic information."""
        response = client.get("/api/v1/auctions/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        if data["items"]:
            auction = data["items"][0]
            assert "id" in auction
            assert "date" in auction
            assert "location" in auction
            assert "auction_objects" in auction
            
            # Should only have basic auction object info
            if auction["auction_objects"]:
                obj = auction["auction_objects"][0]
                assert "id" in obj
                assert "parcel_number" in obj
                assert "property_type" in obj
                # Should NOT have premium fields
                assert "estimated_value" not in obj
                assert "description" not in obj
    
    def test_get_auction_basic(self, client, sample_data):
        """Test getting basic auction information."""
        auction_id = sample_data["auction_id"]
        response = client.get(f"/api/v1/auctions/{auction_id}/basic")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(auction_id)
        assert data["date"] == "2025-10-15"
        assert data["location"] == "Test Location, Zurich"
        assert "auction_objects" in data
        
        # Should only have basic info
        if data["auction_objects"]:
            obj = data["auction_objects"][0]
            assert "parcel_number" in obj
            assert "estimated_value" not in obj  # Premium field
    
    def test_get_auction_full_without_subscription(self, client, sample_data):
        """Test getting full auction information without subscription."""
        auction_id = sample_data["auction_id"]
        response = client.get(f"/api/v1/auctions/{auction_id}/full")
        
        # Should require authentication/subscription
        assert response.status_code in [401, 402]  # Unauthorized or Payment Required
    
    def test_get_auction_full_with_subscription(self, client, sample_data):
        """Test getting full auction information with subscription."""
        auction_id = sample_data["auction_id"]
        user_id = uuid.uuid4()
        
        # First create a subscription
        subscription_data = {
            "auction_id": str(auction_id),
            "subscription_type": "premium",
            "payment_method": "test-payment",
            "amount": "15.00"
        }
        
        response = client.post(
            "/api/v1/subscriptions/purchase",
            json=subscription_data,
            headers={"X-User-ID": str(user_id)}
        )
        
        assert response.status_code == 200
        
        # Now try to get full auction details
        response = client.get(
            f"/api/v1/auctions/{auction_id}/full",
            headers={"X-User-ID": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(auction_id)
        assert "debtors" in data
        assert "contacts" in data
        assert "auction_objects" in data
        
        # Should have premium fields
        if data["auction_objects"]:
            obj = data["auction_objects"][0]
            assert "estimated_value" in obj  # Premium field
            assert "description" in obj  # Premium field
    
    def test_get_auctions_map_data(self, client, sample_data):
        """Test getting auction data for map visualization."""
        response = client.get("/api/v1/auctions/map/data")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        
        if data["items"]:
            item = data["items"][0]
            assert "id" in item
            assert "date" in item
            assert "location" in item
            assert "coordinates" in item
            assert "estimated_value" in item
    
    def test_subscription_purchase(self, client, sample_data):
        """Test subscription purchase."""
        auction_id = sample_data["auction_id"]
        user_id = uuid.uuid4()
        
        subscription_data = {
            "auction_id": str(auction_id),
            "subscription_type": "premium",
            "payment_method": "test-payment",
            "amount": "15.00"
        }
        
        response = client.post(
            "/api/v1/subscriptions/purchase",
            json=subscription_data,
            headers={"X-User-ID": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "subscription_id" in data
        assert "status" in data
        assert data["status"] == "completed"
    
    def test_get_pricing(self, client):
        """Test getting subscription pricing."""
        response = client.get("/api/v1/subscriptions/pricing")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "subscription_types" in data
        assert "basic" in data["subscription_types"]
        assert "premium" in data["subscription_types"]
        
        basic = data["subscription_types"]["basic"]
        assert basic["price"] == "5.00"
        assert basic["currency"] == "CHF"
        
        premium = data["subscription_types"]["premium"]
        assert premium["price"] == "15.00"
        assert premium["currency"] == "CHF"
    
    def test_analytics_endpoints(self, client, sample_data):
        """Test analytics endpoints."""
        auction_id = sample_data["auction_id"]
        user_id = uuid.uuid4()
        
        # Test view statistics
        response = client.get("/api/v1/analytics/view-statistics")
        assert response.status_code == 200
        
        # Test popular auctions
        response = client.get("/api/v1/analytics/popular-auctions")
        assert response.status_code == 200
        
        # Test auction view analytics (requires authentication)
        response = client.get(
            f"/api/v1/analytics/auction/{auction_id}/views",
            headers={"X-User-ID": str(user_id)}
        )
        assert response.status_code == 200
        
        # Test user view history
        response = client.get(
            "/api/v1/analytics/my-view-history",
            headers={"X-User-ID": str(user_id)}
        )
        assert response.status_code == 200


class TestDataValidation:
    """Test data validation and edge cases."""
    
    @pytest.mark.asyncio
    async def test_multilingual_title_validation(self):
        """Test multilingual title validation."""
        async with AsyncSessionLocal() as db:
            # Valid multilingual title
            publication = Publication(
                id=uuid.uuid4(),
                publication_date=date(2025, 9, 6),
                title={
                    "de": "Deutscher Titel",
                    "fr": "Titre français",
                    "it": "Titolo italiano",
                    "en": "English title"
                },
                language="de",
                canton="ZH"
            )
            
            db.add(publication)
            await db.commit()
            
            assert publication.title["de"] == "Deutscher Titel"
            assert publication.title["fr"] == "Titre français"
    
    @pytest.mark.asyncio
    async def test_enum_validation(self):
        """Test enum field validation."""
        async with AsyncSessionLocal() as db:
            # Test valid enum values
            debtor = Debtor(
                id=uuid.uuid4(),
                debtor_type=DebtorType.PERSON,  # Valid enum
                name="Test",
                publication_id=uuid.uuid4()
            )
            
            # This should not raise an error
            db.add(debtor)
            
            # Test invalid enum would raise error
            with pytest.raises(ValueError):
                invalid_debtor = Debtor(
                    id=uuid.uuid4(),
                    debtor_type="invalid_type",  # Invalid enum
                    name="Test",
                    publication_id=uuid.uuid4()
                )
    
    @pytest.mark.asyncio
    async def test_spatial_data_validation(self):
        """Test spatial data validation."""
        async with AsyncSessionLocal() as db:
            # Test valid coordinates
            auction_object = AuctionObject(
                id=uuid.uuid4(),
                latitude=Decimal("47.3769"),  # Valid latitude
                longitude=Decimal("8.5417"),   # Valid longitude
                auction_id=uuid.uuid4()
            )
            
            # Should not raise error
            db.add(auction_object)
            
            # Test invalid coordinates (out of range)
            with pytest.raises(Exception):  # Database constraint violation
                invalid_object = AuctionObject(
                    id=uuid.uuid4(),
                    latitude=Decimal("200.0"),  # Invalid latitude
                    longitude=Decimal("8.5417"),
                    auction_id=uuid.uuid4()
                )
                db.add(invalid_object)
                await db.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
