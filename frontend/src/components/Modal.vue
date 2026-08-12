<script setup>
defineProps({ title: { type: String, default: '' }, wide: { type: Boolean, default: false } })
const emit = defineEmits(['close'])
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-box" :class="{ 'modal-wide': wide }">
      <div class="row" style="justify-content:space-between;margin-bottom:10px;">
        <h3 style="margin:0;">{{ title }}</h3>
        <button class="btn-icon" @click="emit('close')">✕</button>
      </div>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.modal-wide { max-width: 860px; width: 94%; }
</style>
