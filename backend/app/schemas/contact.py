"""Pydantic schemas for Contact model (Premium Content)."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    """Base schema for Contact."""
    name: str = Field(..., max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    contact_type: Optional[str] = Field(None, max_length=100)
    office_id: Optional[str] = Field(None, max_length=100)
    contains_post_office_box: Optional[bool] = None
    post_office_box: Optional[Dict[str, Any]] = None


class ContactCreate(ContactBase):
    """Schema for creating a Contact."""
    publication_id: uuid.UUID


class ContactResponse(ContactBase):
    """Schema for Contact response (Premium content)."""
    id: uuid.UUID
    publication_id: uuid.UUID
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
