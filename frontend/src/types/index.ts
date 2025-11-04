export interface Site {
  site_id: number;
  site_name: string;
  latitude: number;
  longitude: number;
  region: string;
  land_type: string;
  total_suitability_score: number | null;
  analysis_timestamp: string | null;
}

export interface SiteDetail extends Site {
  area_sqm: number;
  solar_irradiance_kwh: number;
  grid_distance_km: number;
  slope_degrees: number;
  road_distance_km: number;
  elevation_m: number;
  solar_irradiance_score: number | null;
  area_score: number | null;
  grid_distance_score: number | null;
  slope_score: number | null;
  infrastructure_score: number | null;
}

export interface SiteListResponse {
  total: number;
  limit: number;
  offset: number;
  sites: Site[];
}

export interface AnalysisWeights {
  solar: number;
  area: number;
  grid_distance: number;
  slope: number;
  infrastructure: number;
}

export interface AnalysisRequest {
  weights: AnalysisWeights;
}

export interface AnalysisResponse {
  success: boolean;
  message: string;
  sites_analyzed: number;
  weights_used: AnalysisWeights;
  timestamp: string;
}

export interface ScoreDistribution {
  range_label: string;
  count: number;
  percentage: number;
}

export interface RegionalStats {
  region: string;
  site_count: number;
  avg_score: number;
  max_score: number;
  min_score: number;
}

export interface LandTypeStats {
  land_type: string;
  site_count: number;
  avg_score: number;
  max_score: number;
}

export interface StatisticsResponse {
  total_sites: number;
  sites_analyzed: number;
  average_score: number;
  median_score: number;
  min_score: number;
  max_score: number;
  std_deviation: number;
  score_distribution: ScoreDistribution[];
  regional_stats: RegionalStats[];
  land_type_stats: LandTypeStats[];
  top_performing_sites: Site[];
}

export interface MapFilters {
  minScore: number;
  maxScore: number;
}
