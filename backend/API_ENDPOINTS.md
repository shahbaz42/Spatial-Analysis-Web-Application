# API Endpoints Reference

Complete reference for all Solar Site Analyzer API endpoints.

---

## Base URL
```
http://localhost:8000
```

---

## 1. GET /api/sites

**Description**: Returns all sites with basic information and optional filtering.

### Query Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `min_score` | float | None | 0-100 | Minimum suitability score |
| `max_score` | float | None | 0-100 | Maximum suitability score |
| `limit` | int | 50 | 1-100 | Number of results to return |
| `offset` | int | 0 | 0+ | Number of results to skip |

### Response Example

```json
{
  "total": 50,
  "limit": 10,
  "offset": 0,
  "sites": [
    {
      "site_id": 9,
      "site_name": "Sulur Airbase Adjacent",
      "latitude": 11.0244,
      "longitude": 77.1686,
      "region": "Tamil Nadu",
      "land_type": "Open Land",
      "total_suitability_score": 94.75,
      "analysis_timestamp": "2024-11-03T18:30:00"
    }
  ]
}
```

### cURL Examples

```bash
# Get all sites
curl http://localhost:8000/api/sites

# Get sites with score >= 80
curl "http://localhost:8000/api/sites?min_score=80"

# Get sites with score between 60 and 80
curl "http://localhost:8000/api/sites?min_score=60&max_score=80"

# Paginated results (10 per page, page 2)
curl "http://localhost:8000/api/sites?limit=10&offset=10"

# Top 5 sites
curl "http://localhost:8000/api/sites?limit=5&offset=0"
```

---

## 2. GET /api/sites/{id}

**Description**: Returns detailed information for a specific site including full analysis breakdown.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | int | Yes | Site ID |

### Response Example

```json
{
  "site_id": 1,
  "site_name": "Periyanaickenpalayam Site",
  "latitude": 11.0765,
  "longitude": 76.9872,
  "area_sqm": 45000,
  "solar_irradiance_kwh": 5.8,
  "grid_distance_km": 2.5,
  "slope_degrees": 3.2,
  "road_distance_km": 0.8,
  "elevation_m": 425,
  "land_type": "Agricultural",
  "region": "Tamil Nadu",
  "solar_irradiance_score": 92.0,
  "area_score": 88.89,
  "grid_distance_score": 92.11,
  "slope_score": 100.0,
  "infrastructure_score": 93.33,
  "total_suitability_score": 92.15,
  "analysis_timestamp": "2024-11-03T18:30:00"
}
```

### cURL Examples

```bash
# Get site with ID 1
curl http://localhost:8000/api/sites/1

# Get site with ID 10
curl http://localhost:8000/api/sites/10

# Pretty print with jq
curl http://localhost:8000/api/sites/1 | jq
```

### Error Responses

**404 Not Found**:
```json
{
  "detail": "Site with ID 999 not found"
}
```

---

## 3. POST /api/analyze

**Description**: Triggers recalculation of suitability scores with custom weights.

### Request Body

```json
{
  "weights": {
    "solar": 0.4,
    "area": 0.3,
    "grid_distance": 0.15,
    "slope": 0.1,
    "infrastructure": 0.05
  }
}
```

### Validation Rules

- All weights must be between 0 and 1
- Sum of all weights must equal approximately 1.0 (±0.01)

### Response Example

```json
{
  "success": true,
  "message": "Successfully recalculated scores for 50 sites",
  "sites_analyzed": 50,
  "weights_used": {
    "solar": 0.4,
    "area": 0.3,
    "grid_distance": 0.15,
    "slope": 0.1,
    "infrastructure": 0.05
  },
  "timestamp": "2024-11-03T18:35:00"
}
```

### cURL Examples

```bash
# Default weights (35-25-20-15-5)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "solar": 0.35,
      "area": 0.25,
      "grid_distance": 0.20,
      "slope": 0.15,
      "infrastructure": 0.05
    }
  }'

# Prioritize solar irradiance
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

# Equal weights
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "solar": 0.2,
      "area": 0.2,
      "grid_distance": 0.2,
      "slope": 0.2,
      "infrastructure": 0.2
    }
  }'
```

### Error Responses

**400 Bad Request** (Invalid weights):
```json
{
  "detail": "Weights must sum to approximately 1.0"
}
```

**400 Bad Request** (Out of range):
```json
{
  "detail": "Weight must be between 0 and 1"
}
```

---

## 4. GET /api/statistics

**Description**: Returns summary statistics across all sites.

### Response Example

```json
{
  "total_sites": 50,
  "sites_analyzed": 50,
  "average_score": 73.45,
  "median_score": 75.20,
  "min_score": 42.30,
  "max_score": 94.75,
  "std_deviation": 12.85,
  "score_distribution": [
    {
      "range_label": "80-100 (Excellent)",
      "count": 15,
      "percentage": 30.0
    },
    {
      "range_label": "60-79 (Good)",
      "count": 25,
      "percentage": 50.0
    },
    {
      "range_label": "40-59 (Fair)",
      "count": 10,
      "percentage": 20.0
    }
  ],
  "regional_stats": [
    {
      "region": "Tamil Nadu",
      "site_count": 50,
      "avg_score": 73.45,
      "max_score": 94.75,
      "min_score": 42.30
    }
  ],
  "land_type_stats": [
    {
      "land_type": "Open Land",
      "site_count": 8,
      "avg_score": 82.15,
      "max_score": 94.75
    },
    {
      "land_type": "Agricultural",
      "site_count": 20,
      "avg_score": 75.30,
      "max_score": 89.20
    }
  ],
  "top_performing_sites": [
    {
      "site_id": 9,
      "site_name": "Sulur Airbase Adjacent",
      "latitude": 11.0244,
      "longitude": 77.1686,
      "region": "Tamil Nadu",
      "land_type": "Open Land",
      "total_suitability_score": 94.75,
      "analysis_timestamp": "2024-11-03T18:30:00"
    }
  ]
}
```

### cURL Examples

```bash
# Get all statistics
curl http://localhost:8000/api/statistics

# Pretty print with jq
curl http://localhost:8000/api/statistics | jq

# Extract only top sites
curl http://localhost:8000/api/statistics | jq '.top_performing_sites'

# Extract regional stats
curl http://localhost:8000/api/statistics | jq '.regional_stats'

# Get average score
curl http://localhost:8000/api/statistics | jq '.average_score'
```

---

## 5. GET /api/export

**Description**: Exports filtered results as CSV or JSON.

### Query Parameters

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `format` | string | json | csv, json | Export format |
| `min_score` | float | None | 0-100 | Minimum score filter |

### Response Formats

#### JSON Format
```json
[
  {
    "site_id": 9,
    "site_name": "Sulur Airbase Adjacent",
    "latitude": 11.0244,
    "longitude": 77.1686,
    "area_sqm": 95000,
    "solar_irradiance_kwh": 6.2,
    "grid_distance_km": 0.5,
    "slope_degrees": 0.8,
    "road_distance_km": 0.2,
    "elevation_m": 405,
    "land_type": "Open Land",
    "region": "Tamil Nadu",
    "solar_irradiance_score": 100.0,
    "area_score": 100.0,
    "grid_distance_score": 100.0,
    "slope_score": 100.0,
    "infrastructure_score": 100.0,
    "total_suitability_score": 94.75,
    "analysis_timestamp": "2024-11-03T18:30:00"
  }
]
```

#### CSV Format
```csv
site_id,site_name,latitude,longitude,area_sqm,solar_irradiance_kwh,grid_distance_km,slope_degrees,road_distance_km,elevation_m,land_type,region,solar_irradiance_score,area_score,grid_distance_score,slope_score,infrastructure_score,total_suitability_score,analysis_timestamp
9,Sulur Airbase Adjacent,11.0244,77.1686,95000,6.2,0.5,0.8,0.2,405,Open Land,Tamil Nadu,100.0,100.0,100.0,100.0,100.0,94.75,2024-11-03T18:30:00
```

### cURL Examples

```bash
# Export all sites as JSON
curl "http://localhost:8000/api/export?format=json" > all_sites.json

# Export all sites as CSV
curl "http://localhost:8000/api/export?format=csv" > all_sites.csv

# Export high-scoring sites (>= 80) as CSV
curl "http://localhost:8000/api/export?format=csv&min_score=80" > top_sites.csv

# Export good sites (>= 70) as JSON
curl "http://localhost:8000/api/export?format=json&min_score=70" > good_sites.json

# Export excellent sites (>= 85) as CSV
curl "http://localhost:8000/api/export?format=csv&min_score=85" -o excellent_sites.csv
```

---

## Additional Endpoints

### GET /

**Description**: Root endpoint - API information.

```bash
curl http://localhost:8000/
```

**Response**:
```json
{
  "message": "Solar Site Analyzer API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### GET /health

**Description**: Health check endpoint.

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Solar Site Analyzer API",
  "version": "1.0.0"
}
```

### GET /docs

**Description**: Interactive API documentation (Swagger UI).

Open in browser: http://localhost:8000/docs

### GET /redoc

**Description**: Alternative API documentation (ReDoc).

Open in browser: http://localhost:8000/redoc

---

## Error Handling

All endpoints return standard HTTP status codes:

### Success Codes

- **200 OK**: Successful GET request
- **201 Created**: Successful POST request

### Client Error Codes

- **400 Bad Request**: Invalid parameters or validation error
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Invalid request body

### Server Error Codes

- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Descriptive error message"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider adding rate limiting middleware.

---

## Authentication

Currently no authentication is required. For production use, consider adding JWT-based authentication.

---

## CORS

CORS is enabled for all origins by default. Configure in `.env`:

```env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Get sites
response = requests.get(f"{BASE_URL}/api/sites", params={"min_score": 80})
print(response.json())

# Analyze with custom weights
response = requests.post(
    f"{BASE_URL}/api/analyze",
    json={
        "weights": {
            "solar": 0.4,
            "area": 0.3,
            "grid_distance": 0.15,
            "slope": 0.1,
            "infrastructure": 0.05
        }
    }
)
print(response.json())

# Get statistics
response = requests.get(f"{BASE_URL}/api/statistics")
print(response.json())
```

---

## Testing with JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Get sites
axios.get(`${BASE_URL}/api/sites`, {
  params: { min_score: 80 }
}).then(response => {
  console.log(response.data);
});

// Analyze with custom weights
axios.post(`${BASE_URL}/api/analyze`, {
  weights: {
    solar: 0.4,
    area: 0.3,
    grid_distance: 0.15,
    slope: 0.1,
    infrastructure: 0.05
  }
}).then(response => {
  console.log(response.data);
});

// Get statistics
axios.get(`${BASE_URL}/api/statistics`)
  .then(response => {
    console.log(response.data);
  });
```

---

## OpenAPI Schema

The full OpenAPI 3.0 schema is available at:

```
http://localhost:8000/openapi.json
```

---

For more information, visit the interactive documentation at http://localhost:8000/docs
