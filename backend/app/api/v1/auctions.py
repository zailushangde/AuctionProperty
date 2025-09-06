"""Auction API endpoints."""

from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.database import get_db
from app.models import Auction, Publication, AuctionObject
from app.schemas.auction import AuctionResponse, AuctionList
from app.api.dependencies import PaginationParams, get_total_count

router = APIRouter(prefix="/auctions", tags=["auctions"])


@router.get("/", response_model=AuctionList)
async def list_auctions(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    date_from: Optional[date] = Query(None, description="Filter auctions from this date"),
    date_to: Optional[date] = Query(None, description="Filter auctions to this date"),
    canton: Optional[str] = Query(None, description="Filter by canton"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    search: Optional[str] = Query(None, description="Search in auction details")
):
    """List auctions with filtering and pagination."""
    
    # Build query
    query = select(Auction).join(Publication)
    
    # Apply filters
    filters = []
    
    if date_from:
        filters.append(Auction.date >= date_from)
    
    if date_to:
        filters.append(Auction.date <= date_to)
    
    if canton:
        filters.append(Publication.canton == canton.upper())
    
    if location:
        filters.append(Auction.location.ilike(f"%{location}%"))
    
    if search:
        search_filter = or_(
            Auction.location.ilike(f"%{search}%"),
            Auction.court.ilike(f"%{search}%"),
            Publication.title.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by date (upcoming first)
    query = query.order_by(desc(Auction.date))
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    auctions = result.scalars().all()
    
    # Get total count
    total = await get_total_count(
        Auction,
        db,
        **{k: v for k, v in {
            'date_from': date_from,
            'date_to': date_to,
            'canton': canton,
            'location': location
        }.items() if v is not None}
    )
    
    # Calculate pages
    pages = (total + pagination.size - 1) // pagination.size
    
    return AuctionList(
        items=auctions,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(
    auction_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed auction information."""
    
    # Get auction with related data
    result = await db.execute(
        select(Auction)
        .where(Auction.id == auction_id)
        .options(
            # Load related objects
            selectinload(Auction.auction_objects),
            selectinload(Auction.publication)
        )
    )
    auction = result.scalar_one_or_none()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    return auction


@router.get("/upcoming/", response_model=AuctionList)
async def get_upcoming_auctions(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to look for upcoming auctions")
):
    """Get upcoming auctions within specified days."""
    
    from datetime import timedelta
    today = date.today()
    future_date = today + timedelta(days=days_ahead)
    
    query = (
        select(Auction)
        .join(Publication)
        .where(
            and_(
                Auction.date >= today,
                Auction.date <= future_date
            )
        )
        .order_by(Auction.date)
        .offset(pagination.offset)
        .limit(pagination.size)
    )
    
    result = await db.execute(query)
    auctions = result.scalars().all()
    
    # Get total count for upcoming auctions
    count_query = select(func.count(Auction.id)).where(
        and_(
            Auction.date >= today,
            Auction.date <= future_date
        )
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    pages = (total + pagination.size - 1) // pagination.size
    
    return AuctionList(
        items=auctions,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )


@router.get("/statistics/")
async def get_auction_statistics(
    db: AsyncSession = Depends(get_db),
    canton: Optional[str] = Query(None, description="Filter by canton")
):
    """Get auction statistics."""
    
    # Base query
    base_query = select(Auction).join(Publication)
    if canton:
        base_query = base_query.where(Publication.canton == canton.upper())
    
    # Total auctions
    total_result = await db.execute(select(func.count(Auction.id)))
    total_auctions = total_result.scalar()
    
    # Upcoming auctions (next 30 days)
    from datetime import timedelta
    today = date.today()
    upcoming_date = today + timedelta(days=30)
    
    upcoming_query = base_query.where(
        and_(
            Auction.date >= today,
            Auction.date <= upcoming_date
        )
    )
    upcoming_result = await db.execute(select(func.count(Auction.id)).select_from(upcoming_query.subquery()))
    upcoming_auctions = upcoming_result.scalar()
    
    # Auctions by canton
    canton_query = (
        select(Publication.canton, func.count(Auction.id))
        .join(Auction)
        .group_by(Publication.canton)
        .order_by(func.count(Auction.id).desc())
    )
    canton_result = await db.execute(canton_query)
    auctions_by_canton = {row[0]: row[1] for row in canton_result.fetchall()}
    
    # Average estimated value
    value_query = (
        select(func.avg(AuctionObject.estimated_value))
        .join(Auction)
        .where(AuctionObject.estimated_value.isnot(None))
    )
    if canton:
        value_query = value_query.join(Publication).where(Publication.canton == canton.upper())
    
    value_result = await db.execute(value_query)
    avg_estimated_value = value_result.scalar()
    
    return {
        "total_auctions": total_auctions,
        "upcoming_auctions": upcoming_auctions,
        "auctions_by_canton": auctions_by_canton,
        "average_estimated_value": float(avg_estimated_value) if avg_estimated_value else None,
        "currency": "CHF"
    }
