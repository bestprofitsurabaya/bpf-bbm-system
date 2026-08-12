<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'

defineProps({ title: { type: String, default: '' }, wide: { type: Boolean, default: false } })
const emit = defineEmits(['close'])

const closeBtn = ref(null)
const boxRef = ref(null)
let lastFocus = null

function close() { emit('close') }

function onKey(e) {
  if (e.key === 'Escape') { close(); return }
  // Focus trap: Tab tidak boleh keluar dari modal (WCAG 2.4.3)
  if (e.key === 'Tab' && boxRef.value) {
    const f = boxRef.value.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')
    if (!f.length) return
    const first = f[0]
    const last = f[f.length - 1]
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
  }
}

onMounted(() => {
  lastFocus = document.activeElement
  closeBtn.value?.focus()
  document.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKey)
  lastFocus?.focus?.()
})
</script>

<template>
  <div class="modal-overlay" role="dialog" aria-modal="true" :aria-label="title" @click.self="close">
    <div ref="boxRef" class="modal-box" :class="{ 'modal-wide': wide }">
      <div class="row" style="justify-content:space-between;margin-bottom:10px;">
        <h3 style="margin:0;">{{ title }}</h3>
        <button ref="closeBtn" class="btn-icon" aria-label="Tutup" title="Tutup (Esc)" @click="close">✕</button>
      </div>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.modal-wide { max-width: 860px; width: 94%; }
</style>
