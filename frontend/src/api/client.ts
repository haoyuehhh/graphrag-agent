import { marked } from 'marked';
import { 
  AnalyzeRequest, 
  AnalyzeResponse, 
  SkillsResponse, 
  HealthCheckResponse 
} from '../types/api';

// 配置类型
interface ApiConfig {
  baseUrl: string;
  useMock: boolean;
}

class ApiClient {
  private config: ApiConfig;

  constructor() {
    // 优先使用环境变量，默认localhost:8000
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const useMock = import.meta.env.VITE_USE_MOCK_DATA === 'true';
    
    this.config = {
      baseUrl,
      useMock
    };
  }

  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    if (this.config.useMock) {
      return this.mockFetch<T>(endpoint);
    }

    const url = `${this.config.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers
        }
      });

      if (!response.ok) {
        throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error('API调用错误:', error);
      throw error;
    }
  }

  private mockFetch<T>(endpoint: string): Promise<T> {
    // 模拟API响应
    const mockResponses: Record<string, () => Promise<T>> = {
      '/health': async () => ({
        status: 'healthy',
        timestamp: new Date().toISOString()
      } as HealthCheckResponse),
      
      '/api/v1/analyze': async () => ({
        analysis: '# 分析结果\n\n这是一个模拟的RAG分析结果。\n\n## 关键发现\n- 竞品分析显示市场趋势\n- 技术架构对比\n- 功能特性评估\n\n## 建议\n1. 优化产品定位\n2. 加强技术栈\n3. 提升用户体验',
        timestamp: new Date().toISOString(),
        query: 'mock query'
      } as AnalyzeResponse),
      
      '/api/v1/skills': async () => ({
        skills: [
          { id: '1', name: '文本分析', description: '分析文本内容', category: 'NLP' },
          { id: '2', name: '数据挖掘', description: '挖掘数据模式', category: 'Data' },
          { id: '3', name: '可视化', description: '数据可视化', category: 'UI' }
        ]
      } as SkillsResponse)
    };

    const mockResponse = mockResponses[endpoint];
    if (mockResponse) {
      return mockResponse();
    }

    throw new Error(`未找到mock响应: ${endpoint}`);
  }

  // 健康检查
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.fetchApi<HealthCheckResponse>('/health');
  }

  // 竞品分析
  async analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    return this.fetchApi<AnalyzeResponse>('/api/v1/analyze', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  // 获取技能列表
  async getSkills(): Promise<SkillsResponse> {
    return this.fetchApi<SkillsResponse>('/api/v1/skills');
  }

  // 将markdown转换为HTML
  static renderMarkdown(markdown: string): string {
    return marked.parse(markdown);
  }
}

export const apiClient = new ApiClient();