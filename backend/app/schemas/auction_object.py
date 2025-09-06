"""Pydantic schemas for AuctionObject model."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
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


class AuctionObjectResponse(AuctionObjectBase):
    """Schema for AuctionObject response."""
    id: uuid.UUID
    auction_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
