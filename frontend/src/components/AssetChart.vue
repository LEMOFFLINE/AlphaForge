<script setup lang="ts">
import { computed } from 'vue';
import type { AccountValue } from '../lib/types';

const props = defineProps<{
  data: AccountValue[];
}>();

const chart = computed(() => {
  if (props.data.length === 0) {
    return { points: '', labels: [] as string[], min: 0, max: 0 };
  }

  const values = props.data.map((item) => item.total_value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(max - min, 1);
  const width = 680;
  const height = 220;

  const points = props.data
    .map((item, index) => {
      const x = props.data.length === 1 ? width / 2 : (index / (props.data.length - 1)) * width;
      const y = height - ((item.total_value - min) / range) * (height - 24) - 12;
      return `${x},${y}`;
    })
    .join(' ');

  const labels = props.data.slice(-5).map((item) =>
    new Date(item.recorded_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
  );

  return { points, labels, min, max };
});

function money(value: number) {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}
</script>

<template>
  <div v-if="data.length === 0" class="flex h-64 items-center justify-center text-text-muted/60">
    暂无数据
  </div>
  <div v-else class="h-64">
    <div class="mb-2 flex justify-between text-xs text-text-muted">
      <span>{{ money(chart.min) }}</span>
      <span>{{ money(chart.max) }}</span>
    </div>
    <svg viewBox="0 0 680 220" class="h-52 w-full overflow-visible">
      <line x1="0" y1="12" x2="680" y2="12" stroke="#e5e7eb" stroke-dasharray="4 4" />
      <line x1="0" y1="110" x2="680" y2="110" stroke="#e5e7eb" stroke-dasharray="4 4" />
      <line x1="0" y1="208" x2="680" y2="208" stroke="#e5e7eb" stroke-dasharray="4 4" />
      <polyline :points="chart.points" fill="none" stroke="#1a3d63" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    <div class="grid grid-cols-5 text-xs text-text-muted">
      <span v-for="label in chart.labels" :key="label">{{ label }}</span>
    </div>
  </div>
</template>
