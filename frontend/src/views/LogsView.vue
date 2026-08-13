<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import LoadingState from '../components/LoadingState.vue'
import EmptyState from '../components/EmptyState.vue'
import ErrorState from '../components/ErrorState.vue'

const logs = ref([])
const loading = ref(true)
const err = ref('')
const fAction = ref('all')
const fRole = ref('all')
const branches = ref([])
const fBranch = ref('current')
const branchLoading = ref(false)
const page = ref(1)
const PER_PAGE = 25

async function loadBranches() {
  try {
    const d = await api('/api/branches/current')
    branches.value = (d && d.branches) || []
  } catch { branches.value = [] }
}

async function loadLogs() {
  loading.value = true; err.value = ''
  try {
    logs.value = await api('/api/audit-logs', {
      params: fBranch.value === 'current' ? {} : { branch: fBranch.value },
    }) || []
  } catch (e) { err.value = e.message }
  finally { loading.value = false }
}

const actions = computed(() => ['all', ...[...new Set(logs.value.map((l) => l.action).filter(Boolean))].sort()])
const roles = computed(() => ['all', ...[...new Set(logs.value.map((l) => l.user_type).filter(Boolean))].sort()])
const filtered = computed(() =>
  logs.value.filter((l) =>
    (fAction.value === 'all' || l.action === fAction.value) &&
    (fRole.value === 'all' || l.user_type === fRole.value)))
const pageCount = computed(() => Math.max(1, Math.ceil(filtered.value.length / PER_PAGE)))
const paged = computed(() => filtered.value.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE))
const todayCount = computed(() =>
  logs.value.filter((l) => new Date(l.created_at).toDateString() === new Date().toDateString()).length)

const actionLabel = (a) => (a || '—').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())

function prevPage() { page.value = Math.max(1, page.value - 1) }
function nextPage() { page.value = Math.min(pageCount.value, page.value + 1) }
function applyFilters() { page.value = 1 }

onMounted(async () => {
  loadBranches()
  loadLogs()
})
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="grow">
        <h3 style="margin:0;">📝 Audit Log</h3>
        <p class="muted" style="font-size:11px;">Jejak digital seluruh aktivitas (ISO/IEC 27001 · A.8.15 logging &amp; monitoring) · Khusus Admin</p>
      </div>
      <span class="badge badge-blue">📅 Hari ini: {{ todayCount }}</span>
      <span class="badge badge-gray">Total: {{ filtered.length }} / {{ logs.length }}</span>
    </div>

    <div v-if="loading"><LoadingState rows="4" label="Memuat audit log…" /></div>
    <div v-else-if="err"><ErrorState :message="err" @retry="loadLogs" /></div>
    <template v-else>
      <div class="card card-pad" style="margin-bottom:16px;">
        <div class="row">
          <div class="field" style="margin:0;flex:1;">
            <label>Filter Cabang</label>
            <select class="select" v-model="fBranch" @change="applyFilters; loadLogs()">
              <option value="current">Cabang aktif</option>
              <option v-for="b in branches" :key="b.code" :value="b.code">{{ b.name }} ({{ b.code }})</option>
            </select>
          </div>
          <div class="field" style="margin:0;flex:1;">
            <label>Filter Aksi</label>
            <select class="select" v-model="fAction" @change="applyFilters">
              <option v-for="a in actions" :key="a" :value="a">{{ a === 'all' ? 'Semua Aksi' : actionLabel(a) }}</option>
            </select>
          </div>
          <div class="field" style="margin:0;flex:1;">
            <label>Filter Peran</label>
            <select class="select" v-model="fRole" @change="applyFilters">
              <option v-for="r in roles" :key="r" :value="r">{{ r === 'all' ? 'Semua Peran' : r.toUpperCase() }}</option>
            </select>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>Waktu</th><th>User</th><th>Tipe</th><th>Aksi</th><th>Ref</th><th>Cabang</th><th>IP</th></tr></thead>
            <tbody>
              <tr v-for="l in paged" :key="l.id">
                <td class="muted">{{ l.created_at }}</td>
                <td><b>{{ l.user_name }}</b></td>
                <td><span class="badge badge-gray">{{ l.user_type }}</span></td>
                <td>{{ actionLabel(l.action) }}</td>
                <td>{{ l.transaction_id || '—' }}</td>
                <td><span v-if="l.branch_code" class="branch-chip">🏢 {{ l.branch_code }}</span><span v-else class="muted">—</span></td>
                <td class="muted">{{ l.ip_address || '—' }}</td>
              </tr>
              <tr v-if="!filtered.length"><td colspan="7" style="padding:0;"><EmptyState message="Tidak ada data dengan filter ini." icon="🔍" /></td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="pageCount > 1" class="pager" style="display:flex;align-items:center;gap:10px;justify-content:center;padding:12px;">
        <button class="btn btn-sm" :disabled="page <= 1" @click="prevPage">← Sebelumnya</button>
        <span class="muted" style="font-size:12px;">Halaman {{ page }} / {{ pageCount }} · {{ filtered.length }} entri</span>
        <button class="btn btn-sm" :disabled="page >= pageCount" @click="nextPage">Berikutnya →</button>
      </div>
    </template>
  </div>
</template>
