"""Auction model for auction events (Main Frontend Entity)."""

import uuid
from datetime import datetime, date, time as dt_time
from typing import List, Optional, Dict, Any
from sqlalchemy import String, DateTime, Date, Time, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Auction(Base):
    """Model for auction events (Main Frontend Entity)."""
    
    __tablename__ = "auctions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Auction details
    date: Mapped[date] = mapped_column(
        Date,
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
    
    # Circulation and Registration deadlines
    circulation_entry_deadline: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True
    )
    circulation_comment_deadline: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    registration_entry_deadline: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True
    )
    registration_comment_deadline: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Foreign key to publication (Internal reference only)
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
