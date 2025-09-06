# 🏠 Swiss Real Estate Auction Aggregation Platform

A comprehensive FastAPI-based backend system for aggregating and processing Swiss real estate auction data from the SHAB (Swiss Official Gazette) publications.

## 🌟 Features

### 📊 **Data Aggregation**
- **SHAB XML Parser**: Automated extraction of auction data from Swiss Official Gazette
- **Real-time Processing**: Live parsing of SHAB publication XML files
- **Multi-language Support**: German, French, Italian, and English content extraction
- **Contact Information**: Complete office and contact details extraction

### 🏗️ **Architecture**
- **FastAPI Backend**: High-performance async API with automatic OpenAPI documentation
- **PostgreSQL Database**: Robust relational database with async support
- **SQLAlchemy ORM**: Type-safe database models with Alembic migrations
- **Celery Task Queue**: Background processing for data fetching and cleanup
- **Redis Cache**: High-speed caching and message broker
- **Docker Support**: Containerized deployment with docker-compose

### 🔍 **Data Extraction**
- **Publication Details**: ID, dates, titles, languages, cantons
- **Auction Information**: Dates, times, locations, circulation, registration deadlines
- **Debtor Information**: Complete company and person details with addresses
- **Property Objects**: Detailed property descriptions and specifications
- **Contact Data**: Office information, addresses, and contact details

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Supabase PostgreSQL Database (configured)
- Redis 6+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AuctionProperty
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up Supabase database configuration**
   ```bash
   # Run the setup script
   python setup_supabase.py
   
   # Or manually edit .env file with your Supabase password
   cp .env.example .env
   # Edit .env and replace [YOUR-PASSWORD] with your actual Supabase password
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   # Development server
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Or using Docker
   docker-compose up -d
   ```

## 📖 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

#### 🔍 **Test Parser**
```bash
# Parse SHAB XML from URL
GET /api/v1/test-parser/parse-url?url=https://www.shab.ch/api/v1/publications/{id}/xml

# Parse sample data
GET /api/v1/test-parser/parse-sample

# Get parser information
GET /api/v1/test-parser/parser-info
```

#### 📋 **Publications**
```bash
# List all publications
GET /api/v1/publications/

# Get publication by ID
GET /api/v1/publications/{publication_id}

# Search publications
GET /api/v1/publications/search?q=search_term&canton=BE
```

#### 🏠 **Auctions**
```bash
# List all auctions
GET /api/v1/auctions/

# Get auction by ID
GET /api/v1/auctions/{auction_id}

# Filter auctions by date range
GET /api/v1/auctions/?date_from=2024-01-01&date_to=2024-12-31
```

#### 👥 **Debtors**
```bash
# List all debtors
GET /api/v1/debtors/

# Get debtor by ID
GET /api/v1/debtors/{debtor_id}

# Search debtors by name
GET /api/v1/debtors/search?name=company_name
```

## 🏗️ Project Structure

```
AuctionProperty/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API routes and endpoints
│   │   │   └── v1/           # API version 1
│   │   │       ├── auctions.py
│   │   │       ├── publications.py
│   │   │       ├── objects.py
│   │   │       └── test_parser.py
│   │   ├── core/             # Core configuration and settings
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/           # SQLAlchemy database models
│   │   │   ├── auction.py
│   │   │   ├── publication.py
│   │   │   ├── debtor.py
│   │   │   ├── auction_object.py
│   │   │   └── contact.py
│   │   ├── schemas/          # Pydantic schemas for validation
│   │   │   ├── auction.py
│   │   │   ├── publication.py
│   │   │   ├── debtor.py
│   │   │   ├── auction_object.py
│   │   │   └── contact.py
│   │   ├── parsers/          # Data parsing modules
│   │   │   └── shab_parser.py
│   │   ├── services/         # Business logic services
│   │   │   ├── auction_service.py
│   │   │   ├── publication_service.py
│   │   │   └── shab_service.py
│   │   ├── tasks/            # Celery background tasks
│   │   │   ├── fetch_shab_data.py
│   │   │   └── cleanup_tasks.py
│   │   └── main.py           # FastAPI application entry point
│   ├── alembic/              # Database migrations
│   ├── tests/                # Test suite
│   ├── scripts/              # Utility scripts
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Docker configuration
│   └── docker-compose.yml   # Docker Compose setup
├── .gitignore               # Git ignore patterns
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory. You can use the provided setup script:

```bash
# Run the Supabase setup script
python setup_supabase.py
```

Or manually create the `.env` file:

```env
# Database Configuration (Supabase)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.hwyuvjamgcawjcpsitrj.supabase.co:5432/postgres

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# SHAB API Configuration
SHAB_BASE_URL=https://www.shab.ch/api/v1
SHAB_FETCH_INTERVAL=3600  # seconds

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## 🐳 Docker Deployment

### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Data Models

### Publication
- **ID**: Unique identifier
- **Publication Date**: When published in SHAB
- **Expiration Date**: Publication validity period
- **Title**: Multilingual titles (DE, FR, IT, EN)
- **Language**: Primary language
- **Canton**: Swiss canton code
- **Registration Office**: Complete office details

### Auction
- **ID**: Unique identifier
- **Date**: Auction date
- **Time**: Auction time
- **Location**: Auction venue
- **Circulation**: Entry deadline and comments
- **Registration**: Registration deadline and comments
- **Objects**: Associated property objects

### Debtor
- **ID**: Unique identifier
- **Type**: Company or Person
- **Name**: Company name or person's name
- **Address**: Complete address information
- **UID**: Swiss company identifier (for companies)
- **Legal Form**: Company legal form
- **Date of Birth**: Person's birth date

### Auction Object
- **ID**: Unique identifier
- **Description**: Property description (HTML content)
- **Parcel Number**: Land registry parcel number
- **Estimated Value**: Property valuation
- **Surface Area**: Property size
- **Property Type**: Type of property
- **Address**: Property location

### Contact
- **ID**: Unique identifier
- **Name**: Contact/office name
- **Address**: Street address
- **Postal Code**: Swiss postal code
- **City**: City name
- **Phone**: Contact phone number
- **Email**: Contact email
- **Type**: Contact type (office, person, etc.)

## 🔄 Background Tasks

The system includes several Celery background tasks:

### Data Fetching
- **Daily SHAB Sync**: Automatically fetch new publications
- **Data Validation**: Validate and clean imported data
- **Contact Extraction**: Extract contact information from JSON APIs

### Maintenance
- **Data Cleanup**: Remove expired publications
- **Report Generation**: Generate daily/weekly reports
- **Cache Management**: Manage Redis cache expiration

## 🚨 Error Handling

The system includes comprehensive error handling:

- **HTTP Exceptions**: Proper HTTP status codes and error messages
- **Validation Errors**: Pydantic model validation with detailed error messages
- **Database Errors**: Graceful handling of database connection issues
- **External API Errors**: Retry logic for SHAB API failures
- **Logging**: Structured logging with different log levels

## 📈 Performance

### Optimization Features
- **Async Operations**: Full async/await support for I/O operations
- **Database Connection Pooling**: Efficient database connection management
- **Redis Caching**: High-speed caching for frequently accessed data
- **Background Processing**: Non-blocking data processing with Celery
- **Pagination**: Efficient data pagination for large datasets

### Monitoring
- **Health Checks**: Application health monitoring endpoints
- **Metrics**: Performance metrics and monitoring
- **Logging**: Comprehensive logging for debugging and monitoring

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints throughout the codebase
- Follow the existing code structure and patterns

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- **Documentation**: Check the API documentation at `/docs`
- **Issues**: Open an issue on GitHub
- **Email**: Contact the development team

## 🔮 Roadmap

### Upcoming Features
- [ ] **GraphQL API**: Alternative query interface
- [ ] **Elasticsearch Integration**: Advanced search capabilities
- [ ] **Real-time Notifications**: WebSocket support for live updates
- [ ] **Data Analytics**: Advanced analytics and reporting
- [ ] **Multi-tenant Support**: Support for multiple organizations
- [ ] **API Rate Limiting**: Advanced rate limiting and throttling
- [ ] **Data Export**: Export functionality for various formats
- [ ] **Mobile API**: Optimized endpoints for mobile applications

### Performance Improvements
- [ ] **Database Indexing**: Optimize database queries
- [ ] **Caching Strategy**: Implement advanced caching
- [ ] **Load Balancing**: Support for horizontal scaling
- [ ] **CDN Integration**: Content delivery network support

---

**Built with ❤️ for the Swiss real estate market**
