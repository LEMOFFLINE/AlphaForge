import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../pages/LoginPage.vue';
import DashboardPage from '../pages/DashboardPage.vue';
import MarketPage from '../pages/MarketPage.vue';
import AnalysisPage from '../pages/AnalysisPage.vue';

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

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return '/login';
  }
});

export default router;
