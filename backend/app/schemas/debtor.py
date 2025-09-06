"""Pydantic schemas for Debtor model."""

import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class DebtorBase(BaseModel):
    """Base schema for Debtor."""
    name: str = Field(..., max_length=200)
    prename: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field("CH", max_length=100)
    legal_form: Optional[str] = Field(None, max_length=100)


class DebtorCreate(DebtorBase):
    """Schema for creating a Debtor."""
    publication_id: uuid.UUID


class DebtorResponse(DebtorBase):
    """Schema for Debtor response."""
    id: uuid.UUID
    publication_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    full_name: str
    
    class Config:
        from_attributes = True
