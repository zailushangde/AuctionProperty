"""Auction view model for analytics and tracking."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ViewType(str, enum.Enum):
    """View type enumeration."""
    LIST = "list"
    DETAIL = "detail"
    MAP = "map"


class AuctionView(Base):
    """Model for tracking auction views and analytics."""
    
    __tablename__ = "auction_views"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Auction reference
    auction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auctions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # User information (optional for anonymous users)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="User ID if logged in, null for anonymous"
    )
    
    # View details
    view_type: Mapped[ViewType] = mapped_column(
        Enum(ViewType),
        nullable=False,
        index=True
    )
    
    # Tracking information
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IPv4 or IPv6 address"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    referrer: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Session information
    session_id: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        index=True
    )
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    auction: Mapped["Auction"] = relationship(
        "Auction",
        foreign_keys=[auction_id]
    )
    
    def __repr__(self) -> str:
        return f"<AuctionView(id={self.id}, auction={self.auction_id}, type={self.view_type}, user={self.user_id})>"
