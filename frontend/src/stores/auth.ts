import { defineStore } from 'pinia';
import type { Account, User } from '../lib/types';

interface AuthState {
  user: User | null;
  token: string | null;
  accounts: Account[];
  currentAccount: Account | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    accounts: [],
    currentAccount: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    setAuth(user: User, token: string) {
      localStorage.setItem('token', token);
      this.user = user;
      this.token = token;
    },
    setAccounts(accounts: Account[]) {
      this.accounts = accounts;
      if (!this.currentAccount && accounts.length > 0) {
        this.currentAccount = accounts[0];
      }
    },
    setCurrentAccount(account: Account | null) {
      this.currentAccount = account;
    },
    logout() {
      localStorage.removeItem('token');
      this.user = null;
      this.token = null;
      this.accounts = [];
      this.currentAccount = null;
    },
  },
});
