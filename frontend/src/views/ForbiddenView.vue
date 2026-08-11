<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="mini-center">
    <div style="font-size:52px;">⛔</div>
    <h1>403 — Akses Ditolak</h1>
    <p class="muted">Role Anda tidak diizinkan membuka halaman ini (ISO/IEC 27001 · kontrol akses).</p>
    <div class="row" style="justify-content:center;margin-top:16px;">
      <button class="btn" @click="router.push('/dashboard')">← Kembali ke Dashboard</button>
    </div>
  </div>
</template>

<style scoped>
.mini-center { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px; }
h1 { font-size: 22px; margin: 8px 0; }
</style>
