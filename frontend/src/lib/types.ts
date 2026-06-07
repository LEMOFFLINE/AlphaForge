// 用户类型
export interface User {
  id: string;
  email: string;
  created_at: string;
}

// 账户类型
export interface Account {
  id: string;
  user_id: string;
  initial_balance: number;
  current_balance: number;
  created_at: string;
}

// 持仓类型
export interface Position {
  id: string;
  account_id: string;
  symbol: string;
  shares: number;
  avg_cost: number;
  created_at: string;
}

// 订单类型
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

// 股票报价类型
export interface Quote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  updated_at: string;
}

// 账户价值历史类型
export interface AccountValue {
  id: string;
  account_id: string;
  total_value: number;
  cash_balance: number;
  positions_value: number;
  recorded_at: string;
}

// 登录请求
export interface LoginRequest {
  email: string;
  password: string;
}

// 注册请求
export interface RegisterRequest {
  email: string;
  password: string;
  initial_balance: 100000 | 1000000 | 10000000;
}

// 认证响应
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
