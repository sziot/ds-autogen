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
      // 将 baseURL 改为包含 /api/v1，这样下面各方法可以使用 /review/... 的相对路径
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
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

  // 上传代码文件 -> POST /api/v1/review/upload
  async uploadCodeFile(file: File): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    // 现在 baseURL 已包含 /api/v1，所以这里使用 /review/upload
    return this.client.post('/review/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // 启动审查 -> POST /api/v1/review/start?task_id={task_id}
  async startCodeReview(taskId: string): Promise<ApiResponse<{ taskId: string }>> {
    // 后端期望 task_id 为 query 参数
    return this.client.post(`/review/start?task_id=${encodeURIComponent(taskId)}`);
  }

  // 获取审查结果 -> GET /api/v1/review/result/{taskId}
  async getReviewResult(taskId: string): Promise<ApiResponse<CodeReviewResult>> {
    return this.client.get(`/review/result/${encodeURIComponent(taskId)}`);
  }

  // 获取历史记录 -> GET /api/v1/review/history
  async getReviewHistory(page = 1, limit = 20): Promise<ApiResponse<ReviewTask[]>> {
    return this.client.get(`/review/history?page=${page}&limit=${limit}`);
  }

  // 下载修复后的文件（保持原样，server 路由如有不同请同步）
  async downloadFixedFile(filePath: string): Promise<Blob> {
    const response = await this.client.get(`/files/download/${encodeURIComponent(filePath)}`, {
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