<script setup>
defineProps({ message: { type: String, default: 'Tidak ada data' }, hint: { type: String, default: '' }, icon: { type: String, default: '📭' } })
</script>

<template>
  <div class="empty" role="status">
    <div class="empty-icon">{{ icon }}</div>
    <div class="empty-title">{{ message }}</div>
    <div v-if="hint" class="muted empty-hint">{{ hint }}</div>
  </div>
</template>

<style scoped>
.empty { display:flex; flex-direction:column; align-items:center; gap:8px; padding:40px 16px; text-align:center; }
.empty-icon { font-size:38px; opacity:.85; }
.empty-title { font-weight:600; }
.empty-hint { font-size:12px; }
</style>
