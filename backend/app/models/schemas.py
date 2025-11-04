"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class SiteBase(BaseModel):
    """Base site information"""
    site_id: int
    site_name: str
    latitude: float
    longitude: float
    area_sqm: int
    solar_irradiance_kwh: float
    grid_distance_km: float
    slope_degrees: float
    road_distance_km: float
    elevation_m: int
    land_type: str
    region: str


class ScoreBreakdown(BaseModel):
    """Individual score components"""
    solar_irradiance_score: float
    area_score: float
    grid_distance_score: float
    slope_score: float
    infrastructure_score: float


class SiteResponse(BaseModel):
    """Basic site response with scores"""
    site_id: int
    site_name: str
    latitude: float
    longitude: float
    region: str
    land_type: str
    total_suitability_score: Optional[float] = None
    analysis_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class SiteDetailResponse(SiteBase):
    """Detailed site response with full breakdown"""
    solar_irradiance_score: Optional[float] = None
    area_score: Optional[float] = None
    grid_distance_score: Optional[float] = None
    slope_score: Optional[float] = None
    infrastructure_score: Optional[float] = None
    total_suitability_score: Optional[float] = None
    analysis_timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SiteListResponse(BaseModel):
    """Paginated list of sites"""
    total: int
    limit: int
    offset: int
    sites: List[SiteResponse]


class AnalysisWeights(BaseModel):
    """Weights for suitability calculation"""
    solar: float = Field(default=0.35, ge=0, le=1, description="Solar irradiance weight")
    area: float = Field(default=0.25, ge=0, le=1, description="Area weight")
    grid_distance: float = Field(default=0.20, ge=0, le=1, description="Grid distance weight")
    slope: float = Field(default=0.15, ge=0, le=1, description="Slope weight")
    infrastructure: float = Field(default=0.05, ge=0, le=1, description="Infrastructure weight")
    
    @field_validator('solar', 'area', 'grid_distance', 'slope', 'infrastructure')
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Ensure weight is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Weight must be between 0 and 1")
        return v
    
    def validate_sum(self) -> bool:
        """Check if weights sum to approximately 1.0"""
        total = self.solar + self.area + self.grid_distance + self.slope + self.infrastructure
        return abs(total - 1.0) < 0.01


class AnalysisRequest(BaseModel):
    """Request for custom analysis"""
    weights: AnalysisWeights
    
    @field_validator('weights')
    @classmethod
    def validate_weights_sum(cls, v: AnalysisWeights) -> AnalysisWeights:
        """Ensure weights sum to 1.0"""
        if not v.validate_sum():
            raise ValueError("Weights must sum to approximately 1.0")
        return v


class AnalysisResponse(BaseModel):
    """Response after analysis recalculation"""
    success: bool
    message: str
    sites_analyzed: int
    weights_used: AnalysisWeights
    timestamp: datetime


class ScoreDistribution(BaseModel):
    """Score distribution buckets"""
    range_label: str
    count: int
    percentage: float


class RegionalStats(BaseModel):
    """Statistics by region"""
    region: str
    site_count: int
    avg_score: float
    max_score: float
    min_score: float


class LandTypeStats(BaseModel):
    """Statistics by land type"""
    land_type: str
    site_count: int
    avg_score: float
    max_score: float


class StatisticsResponse(BaseModel):
    """Overall statistics response"""
    total_sites: int
    sites_analyzed: int
    average_score: float
    median_score: float
    min_score: float
    max_score: float
    std_deviation: float
    score_distribution: List[ScoreDistribution]
    regional_stats: List[RegionalStats]
    land_type_stats: List[LandTypeStats]
    top_performing_sites: List[SiteResponse]
