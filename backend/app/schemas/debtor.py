"""Pydantic schemas for Debtor model (Premium Content)."""

import uuid
from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.debtor import DebtorType


class DebtorBase(BaseModel):
    """Base schema for Debtor."""
    debtor_type: DebtorType
    name: str = Field(..., max_length=200)
    prename: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    country_of_origin: Optional[Dict[str, Any]] = None
    residence_type: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    legal_form: Optional[str] = Field(None, max_length=100)


class DebtorCreate(DebtorBase):
    """Schema for creating a Debtor."""
    publication_id: uuid.UUID


class DebtorResponse(DebtorBase):
    """Schema for Debtor response (Premium content)."""
    id: uuid.UUID
    publication_id: uuid.UUID
    created_at: str
    updated_at: str
    full_name: str
    
    class Config:
        from_attributes = True
