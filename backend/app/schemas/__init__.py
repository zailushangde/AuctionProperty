"""Pydantic schemas for API validation."""

from .publication import PublicationCreate, PublicationResponse, PublicationList
from .auction import (
    AuctionCreate, AuctionBasicResponse, AuctionFullResponse, 
    AuctionMapResponse, AuctionList, AuctionMapList
)
from .debtor import DebtorCreate, DebtorResponse
from .auction_object import (
    AuctionObjectCreate, AuctionObjectBasicResponse, 
    AuctionObjectResponse, AuctionObjectMapResponse
)
from .contact import ContactCreate, ContactResponse
from .user_subscription import (
    UserSubscriptionCreate, UserSubscriptionResponse,
    SubscriptionPurchaseRequest, SubscriptionPurchaseResponse
)
from .auction_view import (
    AuctionViewCreate, AuctionViewResponse, 
    ViewAnalytics, UserViewHistory
)

__all__ = [
    "PublicationCreate",
    "PublicationResponse", 
    "PublicationList",
    "AuctionCreate",
    "AuctionBasicResponse",
    "AuctionFullResponse",
    "AuctionMapResponse",
    "AuctionList",
    "AuctionMapList",
    "DebtorCreate",
    "DebtorResponse",
    "AuctionObjectCreate",
    "AuctionObjectBasicResponse",
    "AuctionObjectResponse",
    "AuctionObjectMapResponse",
    "ContactCreate",
    "ContactResponse",
    "UserSubscriptionCreate",
    "UserSubscriptionResponse",
    "SubscriptionPurchaseRequest",
    "SubscriptionPurchaseResponse",
    "AuctionViewCreate",
    "AuctionViewResponse",
    "ViewAnalytics",
    "UserViewHistory",
]
