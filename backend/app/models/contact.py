"""Contact model for auction contacts (Premium Content)."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Contact(Base):
    """Model for auction contacts (Premium Content)."""
    
    __tablename__ = "contacts"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Contact information
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Address information
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    postal_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Contact type/role
    contact_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="e.g., 'office', 'lawyer', 'court'"
    )
    
    # Office-specific fields
    office_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    contains_post_office_box: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )
    
    # Post office box information
    post_office_box: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Post office box details: {number: '123', zipCode: '1000', town: 'Bern'}"
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
        back_populates="contacts"
    )
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.name}', type='{self.contact_type}')>"
