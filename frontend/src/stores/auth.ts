import { defineStore } from 'pinia';
import { authApi } from '../lib/api';
import type { Account, User } from '../lib/types';

interface AuthState {
  user: User | null;
  initialized: boolean;
  accounts: Account[];
  currentAccount: Account | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    initialized: false,
    accounts: [],
    currentAccount: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user),
  },
  actions: {
    setAuth(user: User) {
      this.user = user;
      this.initialized = true;
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
    clearAuth() {
      this.user = null;
      this.accounts = [];
      this.currentAccount = null;
      this.initialized = true;
    },
    async loadCurrentUser() {
      if (this.initialized) {
        return this.isAuthenticated;
      }

      try {
        this.user = await authApi.me();
        this.initialized = true;
        return true;
      } catch {
        this.clearAuth();
        return false;
      }
    },
    async logout() {
      try {
        await authApi.logout();
      } finally {
        this.clearAuth();
      }
    },
  },
});
