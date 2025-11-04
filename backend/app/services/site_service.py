"""Site service for database operations"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import statistics

from app.models.schemas import (
    SiteResponse,
    SiteDetailResponse,
    SiteListResponse,
    StatisticsResponse,
    ScoreDistribution,
    RegionalStats,
    LandTypeStats
)


class SiteService:
    """Service for handling site-related operations"""
    
    @staticmethod
    async def get_sites(
        db: AsyncSession,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> SiteListResponse:
        """
        Get all sites with optional filtering and pagination
        """
        # Build WHERE clause
        where_conditions = []
        params = {"limit": limit, "offset": offset}
        
        if min_score is not None:
            where_conditions.append("total_suitability_score >= :min_score")
            params["min_score"] = min_score
        
        if max_score is not None:
            where_conditions.append("total_suitability_score <= :max_score")
            params["max_score"] = max_score
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Count query
        count_query = text(f"""
            SELECT COUNT(*) as total
            FROM sites_with_scores
            {where_clause}
        """)
        
        count_result = await db.execute(count_query, params)
        total = count_result.scalar() or 0
        
        # Data query
        data_query = text(f"""
            SELECT 
                site_id, site_name, latitude, longitude, 
                region, land_type, total_suitability_score, 
                analysis_timestamp
            FROM sites_with_scores
            {where_clause}
            ORDER BY total_suitability_score DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = await db.execute(data_query, params)
        rows = result.fetchall()
        
        sites = [
            SiteResponse(
                site_id=row.site_id,
                site_name=row.site_name,
                latitude=float(row.latitude),
                longitude=float(row.longitude),
                region=row.region,
                land_type=row.land_type,
                total_suitability_score=float(row.total_suitability_score) if row.total_suitability_score else None,
                analysis_timestamp=row.analysis_timestamp
            )
            for row in rows
        ]
        
        return SiteListResponse(
            total=total,
            limit=limit,
            offset=offset,
            sites=sites
        )
    
    @staticmethod
    async def get_site_by_id(
        db: AsyncSession,
        site_id: int
    ) -> Optional[SiteDetailResponse]:
        """
        Get detailed information for a specific site
        """
        query = text("""
            SELECT 
                s.site_id, s.site_name, s.latitude, s.longitude,
                s.area_sqm, s.solar_irradiance_kwh, s.grid_distance_km,
                s.slope_degrees, s.road_distance_km, s.elevation_m,
                s.land_type, s.region,
                ar.solar_irradiance_score, ar.area_score,
                ar.grid_distance_score, ar.slope_score,
                ar.infrastructure_score, ar.total_suitability_score,
                ar.analysis_timestamp
            FROM sites s
            LEFT JOIN (
                SELECT site_id, solar_irradiance_score, area_score,
                       grid_distance_score, slope_score, infrastructure_score,
                       total_suitability_score, analysis_timestamp,
                       ROW_NUMBER() OVER (PARTITION BY site_id ORDER BY analysis_timestamp DESC) as rn
                FROM analysis_results
            ) ar ON s.site_id = ar.site_id AND ar.rn = 1
            WHERE s.site_id = :site_id
        """)
        
        result = await db.execute(query, {"site_id": site_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return SiteDetailResponse(
            site_id=row.site_id,
            site_name=row.site_name,
            latitude=float(row.latitude),
            longitude=float(row.longitude),
            area_sqm=row.area_sqm,
            solar_irradiance_kwh=float(row.solar_irradiance_kwh),
            grid_distance_km=float(row.grid_distance_km),
            slope_degrees=float(row.slope_degrees),
            road_distance_km=float(row.road_distance_km),
            elevation_m=row.elevation_m,
            land_type=row.land_type,
            region=row.region,
            solar_irradiance_score=float(row.solar_irradiance_score) if row.solar_irradiance_score else None,
            area_score=float(row.area_score) if row.area_score else None,
            grid_distance_score=float(row.grid_distance_score) if row.grid_distance_score else None,
            slope_score=float(row.slope_score) if row.slope_score else None,
            infrastructure_score=float(row.infrastructure_score) if row.infrastructure_score else None,
            total_suitability_score=float(row.total_suitability_score) if row.total_suitability_score else None,
            analysis_timestamp=row.analysis_timestamp
        )
    
    @staticmethod
    async def get_statistics(db: AsyncSession) -> StatisticsResponse:
        """
        Get comprehensive statistics across all sites
        """
        # Overall stats
        overall_query = text("""
            SELECT 
                COUNT(*) as total_sites,
                COUNT(total_suitability_score) as sites_analyzed,
                AVG(total_suitability_score) as avg_score,
                MIN(total_suitability_score) as min_score,
                MAX(total_suitability_score) as max_score,
                STDDEV(total_suitability_score) as std_dev
            FROM sites_with_scores
        """)
        
        result = await db.execute(overall_query)
        overall = result.fetchone()
        
        # Get all scores for median calculation
        scores_query = text("""
            SELECT total_suitability_score 
            FROM sites_with_scores 
            WHERE total_suitability_score IS NOT NULL
            ORDER BY total_suitability_score
        """)
        
        scores_result = await db.execute(scores_query)
        scores = [float(row.total_suitability_score) for row in scores_result.fetchall()]
        median_score = statistics.median(scores) if scores else 0.0
        
        # Score distribution
        distribution_query = text("""
            SELECT 
                CASE 
                    WHEN total_suitability_score >= 80 THEN '80-100 (Excellent)'
                    WHEN total_suitability_score >= 60 THEN '60-79 (Good)'
                    WHEN total_suitability_score >= 40 THEN '40-59 (Fair)'
                    WHEN total_suitability_score >= 20 THEN '20-39 (Poor)'
                    ELSE '0-19 (Very Poor)'
                END as range_label,
                COUNT(*) as count
            FROM sites_with_scores
            WHERE total_suitability_score IS NOT NULL
            GROUP BY range_label
            ORDER BY MIN(total_suitability_score) DESC
        """)
        
        dist_result = await db.execute(distribution_query)
        total_analyzed = overall.sites_analyzed or 1
        score_distribution = [
            ScoreDistribution(
                range_label=row.range_label,
                count=row.count,
                percentage=round((row.count / total_analyzed) * 100, 2)
            )
            for row in dist_result.fetchall()
        ]
        
        # Regional stats
        regional_query = text("""
            SELECT 
                region,
                COUNT(*) as site_count,
                AVG(total_suitability_score) as avg_score,
                MAX(total_suitability_score) as max_score,
                MIN(total_suitability_score) as min_score
            FROM sites_with_scores
            WHERE total_suitability_score IS NOT NULL
            GROUP BY region
            ORDER BY avg_score DESC
        """)
        
        regional_result = await db.execute(regional_query)
        regional_stats = [
            RegionalStats(
                region=row.region,
                site_count=row.site_count,
                avg_score=round(float(row.avg_score), 2),
                max_score=round(float(row.max_score), 2),
                min_score=round(float(row.min_score), 2)
            )
            for row in regional_result.fetchall()
        ]
        
        # Land type stats
        landtype_query = text("""
            SELECT 
                land_type,
                COUNT(*) as site_count,
                AVG(total_suitability_score) as avg_score,
                MAX(total_suitability_score) as max_score
            FROM sites_with_scores
            WHERE total_suitability_score IS NOT NULL
            GROUP BY land_type
            ORDER BY avg_score DESC
        """)
        
        landtype_result = await db.execute(landtype_query)
        land_type_stats = [
            LandTypeStats(
                land_type=row.land_type,
                site_count=row.site_count,
                avg_score=round(float(row.avg_score), 2),
                max_score=round(float(row.max_score), 2)
            )
            for row in landtype_result.fetchall()
        ]
        
        # Top performing sites
        top_sites_query = text("""
            SELECT 
                site_id, site_name, latitude, longitude,
                region, land_type, total_suitability_score,
                analysis_timestamp
            FROM sites_with_scores
            WHERE total_suitability_score IS NOT NULL
            ORDER BY total_suitability_score DESC
            LIMIT 10
        """)
        
        top_result = await db.execute(top_sites_query)
        top_sites = [
            SiteResponse(
                site_id=row.site_id,
                site_name=row.site_name,
                latitude=float(row.latitude),
                longitude=float(row.longitude),
                region=row.region,
                land_type=row.land_type,
                total_suitability_score=round(float(row.total_suitability_score), 2),
                analysis_timestamp=row.analysis_timestamp
            )
            for row in top_result.fetchall()
        ]
        
        return StatisticsResponse(
            total_sites=overall.total_sites,
            sites_analyzed=overall.sites_analyzed,
            average_score=round(float(overall.avg_score or 0), 2),
            median_score=round(median_score, 2),
            min_score=round(float(overall.min_score or 0), 2),
            max_score=round(float(overall.max_score or 0), 2),
            std_deviation=round(float(overall.std_dev or 0), 2),
            score_distribution=score_distribution,
            regional_stats=regional_stats,
            land_type_stats=land_type_stats,
            top_performing_sites=top_sites
        )
    
    @staticmethod
    async def export_sites(
        db: AsyncSession,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Export sites data with optional filtering
        """
        where_clause = ""
        params = {}
        
        if min_score is not None:
            where_clause = "WHERE total_suitability_score >= :min_score"
            params["min_score"] = min_score
        
        query = text(f"""
            SELECT 
                site_id, site_name, latitude, longitude,
                area_sqm, solar_irradiance_kwh, grid_distance_km,
                slope_degrees, road_distance_km, elevation_m,
                land_type, region,
                solar_irradiance_score, area_score,
                grid_distance_score, slope_score,
                infrastructure_score, total_suitability_score,
                analysis_timestamp
            FROM sites_with_scores
            {where_clause}
            ORDER BY total_suitability_score DESC
        """)
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        return [
            {
                "site_id": row.site_id,
                "site_name": row.site_name,
                "latitude": float(row.latitude),
                "longitude": float(row.longitude),
                "area_sqm": row.area_sqm,
                "solar_irradiance_kwh": float(row.solar_irradiance_kwh),
                "grid_distance_km": float(row.grid_distance_km),
                "slope_degrees": float(row.slope_degrees),
                "road_distance_km": float(row.road_distance_km),
                "elevation_m": row.elevation_m,
                "land_type": row.land_type,
                "region": row.region,
                "solar_irradiance_score": float(row.solar_irradiance_score) if row.solar_irradiance_score else None,
                "area_score": float(row.area_score) if row.area_score else None,
                "grid_distance_score": float(row.grid_distance_score) if row.grid_distance_score else None,
                "slope_score": float(row.slope_score) if row.slope_score else None,
                "infrastructure_score": float(row.infrastructure_score) if row.infrastructure_score else None,
                "total_suitability_score": float(row.total_suitability_score) if row.total_suitability_score else None,
                "analysis_timestamp": row.analysis_timestamp.isoformat() if row.analysis_timestamp else None
            }
            for row in rows
        ]
