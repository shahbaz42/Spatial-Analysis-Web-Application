"""Sites API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services.site_service import SiteService
from app.models.schemas import SiteListResponse, SiteDetailResponse
from app.cache import CacheManager

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get(
    "",
    response_model=SiteListResponse,
    summary="Get all sites",
    description="Returns all sites with basic information and optional filtering by score range"
)
async def get_sites(
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
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Number of results to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of results to skip"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a paginated list of sites with optional score filtering.
    
    **Query Parameters:**
    - **min_score**: Filter sites with score >= this value
    - **max_score**: Filter sites with score <= this value
    - **limit**: Maximum number of results (1-100)
    - **offset**: Number of results to skip for pagination
    
    **Returns:**
    - Paginated list of sites with basic information and scores
    """
    # Validate score range
    if min_score is not None and max_score is not None and min_score > max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_score cannot be greater than max_score"
        )
    
    # Generate cache key
    cache_key = CacheManager.generate_cache_key(
        "sites_list",
        min_score=min_score,
        max_score=max_score,
        limit=limit,
        offset=offset
    )
    
    # Try cache first
    cached_result = await CacheManager.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        result = await SiteService.get_sites(
            db=db,
            min_score=min_score,
            max_score=max_score,
            limit=limit,
            offset=offset
        )
        
        # Cache the result
        await CacheManager.set(cache_key, result)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sites: {str(e)}"
        )


@router.get(
    "/{site_id}",
    response_model=SiteDetailResponse,
    summary="Get site by ID",
    description="Returns detailed information for a specific site including full analysis breakdown"
)
async def get_site_by_id(
    site_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve detailed information for a specific site.
    
    **Path Parameters:**
    - **site_id**: Unique identifier of the site
    
    **Returns:**
    - Complete site information including:
        - Geographic and physical attributes
        - Individual score components
        - Total suitability score
        - Analysis timestamp
    """
    # Generate cache key
    cache_key = CacheManager.generate_cache_key("site_detail", site_id=site_id)
    
    # Try cache first
    cached_result = await CacheManager.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        site = await SiteService.get_site_by_id(db=db, site_id=site_id)
        
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Site with ID {site_id} not found"
            )
        
        # Cache the result
        await CacheManager.set(cache_key, site)
        
        return site
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve site: {str(e)}"
        )
