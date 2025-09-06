"""Pydantic schemas for Publication model."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PublicationBase(BaseModel):
    """Base schema for Publication."""
    publication_date: datetime
    title: str = Field(..., max_length=500)
    language: str = Field(default="de", max_length=10)
    canton: str = Field(..., max_length=10)
    registration_office: str = Field(..., max_length=200)
    content: Optional[str] = None


class PublicationCreate(PublicationBase):
    """Schema for creating a Publication."""
    pass


class PublicationResponse(PublicationBase):
    """Schema for Publication response."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PublicationList(BaseModel):
    """Schema for paginated Publication list."""
    items: List[PublicationResponse]
    total: int
    page: int
    size: int
    pages: int
