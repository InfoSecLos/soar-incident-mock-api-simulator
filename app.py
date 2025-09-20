from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import threading

app = FastAPI(
    title="SOAR Incident Mock API Simulator", 
    version="1.0",
    description="A comprehensive SOAR (Security Orchestration, Automation & Response) incident management API simulator for security automation demonstrations"
)

# Security configuration - DEMO ONLY
security = HTTPBearer(auto_error=False)

# DEMO TOKENS - DO NOT USE IN PRODUCTION
# In production, use proper JWT tokens, environment variables, or OAuth
VALID_TOKENS = {"demo-token-123": "demo_user"}  # Simple token validation for demonstration

# Global ID counter with thread safety
id_counter = {"value": 3}  # Start at 3 since we have 3 initial incidents
id_lock = threading.Lock()

# Pydantic models
class IncidentCreate(BaseModel):
    """Model for creating new incidents (no ID required)"""
    title: str = Field(..., description="Brief description of the security incident")
    status: str = Field(default="open", description="Current status of the incident")
    severity: str = Field(..., description="Severity level: low, medium, high, critical")

class Incident(BaseModel):
    """Complete incident model with ID"""
    id: int = Field(..., description="Unique incident identifier")
    title: str = Field(..., description="Brief description of the security incident")
    status: str = Field(..., description="Current status: open, under investigation, closed")
    severity: str = Field(..., description="Severity level: low, medium, high, critical")

class IncidentUpdate(BaseModel):
    """Model for updating incident status"""
    status: str = Field(..., description="New status for the incident")

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    incidents: List[Incident]
    total: int
    page: int
    per_page: int
    total_pages: int

# Mock incident database
incidents = [
    {"id": 1, "title": "Phishing Email Campaign Detected", "status": "open", "severity": "high"},
    {"id": 2, "title": "Malware Detected on Endpoint", "status": "closed", "severity": "medium"},
    {"id": 3, "title": "Suspicious Login from Foreign IP", "status": "under investigation", "severity": "low"},
]

# Authentication functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """
    Verify the provided Bearer token.
    Returns username if valid, None if invalid or missing.
    
    SECURITY NOTE: This is a demo implementation.
    In production, use proper JWT tokens with:
    - Environment variables for secrets
    - Token expiration
    - Refresh token mechanism
    - Role-based access control
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return VALID_TOKENS.get(token)

def get_next_id() -> int:
    """Thread-safe ID generation for new incidents"""
    with id_lock:
        id_counter["value"] += 1
        return id_counter["value"]

# API Endpoints

@app.get("/", tags=["Root"])
def root():
    """Welcome endpoint with API information"""
    return {
        "message": "SOAR Incident Mock API Simulator",
        "version": "2.0",
        "description": "Security automation demo API for incident management",
        "docs": "/docs",
        "endpoints": {
            "list_incidents": "GET /incidents",
            "get_incident": "GET /incidents/{id}",
            "create_incident": "POST /incidents",
            "update_incident": "PATCH /incidents/{id}",
            "delete_incident": "DELETE /incidents/{id}"
        }
    }

@app.get("/incidents", response_model=PaginatedResponse, tags=["Incidents"])
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
    user: Optional[str] = Depends(verify_token)
):
    """
    Retrieve all incidents with optional filtering and pagination.
    
    **Filters:**
    - status: Filter by incident status (open, under investigation, closed)
    - severity: Filter by severity level (low, medium, high, critical)
    
    **Pagination:**
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 100)
    
    **Authentication:** Optional Bearer token for protected access
    """
    # Apply filters
    filtered_incidents = incidents
    
    if status:
        filtered_incidents = [i for i in filtered_incidents if i["status"].lower() == status.lower()]
    
    if severity:
        filtered_incidents = [i for i in filtered_incidents if i["severity"].lower() == severity.lower()]
    
    # Calculate pagination
    total = len(filtered_incidents)
    per_page = min(per_page, 100)  # Cap at 100 items per page
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_incidents = filtered_incidents[start:end]
    
    return PaginatedResponse(
        incidents=paginated_incidents,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@app.get("/incidents/{incident_id}", response_model=Incident, tags=["Incidents"])
def get_incident(incident_id: int, user: Optional[str] = Depends(verify_token)):
    """
    Retrieve a specific incident by its ID.
    
    **Parameters:**
    - incident_id: The unique identifier of the incident
    
    **Returns:** Full incident details or 404 if not found
    **Authentication:** Optional Bearer token for protected access
    """
    for incident in incidents:
        if incident["id"] == incident_id:
            return incident
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Incident with ID {incident_id} not found"
    )

@app.post("/incidents", response_model=Incident, status_code=status.HTTP_201_CREATED, tags=["Incidents"])
def create_incident(incident_data: IncidentCreate, user: Optional[str] = Depends(verify_token)):
    """
    Create a new security incident.
    
    **Body:** IncidentCreate model (title, severity, optional status)
    **Returns:** Complete incident with auto-generated ID
    **Authentication:** Optional Bearer token for protected access
    
    **Example:**
    ```json
    {
        "title": "lateral movement detected",
        "severity": "high",
        "status": "open"
    }
    ```
    """
    # Generate new incident with auto-incrementing ID
    new_incident = {
        "id": get_next_id(),
        "title": incident_data.title,
        "status": incident_data.status,
        "severity": incident_data.severity
    }
    
    incidents.append(new_incident)
    return new_incident

@app.patch("/incidents/{incident_id}", response_model=Incident, tags=["Incidents"])
def update_incident(
    incident_id: int, 
    update_data: IncidentUpdate, 
    user: Optional[str] = Depends(verify_token)
):
    """
    Update the status of an existing incident.
    
    **Parameters:**
    - incident_id: The unique identifier of the incident
    
    **Body:** IncidentUpdate model (new status)
    **Returns:** Updated incident or 404 if not found
    **Authentication:** Optional Bearer token for protected access
    
    **Valid statuses:** open, under investigation, closed
    """
    for incident in incidents:
        if incident["id"] == incident_id:
            incident["status"] = update_data.status
            return incident
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Incident with ID {incident_id} not found"
    )

@app.delete("/incidents/{incident_id}", response_model=Incident, tags=["Incidents"])
def delete_incident(incident_id: int, user: Optional[str] = Depends(verify_token)):
    """
    Close and remove an incident from the system.
    
    **Parameters:**
    - incident_id: The unique identifier of the incident to delete
    
    **Returns:** The deleted incident or 404 if not found
    **Authentication:** Optional Bearer token for protected access
    
    **Note:** In a real SOAR system, incidents are typically archived rather than deleted.
    """
    for i, incident in enumerate(incidents):
        if incident["id"] == incident_id:
            deleted_incident = incidents.pop(i)
            return deleted_incident
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Incident with ID {incident_id} not found"
    )

# Health check endpoint for monitoring
@app.get("/health", tags=["System"])
def health_check():
    """Simple health check endpoint for monitoring systems"""
    return {
        "status": "healthy",
        "total_incidents": len(incidents),
        "api_version": "2.0"
    }
