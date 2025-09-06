"""Debtor model for auction debtors."""

import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Debtor(Base):
    """Model for auction debtors."""
    
    __tablename__ = "debtors"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Personal information
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
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="CH"
    )
    
    # Additional info
    legal_form: Mapped[Optional[str]] = mapped_column(
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
        back_populates="debtors"
    )
    
    @property
    def full_name(self) -> str:
        """Get full name combining prename and name."""
        if self.prename:
            return f"{self.prename} {self.name}"
        return self.name
    
    def __repr__(self) -> str:
        return f"<Debtor(id={self.id}, name='{self.full_name}')>"
