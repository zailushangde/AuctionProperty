"""Subscription and payment API endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models import UserSubscription, Auction, SubscriptionType
from app.schemas import (
    UserSubscriptionResponse, SubscriptionPurchaseRequest, 
    SubscriptionPurchaseResponse, UserSubscriptionCreate
)
from app.api.dependencies import get_current_user_id

router = APIRouter()


@router.post("/purchase", response_model=SubscriptionPurchaseResponse)
async def purchase_subscription(
    request: SubscriptionPurchaseRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Purchase a subscription for auction details."""
    
    # Check if auction exists
    auction_query = select(Auction).where(Auction.id == request.auction_id)
    auction_result = await db.execute(auction_query)
    auction = auction_result.scalar_one_or_none()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    # Check if user already has an active subscription
    existing_subscription_query = select(UserSubscription).where(
        and_(
            UserSubscription.user_id == user_id,
            UserSubscription.auction_id == request.auction_id,
            UserSubscription.is_active == True
        )
    )
    existing_result = await db.execute(existing_subscription_query)
    existing_subscription = existing_result.scalar_one_or_none()
    
    if existing_subscription:
        raise HTTPException(
            status_code=400, 
            detail="User already has an active subscription for this auction"
        )
    
    # Create subscription record
    subscription = UserSubscription(
        user_id=user_id,
        auction_id=request.auction_id,
        subscription_type=request.subscription_type,
        payment_id=request.payment_method,  # This would be replaced with actual payment processing
        amount_paid=request.amount
    )
    
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    # In a real implementation, you would:
    # 1. Process payment with payment provider (Stripe, PayPal, etc.)
    # 2. Update subscription with actual payment_id
    # 3. Handle payment failures
    
    return SubscriptionPurchaseResponse(
        subscription_id=subscription.id,
        payment_url=None,  # Would be provided by payment provider
        payment_id=subscription.payment_id,
        status="completed",  # Would be updated based on payment status
        message="Subscription purchased successfully"
    )


@router.get("/my-subscriptions", response_model=List[UserSubscriptionResponse])
async def get_my_subscriptions(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get user's active subscriptions."""
    
    query = select(UserSubscription).where(
        and_(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        )
    ).order_by(UserSubscription.purchase_date.desc())
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return subscriptions


@router.get("/check/{auction_id}")
async def check_subscription(
    auction_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Check if user has subscription for specific auction."""
    
    query = select(UserSubscription).where(
        and_(
            UserSubscription.user_id == user_id,
            UserSubscription.auction_id == auction_id,
            UserSubscription.is_active == True
        )
    )
    
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()
    
    return {
        "has_subscription": subscription is not None,
        "subscription_type": subscription.subscription_type if subscription else None,
        "expires_at": subscription.expires_at if subscription else None
    }


@router.post("/cancel/{subscription_id}")
async def cancel_subscription(
    subscription_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a subscription."""
    
    query = select(UserSubscription).where(
        and_(
            UserSubscription.id == subscription_id,
            UserSubscription.user_id == user_id
        )
    )
    
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = False
    await db.commit()
    
    return {"message": "Subscription cancelled successfully"}


@router.get("/pricing")
async def get_pricing():
    """Get subscription pricing information."""
    
    return {
        "subscription_types": {
            "basic": {
                "name": "Basic Access",
                "price": "5.00",
                "currency": "CHF",
                "description": "Access to basic auction details for 30 days",
                "features": [
                    "View auction dates and locations",
                    "Access to property descriptions",
                    "Contact information",
                    "Debtor information"
                ]
            },
            "premium": {
                "name": "Premium Access", 
                "price": "15.00",
                "currency": "CHF",
                "description": "Full access to auction details for 30 days",
                "features": [
                    "All Basic features",
                    "Detailed property valuations",
                    "Historical auction data",
                    "Priority customer support",
                    "Export auction data"
                ]
            }
        }
    }
