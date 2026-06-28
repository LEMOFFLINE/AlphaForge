export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Account {
  id: string;
  user_id: string;
  initial_balance: number;
  current_balance: number;
  created_at: string;
}

export interface Position {
  id: string;
  account_id: string;
  symbol: string;
  shares: number;
  avg_cost: number;
  created_at: string;
}

export interface Order {
  id: string;
  account_id: string;
  symbol: string;
  type: 'buy' | 'sell';
  shares: number;
  price: number;
  commission: number;
  status: 'pending' | 'completed' | 'cancelled';
  created_at: string;
}

export interface Quote {
  symbol: string;
  name?: string;
  price: number;
  change: number;
  change_percent: number;
  volume?: number;
}

export interface AccountValue {
  id: string;
  account_id: string;
  total_value: number;
  cash_balance: number;
  positions_value: number;
  recorded_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest extends LoginRequest {
  initial_balance: 100000 | 1000000 | 10000000;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface OrderCreate {
  account_id: string;
  symbol: string;
  type: 'buy' | 'sell';
  shares: number;
  price: number;
}
