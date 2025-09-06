"""Contact model for auction contacts."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Contact(Base):
    """Model for auction contacts (court officials, lawyers, etc.)."""
    
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
    title: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    fax: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Organization details
    organization: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    department: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Address
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
        back_populates="contacts"
    )
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.name}', type='{self.contact_type}')>"
