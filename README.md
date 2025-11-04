# Solar Site Analyzer

A comprehensive full-stack application for analyzing and managing solar panel installation site suitability using spatial data analysis, machine learning scoring, and interactive visualization.

## 🌟 Features

- **Interactive Map Visualization** - Mapbox GL JS powered interface
- **Intelligent Site Scoring** - Multi-factor weighted analysis algorithm
- **Real-time Analysis** - Custom weight adjustment and instant recalculation
- **High Performance** - Redis caching and async database operations
- **REST API** - Comprehensive FastAPI backend with auto-documentation
- **Modern Frontend** - Vue 3 with TypeScript and Tailwind CSS
- **Production Ready** - Docker containerization with auto-initialization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Solar Site Analyzer                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Frontend (Vue.js 3 + TypeScript)                   │
│  ├─ Interactive Mapbox visualization                │
│  ├─ Site cards and filtering                        │
│  ├─ Weight adjustment controls                      │
│  └─ Real-time statistics dashboard                  │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Backend (FastAPI + Python 3.11)                    │
│  ├─ RESTful API endpoints                           │
│  ├─ MySQL stored procedure integration              │
│  ├─ Redis caching layer                             │
│  └─ Automatic database initialization               │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Data Layer                                          │
│  ├─ MySQL 8.0 (persistent storage)                  │
│  └─ Redis 7 (caching)                               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start with Docker (Recommended)

**Prerequisites**: Docker & Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd solar_site_analyzer

# Configure environment (REQUIRED)
cp .env.example .env
nano .env  # Add your Mapbox token (get free token from mapbox.com)
# Set: VITE_MAPBOX_TOKEN=pk.eyJ1Ijoi...your_token_here

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost
# API Docs: http://localhost:8000/docs
```

**That's it!** The system automatically:
- ✅ Creates database schema
- ✅ Loads 50 sample sites
- ✅ Calculates initial scores
- ✅ Starts all services

📖 **Full Docker Guide**: [README_DOCKER.md](./README_DOCKER.md)

## 🔐 Environment Configuration

### Required Setup

Create a `.env` file from the template:

```bash
cp .env.example .env
```

### Important Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_MAPBOX_TOKEN` | **Yes** | Your Mapbox access token (get free at [mapbox.com](https://mapbox.com)) |
| `DB_PASSWORD` | Yes | Database password |
| `VITE_API_BASE_URL` | No | API endpoint (default: `http://localhost:8000`) |
| `REDIS_ENABLED` | No | Enable caching (default: `True`) |

### Security Best Practices

✅ **DO**:
- Keep `.env` file in your `.gitignore` (already configured)
- Use strong passwords in production
- Get your own Mapbox token (free tier available)
- Share `.env.example` in repository (template only)

❌ **DON'T**:
- Never commit `.env` file to Git
- Don't hardcode tokens in `docker-compose.yml` for public repos
- Don't share your `.env` file or tokens publicly

### Rebuild After Token Changes

If you update `VITE_MAPBOX_TOKEN` in `.env` after initial build:

```bash
docker compose build frontend  # Rebuild with new token
docker compose up -d            # Restart services
```

> **Why?** Vite environment variables are embedded at build time, not runtime.

## 📦 Project Structure

```
solar_site_analyzer/
├── frontend/                # Vue.js 3 application
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── stores/         # Pinia state management
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript definitions
│   ├── Dockerfile          # Frontend container
│   └── package.json
│
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Data models
│   │   ├── cache.py        # Redis cache manager
│   │   ├── config.py       # Configuration
│   │   └── main.py         # Application entry
│   ├── scripts/
│   │   └── init_database.py # DB initialization
│   ├── Dockerfile          # Backend container
│   ├── entrypoint.sh       # Auto-initialization script
│   ├── databaseschema.sql  # MySQL schema & procedures
│   ├── data.csv            # Sample site data (50 sites)
│   └── requirements.txt
│
├── docker-compose.yml      # Unified orchestration
├── .env.example            # Environment template
└── README_DOCKER.md        # Docker deployment guide
```

## 🎯 Core Functionality

### Site Suitability Analysis

The system calculates a comprehensive suitability score (0-100) based on:

| Factor | Default Weight | Description |
|--------|---------------|-------------|
| **Solar Irradiance** | 35% | Daily solar energy potential (kWh/m²/day) |
| **Available Area** | 25% | Land area available for panels (m²) |
| **Grid Distance** | 20% | Proximity to power grid (km) |
| **Terrain Slope** | 15% | Ground slope suitability (degrees) |
| **Infrastructure** | 5% | Road access and proximity (km) |

**Custom Weights**: Users can adjust weights in real-time via the UI

### Calculation Logic

Implemented in **MySQL stored procedures** for optimal performance:

```sql
-- Individual component scores (0-100 scale)
Solar Score = f(irradiance)      -- 100 if ≥5.5 kWh/m²/day
Area Score = f(area)             -- 100 if ≥50,000 m²
Grid Score = f(distance)         -- 100 if ≤1 km (inverse)
Slope Score = f(degrees)         -- 100 if ≤5°
Infrastructure = f(road_dist)    -- 100 if ≤0.5 km

-- Weighted total
Total Score = Σ(component_score × weight)
```

## 📡 API Endpoints

### Sites
- `GET /api/sites` - List all sites (paginated, filterable)
- `GET /api/sites/{id}` - Get site details

### Analysis
- `POST /api/analyze` - Recalculate scores with custom weights
- `GET /api/statistics` - Comprehensive statistics

### Export
- `GET /api/export?format=csv` - Export as CSV
- `GET /api/export?format=json` - Export as JSON

**Interactive Docs**: http://localhost:8000/docs

## 🔧 Technology Stack

### Frontend
- **Framework**: Vue.js 3 (Composition API)
- **Language**: TypeScript
- **State**: Pinia
- **Styling**: Tailwind CSS
- **Maps**: Mapbox GL JS
- **Charts**: Chart.js
- **Icons**: Lucide Vue
- **Build**: Vite
- **Server**: Nginx (production)

### Backend
- **Framework**: FastAPI 0.104
- **Language**: Python 3.11
- **ORM**: SQLAlchemy 2.0 (async)
- **Cache**: Redis 5.0
- **Validation**: Pydantic 2.5
- **Server**: Uvicorn

### Database
- **Primary**: MySQL 8.0
- **Cache**: Redis 7
- **Features**: Stored procedures, views, functions

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (frontend proxy)
- **Init**: Automated database setup

## 🚦 Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 7+ (optional, for caching)

### Backend Local Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Update DB credentials

# Initialize database
mysql -u root -p < databaseschema.sql
python scripts/init_database.py

# Start server
python -m uvicorn app.main:app --reload
```

### Frontend Local Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
nano .env  # Add Mapbox token

# Start dev server
npm run dev
```

## 📊 Performance

### Caching Benefits (Redis)

| Endpoint | Without Cache | With Cache | Speedup |
|----------|--------------|------------|---------|
| GET /sites | 50-200ms | 2-5ms | **40-100x** |
| GET /sites/{id} | 30-100ms | 2-5ms | **15-50x** |
| GET /statistics | 100-500ms | 2-5ms | **50-250x** |

Cache automatically invalidates on data changes.

## 🔒 Security Features

- Input validation (Pydantic)
- SQL injection prevention (parameterized queries)
- CORS configuration
- Health check endpoints
- Nginx security headers
- Environment-based secrets

## 📚 Documentation

- **API Documentation**: Auto-generated Swagger UI at `/docs`
- **Docker Guide**: [README_DOCKER.md](./README_DOCKER.md)
- **Backend README**: [backend/README.md](./backend/README.md)
- **Frontend README**: [frontend/README.md](./frontend/README.md)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# Type checking
npm run type-check
```
