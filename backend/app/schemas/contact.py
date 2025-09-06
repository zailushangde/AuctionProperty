"""Pydantic schemas for Contact model."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    """Base schema for Contact."""
    name: str = Field(..., max_length=200)
    title: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=200)
    fax: Optional[str] = Field(None, max_length=50)
    organization: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    contact_type: Optional[str] = Field(None, max_length=100)


class ContactCreate(ContactBase):
    """Schema for creating a Contact."""
    publication_id: uuid.UUID


class ContactResponse(ContactBase):
    """Schema for Contact response."""
    id: uuid.UUID
    publication_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
