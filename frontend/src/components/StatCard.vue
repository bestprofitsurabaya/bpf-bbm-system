<script setup>
defineProps({
  icon: { type: String, default: '📊' },
  label: { type: String, required: true },
  value: { type: [String, Number], default: '—' },
  color: { type: String, default: '#2563eb' },
  sub: { type: String, default: '' },
})
</script>

<template>
  <div class="stat-card">
    <span class="s-icon" :style="{ background: color + '1a' }">{{ icon }}</span>
    <div class="s-value" :style="{ color }">{{ value }}</div>
    <div class="s-label">{{ label }}</div>
    <div v-if="sub" class="s-label">{{ sub }}</div>
    <div class="s-bar" :style="{ background: color }"></div>
  </div>
</template>
