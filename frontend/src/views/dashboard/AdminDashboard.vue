<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '../../api'
import { useAuthStore } from '../../stores/auth'
import StatCard from '../../components/StatCard.vue'
import Modal from '../../components/Modal.vue'

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
// Antrean Kerja — approve GA / payout / archive / reject / detail
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
const isAdmin = computed(() => auth.role === 'admin')

// Modal detail transaksi
const sel = ref(null)
const selData = ref(null)
const selCross = ref(null)
const selLoading = ref(false)

async function loadQueue() {
  queueLoading.value = true; queueMsg.value = ''
  try { queue.value = (await api('/api/queue', { params: { tab: queueTab.value } })) || [] }
  catch (e) { queueMsg.value = '❌ ' + e.message }
  finally { queueLoading.value = false }
}

async function queueAction(path, label) {
  if (!confirm(`Yakin ${label}?`)) return false
  qBusy.value = true; queueMsg.value = ''
  try {
    const r = await api(path, { method: 'POST' })
    queueMsg.value = '✅ ' + (r.msg || r.message || label)
    loadQueue(); refreshStats()
    return true
  } catch (e) { queueMsg.value = '❌ ' + e.message; return false }
  finally { qBusy.value = false }
}

async function modalAction(path, label) {
  const ok = await queueAction(path, label)
  if (ok) { sel.value = null; selData.value = null; selCross.value = null }
  return ok
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
    if (sel.value) { sel.value = null; selData.value = null; selCross.value = null }
  } catch (e) { queueMsg.value = '❌ ' + e.message }
  finally { qBusy.value = false }
}

async function openDetail(tx) {
  sel.value = tx
  selLoading.value = true
  selData.value = null; selCross.value = null
  try {
    const [d, c] = await Promise.all([
      api(`/api/transactions/detail/${tx.id}`),
      api(`/api/cross-check/${tx.id}`).catch(() => null),
    ])
    selData.value = d
    selCross.value = c
  } catch (e) { queueMsg.value = '❌ ' + e.message }
  finally { selLoading.value = false }
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
                  <button class="btn btn-sm" :disabled="qBusy" title="Detail & verifikasi" @click="openDetail(t)">👁 Detail</button>
                  <template v-if="queueTab === 'ga' && canApprove">
                    <template v-if="t.ml_anomaly_flag">
                      <span class="muted" style="font-size:11px;margin-left:6px;">⚠️ Wajib klasik</span>
                    </template>
                    <template v-else>
                      <button class="btn btn-sm btn-primary" :disabled="qBusy" style="margin-left:6px;" @click="doApprove(t)">✅</button>
                      <button class="btn btn-sm btn-danger" :disabled="qBusy" style="margin-left:6px;" @click="doReject(t)">❌</button>
                    </template>
                  </template>
                  <template v-else-if="queueTab === 'finance' && canFinance">
                    <button class="btn btn-sm btn-primary" :disabled="qBusy" style="margin-left:6px;" @click="doPayout(t)">💰</button>
                  </template>
                  <template v-else-if="queueTab === 'driver_confirm' && canFinance">
                    <button class="btn btn-sm btn-primary" :disabled="qBusy" style="margin-left:6px;" @click="doArchive(t)">📦</button>
                  </template>
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
        <h3>🔎 Verifikasi Mendalam</h3>
        <p class="muted" style="font-size:12px;margin-bottom:10px;">
          Klik <b>👁 Detail</b> pada baris antrean untuk melihat foto bukti, hasil cross-check (health score, flag, budget) &amp; riwayat — langsung dari SPA. Verifikasi klasik tetap tersedia di tab baru.
        </p>
        <div class="row">
          <a class="btn" href="/admin" target="_blank">📋 Dashboard Klasik</a>
          <a class="btn" href="/ga/assignments" target="_blank">🚗 Assignments Klasik</a>
        </div>
      </div>
    </template>

    <!-- Modal Detail Transaksi -->
    <Modal v-if="sel" :title="'🔍 ' + (selData?.display_id || sel.display_id || 'Detail Transaksi')" @close="sel = null; selData = null; selCross = null">
      <div v-if="selLoading" class="empty" style="padding:16px;">⏳ Memuat detail…</div>
      <div v-else-if="selData">
        <div class="row" style="flex-wrap:wrap;gap:8px;margin-bottom:12px;">
          <span class="badge" :class="selData.ml_anomaly_flag ? 'badge-red' : 'badge-green'">{{ selData.ml_anomaly_flag ? '⚠️ Anomali ML' : 'Normal' }}</span>
          <span class="badge badge-blue">{{ selData.status }}</span>
          <span class="badge" :class="selData.is_mypertamina_error ? 'badge-red' : 'badge-gray'">{{ selData.is_mypertamina_error ? '⚠️ Error MyPertamina' : 'MyPertamina OK' }}</span>
        </div>

        <div class="form-grid">
          <div class="field"><label>Driver</label><input class="input" :value="selData.driver_name" disabled /></div>
          <div class="field"><label>Nopol / Kendaraan</label><input class="input" :value="selData.nopol + ' · ' + (selData.vehicle_type || '')" disabled /></div>
          <div class="field"><label>BBM / SPBU</label><input class="input" :value="selData.bbm_type + ' · ' + (selData.spbu_type || '')" disabled /></div>
          <div class="field"><label>Nominal / Liter</label><input class="input" :value="fmt(selData.nominal) + ' · ' + Number(selData.liter || 0).toFixed(2) + ' L'" disabled /></div>
          <div class="field"><label>ODO / Km per Liter</label><input class="input" :value="selData.odo_km + ' km · ' + Number(selData.km_per_liter || 0).toFixed(1) + ' km/L'" disabled /></div>
          <div class="field"><label>Waktu</label><input class="input" :value="selData.created_at" disabled /></div>
        </div>
        <p v-if="selData.gps_address" class="muted" style="font-size:11px;">📍 {{ selData.gps_address }}</p>
        <p v-if="selData.rejection_reason" class="alert alert-error" style="margin:6px 0;">❌ Alasan tolak: {{ selData.rejection_reason }}</p>

        <h4 style="margin:12px 0 8px;">📷 Foto Bukti</h4>
        <div v-if="selData.photos?.length" style="display:flex;gap:8px;flex-wrap:wrap;">
          <a v-for="p in selData.photos" :key="p.url" :href="p.url" target="_blank" style="text-align:center;text-decoration:none;">
            <img :src="p.url" :alt="p.label" style="width:84px;height:84px;object-fit:cover;border-radius:8px;border:1px solid var(--border, #334155);" />
            <div class="muted" style="font-size:10px;">{{ p.label }}</div>
          </a>
        </div>
        <div v-else class="muted" style="font-size:12px;">Tidak ada foto bukti.</div>

        <template v-if="selCross">
          <h4 style="margin:14px 0 8px;">🩺 Cross-Check</h4>
          <div class="row" style="gap:10px;flex-wrap:wrap;">
            <div class="stat-card" style="flex:1;min-width:120px;">
              <div class="s-icon" style="background:#2563eb1a;">🩺</div>
              <div class="s-value" style="color:#2563eb;font-size:20px;">{{ selCross.health_score || 0 }}/100</div>
              <div class="s-label">Health Score</div>
            </div>
            <div class="stat-card" style="flex:1;min-width:120px;">
              <div class="s-icon" style="background:#d977061a;">📊</div>
              <div class="s-value" style="color:#d97706;font-size:20px;">{{ selCross.budget_usage_percent || 0 }}%</div>
              <div class="s-label">Budget Bulanan</div>
            </div>
            <div class="stat-card" style="flex:1;min-width:120px;">
              <div class="s-icon" style="background:#0596691a;">🧮</div>
              <div class="s-value" style="color:#059669;font-size:20px;">{{ Number(selCross.odo_diff || 0).toLocaleString('id-ID') }}</div>
              <div class="s-label">Selisih ODO</div>
            </div>
          </div>
          <ul style="margin:10px 0 0;padding-left:18px;font-size:12px;">
            <li v-for="(f, i) in selCross.flags || []" :key="i" :class="f.level === 'danger' ? 'alert-error' : f.level === 'warning' ? 'alert-info' : 'alert-success'" style="padding:4px 8px;border-radius:6px;margin-bottom:4px;list-style:none;">
              {{ f.level === 'danger' ? '🔴' : f.level === 'warning' ? '🟡' : '🟢' }} {{ f.msg }}
            </li>
            <li v-if="!(selCross.flags || []).length" class="muted" style="list-style:none;">Tidak ada flag — transaksi bersih ✅</li>
          </ul>
          <p class="muted" style="font-size:11px;margin:8px 0 0;">
            Rekomendasi: <b>{{ selCross.recommendation }}</b> · Rata-rata 3 bulan: {{ selCross.avg_3months?.avg_kml || '—' }} km/L ({{ selCross.avg_3months?.tx_count || 0 }} tx)
          </p>
        </template>

        <div class="row" style="justify-content:flex-end;margin-top:14px;gap:6px;flex-wrap:wrap;">
          <a class="btn btn-sm" :href="'/admin?tab=ga_queue'" target="_blank">📋 Klasik</a>
          <template v-if="selData.status === 'pending' || selData.status === 'modified'">
            <button v-if="canApprove && !selData.ml_anomaly_flag" class="btn btn-sm btn-primary" :disabled="qBusy" @click="modalAction(`/api/queue/approve-ga/${selData.id}`, 'menyetujui klaim ini')">✅ Approve</button>
            <button v-if="canApprove" class="btn btn-sm btn-danger" :disabled="qBusy" @click="doReject(selData)">❌ Tolak</button>
          </template>
          <button v-if="selData.status === 'verified_ga' && canFinance" class="btn btn-sm btn-primary" :disabled="qBusy" @click="modalAction(`/api/queue/payout/${selData.id}`, 'mencairkan dana klaim ini')">💰 Cairkan</button>
          <button v-if="selData.status === 'os_finance' && canFinance" class="btn btn-sm btn-primary" :disabled="qBusy" @click="modalAction(`/api/queue/archive/${selData.id}`, 'mengarsipkan klaim ini')">📦 Arsipkan</button>
          <button v-if="selData.status === 'verified_ga' && canApprove" class="btn btn-sm" :disabled="qBusy" @click="modalAction(`/api/queue/unverify/${selData.id}`, 'mengembalikan klaim ke antrean GA')">↩️ Unverify</button>
          <button v-if="isAdmin" class="btn btn-sm btn-danger" :disabled="qBusy" @click="modalAction(`/api/queue/delete/${selData.id}`, 'menghapus PERMANEN transaksi ini')">🗑 Hapus</button>
        </div>
      </div>
    </Modal>
  </div>
</template>
