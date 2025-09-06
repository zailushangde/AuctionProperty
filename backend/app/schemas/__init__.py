"""Pydantic schemas for API validation."""

from .publication import PublicationCreate, PublicationResponse, PublicationList
from .auction import AuctionCreate, AuctionResponse, AuctionList
from .debtor import DebtorCreate, DebtorResponse
from .auction_object import AuctionObjectCreate, AuctionObjectResponse
from .contact import ContactCreate, ContactResponse

__all__ = [
    "PublicationCreate",
    "PublicationResponse", 
    "PublicationList",
    "AuctionCreate",
    "AuctionResponse",
    "AuctionList",
    "DebtorCreate",
    "DebtorResponse",
    "AuctionObjectCreate",
    "AuctionObjectResponse",
    "ContactCreate",
    "ContactResponse",
]
