export interface AnalyzeRequest {
  query: string;
}

export interface AnalyzeResponse {
  analysis: string;
  timestamp: string;
  query: string;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  category: string;
}

export interface SkillsResponse {
  skills: Skill[];
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}