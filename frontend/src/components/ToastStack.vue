<script setup>
import { useRealtimeStore } from '../stores/realtime'
const rt = useRealtimeStore()

const ACCENT = {
  new_claim: 'var(--warning)',
  new_trip_report: 'var(--primary)',
  appointment_update: '#7c3aed',
  water_purchase_new: 'var(--info)',
  success: 'var(--success)',
  error: 'var(--danger)',
}
</script>

<template>
  <div class="toast-stack" aria-live="polite" aria-atomic="false">
    <transition-group name="toast">
      <div v-for="t in rt.toasts" :key="t.id" class="toast" :style="{ borderLeftColor: ACCENT[t.type] || 'var(--primary)' }" @click="rt.dismissToast(t.id)">
        <span class="toast-icon" :class="t.type" aria-hidden="true">{{ t.text.split(' ')[0] }}</span>
        <span>{{ t.text }}</span>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-stack { position: fixed; bottom: 20px; right: 20px; z-index: 2000; display: flex; flex-direction: column; gap: 8px; max-width: 340px; }
.toast {
  background: var(--surface); color: var(--text); border: 1px solid var(--border);
  border-left: 4px solid var(--primary); border-radius: 10px; padding: 10px 14px; font-size: 13px;
  box-shadow: 0 8px 24px rgba(2, 6, 23, .18); cursor: pointer; display: flex; gap: 8px; align-items: center;
  transition: transform .15s;
}
.toast:hover { transform: translateY(-1px); }
.toast-icon { font-size: 15px; }
.toast-enter-active, .toast-leave-active { transition: all .3s ease; }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: translateX(30px); }
@media (max-width: 640px) { .toast-stack { left: 12px; right: 12px; max-width: none; } }
</style>
