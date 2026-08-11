<script setup>
import { useRealtimeStore } from '../stores/realtime'
const rt = useRealtimeStore()
</script>

<template>
  <div class="toast-stack">
    <transition-group name="toast">
      <div v-for="t in rt.toasts" :key="t.id" class="toast" @click="rt.dismissToast(t.id)">
        <span class="toast-icon" :class="t.type">{{ t.text.split(' ')[0] }}</span>
        <span>{{ t.text }}</span>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-stack { position: fixed; bottom: 20px; right: 20px; z-index: 2000; display: flex; flex-direction: column; gap: 8px; max-width: 340px; }
.toast { background: var(--card, #fff); color: var(--text, #0f172a); border: 1px solid var(--border, #e2e8f0); border-left: 4px solid #2563eb; border-radius: 10px; padding: 10px 14px; font-size: 13px; box-shadow: 0 8px 24px rgba(2, 6, 23, .18); cursor: pointer; display: flex; gap: 8px; align-items: center; }
.toast-icon { font-size: 15px; }
.toast-enter-active, .toast-leave-active { transition: all .3s ease; }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: translateX(30px); }
@media (max-width: 640px) { .toast-stack { left: 12px; right: 12px; max-width: none; } }
</style>
