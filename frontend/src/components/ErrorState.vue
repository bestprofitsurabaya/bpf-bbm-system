<script setup>
defineProps({ message: { type: String, default: 'Terjadi kesalahan' }, retryable: { type: Boolean, default: true } })
const emit = defineEmits(['retry'])
</script>

<template>
  <div class="empty" role="alert">
    <div class="empty-icon">⚠️</div>
    <div class="empty-title">{{ message }}</div>
    <button v-if="retryable" class="btn" @click="emit('retry')">🔄 Coba lagi</button>
  </div>
</template>

<style scoped>
.empty { display:flex; flex-direction:column; align-items:center; gap:10px; padding:40px 16px; text-align:center; }
.empty-icon { font-size:38px; }
.empty-title { font-weight:600; color: var(--danger, #b91c1c); }
</style>
