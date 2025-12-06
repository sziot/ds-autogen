import axios, { AxiosInstance } from 'axios';
import { 
  ApiResponse, 
  UploadResponse, 
  CodeReviewResult,
  ReviewTask 
} from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject({
          success: false,
          error: error.response?.data?.error || '网络错误',
          message: error.response?.data?.message || '请求失败',
        });
      }
    );
  }

  // 上传代码文件
  async uploadCodeFile(file: File): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.client.post('/api/review/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // 启动代码审查
  async startCodeReview(taskId: string): Promise<ApiResponse<{ taskId: string }>> {
    return this.client.post('/api/review/start', { taskId });
  }

  // 获取审查结果
  async getReviewResult(taskId: string): Promise<ApiResponse<CodeReviewResult>> {
    return this.client.get(`/api/review/result/${taskId}`);
  }

  // 获取历史记录
  async getReviewHistory(page = 1, limit = 20): Promise<ApiResponse<ReviewTask[]>> {
    return this.client.get(`/api/review/history?page=${page}&limit=${limit}`);
  }

  // 下载修复后的文件
  async downloadFixedFile(filePath: string): Promise<Blob> {
    const response = await this.client.get(`/api/files/download/${encodeURIComponent(filePath)}`, {
      responseType: 'blob',
    });
    return response;
  }

  // 获取 WebSocket URL
  getWebSocketUrl(taskId: string): string {
    const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    return `${baseUrl}/ws/review/${taskId}`;
  }
}

export const apiService = new ApiService();