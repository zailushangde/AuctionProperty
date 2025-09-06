"""Debtor model for auction debtors (Premium Content)."""

import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any
from sqlalchemy import String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class DebtorType(str, enum.Enum):
    """Debtor type enumeration."""
    PERSON = "person"
    COMPANY = "company"


class Debtor(Base):
    """Model for auction debtors (Premium Content)."""
    
    __tablename__ = "debtors"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Debtor type
    debtor_type: Mapped[DebtorType] = mapped_column(
        Enum(DebtorType),
        nullable=False,
        index=True
    )
    
    # Personal/Company information
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    prename: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )
    
    # Country of origin (for persons)
    country_of_origin: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Country information: {name: {de: 'Deutschland', fr: 'Allemagne'}, isoCode: 'DE'}"
    )
    
    # Residence information
    residence_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="e.g., 'switzerland', 'abroad'"
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
    
    # Company-specific fields
    legal_form: Mapped[Optional[str]] = mapped_column(
        String(100),
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
        back_populates="debtors"
    )
    
    @property
    def full_name(self) -> str:
        """Get full name combining prename and name."""
        if self.prename:
            return f"{self.prename} {self.name}"
        return self.name
    
    def __repr__(self) -> str:
        return f"<Debtor(id={self.id}, type={self.debtor_type}, name='{self.full_name}')>"
