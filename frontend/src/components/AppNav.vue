<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const auth = useAuthStore();

async function logout() {
  await auth.logout();
  router.push('/login');
}
</script>

<template>
  <nav class="border-b border-gray-200 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <button class="text-xl font-medium text-primary" @click="router.push('/dashboard')">
        AlphaForge
      </button>
      <div class="flex items-center gap-6">
        <RouterLink to="/dashboard" class="text-text-muted transition-colors hover:text-text" active-class="text-text font-medium">
          控制台
        </RouterLink>
        <RouterLink to="/market" class="text-text-muted transition-colors hover:text-text" active-class="text-text font-medium">
          全球市场
        </RouterLink>
        <RouterLink to="/analysis" class="text-text-muted transition-colors hover:text-text" active-class="text-text font-medium">
          分析
        </RouterLink>
        <button class="text-text-muted transition-colors hover:text-text" @click="logout">
          退出
        </button>
      </div>
    </div>
  </nav>
</template>
