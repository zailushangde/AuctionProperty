"""AuctionObject model for auction objects/properties."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AuctionObject(Base):
    """Model for auction objects (properties, parcels, etc.)."""
    
    __tablename__ = "auction_objects"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Property identification
    parcel_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    property_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    # Property details
    surface_area: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    estimated_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="CHF"
    )
    
    # Description and details
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    property_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Location details
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    municipality: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    canton: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )
    
    # Additional information
    remarks: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Foreign key to auction
    auction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auctions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
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
        back_populates="auction_objects"
    )
    
    def __repr__(self) -> str:
        return f"<AuctionObject(id={self.id}, parcel='{self.parcel_number}', value={self.estimated_value})>"
