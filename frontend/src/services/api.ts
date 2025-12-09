import axios from 'axios';
import { ReviewResult } from '../types';

// 默认走 /api 前缀；如果环境配置为空则尝试补全
const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const reviewCode = async (
  code: string,
  fileName: string,
  filePath?: string
): Promise<ReviewResult> => {
  const response = await api.post<ReviewResult>(`${API_BASE_URL}/review`, {
    code,
    file_name: fileName,
    file_path: filePath || fileName,
  });
  return response.data;
};

export const reviewUploadedFile = async (file: File): Promise<ReviewResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<ReviewResult>(`${API_BASE_URL}/review/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const downloadFixedFile = async (fileName: string): Promise<Blob> => {
  const response = await api.get(`${API_BASE_URL}/download/${fileName}`, {
    responseType: 'blob',
  });
  return response.data;
};

export const listFixedFiles = async () => {
  const response = await api.get(`${API_BASE_URL}/files`);
  return response.data;
};

