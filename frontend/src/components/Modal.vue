<script setup>
defineProps({ title: { type: String, default: '' } })
const emit = defineEmits(['close'])
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-box">
      <div class="row" style="justify-content:space-between;margin-bottom:10px;">
        <h3 style="margin:0;">{{ title }}</h3>
        <button class="btn-icon" @click="emit('close')">✕</button>
      </div>
      <slot />
    </div>
  </div>
</template>
