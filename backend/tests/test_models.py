"""Tests for database models."""

import pytest
from datetime import datetime, date, time
from decimal import Decimal
from app.models import Publication, Auction, Debtor, AuctionObject, Contact


def test_publication_model():
    """Test Publication model creation."""
    pub = Publication(
        publication_date=datetime.now(),
        title="Test Publication",
        language="de",
        canton="ZH",
        registration_office="Test Office"
    )
    
    assert pub.title == "Test Publication"
    assert pub.canton == "ZH"
    assert pub.language == "de"


def test_auction_model():
    """Test Auction model creation."""
    auction = Auction(
        date=datetime.now(),
        location="Test Location",
        auction_type="Zwangsversteigerung"
    )
    
    assert auction.location == "Test Location"
    assert auction.auction_type == "Zwangsversteigerung"


def test_debtor_model():
    """Test Debtor model creation."""
    debtor = Debtor(
        name="Mustermann",
        prename="Max",
        date_of_birth=date(1980, 1, 1)
    )
    
    assert debtor.name == "Mustermann"
    assert debtor.prename == "Max"
    assert debtor.full_name == "Max Mustermann"


def test_auction_object_model():
    """Test AuctionObject model creation."""
    obj = AuctionObject(
        parcel_number="123",
        estimated_value=Decimal("500000.00"),
        surface_area=Decimal("100.50")
    )
    
    assert obj.parcel_number == "123"
    assert obj.estimated_value == Decimal("500000.00")
    assert obj.surface_area == Decimal("100.50")


def test_contact_model():
    """Test Contact model creation."""
    contact = Contact(
        name="Test Contact",
        phone="+41 44 123 45 67",
        email="test@example.com"
    )
    
    assert contact.name == "Test Contact"
    assert contact.phone == "+41 44 123 45 67"
    assert contact.email == "test@example.com"
