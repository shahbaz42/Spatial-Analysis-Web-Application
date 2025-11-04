import axios, { AxiosInstance } from 'axios';
import type {
  SiteListResponse,
  SiteDetail,
  AnalysisRequest,
  AnalysisResponse,
  StatisticsResponse,
} from '@/types';
import { API_BASE_URL } from '@/config';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Get sites with optional filters
  async getSites(params?: {
    min_score?: number;
    max_score?: number;
    limit?: number;
    offset?: number;
  }): Promise<SiteListResponse> {
    const response = await this.client.get<SiteListResponse>('/api/sites', { params });
    return response.data;
  }

  // Get site by ID
  async getSiteById(siteId: number): Promise<SiteDetail> {
    const response = await this.client.get<SiteDetail>(`/api/sites/${siteId}`);
    return response.data;
  }

  // Analyze sites with custom weights
  async analyzeSites(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await this.client.post<AnalysisResponse>('/api/analyze', request);
    return response.data;
  }

  // Get statistics
  async getStatistics(): Promise<StatisticsResponse> {
    const response = await this.client.get<StatisticsResponse>('/api/statistics');
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export default new ApiService();
