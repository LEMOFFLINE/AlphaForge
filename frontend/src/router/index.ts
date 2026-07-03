import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../pages/LoginPage.vue';
import DashboardPage from '../pages/DashboardPage.vue';
import MarketPage from '../pages/MarketPage.vue';
import AnalysisPage from '../pages/AnalysisPage.vue';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginPage },
    { path: '/dashboard', component: DashboardPage, meta: { requiresAuth: true } },
    { path: '/market', component: MarketPage, meta: { requiresAuth: true } },
    { path: '/analysis', component: AnalysisPage, meta: { requiresAuth: true } },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth) {
    const isAuthenticated = auth.isAuthenticated || await auth.loadCurrentUser();
    if (!isAuthenticated) {
      return { path: '/login', query: { redirect: to.fullPath } };
    }
  }

  if (to.path === '/login') {
    const isAuthenticated = auth.isAuthenticated || await auth.loadCurrentUser();
    if (isAuthenticated) {
      return '/dashboard';
    }
  }
});

export default router;
