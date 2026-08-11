<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="mini-center">
    <div style="font-size:52px;">🧭</div>
    <h1>404 — Halaman Tidak Ditemukan</h1>
    <p class="muted">Alamat yang Anda tuju tidak tersedia.</p>
    <div class="row" style="justify-content:center;margin-top:16px;">
      <button class="btn" @click="router.push('/')">← Ke Beranda</button>
    </div>
  </div>
</template>

<style scoped>
.mini-center { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px; }
h1 { font-size: 22px; margin: 8px 0; }
</style>
