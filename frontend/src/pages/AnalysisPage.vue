<script setup lang="ts">
import { nextTick, ref } from 'vue';
import AppNav from '../components/AppNav.vue';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const messages = ref<Message[]>([
  {
    id: '1',
    role: 'assistant',
    content: '你好，我是 AlphaForge 的 AI 投资助手。你可以先在这里记录想分析的标的，后续可以接入真实 AI 分析接口。',
    timestamp: new Date(),
  },
]);
const input = ref('');
const loading = ref(false);
const messagesEnd = ref<HTMLDivElement | null>(null);

async function scrollToBottom() {
  await nextTick();
  messagesEnd.value?.scrollIntoView({ behavior: 'smooth' });
}

async function submit() {
  if (!input.value.trim() || loading.value) return;

  messages.value.push({
    id: Date.now().toString(),
    role: 'user',
    content: input.value.trim(),
    timestamp: new Date(),
  });
  input.value = '';
  loading.value = true;
  await scrollToBottom();

  window.setTimeout(async () => {
    messages.value.push({
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: 'AI 分析后端尚未接入。下一步可以把这里连接到 OpenAI API，并结合你的持仓、订单和实时行情做组合分析。',
      timestamp: new Date(),
    });
    loading.value = false;
    await scrollToBottom();
  }, 800);
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    submit();
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-white">
    <AppNav />

    <main class="mx-auto flex w-full max-w-4xl flex-1 flex-col">
      <div class="flex-1 overflow-y-auto px-6 py-8">
        <div class="space-y-6">
          <div
            v-for="message in messages"
            :key="message.id"
            class="flex gap-4"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div v-if="message.role === 'assistant'" class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary text-white">
              A
            </div>
            <div
              class="max-w-[80%] rounded-2xl px-5 py-3"
              :class="message.role === 'user' ? 'bg-primary text-white' : 'bg-gray-100 text-text'"
            >
              <p class="whitespace-pre-wrap text-sm leading-relaxed">{{ message.content }}</p>
              <p class="mt-2 text-xs" :class="message.role === 'user' ? 'text-white/60' : 'text-text-muted'">
                {{ message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }}
              </p>
            </div>
            <div v-if="message.role === 'user'" class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-300 text-white">
              U
            </div>
          </div>

          <div v-if="loading" class="flex justify-start gap-4">
            <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary text-white">A</div>
            <div class="rounded-2xl bg-gray-100 px-5 py-3 text-sm text-text-muted">正在分析...</div>
          </div>
        </div>
        <div ref="messagesEnd" />
      </div>

      <div class="border-t border-gray-200 px-6 py-4">
        <form class="flex gap-3" @submit.prevent="submit">
          <textarea
            v-model="input"
            rows="1"
            placeholder="输入你的问题..."
            class="min-h-12 max-h-48 flex-1 resize-none rounded-2xl bg-gray-100 px-4 py-3 text-sm transition-all focus:outline-none focus:ring-2 focus:ring-primary/20"
            @keydown="handleKeydown"
          />
          <button
            type="submit"
            :disabled="!input.trim() || loading"
            class="rounded-2xl bg-primary px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-light disabled:cursor-not-allowed disabled:opacity-40"
          >
            发送
          </button>
        </form>
        <p class="mt-3 text-center text-xs text-text-muted">AI 分析功能可作为下一阶段接入真实模型。</p>
      </div>
    </main>
  </div>
</template>
