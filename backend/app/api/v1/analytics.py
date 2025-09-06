"""Analytics API endpoints for auction views and user behavior."""

import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.database import get_db
from app.models import AuctionView, Auction, ViewType
from app.schemas import ViewAnalytics, UserViewHistory
from app.api.dependencies import get_current_user_id

router = APIRouter()


@router.get("/auction/{auction_id}/views", response_model=ViewAnalytics)
async def get_auction_view_analytics(
    auction_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get view analytics for a specific auction (Admin/Internal use)."""
    
    # Check if auction exists
    auction_query = select(Auction).where(Auction.id == auction_id)
    auction_result = await db.execute(auction_query)
    auction = auction_result.scalar_one_or_none()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    # Get view statistics
    views_query = select(
        func.count(AuctionView.id).label('total_views'),
        func.count(func.distinct(AuctionView.user_id)).label('unique_users'),
        func.count(func.distinct(AuctionView.session_id)).label('anonymous_views'),
        func.max(AuctionView.viewed_at).label('last_viewed')
    ).where(AuctionView.auction_id == auction_id)
    
    views_result = await db.execute(views_query)
    views_stats = views_result.first()
    
    # Get view type breakdown
    view_types_query = select(
        AuctionView.view_type,
        func.count(AuctionView.id).label('count')
    ).where(AuctionView.auction_id == auction_id).group_by(AuctionView.view_type)
    
    view_types_result = await db.execute(view_types_query)
    view_types_stats = view_types_result.all()
    
    # Process view type statistics
    list_views = 0
    detail_views = 0
    map_views = 0
    
    for view_type, count in view_types_stats:
        if view_type == ViewType.LIST:
            list_views = count
        elif view_type == ViewType.DETAIL:
            detail_views = count
        elif view_type == ViewType.MAP:
            map_views = count
    
    return ViewAnalytics(
        auction_id=auction_id,
        total_views=views_stats.total_views or 0,
        unique_users=views_stats.unique_users or 0,
        anonymous_views=views_stats.anonymous_views or 0,
        list_views=list_views,
        detail_views=detail_views,
        map_views=map_views,
        last_viewed=views_stats.last_viewed
    )


@router.get("/my-view-history", response_model=List[UserViewHistory])
async def get_my_view_history(
    user_id: uuid.UUID = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get user's view history."""
    
    query = select(AuctionView).join(Auction).where(
        AuctionView.user_id == user_id
    ).order_by(desc(AuctionView.viewed_at)).limit(limit)
    
    result = await db.execute(query)
    views = result.scalars().all()
    
    view_history = []
    for view in views:
        view_history.append(UserViewHistory(
            user_id=view.user_id,
            auction_id=view.auction_id,
            view_type=view.view_type,
            viewed_at=view.viewed_at,
            auction_date=view.auction.date,
            auction_location=view.auction.location
        ))
    
    return view_history


@router.get("/popular-auctions")
async def get_popular_auctions(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Number of auctions to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get most viewed auctions in the specified time period."""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(
        AuctionView.auction_id,
        func.count(AuctionView.id).label('view_count'),
        func.count(func.distinct(AuctionView.user_id)).label('unique_viewers')
    ).where(
        AuctionView.viewed_at >= cutoff_date
    ).group_by(
        AuctionView.auction_id
    ).order_by(
        desc('view_count')
    ).limit(limit)
    
    result = await db.execute(query)
    popular_auctions = result.all()
    
    # Get auction details
    auction_ids = [row.auction_id for row in popular_auctions]
    auctions_query = select(Auction).where(Auction.id.in_(auction_ids))
    auctions_result = await db.execute(auctions_query)
    auctions = {auction.id: auction for auction in auctions_result.scalars().all()}
    
    # Format response
    popular_list = []
    for row in popular_auctions:
        auction = auctions.get(row.auction_id)
        if auction:
            popular_list.append({
                "auction_id": row.auction_id,
                "view_count": row.view_count,
                "unique_viewers": row.unique_viewers,
                "auction_date": auction.date,
                "location": auction.location
            })
    
    return popular_list


@router.get("/view-statistics")
async def get_view_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get overall view statistics."""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total views
    total_views_query = select(func.count(AuctionView.id)).where(
        AuctionView.viewed_at >= cutoff_date
    )
    total_views_result = await db.execute(total_views_query)
    total_views = total_views_result.scalar()
    
    # Unique users
    unique_users_query = select(func.count(func.distinct(AuctionView.user_id))).where(
        and_(
            AuctionView.viewed_at >= cutoff_date,
            AuctionView.user_id.isnot(None)
        )
    )
    unique_users_result = await db.execute(unique_users_query)
    unique_users = unique_users_result.scalar()
    
    # Anonymous views
    anonymous_views_query = select(func.count(AuctionView.id)).where(
        and_(
            AuctionView.viewed_at >= cutoff_date,
            AuctionView.user_id.is_(None)
        )
    )
    anonymous_views_result = await db.execute(anonymous_views_query)
    anonymous_views = anonymous_views_result.scalar()
    
    # View type breakdown
    view_type_query = select(
        AuctionView.view_type,
        func.count(AuctionView.id).label('count')
    ).where(
        AuctionView.viewed_at >= cutoff_date
    ).group_by(AuctionView.view_type)
    
    view_type_result = await db.execute(view_type_query)
    view_type_stats = view_type_result.all()
    
    view_type_breakdown = {}
    for view_type, count in view_type_stats:
        view_type_breakdown[view_type.value] = count
    
    return {
        "period_days": days,
        "total_views": total_views,
        "unique_users": unique_users,
        "anonymous_views": anonymous_views,
        "view_type_breakdown": view_type_breakdown,
        "average_views_per_day": round(total_views / days, 2) if days > 0 else 0
    }
