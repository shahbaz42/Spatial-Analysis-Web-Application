import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  Site,
  SiteDetail,
  AnalysisWeights,
  StatisticsResponse,
  MapFilters,
} from '@/types';
import apiService from '@/services/api';
import { DEFAULT_WEIGHTS } from '@/config';

export const useSiteStore = defineStore('site', () => {
  // State
  const sites = ref<Site[]>([]);
  const selectedSite = ref<Site | null>(null);
  const selectedSiteDetail = ref<SiteDetail | null>(null);
  const statistics = ref<StatisticsResponse | null>(null);
  const loading = ref(false);
  const analyzing = ref(false);
  const error = ref<string | null>(null);

  // Weights and filters
  const weights = ref<AnalysisWeights>({ ...DEFAULT_WEIGHTS });
  const filters = ref<MapFilters>({
    minScore: 0,
    maxScore: 100,
  });

  // Computed
  const filteredSites = computed(() => {
    return sites.value.filter((site) => {
      const score = site.total_suitability_score;
      if (score === null) return false;
      return score >= filters.value.minScore && score <= filters.value.maxScore;
    });
  });

  const sortedSites = computed(() => {
    return [...filteredSites.value].sort((a, b) => {
      const scoreA = a.total_suitability_score ?? 0;
      const scoreB = b.total_suitability_score ?? 0;
      return scoreB - scoreA;
    });
  });

  const totalSites = computed(() => sites.value.length);
  const analyzedSites = computed(() => 
    sites.value.filter(s => s.total_suitability_score !== null).length
  );

  // Actions
  async function fetchSites(params?: {
    min_score?: number;
    max_score?: number;
    limit?: number;
    offset?: number;
  }) {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiService.getSites(params);
      sites.value = response.sites;
      return response;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch sites';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchSiteDetail(siteId: number) {
    loading.value = true;
    error.value = null;
    try {
      const detail = await apiService.getSiteById(siteId);
      selectedSiteDetail.value = detail;
      return detail;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch site details';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function analyzeSitesWithWeights(customWeights: AnalysisWeights) {
    analyzing.value = true;
    error.value = null;
    try {
      const response = await apiService.analyzeSites({ weights: customWeights });
      weights.value = { ...customWeights };
      // Refresh sites after analysis
      await fetchSites();
      return response;
    } catch (err: any) {
      error.value = err.message || 'Failed to analyze sites';
      throw err;
    } finally {
      analyzing.value = false;
    }
  }

  async function fetchStatistics() {
    loading.value = true;
    error.value = null;
    try {
      const stats = await apiService.getStatistics();
      statistics.value = stats;
      return stats;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function selectSite(site: Site | null) {
    selectedSite.value = site;
    if (site) {
      fetchSiteDetail(site.site_id);
    } else {
      selectedSiteDetail.value = null;
    }
  }

  function updateWeights(newWeights: AnalysisWeights) {
    weights.value = { ...newWeights };
  }

  function updateFilters(newFilters: Partial<MapFilters>) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function resetFilters() {
    filters.value = {
      minScore: 0,
      maxScore: 100,
    };
  }

  function resetWeights() {
    weights.value = { ...DEFAULT_WEIGHTS };
  }

  function clearError() {
    error.value = null;
  }

  return {
    // State
    sites,
    selectedSite,
    selectedSiteDetail,
    statistics,
    loading,
    analyzing,
    error,
    weights,
    filters,
    
    // Computed
    filteredSites,
    sortedSites,
    totalSites,
    analyzedSites,
    
    // Actions
    fetchSites,
    fetchSiteDetail,
    analyzeSitesWithWeights,
    fetchStatistics,
    selectSite,
    updateWeights,
    updateFilters,
    resetFilters,
    resetWeights,
    clearError,
  };
});
