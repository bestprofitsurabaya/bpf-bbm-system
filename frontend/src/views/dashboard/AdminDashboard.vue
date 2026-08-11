<script setup>
import { computed, onMounted, ref, watch } from 'vue'
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
  loadQueue()
})

async function refreshStats() {
  // Refresh diam-diam (tanpa mengubah state loading) agar dashboard tidak berkedip.
  try { s.value = await api('/api/stats') } catch { /* abaikan */ }
}

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

// ============================================================
// Antrean Kerja (v2.2.2) — approve GA / payout / archive / reject
// ============================================================
const QUEUE_TABS = [
  { key: 'ga', label: '🕐 Antrean GA', roles: ['ga', 'admin'] },
  { key: 'finance', label: '💰 Finance', roles: ['finance', 'admin'] },
  { key: 'driver_confirm', label: '🤝 Konfirmasi Driver', roles: ['finance', 'admin'] },
]
const queueTab = ref('ga')
const queue = ref([])
const queueLoading = ref(false)
const queueMsg = ref('')
const qBusy = ref(false)

const queueTabs = computed(() => QUEUE_TABS.filter((t) => t.roles.includes(auth.role)))
const canApprove = computed(() => ['ga', 'admin'].includes(auth.role))
const canFinance = computed(() => ['finance', 'admin'].includes(auth.role))

async function loadQueue() {
  queueLoading.value = true; queueMsg.value = ''
  try { queue.value = (await api('/api/queue', { params: { tab: queueTab.value } })) || [] }
  catch (e) { queueMsg.value = '❌ ' + e.message }
  finally { queueLoading.value = false }
}

async function queueAction(path, label) {
  if (!confirm(`Yakin ${label}?`)) return
  qBusy.value = true; queueMsg.value = ''
  try {
    const r = await api(path, { method: 'POST' })
    queueMsg.value = '✅ ' + (r.msg || r.message || label)
    loadQueue(); refreshStats()
  } catch (e) { queueMsg.value = '❌ ' + e.message }
  finally { qBusy.value = false }
}

function doApprove(tx) {
  if (tx.ml_anomaly_flag) {
    queueMsg.value = '⚠️ Transaksi ber-flag anomali ML — wajib verifikasi penuh (foto bukti) di Dashboard Klasik.'
    return
  }
  return queueAction(`/api/queue/approve-ga/${tx.id}`, 'menyetujui klaim ini')
}
const doPayout = (tx) => queueAction(`/api/queue/payout/${tx.id}`, 'mencairkan dana klaim ini')
const doArchive = (tx) => queueAction(`/api/queue/archive/${tx.id}`, 'mengarsipkan klaim ini')

async function doReject(tx) {
  const reason = prompt(`Alasan menolak ${tx.display_id} (${tx.driver_name}):`, '')
  if (reason === null) return
  qBusy.value = true; queueMsg.value = ''
  try {
    const r = await api(`/api/queue/reject/${tx.id}`, { method: 'POST', body: { reason } })
    queueMsg.value = '✅ ' + (r.msg || 'Klaim ditolak')
    loadQueue(); refreshStats()
  } catch (e) { queueMsg.value = '❌ ' + e.message }
  finally { qBusy.value = false }
}

watch(queueTab, loadQueue)
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

      <!-- Antrean Kerja -->
      <div class="card card-pad" style="margin-top:18px;">
        <div class="row" style="flex-wrap:wrap;gap:8px;">
          <h3 style="margin:0;">🕐 Antrean Kerja</h3>
          <button v-for="t in queueTabs" :key="t.key" class="btn btn-sm" :class="queueTab === t.key ? 'btn-primary' : ''" @click="queueTab = t.key">{{ t.label }}</button>
          <span v-if="queueMsg" class="alert" :class="queueMsg.startsWith('✅') ? 'alert-success' : 'alert-error'" style="margin:0;">{{ queueMsg }}</span>
          <div class="spacer"></div>
          <a class="btn btn-sm" href="/admin" target="_blank">📋 Verifikasi Penuh (Klasik)</a>
        </div>
        <div v-if="queueLoading" class="empty" style="padding:20px;">⏳ Memuat antrean…</div>
        <div class="table-wrap" v-else>
          <table class="tbl">
            <thead><tr><th>ID</th><th>Driver</th><th>Nopol</th><th>BBM</th><th>Nominal</th><th>Liter</th><th>ODO</th><th>Anomali</th><th>Waktu</th><th></th></tr></thead>
            <tbody>
              <tr v-for="t in queue" :key="t.id">
                <td><b>{{ t.display_id }}</b></td>
                <td>{{ t.driver_name }}</td>
                <td>{{ t.nopol }}</td>
                <td>{{ t.bbm_type }}</td>
                <td>{{ fmt(t.nominal) }}</td>
                <td>{{ Number(t.liter || 0).toFixed(2) }}</td>
                <td>{{ t.odo_km ?? '—' }}</td>
                <td><span v-if="t.ml_anomaly_flag" class="badge badge-red">⚠️ Anomali</span><span v-else class="muted">—</span></td>
                <td class="muted">{{ t.created_at }}</td>
                <td>
                  <template v-if="queueTab === 'ga' && canApprove">
                    <template v-if="t.ml_anomaly_flag">
                      <span class="muted" style="font-size:11px;">⚠️ Wajib verifikasi klasik</span>
                    </template>
                    <template v-else>
                      <button class="btn btn-sm btn-primary" :disabled="qBusy" @click="doApprove(t)">✅ Approve</button>
                      <button class="btn btn-sm btn-danger" :disabled="qBusy" style="margin-left:6px;" @click="doReject(t)">❌ Tolak</button>
                    </template>
                  </template>
                  <template v-else-if="queueTab === 'finance' && canFinance">
                    <button class="btn btn-sm btn-primary" :disabled="qBusy" @click="doPayout(t)">💰 Cairkan</button>
                  </template>
                  <template v-else-if="queueTab === 'driver_confirm' && canFinance">
                    <button class="btn btn-sm btn-primary" :disabled="qBusy" @click="doArchive(t)">📦 Arsipkan</button>
                  </template>
                  <span v-else class="muted">—</span>
                </td>
              </tr>
              <tr v-if="!queue.length"><td colspan="10" class="empty">Antrean kosong. 🎉</td></tr>
            </tbody>
          </table>
        </div>
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
        <h3>🔎 Verifikasi Mendalam (transisi)</h3>
        <p class="muted" style="font-size:12px;margin-bottom:10px;">
          Untuk verifikasi lengkap (foto bukti, cross-check, finance review, edit ODO) antrean tetap tersedia di antarmuka klasik — dibuka di tab baru.
        </p>
        <div class="row">
          <a class="btn" href="/admin" target="_blank">📋 Dashboard Klasik</a>
          <a class="btn" href="/ga/assignments" target="_blank">🚗 Assignments Klasik</a>
        </div>
      </div>
    </template>
  </div>
</template>
