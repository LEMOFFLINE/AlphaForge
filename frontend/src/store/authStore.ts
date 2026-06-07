import { create } from 'zustand';
import type { User, Account } from '../lib/types';

interface AuthState {
  user: User | null;
  token: string | null;
  accounts: Account[];
  currentAccount: Account | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  setAccounts: (accounts: Account[]) => void;
  setCurrentAccount: (account: Account | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  accounts: [],
  currentAccount: null,
  isAuthenticated: !!localStorage.getItem('token'),
  setAuth: (user, token) => {
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  setAccounts: (accounts) => set({ accounts }),
  setCurrentAccount: (account) => set({ currentAccount: account }),
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false, currentAccount: null });
  },
}));
