<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import AppNav from '../components/AppNav.vue';
import AssetChart from '../components/AssetChart.vue';
import { accountApi, accountValueApi, positionApi, stockApi } from '../lib/api';
import type { AccountValue, Position, Quote } from '../lib/types';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const auth = useAuthStore();

const positions = ref<Position[]>([]);
const quoteCache = ref<Record<string, Quote>>({});
const popularStocks = ref<Quote[]>([]);
const valueHistory = ref<AccountValue[]>([]);
const loading = ref(true);

const currentAccount = computed(() => auth.currentAccount);

const totalValue = computed(() => {
  const positionsValue = positions.value.reduce((sum, position) => {
    const quote = quoteCache.value[position.symbol];
    return sum + (quote ? quote.price * position.shares : position.avg_cost * position.shares);
  }, 0);
  return (currentAccount.value?.current_balance || 0) + positionsValue;
});

const totalPnL = computed(() => totalValue.value - (currentAccount.value?.initial_balance || 0));
const totalPnLPercent = computed(() => {
  const initial = currentAccount.value?.initial_balance || 0;
  return initial > 0 ? (totalPnL.value / initial) * 100 : 0;
});

function money(value: number) {
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

async function loadAccounts() {
  const accounts = await accountApi.getAccounts();
  auth.setAccounts(accounts);
}

async function loadDashboard() {
  if (!auth.currentAccount) {
    loading.value = false;
    return;
  }

  const [posData, historyData, popularData] = await Promise.all([
    positionApi.getPositions(auth.currentAccount.id),
    accountValueApi.getHistory(auth.currentAccount.id, 30),
    stockApi.getPopularQuotes(),
  ]);

  positions.value = posData;
  valueHistory.value = historyData;
  popularStocks.value = popularData;

  const quotes: Record<string, Quote> = {};
  await Promise.all(
    posData.map(async (position) => {
      try {
        quotes[position.symbol] = await stockApi.getQuote(position.symbol);
      } catch {
        quotes[position.symbol] = {
          symbol: position.symbol,
          price: position.avg_cost,
          change: 0,
          change_percent: 0,
        };
      }
    }),
  );
  quoteCache.value = quotes;
  loading.value = false;
}

onMounted(async () => {
  if (!auth.token) {
    router.push('/login');
    return;
  }

  try {
    await loadAccounts();
    await loadDashboard();
  } catch (error) {
    console.error('Failed to load dashboard:', error);
    loading.value = false;
  }
});
</script>

<template>
  <div class="min-h-screen bg-white">
    <AppNav />

    <main class="mx-auto max-w-7xl px-6 py-8">
      <div v-if="loading" class="flex h-64 items-center justify-center text-text-muted">
        加载中...
      </div>

      <div v-else class="space-y-6">
        <div class="grid gap-6 lg:grid-cols-3">
          <section class="rounded-lg bg-gray-50 p-6">
            <h2 class="mb-4 text-sm text-text-muted">账户总览</h2>
            <p class="mb-2 text-3xl font-medium text-text">{{ money(totalValue) }}</p>
            <p class="text-sm" :class="totalPnL >= 0 ? 'text-gain' : 'text-loss'">
              {{ totalPnL >= 0 ? '+' : '' }}{{ money(totalPnL) }}
              ({{ totalPnLPercent >= 0 ? '+' : '' }}{{ totalPnLPercent.toFixed(2) }}%)
            </p>
          </section>

          <section class="rounded-lg bg-gray-50 p-6 lg:col-span-2">
            <div class="mb-4 flex items-center justify-between">
              <h2 class="text-sm text-text-muted">市场</h2>
              <button class="text-sm text-primary hover:underline" @click="router.push('/market')">
                查看全部市场
              </button>
            </div>
            <div v-if="popularStocks.length === 0" class="py-6 text-sm text-text-muted">
              正在等待真实市场数据...
            </div>
            <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-5">
              <div v-for="stock in popularStocks.slice(0, 5)" :key="stock.symbol" class="text-center">
                <p class="text-sm font-medium text-text">{{ stock.symbol }}</p>
                <p class="text-lg text-text">${{ stock.price.toFixed(2) }}</p>
                <p class="text-sm" :class="stock.change >= 0 ? 'text-gain' : 'text-loss'">
                  {{ stock.change >= 0 ? '+' : '' }}{{ stock.change_percent.toFixed(2) }}%
                </p>
              </div>
            </div>
          </section>
        </div>

        <div class="grid gap-6 lg:grid-cols-3">
          <section class="rounded-lg bg-gray-50 p-6 lg:col-span-2">
            <h2 class="mb-4 text-sm text-text-muted">持仓</h2>
            <p v-if="positions.length === 0" class="text-sm text-text-muted">暂无持仓</p>
            <div v-else class="space-y-2">
              <div v-for="position in positions" :key="position.id" class="flex items-center justify-between border-b border-gray-200 py-3 last:border-0">
                <div class="flex items-center gap-4">
                  <span class="font-medium text-text">{{ position.symbol }}</span>
                  <span class="text-sm text-text-muted">{{ position.shares }} 股</span>
                </div>
                <div class="text-right">
                  <p class="text-text">${{ (quoteCache[position.symbol]?.price || position.avg_cost).toFixed(2) }}</p>
                  <p class="text-sm text-text-muted">成本 ${{ position.avg_cost.toFixed(2) }}</p>
                </div>
              </div>
            </div>
          </section>

          <section class="rounded-lg bg-gray-50 p-6">
            <h2 class="mb-4 text-sm text-text-muted">可用资金</h2>
            <p class="text-2xl font-medium text-text">{{ money(currentAccount?.current_balance || 0) }}</p>
          </section>
        </div>

        <section class="rounded-lg bg-gray-50 p-6">
          <h2 class="mb-4 text-sm text-text-muted">资产曲线</h2>
          <AssetChart :data="valueHistory" />
        </section>
      </div>
    </main>
  </div>
</template>
