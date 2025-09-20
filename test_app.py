"""
Comprehensive test suite for SOAR Incident Mock API Simulator.

This test suite covers all endpoints with various scenarios including:
- Success cases
- Error cases (404, validation errors)
- Authentication (with and without tokens)
- Filtering and pagination
- Edge cases

Run with: pytest test_app.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app import app, incidents, id_counter, id_lock

# Create test client
client = TestClient(app)

# Test data - Demo tokens for testing only
VALID_TOKEN = "demo-token-123"  # Demo token - do not use in production
INVALID_TOKEN = "invalid-token"

def reset_test_data():
    """Reset incidents data and ID counter for consistent testing"""
    global incidents
    incidents.clear()
    incidents.extend([
        {"id": 1, "title": "Phishing Email Campaign Detected", "status": "open", "severity": "high"},
        {"id": 2, "title": "Malware Detected on Endpoint", "status": "closed", "severity": "medium"},
        {"id": 3, "title": "Suspicious Login from Foreign IP", "status": "under investigation", "severity": "low"},
    ])
    with id_lock:
        id_counter["value"] = 3

@pytest.fixture(autouse=True)
def setup_test():
    """Setup before each test"""
    reset_test_data()

class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SOAR Incident Mock API Simulator"
        assert data["version"] == "2.0"
        assert "endpoints" in data

class TestHealthCheck:
    """Tests for the health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "total_incidents" in data
        assert data["api_version"] == "2.0"

class TestGetIncidents:
    """Tests for listing incidents with filtering and pagination"""
    
    def test_get_all_incidents(self):
        """Test getting all incidents without filters"""
        response = client.get("/incidents")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 3
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["per_page"] == 10
    
    def test_filter_by_status(self):
        """Test filtering incidents by status"""
        response = client.get("/incidents?status=open")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 1
        assert data["incidents"][0]["status"] == "open"
    
    def test_filter_by_severity(self):
        """Test filtering incidents by severity"""
        response = client.get("/incidents?severity=high")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 1
        assert data["incidents"][0]["severity"] == "high"
    
    def test_combined_filters(self):
        """Test combining status and severity filters"""
        response = client.get("/incidents?status=open&severity=high")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 1
        assert data["incidents"][0]["status"] == "open"
        assert data["incidents"][0]["severity"] == "high"
    
    def test_pagination(self):
        """Test pagination functionality"""
        response = client.get("/incidents?per_page=2&page=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 2
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total"] == 3
        assert data["total_pages"] == 2
    
    def test_pagination_second_page(self):
        """Test second page of pagination"""
        response = client.get("/incidents?per_page=2&page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 1
        assert data["page"] == 2
    
    def test_pagination_with_token(self):
        """Test pagination with authentication token"""
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        response = client.get("/incidents?per_page=2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 2

class TestGetSingleIncident:
    """Tests for getting a single incident by ID"""
    
    def test_get_existing_incident(self):
        """Test getting an existing incident"""
        response = client.get("/incidents/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Phishing Email Campaign Detected"
    
    def test_get_nonexistent_incident(self):
        """Test getting a non-existent incident"""
        response = client.get("/incidents/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_incident_with_token(self):
        """Test getting incident with valid token"""
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        response = client.get("/incidents/1", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

class TestCreateIncident:
    """Tests for creating new incidents"""
    
    def test_create_incident_minimal(self):
        """Test creating incident with minimal required fields"""
        incident_data = {
            "title": "New Security Incident",
            "severity": "medium"
        }
        response = client.post("/incidents", json=incident_data)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 4  # Auto-incremented ID
        assert data["title"] == "New Security Incident"
        assert data["severity"] == "medium"
        assert data["status"] == "open"  # Default status
    
    def test_create_incident_complete(self):
        """Test creating incident with all fields"""
        incident_data = {
            "title": "Critical Security Breach",
            "severity": "critical",
            "status": "under investigation"
        }
        response = client.post("/incidents", json=incident_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Critical Security Breach"
        assert data["severity"] == "critical"
        assert data["status"] == "under investigation"
    
    def test_create_incident_with_token(self):
        """Test creating incident with authentication token"""
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        incident_data = {
            "title": "Authenticated Incident",
            "severity": "high"
        }
        response = client.post("/incidents", json=incident_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Authenticated Incident"
    
    def test_create_incident_invalid_data(self):
        """Test creating incident with invalid data"""
        incident_data = {
            "severity": "medium"
            # Missing required title field
        }
        response = client.post("/incidents", json=incident_data)
        assert response.status_code == 422  # Validation error
    
    def test_auto_incrementing_ids(self):
        """Test that IDs are auto-incremented correctly"""
        incident1_data = {"title": "Incident 1", "severity": "low"}
        incident2_data = {"title": "Incident 2", "severity": "medium"}
        
        response1 = client.post("/incidents", json=incident1_data)
        response2 = client.post("/incidents", json=incident2_data)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        
        assert id2 == id1 + 1

class TestUpdateIncident:
    """Tests for updating incident status"""
    
    def test_update_existing_incident(self):
        """Test updating an existing incident"""
        update_data = {"status": "closed"}
        response = client.patch("/incidents/1", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "closed"
        assert data["id"] == 1
    
    def test_update_nonexistent_incident(self):
        """Test updating a non-existent incident"""
        update_data = {"status": "closed"}
        response = client.patch("/incidents/999", json=update_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_with_token(self):
        """Test updating incident with authentication token"""
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        update_data = {"status": "under investigation"}
        response = client.patch("/incidents/2", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "under investigation"
    
    def test_update_invalid_data(self):
        """Test updating with invalid data"""
        response = client.patch("/incidents/1", json={})
        assert response.status_code == 422  # Missing required status field

class TestDeleteIncident:
    """Tests for deleting incidents"""
    
    def test_delete_existing_incident(self):
        """Test deleting an existing incident"""
        response = client.delete("/incidents/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        
        # Verify incident is actually deleted
        get_response = client.get("/incidents/1")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_incident(self):
        """Test deleting a non-existent incident"""
        response = client.delete("/incidents/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_delete_with_token(self):
        """Test deleting incident with authentication token"""
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        response = client.delete("/incidents/2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2

class TestAuthentication:
    """Tests for authentication functionality"""
    
    def test_invalid_token(self):
        """Test that invalid tokens don't break the API (optional auth)"""
        headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
        response = client.get("/incidents", headers=headers)
        assert response.status_code == 200  # Should still work, auth is optional
    
    def test_malformed_auth_header(self):
        """Test malformed authorization header"""
        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/incidents", headers=headers)
        assert response.status_code == 200  # Should still work, auth is optional
    
    def test_no_auth_header(self):
        """Test requests without authorization header"""
        response = client.get("/incidents")
        assert response.status_code == 200  # Should work, auth is optional

class TestEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def test_case_insensitive_filters(self):
        """Test that filters are case insensitive"""
        response = client.get("/incidents?status=OPEN")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 1
        
        response = client.get("/incidents?severity=HIGH")
        assert response.status_code == 200
        data = response.json()
        assert len(data["incidents"]) == 1
    
    def test_large_per_page_limit(self):
        """Test that per_page is capped at 100"""
        response = client.get("/incidents?per_page=1000")
        assert response.status_code == 200
        data = response.json()
        assert data["per_page"] == 100  # Should be capped
    
    def test_zero_page(self):
        """Test behavior with page=0"""
        response = client.get("/incidents?page=0")
        assert response.status_code == 200
        data = response.json()
        # Should handle gracefully (though results may vary)
    
    def test_negative_page(self):
        """Test behavior with negative page number"""
        response = client.get("/incidents?page=-1")
        assert response.status_code == 200
        # Should handle gracefully

# Performance and concurrency tests
class TestConcurrency:
    """Tests for concurrent operations"""
    
    def test_concurrent_incident_creation(self):
        """Test that concurrent incident creation produces unique IDs"""
        import threading
        import time
        
        created_incidents = []
        
        def create_incident():
            incident_data = {"title": f"Concurrent Incident {threading.current_thread().ident}", "severity": "low"}
            response = client.post("/incidents", json=incident_data)
            if response.status_code == 201:
                created_incidents.append(response.json())
        
        # Create multiple threads to create incidents concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_incident)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all incidents have unique IDs
        ids = [incident["id"] for incident in created_incidents]
        assert len(ids) == len(set(ids)), "Duplicate IDs found in concurrent creation"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
