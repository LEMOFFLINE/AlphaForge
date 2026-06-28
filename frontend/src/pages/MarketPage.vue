<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import AppNav from '../components/AppNav.vue';
import { accountApi, orderApi, stockApi } from '../lib/api';
import type { OrderCreate, Quote } from '../lib/types';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const stocks = ref<Quote[]>([]);
const loading = ref(true);
const tradeLoading = ref(false);
const error = ref('');
const lastUpdate = ref('');
const selectedStock = ref<Quote | null>(null);
const tradeType = ref<OrderCreate['type']>('buy');
const shares = ref('');

const estimatedAmount = computed(() => {
  const count = Number.parseInt(shares.value, 10) || 0;
  if (!selectedStock.value) return 0;
  const gross = selectedStock.value.price * count;
  return tradeType.value === 'buy' ? gross * 1.001 + 5 : gross * 0.999 - 5;
});

async function loadAccounts() {
  const accounts = await accountApi.getAccounts();
  auth.setAccounts(accounts);
}

async function loadMarketData() {
  loading.value = true;
  try {
    stocks.value = await stockApi.getPopularQuotes();
    lastUpdate.value = new Date().toLocaleTimeString('zh-CN');
  } catch (err) {
    console.error('Failed to load market data:', err);
  } finally {
    loading.value = false;
  }
}

function openTrade(stock: Quote, type: OrderCreate['type'] = 'buy') {
  selectedStock.value = stock;
  tradeType.value = type;
  shares.value = '';
  error.value = '';
}

function closeTrade() {
  selectedStock.value = null;
  error.value = '';
}

async function submitTrade() {
  if (!selectedStock.value || !auth.currentAccount) {
    error.value = '请先选择账户';
    return;
  }

  const shareCount = Number.parseInt(shares.value, 10);
  if (!shareCount || shareCount <= 0) {
    error.value = '请输入有效股数';
    return;
  }

  tradeLoading.value = true;
  error.value = '';

  try {
    await orderApi.createOrder({
      account_id: auth.currentAccount.id,
      symbol: selectedStock.value.symbol,
      type: tradeType.value,
      shares: shareCount,
      price: selectedStock.value.price,
    });
    await loadAccounts();
    closeTrade();
  } catch (err: unknown) {
    const detail = typeof err === 'object' && err !== null && 'response' in err
      ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      : undefined;
    error.value = detail || '交易失败';
  } finally {
    tradeLoading.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadAccounts(), loadMarketData()]);
  window.setInterval(loadMarketData, 5 * 60 * 1000);
});
</script>

<template>
  <div class="min-h-screen bg-white">
    <AppNav />

    <main class="mx-auto max-w-7xl px-6 py-8">
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-medium text-text">全球市场</h2>
          <p class="text-sm text-text-muted">
            最后更新 {{ lastUpdate || '等待数据' }} · 使用 Alpha Vantage 真实数据
          </p>
        </div>
        <button class="rounded-lg bg-gray-100 px-4 py-2 transition-colors hover:bg-gray-200" @click="loadMarketData">
          刷新
        </button>
      </div>

      <div v-if="loading" class="rounded-lg bg-gray-50 p-10 text-center text-text-muted">
        正在加载真实市场数据...
      </div>

      <div v-else-if="stocks.length === 0" class="rounded-lg bg-gray-50 p-10 text-center text-text-muted">
        暂无市场数据。Alpha Vantage 免费接口可能正在限流，请稍后刷新。
      </div>

      <div v-else class="overflow-hidden rounded-lg bg-gray-50">
        <table class="w-full">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-text-muted">代码</th>
              <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-text-muted">名称</th>
              <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-text-muted">价格</th>
              <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-text-muted">涨跌</th>
              <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-text-muted">涨跌幅</th>
              <th class="px-6 py-3 text-center text-xs font-medium uppercase tracking-wider text-text-muted">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="stock in stocks" :key="stock.symbol" class="transition-colors hover:bg-gray-100">
              <td class="whitespace-nowrap px-6 py-4 font-medium text-text">{{ stock.symbol }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-text-muted">{{ stock.name || '-' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-right font-medium text-text">${{ stock.price.toFixed(2) }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-right" :class="stock.change >= 0 ? 'text-gain' : 'text-loss'">
                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right" :class="stock.change_percent >= 0 ? 'text-gain' : 'text-loss'">
                {{ stock.change_percent >= 0 ? '+' : '' }}{{ stock.change_percent.toFixed(2) }}%
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-center">
                <button class="text-sm text-primary hover:underline" @click="openTrade(stock)">交易</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <div v-if="selectedStock" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <section class="w-full max-w-md rounded-lg bg-white p-6">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-xl font-medium text-text">{{ selectedStock.symbol }} - {{ selectedStock.name || 'Stock' }}</h3>
          <button class="text-text-muted hover:text-text" @click="closeTrade">关闭</button>
        </div>

        <div class="mb-4 rounded bg-gray-50 p-3">
          <p class="text-sm text-text-muted">当前价格</p>
          <p class="text-xl font-medium">${{ selectedStock.price.toFixed(2) }}</p>
          <p class="text-sm" :class="selectedStock.change >= 0 ? 'text-gain' : 'text-loss'">
            {{ selectedStock.change >= 0 ? '+' : '' }}{{ selectedStock.change_percent.toFixed(2) }}%
          </p>
        </div>

        <form class="space-y-4" @submit.prevent="submitTrade">
          <div class="flex gap-2">
            <button
              type="button"
              class="flex-1 rounded-lg py-2 transition-colors"
              :class="tradeType === 'buy' ? 'bg-gain text-white' : 'bg-gray-100 text-text hover:bg-gray-200'"
              @click="tradeType = 'buy'"
            >
              买入
            </button>
            <button
              type="button"
              class="flex-1 rounded-lg py-2 transition-colors"
              :class="tradeType === 'sell' ? 'bg-loss text-white' : 'bg-gray-100 text-text hover:bg-gray-200'"
              @click="tradeType = 'sell'"
            >
              卖出
            </button>
          </div>

          <label class="block">
            <span class="mb-1 block text-sm text-text-muted">股数</span>
            <input
              v-model="shares"
              type="number"
              min="1"
              class="w-full rounded-lg border border-gray-200 px-3 py-2 focus:border-primary focus:outline-none"
              placeholder="输入股数"
            />
          </label>

          <div class="flex justify-between text-sm">
            <span class="text-text-muted">可用资金</span>
            <span>${{ (auth.currentAccount?.current_balance || 0).toFixed(2) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-text-muted">预估金额</span>
            <span>${{ Math.abs(estimatedAmount).toFixed(2) }}</span>
          </div>

          <p v-if="error" class="text-sm text-loss">{{ error }}</p>

          <button
            type="submit"
            :disabled="tradeLoading || !shares"
            class="w-full rounded-lg bg-primary py-3 text-white transition-colors hover:bg-primary-light disabled:opacity-50"
          >
            {{ tradeLoading ? '处理中...' : tradeType === 'buy' ? '买入' : '卖出' }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>
