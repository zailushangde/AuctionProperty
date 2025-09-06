"""User subscription model for payment system."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class SubscriptionType(str, enum.Enum):
    """Subscription type enumeration."""
    BASIC = "basic"
    PREMIUM = "premium"


class UserSubscription(Base):
    """Model for user subscriptions to auction details."""
    
    __tablename__ = "user_subscriptions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # User information
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="External user ID (from auth system)"
    )
    
    # Auction reference
    auction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auctions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Subscription details
    subscription_type: Mapped[SubscriptionType] = mapped_column(
        Enum(SubscriptionType),
        nullable=False,
        default=SubscriptionType.BASIC
    )
    
    # Payment information
    purchase_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Payment tracking
    payment_id: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="External payment system ID"
    )
    amount_paid: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Amount paid in CHF"
    )
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    auction: Mapped["Auction"] = relationship(
        "Auction",
        foreign_keys=[auction_id]
    )
    
    def __repr__(self) -> str:
        return f"<UserSubscription(id={self.id}, user={self.user_id}, auction={self.auction_id}, type={self.subscription_type})>"
