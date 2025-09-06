"""API dependencies for database and authentication."""

import uuid
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import Depends, HTTPException, Query, Header
from app.database import get_db
from app.models import Publication, Auction, AuctionObject


async def get_publication_by_id(
    publication_id: str,
    db: AsyncSession = Depends(get_db)
) -> Publication:
    """Get publication by ID or raise 404."""
    result = await db.execute(
        select(Publication).where(Publication.id == publication_id)
    )
    publication = result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    return publication


async def get_auction_by_id(
    auction_id: str,
    db: AsyncSession = Depends(get_db)
) -> Auction:
    """Get auction by ID or raise 404."""
    result = await db.execute(
        select(Auction).where(Auction.id == auction_id)
    )
    auction = result.scalar_one_or_none()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    return auction


async def get_auction_object_by_parcel(
    parcel_number: str,
    db: AsyncSession = Depends(get_db)
) -> AuctionObject:
    """Get auction object by parcel number or raise 404."""
    result = await db.execute(
        select(AuctionObject).where(AuctionObject.parcel_number == parcel_number)
    )
    auction_object = result.scalar_one_or_none()
    
    if not auction_object:
        raise HTTPException(status_code=404, detail="Auction object not found")
    
    return auction_object


class PaginationParams:
    """Pagination parameters."""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Page size")
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size


async def get_total_count(
    model_class,
    db: AsyncSession,
    **filters
) -> int:
    """Get total count for pagination."""
    query = select(func.count(model_class.id))
    
    for field, value in filters.items():
        if hasattr(model_class, field) and value is not None:
            query = query.where(getattr(model_class, field) == value)
    
    result = await db.execute(query)
    return result.scalar()


async def get_current_user_id(
    x_user_id: Optional[str] = Header(None, description="User ID from authentication system")
) -> Optional[uuid.UUID]:
    """Get current user ID from headers (simplified authentication)."""
    if not x_user_id:
        return None
    
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


async def require_authentication(
    user_id: Optional[uuid.UUID] = Depends(get_current_user_id)
) -> uuid.UUID:
    """Require user to be authenticated."""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id
