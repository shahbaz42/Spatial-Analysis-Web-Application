# Solar Site Analyzer API

A FastAPI backend for analyzing and managing solar panel installation site suitability with MySQL database.

## Features

- **RESTful API** with comprehensive endpoints for site analysis
- **Custom Weight Analysis** - Recalculate scores with custom parameters
- **Statistical Analysis** - Get detailed statistics and distributions
- **Data Export** - Export results in CSV or JSON format
- **Async Database Operations** - High-performance async I/O
- **Production-Ready** - Proper error handling, validation, and logging
- **Auto-Generated Documentation** - Interactive API docs with Swagger UI
- **Redis Caching** - Cache responses for faster access
- **Docker Support** - Containerized development and deployment

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── cache.py             # Cache management
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models for validation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── site_service.py      # Site business logic
│   │   └── analysis_service.py  # Analysis calculations
│   └── routers/
│       ├── __init__.py
│       ├── sites.py         # Site endpoints
│       ├── analysis.py      # Analysis endpoints
│       └── export.py        # Export endpoints
├── data.csv                 # Sample site data
├── databaseschema.sql       # Database schema
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## API Endpoints

### Sites

- **GET /api/sites** - Get all sites with filtering and pagination
  - Query params: `min_score`, `max_score`, `limit`, `offset`
  
- **GET /api/sites/{id}** - Get detailed site information
  - Returns full analysis breakdown

### Analysis

- **POST /api/analyze** - Recalculate scores with custom weights
  - Request body: `{ "weights": { "solar": 0.4, "area": 0.3, ... } }`
  
- **GET /api/statistics** - Get comprehensive statistics
  - Returns averages, distributions, regional stats, etc.

### Export

- **GET /api/export** - Export filtered results
  - Query params: `format` (csv/json), `min_score`


## Quick Start
## Option 1: Local Development Setup (Recommended for Development)

### Step 1: Set up MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Run the schema script
source databaseschema.sql
```

### Step 2: Set up Python Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Update these values:
```
DB_USER=root
DB_PASSWORD=your_mysql_password
```

### Step 4: Initialize Database with Data

```bash
# Run the initialization script
python scripts/init_database.py
```

This will:
- Load all 50 sites from data.csv
- Calculate initial suitability scores
- Set up the database completely

### Step 5: Start the API Server

```bash
# Development mode with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Access the API

Open your browser:
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

---


## Development Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### 2. Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Create database and import schema
source databaseschema.sql

# Import sample data
LOAD DATA LOCAL INFILE 'data.csv'
INTO TABLE sites
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(site_id, site_name, latitude, longitude, area_sqm, 
 solar_irradiance_kwh, grid_distance_km, slope_degrees, 
 road_distance_km, elevation_m, land_type, region);

# Calculate initial scores
CALL calculate_suitability_scores();
```

### 3. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

Update the following variables:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=solar_site_analyzer
```

### 5. Run the Application

```bash
# Development mode (with auto-reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py directly
python app/main.py

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Analysis Formula

The suitability score (0-100) is calculated using:

```
Total Score = (
    solar_irradiance_score × solar_weight +
    area_score × area_weight +
    grid_distance_score × grid_weight +
    slope_score × slope_weight +
    infrastructure_score × infra_weight
)
```

### Default Weights
- Solar Irradiance: 0.35 (35%)
- Area: 0.25 (25%)
- Grid Distance: 0.20 (20%)
- Slope: 0.15 (15%)
- Infrastructure: 0.05 (5%)

### Individual Score Calculations

1. **Solar Irradiance Score** (0-100):
   - 100: ≥ 5.5 kWh/m²/day
   - 0: < 3.0 kWh/m²/day
   - Linear scaling between

2. **Area Score** (0-100):
   - 100: ≥ 50,000 m²
   - 0: < 5,000 m²
   - Linear scaling between

3. **Grid Distance Score** (0-100):
   - 100: ≤ 1 km
   - 0: ≥ 20 km
   - Linear inverse relationship

4. **Slope Score** (0-100):
   - 100: 0-5 degrees
   - 50: 5-15 degrees
   - 0: > 20 degrees

5. **Infrastructure Score** (0-100):
   - 100: ≤ 0.5 km from road
   - 0: ≥ 5 km from road
   - Linear inverse relationship

## Development

### Design Patterns

**1. Layered Architecture**:
- **Router Layer**: HTTP request/response handling
- **Service Layer**: Business logic and calculations
- **Database Layer**: Data access and persistence

**2. Dependency Injection**:
- Database sessions injected via `Depends(get_db)`
- Settings injected via `get_settings()`

**3. Async/Await**:
- Fully async database operations
- Non-blocking I/O for high performance

**4. Configuration Management**:
- Environment-based configuration
- Settings cached with `@lru_cache()`

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

## Production Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DB_HOST | MySQL host | localhost |
| DB_PORT | MySQL port | 3306 |
| DB_USER | MySQL username | root |
| DB_PASSWORD | MySQL password | - |
| DB_NAME | Database name | solar_site_analyzer |
| DEBUG | Enable debug mode | False |
| CORS_ORIGINS | Allowed CORS origins | * |

## Error Handling

The API uses standard HTTP status codes:

- **200 OK** - Successful request
- **400 Bad Request** - Invalid parameters or validation error
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

All errors return JSON with details:
```json
{
  "detail": "Error message description"
}
```
## Redis Caching
This application implements Redis caching to improve API performance by reducing database queries and computation overhead. The caching layer is designed to be transparent, fault-tolerant, and easy to manage.

The following API endpoints implement Redis caching:

| Endpoint | Cache Prefix | TTL | Invalidated By |
|----------|-------------|-----|----------------|
| `GET /api/sites` | `sites_list` | 300s | POST /api/analyze |
| `GET /api/sites/{id}` | `site_detail` | 300s | POST /api/analyze |
| `GET /api/statistics` | `statistics` | 300s | POST /api/analyze |
| `GET /api/export` | `export_data` | 300s | POST /api/analyze |


## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on the GitHub repository.
