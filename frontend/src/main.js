import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useRealtimeStore } from './stores/realtime'
import './styles/main.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Error boundary global (v2.21): kesalahan tak tertangkap di komponen tidak
// lagi berakhir layar kosong — tampilkan toast ringkas + log ke console.
app.config.errorHandler = (err, instance, info) => {
  console.error('[error-boundary]', info, err)
  try {
    useRealtimeStore(pinia).push(`⚠️ ${err?.message || 'Terjadi kesalahan'}`, 'error')
  } catch { /* store belum siap — abaikan */ }
}

app.mount('#app')

// PWA: daftarkan service worker khusus SPA (scope /app/) saat produksi
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/app/sw.js', { scope: '/app/' }).catch(() => {})
  })
}
