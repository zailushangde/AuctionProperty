"""Integration tests to verify the complete system works end-to-end."""

import pytest
import uuid
from datetime import date
from fastapi.testclient import TestClient

from app.main import app


class TestSystemIntegration:
    """Test complete system integration."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_api_health_check(self, client):
        """Test that the API is running and healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auction-platform"
    
    def test_api_documentation(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_auctions_endpoint_structure(self, client):
        """Test that auctions endpoint returns correct structure."""
        response = client.get("/api/v1/auctions/")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["items", "total", "page", "size", "pages"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Test pagination structure
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["size"], int)
        assert isinstance(data["pages"], int)
    
    def test_subscriptions_pricing(self, client):
        """Test subscription pricing endpoint."""
        response = client.get("/api/v1/subscriptions/pricing")
        assert response.status_code == 200
        
        data = response.json()
        assert "subscription_types" in data
        
        subscription_types = data["subscription_types"]
        assert "basic" in subscription_types
        assert "premium" in subscription_types
        
        # Test basic subscription
        basic = subscription_types["basic"]
        assert basic["price"] == "5.00"
        assert basic["currency"] == "CHF"
        assert "features" in basic
        
        # Test premium subscription
        premium = subscription_types["premium"]
        assert premium["price"] == "15.00"
        assert premium["currency"] == "CHF"
        assert "features" in premium
    
    def test_analytics_endpoints(self, client):
        """Test analytics endpoints."""
        # Test view statistics
        response = client.get("/api/v1/analytics/view-statistics")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "period_days", "total_views", "unique_users", 
            "anonymous_views", "view_type_breakdown", "average_views_per_day"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Test popular auctions
        response = client.get("/api/v1/analytics/popular-auctions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_map_data_endpoint(self, client):
        """Test map data endpoint."""
        response = client.get("/api/v1/auctions/map/data")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
    
    def test_authentication_headers(self, client):
        """Test that authentication headers are properly handled."""
        user_id = str(uuid.uuid4())
        
        # Test with valid user ID
        response = client.get(
            "/api/v1/analytics/my-view-history",
            headers={"X-User-ID": user_id}
        )
        assert response.status_code == 200
        
        # Test with invalid user ID format
        response = client.get(
            "/api/v1/analytics/my-view-history",
            headers={"X-User-ID": "invalid-uuid"}
        )
        assert response.status_code == 400
        
        # Test without user ID
        response = client.get("/api/v1/analytics/my-view-history")
        assert response.status_code == 401
    
    def test_subscription_workflow(self, client):
        """Test complete subscription workflow."""
        user_id = str(uuid.uuid4())
        auction_id = str(uuid.uuid4())
        
        # 1. Check subscription (should not exist)
        response = client.get(
            f"/api/v1/subscriptions/check/{auction_id}",
            headers={"X-User-ID": user_id}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_subscription"] is False
        
        # 2. Purchase subscription
        subscription_data = {
            "auction_id": auction_id,
            "subscription_type": "premium",
            "payment_method": "test-payment",
            "amount": "15.00"
        }
        
        response = client.post(
            "/api/v1/subscriptions/purchase",
            json=subscription_data,
            headers={"X-User-ID": user_id}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "subscription_id" in data
        assert data["status"] == "completed"
        
        # 3. Check subscription again (should exist now)
        response = client.get(
            f"/api/v1/subscriptions/check/{auction_id}",
            headers={"X-User-ID": user_id}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_subscription"] is True
        assert data["subscription_type"] == "premium"
        
        # 4. Get user's subscriptions
        response = client.get(
            "/api/v1/subscriptions/my-subscriptions",
            headers={"X-User-ID": user_id}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_error_handling(self, client):
        """Test error handling for various scenarios."""
        # Test 404 for non-existent auction
        fake_auction_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/auctions/{fake_auction_id}/basic")
        assert response.status_code == 404
        
        # Test 404 for non-existent auction full details
        response = client.get(f"/api/v1/auctions/{fake_auction_id}/full")
        assert response.status_code in [401, 402, 404]  # Depends on auth
        
        # Test invalid query parameters
        response = client.get("/api/v1/auctions/?page=0")  # Invalid page
        assert response.status_code == 422  # Validation error
        
        response = client.get("/api/v1/auctions/?size=1000")  # Too large
        assert response.status_code == 422  # Validation error
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options("/api/v1/auctions/")
        assert response.status_code == 200
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_content_type_headers(self, client):
        """Test that responses have correct content type."""
        response = client.get("/api/v1/auctions/")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        
        response = client.get("/api/v1/subscriptions/pricing")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
    
    def test_api_versioning(self, client):
        """Test that API versioning is working."""
        # Test v1 endpoints
        response = client.get("/api/v1/auctions/")
        assert response.status_code == 200
        
        # Test that non-versioned endpoints don't exist
        response = client.get("/api/auctions/")
        assert response.status_code == 404


class TestDataConsistency:
    """Test data consistency across the system."""
    
    def test_schema_validation(self):
        """Test that all schemas are properly defined."""
        from app.schemas import (
            AuctionBasicResponse, AuctionFullResponse, AuctionMapResponse,
            UserSubscriptionResponse, SubscriptionPurchaseRequest,
            ViewAnalytics, UserViewHistory
        )
        
        # Test that schemas can be instantiated
        basic_response = AuctionBasicResponse(
            id=uuid.uuid4(),
            date=date(2025, 10, 15),
            location="Test Location",
            created_at="2025-09-06T10:00:00Z",
            updated_at="2025-09-06T10:00:00Z",
            auction_objects=[]
        )
        
        assert basic_response.date == date(2025, 10, 15)
        assert basic_response.location == "Test Location"
        
        # Test subscription request
        subscription_request = SubscriptionPurchaseRequest(
            auction_id=uuid.uuid4(),
            subscription_type="premium",
            payment_method="test",
            amount="15.00"
        )
        
        assert subscription_request.subscription_type == "premium"
        assert subscription_request.amount == "15.00"
    
    def test_model_relationships(self):
        """Test that model relationships are properly defined."""
        from app.models import (
            Publication, Auction, AuctionObject, Debtor, Contact,
            UserSubscription, AuctionView
        )
        
        # Test that relationships exist
        assert hasattr(Publication, 'auctions')
        assert hasattr(Publication, 'debtors')
        assert hasattr(Publication, 'contacts')
        
        assert hasattr(Auction, 'auction_objects')
        assert hasattr(Auction, 'publication')
        
        assert hasattr(AuctionObject, 'auction')
        
        assert hasattr(Debtor, 'publication')
        assert hasattr(Contact, 'publication')
        
        assert hasattr(UserSubscription, 'auction')
        assert hasattr(AuctionView, 'auction')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
