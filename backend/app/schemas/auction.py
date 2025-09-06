"""Pydantic schemas for Auction model."""

import uuid
from datetime import datetime, time as dt_time
from typing import List, Optional
from pydantic import BaseModel, Field

from .auction_object import AuctionObjectResponse


class AuctionBase(BaseModel):
    """Base schema for Auction."""
    date: datetime
    time: Optional[dt_time] = None
    location: str = Field(..., max_length=500)
    auction_type: Optional[str] = Field(None, max_length=100)
    court: Optional[str] = Field(None, max_length=200)


class AuctionCreate(AuctionBase):
    """Schema for creating an Auction."""
    publication_id: uuid.UUID


class AuctionResponse(AuctionBase):
    """Schema for Auction response."""
    id: uuid.UUID
    publication_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    auction_objects: List[AuctionObjectResponse] = []
    
    class Config:
        from_attributes = True


class AuctionList(BaseModel):
    """Schema for paginated Auction list."""
    items: List[AuctionResponse]
    total: int
    page: int
    size: int
    pages: int
