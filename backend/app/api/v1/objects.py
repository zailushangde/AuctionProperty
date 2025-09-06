"""Auction Object API endpoints."""

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_db
from app.models import AuctionObject, Auction, Publication
from app.schemas.auction_object import AuctionObjectResponse
from app.api.dependencies import PaginationParams, get_total_count

router = APIRouter(prefix="/objects", tags=["objects"])


@router.get("/", response_model=List[AuctionObjectResponse])
async def list_auction_objects(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    canton: Optional[str] = Query(None, description="Filter by canton"),
    municipality: Optional[str] = Query(None, description="Filter by municipality"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    min_value: Optional[Decimal] = Query(None, description="Minimum estimated value"),
    max_value: Optional[Decimal] = Query(None, description="Maximum estimated value"),
    search: Optional[str] = Query(None, description="Search in description and address")
):
    """List auction objects with filtering and pagination."""
    
    # Build query
    query = (
        select(AuctionObject)
        .join(Auction)
        .join(Publication)
    )
    
    # Apply filters
    filters = []
    
    if canton:
        filters.append(Publication.canton == canton.upper())
    
    if municipality:
        filters.append(AuctionObject.municipality.ilike(f"%{municipality}%"))
    
    if property_type:
        filters.append(AuctionObject.property_type.ilike(f"%{property_type}%"))
    
    if min_value:
        filters.append(AuctionObject.estimated_value >= min_value)
    
    if max_value:
        filters.append(AuctionObject.estimated_value <= max_value)
    
    if search:
        search_filter = or_(
            AuctionObject.description.ilike(f"%{search}%"),
            AuctionObject.address.ilike(f"%{search}%"),
            AuctionObject.parcel_number.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by estimated value (highest first)
    query = query.order_by(desc(AuctionObject.estimated_value))
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    objects = result.scalars().all()
    
    return objects


@router.get("/{parcel_number}", response_model=AuctionObjectResponse)
async def get_auction_object_by_parcel(
    parcel_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get auction object by parcel number."""
    
    result = await db.execute(
        select(AuctionObject)
        .where(AuctionObject.parcel_number == parcel_number)
        .options(
            selectinload(AuctionObject.auction).selectinload(Auction.publication)
        )
    )
    auction_object = result.scalar_one_or_none()
    
    if not auction_object:
        raise HTTPException(status_code=404, detail="Auction object not found")
    
    return auction_object


@router.get("/property/{property_number}", response_model=AuctionObjectResponse)
async def get_auction_object_by_property(
    property_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get auction object by property number."""
    
    result = await db.execute(
        select(AuctionObject)
        .where(AuctionObject.property_number == property_number)
        .options(
            selectinload(AuctionObject.auction).selectinload(Auction.publication)
        )
    )
    auction_object = result.scalar_one_or_none()
    
    if not auction_object:
        raise HTTPException(status_code=404, detail="Auction object not found")
    
    return auction_object


@router.get("/search/parcel/", response_model=List[AuctionObjectResponse])
async def search_parcels(
    query: str = Query(..., description="Search term for parcel numbers"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """Search for parcels by partial parcel number match."""
    
    result = await db.execute(
        select(AuctionObject)
        .where(AuctionObject.parcel_number.ilike(f"%{query}%"))
        .options(
            selectinload(AuctionObject.auction).selectinload(Auction.publication)
        )
        .limit(limit)
    )
    objects = result.scalars().all()
    
    return objects


@router.get("/statistics/")
async def get_object_statistics(
    db: AsyncSession = Depends(get_db),
    canton: Optional[str] = Query(None, description="Filter by canton")
):
    """Get auction object statistics."""
    
    # Base query
    base_query = (
        select(AuctionObject)
        .join(Auction)
        .join(Publication)
    )
    if canton:
        base_query = base_query.where(Publication.canton == canton.upper())
    
    # Total objects
    total_result = await db.execute(select(func.count(AuctionObject.id)))
    total_objects = total_result.scalar()
    
    # Objects with estimated values
    value_result = await db.execute(
        select(func.count(AuctionObject.id))
        .where(AuctionObject.estimated_value.isnot(None))
    )
    objects_with_value = value_result.scalar()
    
    # Average estimated value
    avg_value_result = await db.execute(
        select(func.avg(AuctionObject.estimated_value))
        .where(AuctionObject.estimated_value.isnot(None))
    )
    avg_estimated_value = avg_value_result.scalar()
    
    # Total estimated value
    total_value_result = await db.execute(
        select(func.sum(AuctionObject.estimated_value))
        .where(AuctionObject.estimated_value.isnot(None))
    )
    total_estimated_value = total_value_result.scalar()
    
    # Objects by property type
    type_query = (
        select(AuctionObject.property_type, func.count(AuctionObject.id))
        .where(AuctionObject.property_type.isnot(None))
        .group_by(AuctionObject.property_type)
        .order_by(func.count(AuctionObject.id).desc())
    )
    type_result = await db.execute(type_query)
    objects_by_type = {row[0]: row[1] for row in type_result.fetchall()}
    
    # Objects by canton
    canton_query = (
        select(Publication.canton, func.count(AuctionObject.id))
        .join(Auction)
        .join(AuctionObject)
        .group_by(Publication.canton)
        .order_by(func.count(AuctionObject.id).desc())
    )
    canton_result = await db.execute(canton_query)
    objects_by_canton = {row[0]: row[1] for row in canton_result.fetchall()}
    
    return {
        "total_objects": total_objects,
        "objects_with_estimated_value": objects_with_value,
        "average_estimated_value": float(avg_estimated_value) if avg_estimated_value else None,
        "total_estimated_value": float(total_estimated_value) if total_estimated_value else None,
        "currency": "CHF",
        "objects_by_property_type": objects_by_type,
        "objects_by_canton": objects_by_canton
    }
