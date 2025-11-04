# Quick Start Guide

Get the Solar Site Analyzer API up and running in minutes!

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

## Option 2: Docker Setup (Recommended for Production)

### Prerequisites
- Docker
- Docker Compose

### Step 1: Start Everything

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 2: Initialize Database

```bash
# Run initialization inside container
docker-compose exec api python scripts/init_database.py
```

### Step 3: Access the API

- **API Docs**: http://localhost:8000/docs
- **API Root**: http://localhost:8000

### Stop Services

```bash
docker-compose down

# To remove volumes (all data)
docker-compose down -v
```

---

## Quick Test Commands

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Get All Sites
```bash
curl http://localhost:8000/api/sites?limit=5
```

### 3. Get Top Scoring Sites
```bash
curl "http://localhost:8000/api/sites?min_score=80&limit=10"
```

### 4. Get Specific Site Details
```bash
curl http://localhost:8000/api/sites/1
```

### 5. Get Statistics
```bash
curl http://localhost:8000/api/statistics
```

### 6. Recalculate with Custom Weights
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "solar": 0.4,
      "area": 0.3,
      "grid_distance": 0.15,
      "slope": 0.1,
      "infrastructure": 0.05
    }
  }'
```

### 7. Export as CSV
```bash
curl "http://localhost:8000/api/export?format=csv&min_score=70" -o sites.csv
```

### 8. Export as JSON
```bash
curl "http://localhost:8000/api/export?format=json" -o sites.json
```

---

## Troubleshooting

### Database Connection Error

**Problem**: `Can't connect to MySQL server`

**Solution**:
1. Check MySQL is running: `sudo systemctl status mysql`
2. Verify credentials in `.env` file
3. Check if database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### Import Error

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
1. Ensure you're in the backend directory
2. Activate virtual environment: `source .venv/bin/activate`
3. Reinstall requirements: `pip install -r requirements.txt`

### Port Already in Use

**Problem**: `Address already in use: 0.0.0.0:8000`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Database Already Initialized

**Problem**: Duplicate key errors when running init script

**Solution**: 
The script uses `ON DUPLICATE KEY UPDATE`, so it's safe to rerun. If you want a fresh start:
```sql
-- In MySQL
USE solar_site_analyzer;
TRUNCATE TABLE analysis_results;
TRUNCATE TABLE sites;
```

Then rerun: `python scripts/init_database.py`

---

## Next Steps

1. **Explore the API Documentation**: Visit http://localhost:8000/docs
2. **Try Different Endpoints**: Use the interactive Swagger UI to test all endpoints
3. **Customize Analysis**: Experiment with different weight combinations
4. **Export Data**: Download filtered results for further analysis
5. **Check Statistics**: View comprehensive analytics at `/api/statistics`

---

## Common Use Cases

### Find Best Sites for Solar Installation
```bash
curl "http://localhost:8000/api/sites?min_score=85&limit=20"
```

### Analyze with High Solar Priority
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "solar": 0.5,
      "area": 0.2,
      "grid_distance": 0.15,
      "slope": 0.1,
      "infrastructure": 0.05
    }
  }'
```

### Get Regional Performance
```bash
curl http://localhost:8000/api/statistics | jq '.regional_stats'
```

### Export High-Scoring Sites
```bash
curl "http://localhost:8000/api/export?format=csv&min_score=75" > best_sites.csv
```

---

## Development Tips

### Enable Debug Mode
In `.env`:
```
DEBUG=True
```

### Watch for Changes
The `--reload` flag automatically restarts on code changes:
```bash
uvicorn app.main:app --reload
```

### Test API with HTTPie (Alternative to curl)
```bash
# Install httpie
pip install httpie

# Use it
http GET http://localhost:8000/api/sites limit==5
```

### Pretty Print JSON Responses
```bash
curl http://localhost:8000/api/statistics | python -m json.tool
# or with jq
curl http://localhost:8000/api/statistics | jq .
```

---

For detailed documentation, see [README.md](README.md)
