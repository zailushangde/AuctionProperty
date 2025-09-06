"""Pydantic schemas for AuctionView model."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.auction_view import ViewType


class AuctionViewBase(BaseModel):
    """Base schema for AuctionView."""
    auction_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    view_type: ViewType
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    referrer: Optional[str] = Field(None, max_length=500)
    session_id: Optional[str] = Field(None, max_length=200)


class AuctionViewCreate(AuctionViewBase):
    """Schema for creating an AuctionView."""
    pass


class AuctionViewResponse(AuctionViewBase):
    """Schema for AuctionView response."""
    id: uuid.UUID
    viewed_at: datetime
    created_at: str
    
    class Config:
        from_attributes = True


class ViewAnalytics(BaseModel):
    """Schema for view analytics."""
    auction_id: uuid.UUID
    total_views: int
    unique_users: int
    anonymous_views: int
    list_views: int
    detail_views: int
    map_views: int
    last_viewed: Optional[datetime] = None


class UserViewHistory(BaseModel):
    """Schema for user view history."""
    user_id: uuid.UUID
    auction_id: uuid.UUID
    view_type: ViewType
    viewed_at: datetime
    auction_date: datetime
    auction_location: str
