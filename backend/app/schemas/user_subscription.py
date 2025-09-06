"""Pydantic schemas for UserSubscription model."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.user_subscription import SubscriptionType


class UserSubscriptionBase(BaseModel):
    """Base schema for UserSubscription."""
    user_id: uuid.UUID
    auction_id: uuid.UUID
    subscription_type: SubscriptionType
    expires_at: Optional[datetime] = None
    is_active: bool = True
    payment_id: Optional[str] = Field(None, max_length=200)
    amount_paid: Optional[str] = Field(None, max_length=20)


class UserSubscriptionCreate(UserSubscriptionBase):
    """Schema for creating a UserSubscription."""
    pass


class UserSubscriptionResponse(UserSubscriptionBase):
    """Schema for UserSubscription response."""
    id: uuid.UUID
    purchase_date: datetime
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class SubscriptionPurchaseRequest(BaseModel):
    """Schema for subscription purchase request."""
    auction_id: uuid.UUID
    subscription_type: SubscriptionType
    payment_method: str = Field(..., description="Payment method identifier")
    amount: str = Field(..., description="Amount to pay in CHF")


class SubscriptionPurchaseResponse(BaseModel):
    """Schema for subscription purchase response."""
    subscription_id: uuid.UUID
    payment_url: Optional[str] = None
    payment_id: Optional[str] = None
    status: str = Field(..., description="Payment status")
    message: str = Field(..., description="Response message")
