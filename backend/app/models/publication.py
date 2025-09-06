"""Publication model for SHAB publications."""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Publication(Base):
    """Model for SHAB publications containing auction information."""
    
    __tablename__ = "publications"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # SHAB specific fields
    publication_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True
    )
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="de"
    )
    canton: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )
    registration_office: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    # Content
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
    
    # Relationships
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
        return f"<Publication(id={self.id}, title='{self.title[:50]}...', date={self.publication_date})>"
