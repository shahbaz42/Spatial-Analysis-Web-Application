"""Export API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal
import csv
import io
import json

from app.database import get_db
from app.services.site_service import SiteService

router = APIRouter(tags=["Export"])


@router.get(
    "/export",
    summary="Export filtered results",
    description="Exports filtered site results as CSV or JSON format"
)
async def export_sites(
    format: Literal["csv", "json"] = Query(
        "json",
        description="Export format (csv or json)"
    ),
    min_score: Optional[float] = Query(
        None,
        ge=0,
        le=100,
        description="Minimum suitability score filter"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Export filtered site data in CSV or JSON format.
    
    **Query Parameters:**
    - **format**: Output format - 'csv' or 'json' (default: json)
    - **min_score**: Minimum suitability score filter (optional)
    
    **Returns:**
    - CSV file download (if format=csv)
    - JSON array (if format=json)
    
    **Exported Fields:**
    - Site identification and location
    - Physical attributes
    - Individual score components
    - Total suitability score
    - Analysis timestamp
    """
    try:
        sites_data = await SiteService.export_sites(
            db=db,
            min_score=min_score
        )
        
        if format == "csv":
            return _export_as_csv(sites_data)
        else:  # json
            return JSONResponse(content=sites_data)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export sites: {str(e)}"
        )


def _export_as_csv(data: list) -> StreamingResponse:
    """
    Convert data to CSV format and return as streaming response
    """
    if not data:
        # Return empty CSV with headers only
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "site_id", "site_name", "latitude", "longitude",
            "area_sqm", "solar_irradiance_kwh", "grid_distance_km",
            "slope_degrees", "road_distance_km", "elevation_m",
            "land_type", "region",
            "solar_irradiance_score", "area_score",
            "grid_distance_score", "slope_score",
            "infrastructure_score", "total_suitability_score",
            "analysis_timestamp"
        ])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sites_export.csv"}
        )
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sites_export.csv"}
    )
