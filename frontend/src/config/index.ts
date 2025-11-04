export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

export const DEFAULT_WEIGHTS = {
  solar: 0.35,
  area: 0.25,
  grid_distance: 0.20,
  slope: 0.15,
  infrastructure: 0.05,
};

export const DEFAULT_MAP_CENTER: [number, number] = [78.9629, 20.5937]; // Center of India
export const DEFAULT_MAP_ZOOM = 5;

export const SCORE_COLORS = {
  excellent: '#10b981', // green-500
  good: '#84cc16',      // lime-500
  moderate: '#f59e0b',  // amber-500
  poor: '#f97316',      // orange-500
  veryPoor: '#ef4444',  // red-500
};

export function getScoreColor(score: number | null): string {
  if (score === null) return '#9ca3af'; // gray-400
  if (score >= 80) return SCORE_COLORS.excellent;
  if (score >= 60) return SCORE_COLORS.good;
  if (score >= 40) return SCORE_COLORS.moderate;
  if (score >= 20) return SCORE_COLORS.poor;
  return SCORE_COLORS.veryPoor;
}

export function getScoreLabel(score: number | null): string {
  if (score === null) return 'Not Analyzed';
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Moderate';
  if (score >= 20) return 'Poor';
  return 'Very Poor';
}
