## API Endpoint Specifications

### Required Endpoints

1. **GET /api/sites**
   - Returns all sites with basic information
   - Query parameters: `min_score`, `max_score`, `limit`, `offset`

2. **GET /api/sites/{id}**
   - Returns detailed information for a specific site
   - Includes full analysis breakdown

3. **POST /api/analyze**
   - Triggers recalculation with custom weights
   - Request body: `{ "weights": { "solar": 0.4, "area": 0.3, ... } }`

4. **GET /api/statistics**
   - Returns summary statistics across all sites
   - Average scores, distributions, etc.

5. **GET /api/export**
   - Exports filtered results as CSV or JSON
   - Query parameters: `format`, `min_score`


## Spatial Analysis Formula

Calculate the suitability score (0-100) using weighted average:

```
Suitability Score = (
    solar_irradiance_score * 0.35 +
    area_score * 0.25 +
    grid_distance_score * 0.20 +
    slope_score * 0.15 +
    infrastructure_score * 0.05
)
```

**Individual Score Calculations:**

1. **Solar Irradiance Score** (0-100):
   - 100: >= 5.5 kWh/m²/day
   - Proportional scaling down to 0 for < 3.0 kWh/m²/day

2. **Area Score** (0-100):
   - 100: >= 50,000 m²
   - Proportional scaling down to 0 for < 5,000 m²

3. **Grid Distance Score** (0-100):
   - 100: <= 1 km
   - 0: >= 20 km
   - Linear inverse relationship

4. **Slope Score** (0-100):
   - 100: 0-5 degrees
   - 50: 5-15 degrees
   - 0: > 20 degrees

5. **Infrastructure Score** (0-100):
   - Based on proximity to roads/utilities
   - 100: <= 0.5 km
   - 0: >= 5 km

---
