# Swiss Real Estate Auction Aggregation Platform

A FastAPI-based backend for aggregating and managing Swiss real estate auction data from SHAB (Swiss Official Gazette) publications.

## Features

- 🔁 **SHAB XML Importer**: Fetches and parses SHAB publication XML files
- 🧠 **Database Models**: SQLAlchemy models for publications, auctions, debtors, objects, and contacts
- 🧾 **REST API**: FastAPI endpoints for querying auction data
- 🗓️ **Background Tasks**: Celery-based scheduling for data fetching and cleanup
- 🐳 **Docker Support**: Complete containerization with docker-compose

## Architecture

### Database Models

- **Publication**: SHAB publication metadata
- **Auction**: Auction events with date, time, location
- **Debtor**: Debtor information
- **AuctionObject**: Property/parcel details with estimated values
- **Contact**: Contact information for court officials

### API Endpoints

- `GET /api/v1/auctions/` - List auctions with filtering
- `GET /api/v1/auctions/{id}` - Get auction details
- `GET /api/v1/publications/` - List publications
- `GET /api/v1/objects/{parcel_no}` - Get parcel information
- `GET /api/v1/auctions/statistics/` - Auction statistics
- `GET /api/v1/publications/statistics/` - Publication statistics

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone and setup**:
   ```bash
   cd backend
   cp env.example .env
   # Edit .env with your configuration
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**:
   ```bash
   docker-compose exec web python scripts/run_migrations.py
   ```

4. **Access the application**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Celery Flower: http://localhost:5555

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database**:
   ```bash
   # Start PostgreSQL and Redis
   # Update .env with your database URL
   python scripts/init_db.py
   python scripts/run_migrations.py
   ```

3. **Start services**:
   ```bash
   # Terminal 1: FastAPI
   uvicorn app.main:app --reload
   
   # Terminal 2: Celery Worker
   celery -A app.celery_app worker --loglevel=info
   
   # Terminal 3: Celery Beat
   celery -A app.celery_app beat --loglevel=info
   ```

## Configuration

Create a `.env` file based on `env.example`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/auction_db
REDIS_URL=redis://localhost:6379/0
SHAB_BASE_URL=https://amtsblattportal.ch/api/v1
DEBUG=false
FETCH_INTERVAL_HOURS=24
```

## API Usage

### List Auctions
```bash
curl "http://localhost:8000/api/v1/auctions/?canton=ZH&date_from=2024-01-01"
```

### Get Auction Details
```bash
curl "http://localhost:8000/api/v1/auctions/{auction_id}"
```

### Search Parcels
```bash
curl "http://localhost:8000/api/v1/objects/search/parcel/?query=123"
```

### Get Statistics
```bash
curl "http://localhost:8000/api/v1/auctions/statistics/"
```

## Background Tasks

The platform includes several automated background tasks:

- **fetch_shab_data**: Fetches new SHAB data (runs daily)
- **cleanup_expired_data**: Removes old auction data (runs daily)
- **generate_daily_report**: Generates daily statistics (runs daily)

### Manual Task Execution

```bash
# Fetch SHAB data manually
python scripts/fetch_shab_data.py --days 7

# Trigger Celery tasks
celery -A app.celery_app call app.tasks.fetch_shab_data
```

## Development

### Code Quality

```bash
# Format code
black app/
isort app/

# Type checking
mypy app/

# Run tests
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Production Deployment

1. **Update configuration**:
   - Set `DEBUG=false`
   - Use strong `SECRET_KEY`
   - Configure production database
   - Set up proper CORS origins

2. **Deploy with Docker**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Monitor services**:
   - Check logs: `docker-compose logs -f`
   - Monitor Celery: http://your-domain:5555

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env

2. **Celery tasks not running**:
   - Check Redis connection
   - Verify worker is running: `celery -A app.celery_app inspect active`

3. **SHAB API errors**:
   - Check network connectivity
   - Verify SHAB_BASE_URL is correct

### Logs

```bash
# View application logs
docker-compose logs -f web

# View Celery worker logs
docker-compose logs -f celery-worker

# View Celery beat logs
docker-compose logs -f celery-beat
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
