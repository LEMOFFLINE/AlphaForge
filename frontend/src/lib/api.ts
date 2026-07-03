import axios from 'axios';
import type {
  Account,
  AccountValue,
  AuthResponse,
  LoginRequest,
  Order,
  OrderCreate,
  Position,
  Quote,
  RegisterRequest,
  StockTrend,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authApi = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/api/auth/login', data);
    return response.data;
  },
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },
  async me() {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  async logout(): Promise<void> {
    await api.post('/api/auth/logout');
  },
};

export const accountApi = {
  async getAccounts(): Promise<Account[]> {
    const response = await api.get('/api/accounts');
    return response.data;
  },
  async getAccount(id: string): Promise<Account> {
    const response = await api.get(`/api/accounts/${id}`);
    return response.data;
  },
};

export const positionApi = {
  async getPositions(accountId: string): Promise<Position[]> {
    const response = await api.get(`/api/accounts/${accountId}/positions`);
    return response.data;
  },
};

export const orderApi = {
  async createOrder(data: OrderCreate): Promise<Order> {
    const response = await api.post('/api/orders', data);
    return response.data;
  },
  async getOrders(accountId: string): Promise<Order[]> {
    const response = await api.get(`/api/orders/${accountId}`);
    return response.data;
  },
};

export const stockApi = {
  async getQuote(symbol: string): Promise<Quote> {
    const response = await api.get(`/api/stocks/quote/${symbol}`);
    return response.data;
  },
  async getPopularQuotes(): Promise<Quote[]> {
    const response = await api.get('/api/stocks/popular/quotes');
    return response.data;
  },
  async search(query: string) {
    const response = await api.get(`/api/stocks/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },
  async getDailyData(symbol: string) {
    const response = await api.get(`/api/stocks/daily/${symbol}`);
    return response.data;
  },
  async getTrend(symbol: string, range: '1d' | '7d'): Promise<StockTrend> {
    const response = await api.get(`/api/stocks/trend/${symbol}?range=${range}`);
    return response.data;
  },
};

export const accountValueApi = {
  async getHistory(accountId: string, days = 30): Promise<AccountValue[]> {
    const response = await api.get(`/api/account-values/${accountId}?days=${days}`);
    return response.data;
  },
  async recordValue(accountId: string): Promise<void> {
    await api.post(`/api/account-values/record/${accountId}`);
  },
};

export default api;
