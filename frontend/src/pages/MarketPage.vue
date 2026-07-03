<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import AppNav from '../components/AppNav.vue';
import { accountApi, orderApi, stockApi } from '../lib/api';
import type { OrderCreate, Quote, StockTrend, StockTrendPoint } from '../lib/types';
import { useAuthStore } from '../stores/auth';

const PAGE_SIZE = 20;
const DISPLAY_TIME_ZONE = 'Asia/Shanghai';

const auth = useAuthStore();
const stocks = ref<Quote[]>([]);
const loading = ref(true);
const tradeLoading = ref(false);
const error = ref('');
const lastUpdate = ref('');
const selectedStock = ref<Quote | null>(null);
const tradeType = ref<OrderCreate['type']>('buy');
const shares = ref('');
const currentPage = ref(1);
const expandedSymbol = ref<string | null>(null);
const trendRange = ref<'1d' | '7d'>('1d');
const trendCache = ref<Record<string, StockTrend>>({});
const trendLoading = ref(false);
const trendError = ref('');

const totalPages = computed(() => Math.max(1, Math.ceil(stocks.value.length / PAGE_SIZE)));
const visibleStocks = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE;
  return stocks.value.slice(start, start + PAGE_SIZE);
});

const pageStart = computed(() => stocks.value.length === 0 ? 0 : (currentPage.value - 1) * PAGE_SIZE + 1);
const pageEnd = computed(() => Math.min(currentPage.value * PAGE_SIZE, stocks.value.length));
const expandedTrend = computed(() => {
  if (!expandedSymbol.value) return null;
  return trendCache.value[trendKey(expandedSymbol.value, trendRange.value)] || null;
});

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
    currentPage.value = Math.min(currentPage.value, totalPages.value);
    lastUpdate.value = new Date().toLocaleTimeString('zh-CN', { timeZone: DISPLAY_TIME_ZONE });
  } catch (err) {
    console.error('Failed to load market data:', err);
  } finally {
    loading.value = false;
  }
}

function goToPage(page: number) {
  currentPage.value = Math.min(Math.max(page, 1), totalPages.value);
  expandedSymbol.value = null;
}

function trendKey(symbol: string, range: '1d' | '7d') {
  return `${symbol}:${range}`;
}

async function loadTrend(symbol: string, range: '1d' | '7d') {
  const key = trendKey(symbol, range);
  if (trendCache.value[key]) return;

  trendLoading.value = true;
  trendError.value = '';
  try {
    trendCache.value[key] = await stockApi.getTrend(symbol, range);
  } catch (err) {
    console.error('Failed to load stock trend:', err);
    trendError.value = '走势暂时不可用';
  } finally {
    trendLoading.value = false;
  }
}

async function toggleTrend(stock: Quote) {
  if (expandedSymbol.value === stock.symbol) {
    expandedSymbol.value = null;
    return;
  }

  expandedSymbol.value = stock.symbol;
  trendRange.value = '1d';
  await loadTrend(stock.symbol, trendRange.value);
}

async function setTrendRange(range: '1d' | '7d') {
  trendRange.value = range;
  if (expandedSymbol.value) {
    await loadTrend(expandedSymbol.value, range);
  }
}

function chartPath(points: StockTrendPoint[]) {
  if (points.length === 0) return '';

  const values = points.map((point) => point.price);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(max - min, 0.01);
  const width = 860;
  const height = 220;
  const singlePointY = height / 2;
  if (points.length === 1) {
    return `0,${singlePointY} ${width},${singlePointY}`;
  }

  return points
    .map((point, index) => {
      const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width;
      const y = height - ((point.price - min) / range) * (height - 28) - 14;
      return `${x},${y}`;
    })
    .join(' ');
}

function chartSummary(points: StockTrendPoint[]) {
  if (points.length === 0) {
    return { first: 0, last: 0, change: 0, changePercent: 0, min: 0, max: 0 };
  }

  const first = points[0].price;
  const last = points[points.length - 1].price;
  const change = last - first;
  const changePercent = first > 0 ? (change / first) * 100 : 0;
  const values = points.map((point) => point.price);
  return {
    first,
    last,
    change,
    changePercent,
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

function trendLabels(points: StockTrendPoint[]) {
  if (points.length === 0) return [];
  const timeZone = expandedTrend.value?.timezone || DISPLAY_TIME_ZONE;
  const localDates = points.map((point) => new Date(point.timestamp * 1000).toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    timeZone,
  }));
  const crossesDate = new Set(localDates).size > 1;
  const sample = points.filter((_, index) => {
    const stride = Math.max(1, Math.floor(points.length / 4));
    return index % stride === 0;
  }).slice(0, 5);

  return sample.map((point) => {
    const date = new Date(point.timestamp * 1000);
    if (trendRange.value !== '1d') {
      return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric', timeZone });
    }

    const time = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', timeZone });
    if (!crossesDate) {
      return time;
    }

    const day = date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric', timeZone });
    return `${day} ${time}`;
  });
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
  window.setInterval(loadMarketData, 60 * 60 * 1000);
});
</script>

<template>
  <div class="min-h-screen bg-white">
    <AppNav />

    <main class="mx-auto max-w-7xl px-6 py-8">
      <div class="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 class="text-2xl font-medium text-text">全球市场</h2>
          <p class="mt-1 text-sm text-text-muted">
            {{ stocks.length }} 只热门美股 · 每页 {{ PAGE_SIZE }} 只 · 每小时自动刷新 · 数据源 Finnhub
          </p>
          <p class="mt-1 text-xs text-text-muted">
            最后读取缓存：{{ lastUpdate || '等待数据' }}
          </p>
        </div>
        <button class="self-start rounded-lg bg-gray-100 px-4 py-2 transition-colors hover:bg-gray-200 md:self-auto" @click="loadMarketData">
          刷新缓存
        </button>
      </div>

      <div v-if="loading" class="rounded-lg bg-gray-50 p-10 text-center text-text-muted">
        正在加载市场数据...
      </div>

      <div v-else-if="stocks.length === 0" class="rounded-lg bg-gray-50 p-10 text-center text-text-muted">
        暂无市场数据。后台会按小时刷新行情，请稍后再试。
      </div>

      <div v-else class="overflow-hidden rounded-lg bg-gray-50">
        <div class="overflow-x-auto">
          <table class="w-full min-w-[760px]">
            <thead class="bg-gray-100">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase text-text-muted">代码</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase text-text-muted">名称</th>
                <th class="px-6 py-3 text-right text-xs font-medium uppercase text-text-muted">价格</th>
                <th class="px-6 py-3 text-right text-xs font-medium uppercase text-text-muted">涨跌</th>
                <th class="px-6 py-3 text-right text-xs font-medium uppercase text-text-muted">涨跌幅</th>
                <th class="px-6 py-3 text-center text-xs font-medium uppercase text-text-muted">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <template v-for="stock in visibleStocks" :key="stock.symbol">
                <tr
                  class="cursor-pointer transition-colors hover:bg-gray-100"
                  :class="expandedSymbol === stock.symbol ? 'bg-white' : ''"
                  @click="toggleTrend(stock)"
                >
                  <td class="whitespace-nowrap px-6 py-3 font-medium text-text">
                    <span class="mr-2 inline-block w-3 text-text-muted">{{ expandedSymbol === stock.symbol ? '−' : '+' }}</span>
                    {{ stock.symbol }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-3 text-sm text-text-muted">{{ stock.name || '-' }}</td>
                  <td class="whitespace-nowrap px-6 py-3 text-right font-medium text-text">${{ stock.price.toFixed(2) }}</td>
                  <td class="whitespace-nowrap px-6 py-3 text-right" :class="stock.change >= 0 ? 'text-gain' : 'text-loss'">
                    {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-3 text-right" :class="stock.change_percent >= 0 ? 'text-gain' : 'text-loss'">
                    {{ stock.change_percent >= 0 ? '+' : '' }}{{ stock.change_percent.toFixed(2) }}%
                  </td>
                  <td class="whitespace-nowrap px-6 py-3 text-center">
                    <button class="text-sm text-primary hover:underline" @click.stop="openTrade(stock)">交易</button>
                  </td>
                </tr>
                <tr v-if="expandedSymbol === stock.symbol" class="bg-white">
                  <td colspan="6" class="px-6 py-5">
                    <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p class="text-sm font-medium text-text">{{ stock.symbol }} 走势</p>
                        <p class="text-xs text-text-muted">点击股票行可收起，数据仅用于趋势参考</p>
                      </div>
                      <div class="flex gap-2">
                        <button
                          class="rounded border px-3 py-1.5 text-sm transition-colors"
                          :class="trendRange === '1d' ? 'border-primary bg-primary text-white' : 'border-gray-200 text-text-muted hover:bg-gray-50'"
                          @click.stop="setTrendRange('1d')"
                        >
                          近1天
                        </button>
                        <button
                          class="rounded border px-3 py-1.5 text-sm transition-colors"
                          :class="trendRange === '7d' ? 'border-primary bg-primary text-white' : 'border-gray-200 text-text-muted hover:bg-gray-50'"
                          @click.stop="setTrendRange('7d')"
                        >
                          近7天
                        </button>
                      </div>
                    </div>

                    <div v-if="trendLoading" class="flex h-56 items-center justify-center rounded bg-gray-50 text-sm text-text-muted">
                      正在加载走势...
                    </div>
                    <div v-else-if="trendError" class="flex h-56 items-center justify-center rounded bg-gray-50 text-sm text-loss">
                      {{ trendError }}
                    </div>
                    <div v-else-if="expandedTrend" class="rounded bg-gray-50 p-4">
                      <div class="mb-2 flex items-center justify-between text-xs text-text-muted">
                        <span>${{ chartSummary(expandedTrend.points).min.toFixed(2) }}</span>
                        <span
                          :class="chartSummary(expandedTrend.points).change >= 0 ? 'text-gain' : 'text-loss'"
                        >
                          {{ chartSummary(expandedTrend.points).change >= 0 ? '+' : '' }}{{ chartSummary(expandedTrend.points).change.toFixed(2) }}
                          ({{ chartSummary(expandedTrend.points).changePercent >= 0 ? '+' : '' }}{{ chartSummary(expandedTrend.points).changePercent.toFixed(2) }}%)
                        </span>
                        <span>${{ chartSummary(expandedTrend.points).max.toFixed(2) }}</span>
                      </div>
                      <svg viewBox="0 0 860 220" class="h-56 w-full overflow-visible">
                        <line x1="0" y1="14" x2="860" y2="14" stroke="#e5e7eb" stroke-dasharray="4 4" />
                        <line x1="0" y1="110" x2="860" y2="110" stroke="#e5e7eb" stroke-dasharray="4 4" />
                        <line x1="0" y1="206" x2="860" y2="206" stroke="#e5e7eb" stroke-dasharray="4 4" />
                        <polyline
                          :points="chartPath(expandedTrend.points)"
                          fill="none"
                          :stroke="chartSummary(expandedTrend.points).change >= 0 ? '#22c55e' : '#ef4444'"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                      <div class="grid grid-cols-5 text-xs text-text-muted">
                        <span v-for="label in trendLabels(expandedTrend.points)" :key="label">{{ label }}</span>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <div class="flex flex-col gap-3 border-t border-gray-200 px-6 py-4 text-sm text-text-muted md:flex-row md:items-center md:justify-between">
          <span>显示 {{ pageStart }}-{{ pageEnd }} / {{ stocks.length }}</span>
          <div class="flex items-center gap-2">
            <button
              class="rounded border border-gray-200 px-3 py-1.5 transition-colors hover:bg-white disabled:opacity-40"
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
            >
              上一页
            </button>
            <button
              v-for="page in totalPages"
              :key="page"
              class="h-8 w-8 rounded border text-center transition-colors"
              :class="page === currentPage ? 'border-primary bg-primary text-white' : 'border-gray-200 hover:bg-white'"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
            <button
              class="rounded border border-gray-200 px-3 py-1.5 transition-colors hover:bg-white disabled:opacity-40"
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>
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
