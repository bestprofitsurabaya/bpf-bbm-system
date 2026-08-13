<script setup>
defineProps({ rows: { type: Number, default: 3 }, label: { type: String, default: 'Memuat…' } })
</script>

<template>
  <div class="empty skeleton" role="status" aria-live="polite" :aria-label="label">
    <div v-for="i in rows" :key="i" class="skeleton-line" :style="{ width: `${90 - i * 12}%` }"></div>
  </div>
</template>

<style scoped>
.skeleton { padding: 32px 16px; display: flex; flex-direction: column; gap: 12px; }
.skeleton-line { height: 14px; border-radius: 6px; background: var(--skeleton, #e2e8f0); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .45; } }
</style>
