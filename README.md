# SOAR Incident Mock API Simulator

> **A RESTful API built with FastAPI to simulate SOAR (Security Orchestration, Automation & Response) incident handling workflows for security automation demonstrations.**

## Features

### Core SOAR Incident Management
- **Full CRUD Operations** - Create, Read, Update, Delete incidents
- **Advanced Filtering** - Filter by status and severity levels
- **Pagination Support** - Handle large incident datasets efficiently
- **Auto-incrementing IDs** - Production-ready ID management
- **Comprehensive Validation** - Robust input validation with Pydantic

### Security & Authentication
- **Bearer Token Authentication** - Optional API protection
- **Security Headers** - HTTP security best practices
- **Comprehensive Logging** - Audit trail capabilities

### Developer Experience
- **Interactive API Documentation** - Auto-generated with Swagger UI
- **Complete Test Suite** - 25+ test cases with pytest
- **Health Monitoring** - Built-in health check endpoints
- **Comprehensive Documentation** - Detailed API specifications

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API information and welcome | No |
| `GET` | `/health` | Health check for monitoring | No |
| `GET` | `/incidents` | List all incidents with filtering & pagination | Optional |
| `GET` | `/incidents/{id}` | Get specific incident by ID | Optional |
| `POST` | `/incidents` | Create new incident | Optional |
| `PATCH` | `/incidents/{id}` | Update incident status | Optional |
| `DELETE` | `/incidents/{id}` | Delete incident | Optional |

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd soar-incident-mock-api-simulator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server:**
   ```bash
   uvicorn app:app --reload
   ```

4. **Access the API:**
   - **API Base URL:** http://localhost:8000
   - **Interactive Docs:** http://localhost:8000/docs
   - **ReDoc Documentation:** http://localhost:8000/redoc

## Security Notice

This is a **demonstration project** designed for portfolio and educational purposes. While it follows security best practices for API design, it includes simplifications for demo purposes:

### Demo Limitations:
- **Hardcoded demo token** (`demo-token-123`) - Use environment variables in production
- **In-memory data storage** - Use encrypted databases in production  
- **HTTP localhost** - Use HTTPS with proper certificates in production
- **No rate limiting** - Implement rate limiting for production APIs
- **Simple authentication** - Use OAuth 2.0, JWT with expiration, or enterprise SSO


## API Usage Examples

### 1. List All Incidents
```bash
curl -X GET "http://localhost:8000/incidents"
```

**Response:**
```json
{
  "incidents": [
    {
      "id": 1,
      "title": "Phishing Email Campaign Detected",
      "status": "open",
      "severity": "high"
    }
  ],
  "total": 3,
  "page": 1,
  "per_page": 10,
  "total_pages": 1
}
```

### 2. Filter by Severity and Status
```bash
curl -X GET "http://localhost:8000/incidents?severity=high&status=open"
```

### 3. Pagination
```bash
curl -X GET "http://localhost:8000/incidents?page=1&per_page=5"
```

### 4. Create New Incident
```bash
curl -X POST "http://localhost:8000/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ransomware Detection on Critical Server",
    "severity": "critical",
    "status": "open"
  }'
```

**Response:**
```json
{
  "id": 4,
  "title": "Ransomware Detection on Critical Server",
  "status": "open",
  "severity": "critical"
}
```

### 5. Update Incident Status
```bash
curl -X PATCH "http://localhost:8000/incidents/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "under investigation"}'
```

### 6. Get Single Incident
```bash
curl -X GET "http://localhost:8000/incidents/1"
```

### 7. Delete Incident
```bash
curl -X DELETE "http://localhost:8000/incidents/1"
```

## Authentication

The API supports optional Bearer token authentication for protected access:

```bash
curl -X GET "http://localhost:8000/incidents" \
  -H "Authorization: Bearer demo-token-123"
```

**Valid demo token:** `demo-token-123`

**Security Notice:** This is a demonstration project. The authentication implementation uses hardcoded tokens for simplicity. In production environments, always use:
- Environment variables for secrets
- Proper JWT tokens with expiration
- OAuth 2.0 or similar protocols
- Role-based access control
- HTTPS encryption

## Data Models

### Incident Model
```json
{
  "id": 1,
  "title": "Security incident description",
  "status": "open | under investigation | closed",
  "severity": "low | medium | high | critical"
}
```

### Create Incident (Input)
```json
{
  "title": "Required: Brief incident description",
  "severity": "Required: low | medium | high | critical",
  "status": "Optional: defaults to 'open'"
}
```

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests with verbose output
pytest test_app.py -v

# Run tests with coverage
pytest test_app.py --cov=app

# Run specific test class
pytest test_app.py::TestGetIncidents -v
```

### Test Coverage
- All endpoint success scenarios
- Error handling (404, validation errors)
- Authentication testing
- Filtering and pagination
- Concurrent operations
- Edge cases and boundary conditions

## Health Monitoring

Check API health status:
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "total_incidents": 3,
  "api_version": "2.0"
}
```

## Security Features

### Input Validation
- Pydantic models ensure data integrity
- Type checking and validation
- Sanitized error messages

### Authentication
- Bearer token support
- Optional authentication (graceful degradation)
- Secure header handling

### Best Practices
- CORS support ready
- Rate limiting ready (add middleware)
- Comprehensive logging structure
- Error handling with appropriate HTTP status codes

## SOAR Relevance

This API demonstrates key concepts used in Security Orchestration, Automation & Response platforms:

### Incident Management
- **Incident Lifecycle:** Open → Under Investigation → Closed
- **Severity Classification:** Critical, High, Medium, Low
- **Status Tracking:** Real-time incident status updates

### Automation Ready
- **RESTful Design:** Easy integration with SOAR platforms
- **Filtering & Search:** Support for automated incident queries
- **Bulk Operations:** Pagination for handling large incident volumes

### Security Operations
- **Authentication:** API security for sensitive operations
- **Audit Trail:** Comprehensive logging for compliance
- **Monitoring:** Health checks for operational visibility

## Production Considerations

For production deployment, consider adding:

- **Database Integration** (PostgreSQL, MongoDB)
- **JWT Authentication** with role-based access
- **Rate Limiting** middleware
- **CORS Configuration** for web interfaces
- **Logging** with structured formats
- **Metrics Collection** (Prometheus, etc.)
- **API Versioning** strategy
- **Error Tracking** (Sentry, etc.)

## Development

### Project Structure
```
soar-incident-mock-api-simulator/
├── app.py              # Main FastAPI application
├── test_app.py         # Comprehensive test suite
├── requirements.txt    # Python dependencies
├── README.md          # This documentation
└── .gitignore         # Git ignore rules
```

### Code Style
- **Type Hints:** Full type annotation coverage
- **Docstrings:** Comprehensive API documentation
- **Error Handling:** Proper HTTP status codes
- **Testing:** High test coverage with multiple scenarios

## Learning Objectives

This project demonstrates:

1. **RESTful API Design** - Following REST principles
2. **Security Engineering** - Authentication and input validation
3. **Test-Driven Development** - Comprehensive test coverage
4. **Documentation** - Clear API documentation and examples
5. **SOAR Concepts** - Incident management workflows
6. **Production Readiness** - Monitoring, health checks, error handling

## Contributing

This is a portfolio demonstration project. For suggestions or improvements:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

This project is created for educational and portfolio demonstration purposes.

---

**Perfect for demonstrating:**
- Security automation engineering skills
- API development and testing expertise
- SOAR/SOC operational understanding
- Test-driven development practices
- Technical documentation abilities
