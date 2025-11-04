"""
Database initialization script
Loads data from CSV and calculates initial scores
"""

import asyncio
import csv
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import get_db_context
from app.services.analysis_service import AnalysisService
from app.models.schemas import AnalysisWeights


async def load_csv_data(csv_file: str):
    """Load site data from CSV file into database"""
    
    print(f"Loading data from {csv_file}...")
    
    async with get_db_context() as db:
        # Read CSV file
        sites_data = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sites_data.append(row)
        
        print(f"Found {len(sites_data)} sites in CSV")
        
        # Insert sites into database
        insert_query = text("""
            INSERT INTO sites (
                site_id, site_name, latitude, longitude, area_sqm,
                solar_irradiance_kwh, grid_distance_km, slope_degrees,
                road_distance_km, elevation_m, land_type, region
            ) VALUES (
                :site_id, :site_name, :latitude, :longitude, :area_sqm,
                :solar_irradiance_kwh, :grid_distance_km, :slope_degrees,
                :road_distance_km, :elevation_m, :land_type, :region
            ) ON DUPLICATE KEY UPDATE
                site_name = VALUES(site_name),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                area_sqm = VALUES(area_sqm),
                solar_irradiance_kwh = VALUES(solar_irradiance_kwh),
                grid_distance_km = VALUES(grid_distance_km),
                slope_degrees = VALUES(slope_degrees),
                road_distance_km = VALUES(road_distance_km),
                elevation_m = VALUES(elevation_m),
                land_type = VALUES(land_type),
                region = VALUES(region)
        """)
        
        for site in sites_data:
            await db.execute(insert_query, site)
        
        await db.commit()
        print(f"Successfully inserted/updated {len(sites_data)} sites")


async def calculate_initial_scores():
    """Calculate initial suitability scores for all sites"""
    
    print("Calculating initial suitability scores...")
    
    async with get_db_context() as db:
        # Use default weights
        default_weights = AnalysisWeights()
        
        # Perform analysis
        result = await AnalysisService.recalculate_all_sites(db, default_weights)
        
        print(f"Successfully calculated scores for {result.sites_analyzed} sites")
        return result


async def main():
    """Main initialization function"""
    
    print("=" * 60)
    print("Solar Site Analyzer - Database Initialization")
    print("=" * 60)
    
    # Get CSV file path
    csv_file = Path(__file__).parent.parent / "data.csv"
    
    if not csv_file.exists():
        print(f"Error: CSV file not found at {csv_file}")
        sys.exit(1)
    
    try:
        # Load data from CSV
        await load_csv_data(str(csv_file))
        
        # Calculate initial scores
        await calculate_initial_scores()
        
        print("\n" + "=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)
        print("\nYou can now start the API server:")
        print("  python -m uvicorn app.main:app --reload")
        print("\nOr visit the API docs at:")
        print("  http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\nError during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
