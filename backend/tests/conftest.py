"""Test configuration and fixtures."""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(test_db):
    """Create test client with database dependency override."""
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_publication(test_db):
    """Create a sample publication for testing."""
    from app.models import Publication
    import uuid
    
    publication = Publication(
        id=uuid.uuid4(),
        publication_date="2025-09-06",
        expiration_date="2026-09-06",
        title={
            "de": "Test Publication",
            "fr": "Publication Test",
            "en": "Test Publication"
        },
        language="de",
        canton="ZH",
        content="Test content"
    )
    
    test_db.add(publication)
    await test_db.commit()
    await test_db.refresh(publication)
    
    return publication


@pytest.fixture
async def sample_auction(test_db, sample_publication):
    """Create a sample auction for testing."""
    from app.models import Auction
    import uuid
    
    auction = Auction(
        id=uuid.uuid4(),
        date="2025-10-15",
        time="14:30:00",
        location="Test Location, Zurich",
        circulation_entry_deadline="2025-09-25",
        registration_entry_deadline="2025-10-05",
        publication_id=sample_publication.id
    )
    
    test_db.add(auction)
    await test_db.commit()
    await test_db.refresh(auction)
    
    return auction


@pytest.fixture
async def sample_auction_object(test_db, sample_auction):
    """Create a sample auction object for testing."""
    from app.models import AuctionObject
    import uuid
    from decimal import Decimal
    
    auction_object = AuctionObject(
        id=uuid.uuid4(),
        parcel_number="1234",
        estimated_value=Decimal("500000.00"),
        description="Test property description",
        property_type="House",
        address="Test Street 123",
        municipality="Zurich",
        canton="ZH",
        latitude=Decimal("47.3769"),
        longitude=Decimal("8.5417"),
        auction_id=sample_auction.id
    )
    
    test_db.add(auction_object)
    await test_db.commit()
    await test_db.refresh(auction_object)
    
    return auction_object


@pytest.fixture
async def sample_debtor(test_db, sample_publication):
    """Create a sample debtor for testing."""
    from app.models import Debtor, DebtorType
    import uuid
    
    debtor = Debtor(
        id=uuid.uuid4(),
        debtor_type=DebtorType.PERSON,
        name="Smith",
        prename="John",
        date_of_birth="1980-05-15",
        country_of_origin={
            "name": {"de": "Deutschland", "en": "Germany"},
            "isoCode": "DE"
        },
        residence_type="switzerland",
        address="Test Street 123",
        city="Test City",
        postal_code="8001",
        publication_id=sample_publication.id
    )
    
    test_db.add(debtor)
    await test_db.commit()
    await test_db.refresh(debtor)
    
    return debtor


@pytest.fixture
async def sample_contact(test_db, sample_publication):
    """Create a sample contact for testing."""
    from app.models import Contact
    import uuid
    
    contact = Contact(
        id=uuid.uuid4(),
        name="Test Office",
        phone="+41 44 123 45 67",
        email="test@office.ch",
        address="Office Street 456",
        city="Office City",
        postal_code="8002",
        contact_type="office",
        office_id="office-123",
        contains_post_office_box=False,
        publication_id=sample_publication.id
    )
    
    test_db.add(contact)
    await test_db.commit()
    await test_db.refresh(contact)
    
    return contact


@pytest.fixture
async def sample_subscription(test_db, sample_auction):
    """Create a sample user subscription for testing."""
    from app.models import UserSubscription, SubscriptionType
    import uuid
    
    subscription = UserSubscription(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        auction_id=sample_auction.id,
        subscription_type=SubscriptionType.PREMIUM,
        payment_id="payment-123",
        amount_paid="15.00",
        is_active=True
    )
    
    test_db.add(subscription)
    await test_db.commit()
    await test_db.refresh(subscription)
    
    return subscription


@pytest.fixture
async def sample_auction_view(test_db, sample_auction):
    """Create a sample auction view for testing."""
    from app.models import AuctionView, ViewType
    import uuid
    
    view = AuctionView(
        id=uuid.uuid4(),
        auction_id=sample_auction.id,
        user_id=uuid.uuid4(),
        view_type=ViewType.DETAIL,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0...",
        session_id="session-123"
    )
    
    test_db.add(view)
    await test_db.commit()
    await test_db.refresh(view)
    
    return view
