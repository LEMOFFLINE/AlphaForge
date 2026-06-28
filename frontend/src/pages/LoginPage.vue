<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import heroImage from '../assets/hero.jpg';
import { authApi } from '../lib/api';
import { useAuthStore } from '../stores/auth';
import type { RegisterRequest } from '../lib/types';

const router = useRouter();
const auth = useAuthStore();

const isLogin = ref(true);
const email = ref('');
const password = ref('');
const initialBalance = ref<RegisterRequest['initial_balance']>(100000);
const error = ref('');
const loading = ref(false);

const balanceOptions: Array<{ value: RegisterRequest['initial_balance']; label: string }> = [
  { value: 100000, label: '$100K' },
  { value: 1000000, label: '$1M' },
  { value: 10000000, label: '$10M' },
];

async function submit() {
  error.value = '';
  loading.value = true;

  try {
    const response = isLogin.value
      ? await authApi.login({ email: email.value, password: password.value })
      : await authApi.register({
          email: email.value,
          password: password.value,
          initial_balance: initialBalance.value,
        });

    auth.setAuth(response.user, response.access_token);
    router.push('/dashboard');
  } catch (err: unknown) {
    const detail = typeof err === 'object' && err !== null && 'response' in err
      ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      : undefined;
    error.value = detail || '操作失败，请重试';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="grid min-h-screen bg-white lg:grid-cols-2">
    <section class="flex items-center justify-center px-6 py-12">
      <div class="w-full max-w-md">
        <h1 class="mb-2 text-4xl font-medium text-primary">AlphaForge</h1>
        <p class="mb-12 text-text-muted">虚拟投资交易平台</p>

        <div class="mb-8 flex gap-4">
          <button
            class="border-b-2 pb-2 transition-colors"
            :class="isLogin ? 'border-primary text-primary' : 'border-transparent text-text-muted'"
            @click="isLogin = true"
          >
            登录
          </button>
          <button
            class="border-b-2 pb-2 transition-colors"
            :class="!isLogin ? 'border-primary text-primary' : 'border-transparent text-text-muted'"
            @click="isLogin = false"
          >
            注册
          </button>
        </div>

        <form class="space-y-6" @submit.prevent="submit">
          <input
            v-model="email"
            type="email"
            placeholder="邮箱"
            required
            class="w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
          />
          <input
            v-model="password"
            type="password"
            placeholder="密码"
            required
            minlength="6"
            class="w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
          />

          <div v-if="!isLogin">
            <label class="mb-2 block text-sm text-text-muted">选择初始本金</label>
            <div class="grid grid-cols-3 gap-3">
              <button
                v-for="option in balanceOptions"
                :key="option.value"
                type="button"
                class="rounded-lg border py-3 transition-colors"
                :class="initialBalance === option.value ? 'border-primary bg-primary/10 text-primary' : 'border-gray-200 bg-white text-text-muted hover:border-gray-300'"
                @click="initialBalance = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>

          <p v-if="error" class="text-sm text-loss">{{ error }}</p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-lg bg-primary py-3 text-white transition-colors hover:bg-primary-light disabled:cursor-not-allowed disabled:opacity-50"
          >
            {{ loading ? '处理中...' : isLogin ? '登录' : '注册' }}
          </button>
        </form>
      </div>
    </section>

    <section class="relative hidden overflow-hidden bg-gray-50 lg:block">
      <img :src="heroImage" alt="AlphaForge market screen" class="h-full w-full object-cover" />
      <div class="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
      <div class="absolute bottom-12 left-12 right-12 text-white">
        <h2 class="mb-4 text-3xl font-medium">真实市场数据</h2>
        <p class="text-white/80">零风险练习 · 智能分析 · 投资成长</p>
      </div>
    </section>
  </div>
</template>
