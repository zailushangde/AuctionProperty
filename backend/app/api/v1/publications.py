"""Publication API endpoints."""

from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_db
from app.models import Publication, Auction, Debtor, Contact
from app.schemas.publication import PublicationResponse, PublicationList
from app.api.dependencies import PaginationParams, get_total_count

router = APIRouter(prefix="/publications", tags=["publications"])


@router.get("/", response_model=PublicationList)
async def list_publications(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    date_from: Optional[date] = Query(None, description="Filter publications from this date"),
    date_to: Optional[date] = Query(None, description="Filter publications to this date"),
    canton: Optional[str] = Query(None, description="Filter by canton"),
    language: Optional[str] = Query(None, description="Filter by language"),
    search: Optional[str] = Query(None, description="Search in title and content")
):
    """List publications with filtering and pagination."""
    
    # Build query
    query = select(Publication)
    
    # Apply filters
    filters = []
    
    if date_from:
        filters.append(Publication.publication_date >= date_from)
    
    if date_to:
        filters.append(Publication.publication_date <= date_to)
    
    if canton:
        filters.append(Publication.canton == canton.upper())
    
    if language:
        filters.append(Publication.language == language.lower())
    
    if search:
        search_filter = or_(
            Publication.title.ilike(f"%{search}%"),
            Publication.content.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by publication date (newest first)
    query = query.order_by(desc(Publication.publication_date))
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    publications = result.scalars().all()
    
    # Get total count
    total = await get_total_count(
        Publication,
        db,
        **{k: v for k, v in {
            'date_from': date_from,
            'date_to': date_to,
            'canton': canton,
            'language': language
        }.items() if v is not None}
    )
    
    # Calculate pages
    pages = (total + pagination.size - 1) // pagination.size
    
    return PublicationList(
        items=publications,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )


@router.get("/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed publication information."""
    
    # Get publication with related data
    result = await db.execute(
        select(Publication)
        .where(Publication.id == publication_id)
        .options(
            selectinload(Publication.auctions),
            selectinload(Publication.debtors),
            selectinload(Publication.contacts)
        )
    )
    publication = result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    return publication


@router.get("/{publication_id}/auctions/")
async def get_publication_auctions(
    publication_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all auctions for a specific publication."""
    
    # Check if publication exists
    pub_result = await db.execute(
        select(Publication).where(Publication.id == publication_id)
    )
    publication = pub_result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    # Get auctions for this publication
    result = await db.execute(
        select(Auction)
        .where(Auction.publication_id == publication_id)
        .options(selectinload(Auction.auction_objects))
    )
    auctions = result.scalars().all()
    
    return {
        "publication_id": publication_id,
        "publication_title": publication.title,
        "auctions": auctions
    }


@router.get("/{publication_id}/debtors/")
async def get_publication_debtors(
    publication_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all debtors for a specific publication."""
    
    # Check if publication exists
    pub_result = await db.execute(
        select(Publication).where(Publication.id == publication_id)
    )
    publication = pub_result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    # Get debtors for this publication
    result = await db.execute(
        select(Debtor).where(Debtor.publication_id == publication_id)
    )
    debtors = result.scalars().all()
    
    return {
        "publication_id": publication_id,
        "publication_title": publication.title,
        "debtors": debtors
    }


@router.get("/{publication_id}/contacts/")
async def get_publication_contacts(
    publication_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all contacts for a specific publication."""
    
    # Check if publication exists
    pub_result = await db.execute(
        select(Publication).where(Publication.id == publication_id)
    )
    publication = pub_result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    # Get contacts for this publication
    result = await db.execute(
        select(Contact).where(Contact.publication_id == publication_id)
    )
    contacts = result.scalars().all()
    
    return {
        "publication_id": publication_id,
        "publication_title": publication.title,
        "contacts": contacts
    }


@router.get("/statistics/")
async def get_publication_statistics(
    db: AsyncSession = Depends(get_db),
    canton: Optional[str] = Query(None, description="Filter by canton")
):
    """Get publication statistics."""
    
    # Base query
    base_query = select(Publication)
    if canton:
        base_query = base_query.where(Publication.canton == canton.upper())
    
    # Total publications
    total_result = await db.execute(select(func.count(Publication.id)))
    total_publications = total_result.scalar()
    
    # Publications by canton
    canton_query = (
        select(Publication.canton, func.count(Publication.id))
        .group_by(Publication.canton)
        .order_by(func.count(Publication.id).desc())
    )
    canton_result = await db.execute(canton_query)
    publications_by_canton = {row[0]: row[1] for row in canton_result.fetchall()}
    
    # Publications by language
    language_query = (
        select(Publication.language, func.count(Publication.id))
        .group_by(Publication.language)
        .order_by(func.count(Publication.id).desc())
    )
    language_result = await db.execute(language_query)
    publications_by_language = {row[0]: row[1] for row in language_result.fetchall()}
    
    # Recent publications (last 30 days)
    from datetime import timedelta
    thirty_days_ago = date.today() - timedelta(days=30)
    
    recent_query = base_query.where(Publication.publication_date >= thirty_days_ago)
    recent_result = await db.execute(select(func.count(Publication.id)).select_from(recent_query.subquery()))
    recent_publications = recent_result.scalar()
    
    return {
        "total_publications": total_publications,
        "recent_publications": recent_publications,
        "publications_by_canton": publications_by_canton,
        "publications_by_language": publications_by_language
    }
