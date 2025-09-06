"""Publication model for SHAB publications (Internal Reference Only)."""

import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import String, DateTime, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Publication(Base):
    """Model for SHAB publications (Internal Reference Only - Not exposed to frontend)."""
    
    __tablename__ = "publications"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # SHAB specific fields
    publication_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )
    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True
    )
    title: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Multilingual titles: {de: 'German', fr: 'French', it: 'Italian', en: 'English'}"
    )
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="de",
        index=True
    )
    canton: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )
    
    # Content (for internal processing)
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
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
    
    # Relationships (Internal only - not exposed to frontend)
    auctions: Mapped[List["Auction"]] = relationship(
        "Auction",
        back_populates="publication",
        cascade="all, delete-orphan"
    )
    debtors: Mapped[List["Debtor"]] = relationship(
        "Debtor",
        back_populates="publication",
        cascade="all, delete-orphan"
    )
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact",
        back_populates="publication",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        title_preview = self.title.get('de', 'No title')[:50] if isinstance(self.title, dict) else str(self.title)[:50]
        return f"<Publication(id={self.id}, title='{title_preview}...', date={self.publication_date})>"
