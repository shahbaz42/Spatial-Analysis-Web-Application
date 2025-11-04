"""Analysis service for calculating suitability scores"""

from typing import Dict, Tuple
from decimal import Decimal
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.models.schemas import AnalysisWeights, AnalysisResponse


class AnalysisService:
    """Service for handling suitability analysis calculations"""
    
    @staticmethod
    def calculate_solar_score(solar_irradiance: float) -> float:
        """
        Calculate solar irradiance score (0-100)
        100: >= 5.5 kWh/m²/day
        0: < 3.0 kWh/m²/day
        """
        if solar_irradiance >= 5.5:
            return 100.0
        elif solar_irradiance < 3.0:
            return 0.0
        else:
            return ((solar_irradiance - 3.0) / 2.5) * 100
    
    @staticmethod
    def calculate_area_score(area: int) -> float:
        """
        Calculate area score (0-100)
        100: >= 50,000 m²
        0: < 5,000 m²
        """
        if area >= 50000:
            return 100.0
        elif area < 5000:
            return 0.0
        else:
            return ((area - 5000) / 45000) * 100
    
    @staticmethod
    def calculate_grid_distance_score(distance: float) -> float:
        """
        Calculate grid distance score (0-100, inverse relationship)
        100: <= 1 km
        0: >= 20 km
        """
        if distance <= 1:
            return 100.0
        elif distance >= 20:
            return 0.0
        else:
            return 100 - ((distance - 1) / 19) * 100
    
    @staticmethod
    def calculate_slope_score(slope: float) -> float:
        """
        Calculate slope score (0-100)
        100: 0-5 degrees
        50: 5-15 degrees
        0: > 20 degrees
        """
        if slope <= 5:
            return 100.0
        elif slope > 20:
            return 0.0
        elif slope <= 15:
            return 100 - ((slope - 5) / 10) * 50
        else:
            return 50 - ((slope - 15) / 5) * 50
    
    @staticmethod
    def calculate_infrastructure_score(road_distance: float) -> float:
        """
        Calculate infrastructure score (0-100, based on road proximity)
        100: <= 0.5 km
        0: >= 5 km
        """
        if road_distance <= 0.5:
            return 100.0
        elif road_distance >= 5:
            return 0.0
        else:
            return 100 - ((road_distance - 0.5) / 4.5) * 100
    
    @staticmethod
    def calculate_total_score(
        solar_score: float,
        area_score: float,
        grid_score: float,
        slope_score: float,
        infra_score: float,
        weights: AnalysisWeights
    ) -> float:
        """Calculate weighted total suitability score"""
        return (
            solar_score * weights.solar +
            area_score * weights.area +
            grid_score * weights.grid_distance +
            slope_score * weights.slope +
            infra_score * weights.infrastructure
        )
    
    @staticmethod
    def calculate_all_scores(
        solar_irradiance: float,
        area: int,
        grid_distance: float,
        slope: float,
        road_distance: float,
        weights: AnalysisWeights
    ) -> Tuple[float, float, float, float, float, float]:
        """
        Calculate all individual scores and total score
        Returns: (solar, area, grid, slope, infra, total)
        """
        solar_score = AnalysisService.calculate_solar_score(solar_irradiance)
        area_score = AnalysisService.calculate_area_score(area)
        grid_score = AnalysisService.calculate_grid_distance_score(grid_distance)
        slope_score = AnalysisService.calculate_slope_score(slope)
        infra_score = AnalysisService.calculate_infrastructure_score(road_distance)
        
        total_score = AnalysisService.calculate_total_score(
            solar_score, area_score, grid_score, slope_score, infra_score, weights
        )
        
        return solar_score, area_score, grid_score, slope_score, infra_score, total_score
    
    @staticmethod
    async def recalculate_all_sites(
        db: AsyncSession,
        weights: AnalysisWeights
    ) -> AnalysisResponse:
        """
        Recalculate suitability scores for all sites with custom weights
        """
        # First, update the weights in the database
        await AnalysisService._update_weights(db, weights)
        
        # Fetch all sites
        query = text("""
            SELECT 
                site_id, solar_irradiance_kwh, area_sqm, 
                grid_distance_km, slope_degrees, road_distance_km
            FROM sites
        """)
        
        result = await db.execute(query)
        sites = result.fetchall()
        
        # Calculate scores for each site
        sites_analyzed = 0
        for site in sites:
            scores = AnalysisService.calculate_all_scores(
                solar_irradiance=float(site.solar_irradiance_kwh),
                area=site.area_sqm,
                grid_distance=float(site.grid_distance_km),
                slope=float(site.slope_degrees),
                road_distance=float(site.road_distance_km),
                weights=weights
            )
            
            # Insert new analysis result
            insert_query = text("""
                INSERT INTO analysis_results (
                    site_id, solar_irradiance_score, area_score, 
                    grid_distance_score, slope_score, infrastructure_score,
                    total_suitability_score, parameters_snapshot
                ) VALUES (
                    :site_id, :solar_score, :area_score,
                    :grid_score, :slope_score, :infra_score,
                    :total_score, :params_json
                )
            """)
            
            params_snapshot = json.dumps({
                "solar_weight": weights.solar,
                "area_weight": weights.area,
                "grid_weight": weights.grid_distance,
                "slope_weight": weights.slope,
                "infra_weight": weights.infrastructure
            })
            
            await db.execute(insert_query, {
                "site_id": site.site_id,
                "solar_score": scores[0],
                "area_score": scores[1],
                "grid_score": scores[2],
                "slope_score": scores[3],
                "infra_score": scores[4],
                "total_score": scores[5],
                "params_json": params_snapshot
            })
            sites_analyzed += 1
        
        await db.commit()
        
        return AnalysisResponse(
            success=True,
            message=f"Successfully recalculated scores for {sites_analyzed} sites",
            sites_analyzed=sites_analyzed,
            weights_used=weights,
            timestamp=datetime.now()
        )
    
    @staticmethod
    async def _update_weights(db: AsyncSession, weights: AnalysisWeights):
        """Update weights in the analysis_parameters table"""
        weight_mappings = {
            "solar_irradiance_weight": weights.solar,
            "area_weight": weights.area,
            "grid_distance_weight": weights.grid_distance,
            "slope_weight": weights.slope,
            "infrastructure_weight": weights.infrastructure
        }
        
        for param_name, weight_value in weight_mappings.items():
            query = text("""
                UPDATE analysis_parameters 
                SET weight_value = :weight_value,
                    updated_at = CURRENT_TIMESTAMP
                WHERE parameter_name = :param_name
            """)
            await db.execute(query, {
                "weight_value": weight_value,
                "param_name": param_name
            })
        
        await db.commit()
