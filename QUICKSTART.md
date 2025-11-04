# Quick Start Guide

Get the Solar Site Analyzer running in under 5 minutes!

## 🚀 Fastest Way (Docker)

### Step 1: Prerequisites

Make sure you have Docker and Docker Compose installed:

```bash
# Check Docker
docker --version
# Should show: Docker version 20.10.x or higher

# Check Docker Compose
docker compose --version
# Should show: Docker Compose version 2.x or higher
```

If not installed:
- **Windows/Mac**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

### Step 2: Clone and Configure

```bash
# Clone the repository
git clone <your-repository-url>
cd solar_site_analyzer

# Create environment file
cp .env.example .env
```

### Step 3: Add Mapbox Token (Required)

1. Get a free token from [Mapbox](https://www.mapbox.com/)
2. Edit `.env` and add your token:
   ```bash
   nano .env  # or use any editor
   ```
   
   Update this line:
   ```
   VITE_MAPBOX_TOKEN=pk.your_actual_mapbox_token_here
   ```

### Step 4: Start Everything

```bash
# Start all services (one command!)
docker compose up -d
```

This will:
- ✅ Pull Docker images (MySQL, Redis)
- ✅ Build backend and frontend
- ✅ Create database and tables
- ✅ Load 50 sample sites
- ✅ Calculate initial scores
- ✅ Start all services

**First run takes 2-3 minutes. Subsequent starts take ~10 seconds.**

### Step 5: Access the Application

Open your browser:
- **🌐 Frontend (Main App)**: http://localhost
- **📚 API Docs**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/health

### Step 6: Verify Everything Works

```bash
# Check all services are running
docker-compose ps

# You should see 4 services: mysql, redis, api, frontend
# All should be "Up" and "healthy"
```

### Step 7: View Logs (Optional)

```bash
# See what's happening
docker-compose logs -f

# Or for specific service
docker-compose logs -f api
docker-compose logs -f frontend
```

## 🎉 That's It!

You now have a fully functional Solar Site Analyzer with:
- 50 pre-loaded sites across India
- Interactive map visualization
- Real-time score recalculation
- Comprehensive API
- Redis caching for performance

## 🎮 Try These Features

1. **View Sites on Map**: Click markers to see site details
2. **Filter by Score**: Use the sidebar score range filter
3. **Adjust Weights**: Change importance of factors and recalculate
4. **View Statistics**: Check the statistics dashboard
5. **Export Data**: Download sites as CSV or JSON

## 🛑 Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (complete reset)
docker-compose down -v
```

## 🔄 Restart or Update

```bash
# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# View updated logs
docker-compose logs -f
```

## ❓ Troubleshooting

### Port Already in Use?

If port 80 or 8000 is already in use:

```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :8000

# Option 1: Stop the conflicting service
# Option 2: Change ports in docker-compose.yml:
#   ports:
#     - "8080:80"     # Frontend on port 8080
#     - "8001:8000"   # Backend on port 8001
```

### Map Not Loading?

- Ensure you added a valid Mapbox token to `.env`
- Check browser console for errors (F12)
- Verify frontend is running: `docker-compose ps frontend`

### Database Issues?

```bash
# Check database initialization
docker-compose logs api | grep -i database

# Manually reinitialize if needed
docker-compose down -v
docker-compose up -d
```

### Services Won't Start?

```bash
# View detailed logs
docker-compose logs

# Try rebuilding
docker-compose down
docker-compose up -d --build

# Check Docker status
docker info
```

## 📖 Next Steps

- Read the full [README.md](./README.md)
- Check [README_DOCKER.md](./README_DOCKER.md) for advanced Docker usage
- Explore the [API documentation](http://localhost:8000/docs)
- Customize weights and analyze your own solar sites!
