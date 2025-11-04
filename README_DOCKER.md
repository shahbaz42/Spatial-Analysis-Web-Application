# Solar Site Analyzer - Docker Deployment Guide

Complete containerized deployment of the Solar Site Analyzer application with MySQL, Redis, FastAPI backend, and Vue.js frontend.

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB free disk space

### One-Command Deployment

```bash
# Clone the repository
git clone <repository-url>
cd solar_site_analyzer

# Create environment file
cp .env.example .env

# Edit .env and add your Mapbox token (required for map visualization)
nano .env  # or use your preferred editor

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

That's it! The application will:
1. ✅ Start MySQL database
2. ✅ Start Redis cache
3. ✅ Create database schema
4. ✅ Load 50 sample sites from CSV
5. ✅ Calculate initial suitability scores
6. ✅ Start FastAPI backend with caching
7. ✅ Build and serve Vue.js frontend

### Access the Application

- **Frontend (Web UI)**: http://localhost
- **Backend API Docs**: http://localhost:8000/docs
- **Backend API Alternative Docs**: http://localhost:8000/redoc
- **API Health Check**: http://localhost:8000/health

## 📦 Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 80 | Vue.js SPA served by Nginx |
| **Backend** | 8000 | FastAPI REST API |
| **MySQL** | 3306 | Database |
| **Redis** | 6379 | Cache layer |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User Browser                      │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Frontend Container (Nginx + Vue.js)  :80           │
│  - Serves static files                              │
│  - Proxies /api to backend                          │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Backend Container (FastAPI)  :8000                 │
│  - REST API endpoints                               │
│  - Business logic                                   │
│  - Auto DB initialization                           │
└─────┬──────────────────────┬────────────────────────┘
      │                      │
      ▼                      ▼
┌──────────────┐    ┌──────────────────┐
│ MySQL :3306  │    │  Redis :6379     │
│ - Site data  │    │  - API cache     │
│ - Scores     │    │  - 300s TTL      │
└──────────────┘    └──────────────────┘
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Database Configuration
DB_USER=solaruser
DB_PASSWORD=solarpassword
DB_NAME=solar_site_analyzer

# Redis Configuration
REDIS_ENABLED=True
REDIS_TTL=300

# API Configuration
DEBUG=False

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=pk.your_actual_mapbox_token_here
```

### Mapbox Token

The frontend requires a Mapbox access token for map visualization:

1. Sign up at https://www.mapbox.com/
2. Create an access token
3. Add it to `.env` as `VITE_MAPBOX_TOKEN`

## 📋 Docker Commands

### Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Start and view logs
docker-compose up

# Start specific service
docker-compose up -d mysql
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f mysql
docker-compose logs -f redis
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build api
docker-compose up -d --build frontend
```

## 🔍 Service Details

### MySQL Database

**Container**: `solar_analyzer_db`
**Image**: `mysql:8.0`
**Data**: Persisted in `mysql_data` volume

```bash
# Access MySQL shell
docker-compose exec mysql mysql -u solaruser -p

# View database
USE solar_site_analyzer;
SHOW TABLES;
SELECT COUNT(*) FROM sites;
```

### Redis Cache

**Container**: `solar_analyzer_redis`
**Image**: `redis:7-alpine`
**Data**: Persisted in `redis_data` volume

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Monitor cache activity
docker-compose exec redis redis-cli MONITOR

# Check keys
docker-compose exec redis redis-cli KEYS "*"

# Clear cache
docker-compose exec redis redis-cli FLUSHDB
```

### Backend API

**Container**: `solar_analyzer_api`
**Build**: `./backend/Dockerfile`
**Initialization**: Automatic via `entrypoint.sh`

The backend automatically:
1. Waits for MySQL to be ready
2. Checks if database is initialized
3. If not initialized:
   - Imports schema from `databaseschema.sql`
   - Loads 50 sites from `data.csv`
   - Calculates initial suitability scores
4. Starts FastAPI server

```bash
# View API logs
docker-compose logs -f api

# Access container shell
docker-compose exec api bash

# Manually reinitialize database
docker-compose exec api python scripts/init_database.py
```

### Frontend

**Container**: `solar_analyzer_frontend`
**Build**: Multi-stage (Node.js builder + Nginx server)
**Nginx**: Configured with gzip, caching, API proxy

```bash
# View frontend logs
docker-compose logs -f frontend

# Access container shell
docker-compose exec frontend sh

# View nginx config
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

## 🔄 Database Reinitialization

If you need to reset the database:

```bash
# Method 1: Stop, remove volumes, and restart
docker-compose down -v
docker-compose up -d

# Method 2: Manual reinitialization
docker-compose exec api python scripts/init_database.py

# Method 3: Import schema only
docker-compose exec api mysql -h mysql -u solaruser -p < databaseschema.sql
```

## 📊 Monitoring

### Health Checks

All services have health checks:

```bash
# Check service health status
docker-compose ps

# Detailed health status
docker inspect --format='{{json .State.Health}}' solar_analyzer_api | jq
docker inspect --format='{{json .State.Health}}' solar_analyzer_frontend | jq
```

### Resource Usage

```bash
# View resource consumption
docker stats

# Specific service stats
docker stats solar_analyzer_api
```

## 🐛 Troubleshooting

### Frontend Not Loading

1. **Check if services are running**:
   ```bash
   docker-compose ps
   ```

2. **Check frontend logs**:
   ```bash
   docker-compose logs frontend
   ```

3. **Verify API is accessible**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Check Mapbox token**:
   - Ensure `VITE_MAPBOX_TOKEN` is set in `.env`
   - Token must be valid and active

### Database Connection Issues

1. **Check MySQL health**:
   ```bash
   docker-compose exec mysql mysqladmin ping
   ```

2. **Verify credentials**:
   ```bash
   docker-compose exec mysql mysql -u solaruser -p
   ```

3. **Check database initialization**:
   ```bash
   docker-compose logs api | grep -i "database\|mysql"
   ```

### Backend API Errors

1. **Check API logs**:
   ```bash
   docker-compose logs -f api
   ```

2. **Verify environment variables**:
   ```bash
   docker-compose exec api env | grep DB_
   ```

3. **Test database connection**:
   ```bash
   docker-compose exec api python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"
   ```

### Redis Cache Issues

1. **Check Redis is running**:
   ```bash
   docker-compose exec redis redis-cli PING
   ```

2. **Monitor cache operations**:
   ```bash
   docker-compose logs api | grep -i cache
   ```

3. **Clear cache if stale**:
   ```bash
   docker-compose exec redis redis-cli FLUSHDB
   docker-compose restart api
   ```

### Port Conflicts

If ports are already in use:

```bash
# Option 1: Change ports in docker-compose.yml
# ports:
#   - "8080:80"     # Frontend
#   - "8001:8000"   # Backend

# Option 2: Stop conflicting services
sudo lsof -i :80
sudo lsof -i :8000
```

### Container Won't Start

1. **Check logs**:
   ```bash
   docker-compose logs <service-name>
   ```

2. **Rebuild container**:
   ```bash
   docker-compose up -d --build <service-name>
   ```

3. **Remove and recreate**:
   ```bash
   docker-compose rm -f <service-name>
   docker-compose up -d <service-name>
   ```

## 🔐 Security Considerations

### Production Deployment

For production environments:

1. **Change default passwords**:
   ```bash
   # In .env
   DB_PASSWORD=<strong-random-password>
   REDIS_PASSWORD=<strong-random-password>
   ```

2. **Enable HTTPS**:
   - Use reverse proxy (Nginx, Traefik, Caddy)
   - Obtain SSL certificate (Let's Encrypt)

3. **Restrict network access**:
   - Don't expose MySQL/Redis ports publicly
   - Use firewall rules
   - Implement rate limiting

4. **Update regularly**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## 📈 Performance Optimization

### Frontend Build Optimization

The frontend Dockerfile uses multi-stage builds:
- **Stage 1**: Build optimized production bundle
- **Stage 2**: Serve with Nginx (lightweight)

Benefits:
- Small image size (~30MB)
- Fast startup time
- Gzip compression enabled
- Static asset caching

### Backend Performance

- Redis caching (60-95% database query reduction)
- Connection pooling
- Async I/O operations
- Health check monitoring

### Database Optimization

```sql
-- Check MySQL performance
docker-compose exec mysql mysql -u root -p -e "SHOW VARIABLES LIKE '%max_connections%';"
docker-compose exec mysql mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
```

## 📦 Backup and Restore

### Backup Database

```bash
# Create backup
docker-compose exec mysql mysqldump -u solaruser -p solar_site_analyzer > backup.sql

# Or with docker directly
docker-compose exec -T mysql mysqldump -u solaruser -psolarpassword solar_site_analyzer > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T mysql mysql -u solaruser -psolarpassword solar_site_analyzer < backup.sql
```

### Backup Volumes

```bash
# Backup MySQL data volume
docker run --rm -v solar_site_analyzer_mysql_data:/data -v $(pwd):/backup ubuntu tar czf /backup/mysql_data_backup.tar.gz -C /data .

# Backup Redis data volume
docker run --rm -v solar_site_analyzer_redis_data:/data -v $(pwd):/backup ubuntu tar czf /backup/redis_data_backup.tar.gz -C /data .
```
