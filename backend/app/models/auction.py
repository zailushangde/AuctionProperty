"""Auction model for auction events."""

import uuid
from datetime import datetime, time as dt_time
from typing import List, Optional
from sqlalchemy import String, DateTime, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Auction(Base):
    """Model for auction events."""
    
    __tablename__ = "auctions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Auction details
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    time: Mapped[Optional[dt_time]] = mapped_column(
        Time,
        nullable=True
    )
    location: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    # Additional auction info
    auction_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    court: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Foreign key to publication
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publications.id", ondelete="CASCADE"),
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
    publication: Mapped["Publication"] = relationship(
        "Publication",
        back_populates="auctions"
    )
    auction_objects: Mapped[List["AuctionObject"]] = relationship(
        "AuctionObject",
        back_populates="auction",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Auction(id={self.id}, date={self.date}, location='{self.location[:30]}...')>"
