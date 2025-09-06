"""Pydantic schemas for Auction model (Main Frontend Entity)."""

import uuid
from datetime import date, time as dt_time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .auction_object import AuctionObjectResponse, AuctionObjectBasicResponse
from .debtor import DebtorResponse
from .contact import ContactResponse


class AuctionBase(BaseModel):
    """Base schema for Auction."""
    date: date
    time: Optional[dt_time] = None
    location: str = Field(..., max_length=500)
    circulation_entry_deadline: Optional[date] = None
    circulation_comment_deadline: Optional[str] = None
    registration_entry_deadline: Optional[date] = None
    registration_comment_deadline: Optional[str] = None


class AuctionCreate(AuctionBase):
    """Schema for creating an Auction."""
    publication_id: uuid.UUID


class AuctionBasicResponse(AuctionBase):
    """Schema for basic Auction response (Free content)."""
    id: uuid.UUID
    created_at: str
    updated_at: str
    auction_objects: List[AuctionObjectBasicResponse] = []
    
    class Config:
        from_attributes = True


class AuctionFullResponse(AuctionBase):
    """Schema for full Auction response (Premium content)."""
    id: uuid.UUID
    created_at: str
    updated_at: str
    auction_objects: List[AuctionObjectResponse] = []
    debtors: List[DebtorResponse] = []
    contacts: List[ContactResponse] = []
    
    class Config:
        from_attributes = True


class AuctionMapResponse(BaseModel):
    """Schema for Auction map response."""
    id: uuid.UUID
    date: date
    time: Optional[dt_time] = None
    location: str
    coordinates: Optional[Dict[str, float]] = None  # {lat: float, lng: float}
    estimated_value: Optional[float] = None
    currency: str = "CHF"
    
    class Config:
        from_attributes = True


class AuctionList(BaseModel):
    """Schema for paginated Auction list."""
    items: List[AuctionBasicResponse]
    total: int
    page: int
    size: int
    pages: int


class AuctionMapList(BaseModel):
    """Schema for Auction map data."""
    items: List[AuctionMapResponse]
    total: int
