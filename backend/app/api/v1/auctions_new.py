"""New Auction API endpoints with payment system and map support."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Auction, AuctionObject, Debtor, Contact, UserSubscription, AuctionView
from app.schemas import (
    AuctionBasicResponse, AuctionFullResponse, AuctionMapResponse,
    AuctionList, AuctionMapList, AuctionViewCreate
)
from app.models import ViewType
from app.api.dependencies import get_current_user_id

router = APIRouter()


@router.get("/", response_model=AuctionList)
async def list_auctions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    canton: Optional[str] = Query(None, description="Filter by canton"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    sort_by: str = Query("date", description="Sort by: date, created_at"),
    sort_order: str = Query("asc", description="Sort order: asc, desc"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """List auctions with basic information (Free content)."""
    
    # Build query
    query = select(Auction).options(
        selectinload(Auction.auction_objects)
    )
    
    # Apply filters
    if canton:
        query = query.join(Auction.publication).where(
            Auction.publication.has(canton=canton)
        )
    
    if date_from:
        query = query.where(Auction.date >= date_from)
    
    if date_to:
        query = query.where(Auction.date <= date_to)
    
    # Apply sorting
    if sort_by == "date":
        order_column = Auction.date
    elif sort_by == "created_at":
        order_column = Auction.created_at
    else:
        order_column = Auction.date
    
    if sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    # Get total count
    count_query = select(func.count(Auction.id))
    if canton:
        count_query = count_query.join(Auction.publication).where(
            Auction.publication.has(canton=canton)
        )
    if date_from:
        count_query = count_query.where(Auction.date >= date_from)
    if date_to:
        count_query = count_query.where(Auction.date <= date_to)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Execute query
    result = await db.execute(query)
    auctions = result.scalars().all()
    
    # Track view
    if request:
        await track_auction_view(
            auction_id=None,  # We'll track individual views
            view_type=ViewType.LIST,
            request=request,
            db=db
        )
    
    # Convert to response format
    auction_responses = []
    for auction in auctions:
        # Only include basic auction object info
        basic_objects = []
        for obj in auction.auction_objects:
            basic_objects.append({
                "id": obj.id,
                "parcel_number": obj.parcel_number,
                "property_type": obj.property_type,
                "municipality": obj.municipality,
                "canton": obj.canton
            })
        
        auction_responses.append(AuctionBasicResponse(
            id=auction.id,
            date=auction.date,
            time=auction.time,
            location=auction.location,
            circulation_entry_deadline=auction.circulation_entry_deadline,
            circulation_comment_deadline=auction.circulation_comment_deadline,
            registration_entry_deadline=auction.registration_entry_deadline,
            registration_comment_deadline=auction.registration_comment_deadline,
            created_at=auction.created_at.isoformat(),
            updated_at=auction.updated_at.isoformat(),
            auction_objects=basic_objects
        ))
    
    pages = (total + size - 1) // size
    
    return AuctionList(
        items=auction_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{auction_id}/basic", response_model=AuctionBasicResponse)
async def get_auction_basic(
    auction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Get basic auction information (Free content)."""
    
    query = select(Auction).options(
        selectinload(Auction.auction_objects)
    ).where(Auction.id == auction_id)
    
    result = await db.execute(query)
    auction = result.scalar_one_or_none()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    # Track view
    if request:
        await track_auction_view(
            auction_id=auction_id,
            view_type=ViewType.DETAIL,
            request=request,
            db=db
        )
    
    # Convert to response format
    basic_objects = []
    for obj in auction.auction_objects:
        basic_objects.append({
            "id": obj.id,
            "parcel_number": obj.parcel_number,
            "property_type": obj.property_type,
            "municipality": obj.municipality,
            "canton": obj.canton
        })
    
    return AuctionBasicResponse(
        id=auction.id,
        date=auction.date,
        time=auction.time,
        location=auction.location,
        circulation_entry_deadline=auction.circulation_entry_deadline,
        circulation_comment_deadline=auction.circulation_comment_deadline,
        registration_entry_deadline=auction.registration_entry_deadline,
        registration_comment_deadline=auction.registration_comment_deadline,
        created_at=auction.created_at.isoformat(),
        updated_at=auction.updated_at.isoformat(),
        auction_objects=basic_objects
    )


@router.get("/{auction_id}/full", response_model=AuctionFullResponse)
async def get_auction_full(
    auction_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Get full auction information (Premium content - requires subscription)."""
    
    # Check if user has subscription
    if user_id:
        subscription_query = select(UserSubscription).where(
            and_(
                UserSubscription.user_id == user_id,
                UserSubscription.auction_id == auction_id,
                UserSubscription.is_active == True
            )
        )
        subscription_result = await db.execute(subscription_query)
        subscription = subscription_result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(
                status_code=402, 
                detail="Premium subscription required to view full auction details"
            )
    
    # Get auction with all related data
    query = select(Auction).options(
        selectinload(Auction.auction_objects),
        selectinload(Auction.publication).selectinload(Auction.publication.debtors),
        selectinload(Auction.publication).selectinload(Auction.publication.contacts)
    ).where(Auction.id == auction_id)
    
    result = await db.execute(query)
    auction = result.scalar_one_or_none()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    # Track view
    if request:
        await track_auction_view(
            auction_id=auction_id,
            view_type=ViewType.DETAIL,
            request=request,
            db=db,
            user_id=user_id
        )
    
    return AuctionFullResponse(
        id=auction.id,
        date=auction.date,
        time=auction.time,
        location=auction.location,
        circulation_entry_deadline=auction.circulation_entry_deadline,
        circulation_comment_deadline=auction.circulation_comment_deadline,
        registration_entry_deadline=auction.registration_entry_deadline,
        registration_comment_deadline=auction.registration_comment_deadline,
        created_at=auction.created_at.isoformat(),
        updated_at=auction.updated_at.isoformat(),
        auction_objects=auction.auction_objects,
        debtors=auction.publication.debtors,
        contacts=auction.publication.contacts
    )


@router.get("/map/data", response_model=AuctionMapList)
async def get_auctions_map_data(
    canton: Optional[str] = Query(None, description="Filter by canton"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Get auction data for map visualization (Free content)."""
    
    # Build query for map data
    query = select(Auction).options(
        selectinload(Auction.auction_objects)
    )
    
    # Apply filters
    if canton:
        query = query.join(Auction.publication).where(
            Auction.publication.has(canton=canton)
        )
    
    if date_from:
        query = query.where(Auction.date >= date_from)
    
    if date_to:
        query = query.where(Auction.date <= date_to)
    
    # Only get auctions with coordinates
    query = query.join(AuctionObject).where(
        AuctionObject.coordinates.isnot(None)
    )
    
    result = await db.execute(query)
    auctions = result.scalars().all()
    
    # Track view
    if request:
        await track_auction_view(
            auction_id=None,
            view_type=ViewType.MAP,
            request=request,
            db=db
        )
    
    # Convert to map response format
    map_responses = []
    for auction in auctions:
        for obj in auction.auction_objects:
            if obj.latitude and obj.longitude:
                map_responses.append(AuctionMapResponse(
                    id=auction.id,
                    date=auction.date,
                    time=auction.time,
                    location=auction.location,
                    coordinates={"lat": float(obj.latitude), "lng": float(obj.longitude)},
                    estimated_value=float(obj.estimated_value) if obj.estimated_value else None,
                    currency=obj.currency
                ))
    
    return AuctionMapList(
        items=map_responses,
        total=len(map_responses)
    )


async def track_auction_view(
    auction_id: Optional[uuid.UUID],
    view_type: ViewType,
    request: Request,
    db: AsyncSession,
    user_id: Optional[uuid.UUID] = None
):
    """Track auction view for analytics."""
    try:
        # Get client IP
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Create view record
        view = AuctionView(
            auction_id=auction_id,
            user_id=user_id,
            view_type=view_type,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            referrer=request.headers.get("referer"),
            session_id=request.headers.get("x-session-id")
        )
        
        db.add(view)
        await db.commit()
        
    except Exception as e:
        # Don't fail the main request if tracking fails
        print(f"Failed to track view: {e}")
        await db.rollback()
