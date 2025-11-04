"""Analysis API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services.analysis_service import AnalysisService
from app.services.site_service import SiteService
from app.models.schemas import AnalysisRequest, AnalysisResponse, StatisticsResponse
from app.cache import CacheManager, invalidate_cache

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Recalculate scores with custom weights",
    description="Triggers recalculation of suitability scores for all sites using custom weight values"
)
async def analyze_with_custom_weights(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Recalculate suitability scores for all sites with custom weights.
    
    **Request Body:**
    ```json
    {
        "weights": {
            "solar": 0.4,
            "area": 0.3,
            "grid_distance": 0.2,
            "slope": 0.08,
            "infrastructure": 0.02
        }
    }
    ```
    
    **Requirements:**
    - All weights must be between 0 and 1
    - Sum of all weights must equal approximately 1.0
    
    **Returns:**
    - Analysis result with number of sites processed
    - Weights used in the calculation
    - Timestamp of the analysis
    """
    try:
        result = await AnalysisService.recalculate_all_sites(
            db=db,
            weights=request.weights
        )
        
        # Invalidate all cached data since scores have been recalculated
        await invalidate_cache("sites_list")
        await invalidate_cache("site_detail")
        await invalidate_cache("statistics")
        await invalidate_cache("export_data")
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform analysis: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Get summary statistics",
    description="Returns comprehensive statistics across all sites including distributions and rankings"
)
async def get_statistics(
    min_score: Optional[float] = Query(
        None,
        ge=0,
        le=100,
        description="Minimum suitability score filter"
    ),
    max_score: Optional[float] = Query(
        None,
        ge=0,
        le=100,
        description="Maximum suitability score filter"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve comprehensive statistics across all sites or filtered results.
    
    **Query Parameters:**
    - **min_score**: Minimum suitability score filter (optional)
    - **max_score**: Maximum suitability score filter (optional)
    
    **Returns:**
    - **Overall metrics**: Total sites, average/median/min/max scores, standard deviation
    - **Score distribution**: Count and percentage of sites in each score range
    - **Regional statistics**: Average, max, and min scores by region
    - **Land type statistics**: Average and max scores by land type
    - **Top performers**: Top 10 sites by suitability score
    """
    # Generate cache key
    cache_key = CacheManager.generate_cache_key(
        "statistics",
        min_score=min_score,
        max_score=max_score
    )
    
    # Try cache first
    cached_result = await CacheManager.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        statistics = await SiteService.get_statistics(
            db=db,
            min_score=min_score,
            max_score=max_score
        )
        
        # Cache the result
        await CacheManager.set(cache_key, statistics)
        
        return statistics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )
