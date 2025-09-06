"""Pydantic schemas for AuctionObject model (Premium Content)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AuctionObjectBase(BaseModel):
    """Base schema for AuctionObject."""
    parcel_number: Optional[str] = Field(None, max_length=100)
    property_number: Optional[str] = Field(None, max_length=100)
    surface_area: Optional[Decimal] = None
    estimated_value: Optional[Decimal] = None
    currency: str = Field("CHF", max_length=3)
    description: Optional[str] = None
    property_type: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    municipality: Optional[str] = Field(None, max_length=100)
    canton: Optional[str] = Field(None, max_length=10)
    remarks: Optional[str] = None


class AuctionObjectCreate(AuctionObjectBase):
    """Schema for creating an AuctionObject."""
    auction_id: uuid.UUID
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class AuctionObjectBasicResponse(BaseModel):
    """Schema for basic AuctionObject response (Free content)."""
    id: uuid.UUID
    parcel_number: Optional[str] = None
    property_type: Optional[str] = None
    municipality: Optional[str] = None
    canton: Optional[str] = None
    
    class Config:
        from_attributes = True


class AuctionObjectResponse(AuctionObjectBase):
    """Schema for full AuctionObject response (Premium content)."""
    id: uuid.UUID
    auction_id: uuid.UUID
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    coordinates: Optional[Dict[str, float]] = None  # {lat: float, lng: float}
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AuctionObjectMapResponse(BaseModel):
    """Schema for AuctionObject map response."""
    id: uuid.UUID
    parcel_number: Optional[str] = None
    property_type: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    currency: str = "CHF"
    coordinates: Optional[Dict[str, float]] = None  # {lat: float, lng: float}
    municipality: Optional[str] = None
    canton: Optional[str] = None
    
    class Config:
        from_attributes = True
