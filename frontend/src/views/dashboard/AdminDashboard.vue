<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api'
import { useAuthStore } from '../../stores/auth'
import StatCard from '../../components/StatCard.vue'

const auth = useAuthStore()
const s = ref(null)
const loading = ref(true)
const err = ref('')

const fmt = (n) => 'Rp ' + Number(n || 0).toLocaleString('id-ID')

onMounted(async () => {
  try { s.value = await api('/api/stats') }
  catch (e) { err.value = e.message }
  finally { loading.value = false }
})

const cards = computed(() => {
  if (!s.value) return []
  const c = [
    { icon: '🕐', label: 'Antrean GA (pending)', value: s.value.pending, color: '#dc2626', roles: ['ga', 'admin'] },
    { icon: '✅', label: 'Verified GA', value: s.value.verified_ga, color: '#0891b2', roles: ['ga', 'admin'] },
    { icon: '💰', label: 'Menunggu Finance (os_finance)', value: s.value.os_finance, color: '#d97706', roles: ['finance', 'admin'] },
    { icon: '📦', label: 'Terarsip', value: s.value.archived, color: '#059669', roles: ['ga', 'finance', 'admin'] },
    { icon: '📅', label: 'Transaksi Hari Ini', value: s.value.today_tx, color: '#2563eb', roles: ['ga', 'finance', 'admin'] },
    { icon: '💵', label: 'Nominal Hari Ini', value: fmt(s.value.today_nominal), color: '#7c3aed', roles: ['finance', 'admin'] },
  ]
  return c.filter((x) => x.roles.includes(auth.role))
})

const quick = computed(() => {
  const m = [
    { icon: '🗺️', label: 'Log Perjalanan', path: '/trips', roles: ['ga', 'finance', 'admin'] },
    { icon: '🚗', label: 'Assignments', path: '/assignments', roles: ['ga', 'admin'] },
    { icon: '📋', label: 'Rekap', path: '/rekap', roles: ['finance', 'admin'] },
    { icon: '📈', label: 'Analytics', path: '/analytics', roles: ['ga', 'finance', 'admin'] },
    { icon: '👥', label: 'Manajemen User', path: '/users', roles: ['admin'] },
    { icon: '📝', label: 'Audit Log', path: '/logs', roles: ['admin'] },
    { icon: '⚙️', label: 'Pengaturan', path: '/settings', roles: ['admin'] },
  ]
  return m.filter((x) => x.roles.includes(auth.role))
})
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
      <div style="font-size:26px;">{{ auth.meta?.icon }}</div>
      <div class="grow">
        <div style="font-weight:800;font-size:16px;">Selamat datang, {{ auth.user?.full_name || auth.user?.user_name }}</div>
        <div class="muted" style="font-size:12px;">
          Dashboard {{ auth.meta?.label }} · data transaksi &amp; klaim BBM terkini
        </div>
      </div>
      <span class="role-chip" :style="{ background: auth.meta?.color }">{{ auth.meta?.label }}</span>
    </div>

    <div v-if="loading" class="empty">⏳ Memuat data…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <template v-else>
      <div class="stat-grid">
        <StatCard v-for="c in cards" :key="c.label" :icon="c.icon" :label="c.label" :value="c.value" :color="c.color" />
      </div>

      <div class="card card-pad" style="margin-top:18px;">
        <h3>⚡ Aksi Cepat</h3>
        <div class="stat-grid">
          <router-link v-for="q in quick" :key="q.path" :to="q.path" style="text-decoration:none;">
            <div class="stat-card" style="display:flex;align-items:center;gap:12px;">
              <span style="font-size:22px;">{{ q.icon }}</span>
              <span style="font-weight:600;font-size:13px;">{{ q.label }}</span>
            </div>
          </router-link>
        </div>
      </div>

      <div class="card card-pad" style="margin-top:18px;">
        <h3>🔧 Panel Lanjutan (transisi)</h3>
        <p class="muted" style="font-size:12px;margin-bottom:10px;">
          Alur kerja persetujuan klaim (antrean GA / Finance / TTD) masih berjalan di antarmuka klasik — dibuka di tab baru.
        </p>
        <div class="row">
          <a class="btn" href="/admin" target="_blank">📋 Dashboard Klasik</a>
          <a class="btn" href="/ga/assignments" target="_blank">🚗 Assignments Klasik</a>
        </div>
      </div>
    </template>
  </div>
</template>
