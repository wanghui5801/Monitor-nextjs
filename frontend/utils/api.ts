import { API_URL } from '../config/config';

export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  // 从 localStorage 获取 token
  const token = localStorage.getItem('adminToken');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  return response;
};
