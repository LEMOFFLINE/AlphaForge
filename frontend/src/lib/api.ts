import axios from 'axios';
import type { LoginRequest, RegisterRequest, AuthResponse, Account, Position, Order, Quote, AccountValue } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 认证 API
export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/login', data);
    return response.data;
  },
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },
  logout: async () => {
    await api.post('/api/auth/logout');
  },
  me: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// 账户 API
export const accountApi = {
  getAccounts: async (): Promise<Account[]> => {
    const response = await api.get('/api/accounts');
    return response.data;
  },
  createAccount: async (initialBalance: number): Promise<Account> => {
    const response = await api.post('/api/accounts', { initial_balance: initialBalance });
    return response.data;
  },
  getAccount: async (id: string): Promise<Account> => {
    const response = await api.get(`/api/accounts/${id}`);
    return response.data;
  },
};

// 持仓 API
export const positionApi = {
  getPositions: async (accountId: string): Promise<Position[]> => {
    const response = await api.get(`/api/accounts/${accountId}/positions`);
    return response.data;
  },
};

// 订单 API
export const orderApi = {
  createOrder: async (data: Omit<Order, 'id' | 'status' | 'created_at' | 'commission'>): Promise<Order> => {
    const response = await api.post('/api/orders', data);
    return response.data;
  },
  getOrders: async (accountId: string): Promise<Order[]> => {
    const response = await api.get(`/api/orders/${accountId}`);
    return response.data;
  },
};

// 股票 API
export const stockApi = {
  getQuote: async (symbol: string): Promise<Quote> => {
    const response = await api.get(`/api/stocks/quote/${symbol}`);
    return response.data;
  },
  search: async (query: string): Promise<Quote[]> => {
    const response = await api.get(`/api/stocks/search?q=${query}`);
    return response.data;
  },
  getDailyData: async (symbol: string): Promise<any> => {
    const response = await api.get(`/api/stocks/daily/${symbol}`);
    return response.data;
  },
  getPopular: async (): Promise<any[]> => {
    const response = await api.get('/api/stocks/popular');
    return response.data;
  },
  getPopularQuotes: async (): Promise<any[]> => {
    const response = await api.get('/api/stocks/popular/quotes');
    return response.data;
  },
};

// 账户价值 API
export const accountValueApi = {
  getHistory: async (accountId: string, days: number = 30): Promise<AccountValue[]> => {
    const response = await api.get(`/api/account-values/${accountId}?days=${days}`);
    return response.data;
  },
  recordValue: async (accountId: string): Promise<void> => {
    await api.post(`/api/account-values/record/${accountId}`);
  },
};

export default api;
